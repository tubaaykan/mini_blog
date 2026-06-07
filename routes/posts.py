import logging
import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from forms import CommentForm, PostForm
from models import Comment, Post
from utils.db import session_scope
from utils.decorators import handle_route_errors
from utils.images import generate_thumbnail, save_image, validate_image
from utils.security import sanitize_text


logger = logging.getLogger(__name__)
posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/new", methods=["GET", "POST"])
@handle_route_errors()
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        image_filename = None
        thumbnail_filename = None

        upload = form.image.data
        if upload and upload.filename:
            is_valid, error = validate_image(
                upload,
                current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
                current_app.config["ALLOWED_IMAGE_MIME_TYPES"],
            )
            if not is_valid:
                flash(error, "danger")
                return render_template("new.html", form=form)

            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            thumb_dir = os.path.join(upload_dir, "thumbs")
            image_filename = save_image(upload, upload_dir)
            thumbnail_filename = generate_thumbnail(upload_dir, image_filename, thumb_dir)

        post = Post(
            title=sanitize_text(form.title.data),
            content=sanitize_text(form.content.data),
            image_filename=image_filename,
            thumbnail_filename=thumbnail_filename,
            image_alt_text=sanitize_text(form.image_alt_text.data) if form.image_alt_text.data else None,
        )

        try:
            with session_scope() as session:
                session.add(post)
            flash("Post created.", "success")
            return redirect(url_for("main.index"))
        except SQLAlchemyError:
            logger.exception("Failed to create post")
            flash("Database error while creating post.", "danger")

    return render_template("new.html", form=form)


@posts_bp.route("/post/<int:post_id>")
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = CommentForm()
    return render_template("post.html", post=post, comment_form=comment_form)


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@handle_route_errors()
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        upload = form.image.data
        if upload and upload.filename:
            is_valid, error = validate_image(
                upload,
                current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
                current_app.config["ALLOWED_IMAGE_MIME_TYPES"],
            )
            if not is_valid:
                flash(error, "danger")
                return render_template("edit.html", form=form, post=post)

            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            thumb_dir = os.path.join(upload_dir, "thumbs")
            post.image_filename = save_image(upload, upload_dir)
            post.thumbnail_filename = generate_thumbnail(upload_dir, post.image_filename, thumb_dir)

        post.title = sanitize_text(form.title.data)
        post.content = sanitize_text(form.content.data)
        post.image_alt_text = sanitize_text(form.image_alt_text.data) if form.image_alt_text.data else None

        try:
            with session_scope():
                pass
            flash("Post updated.", "success")
            return redirect(url_for("posts.show_post", post_id=post.id))
        except SQLAlchemyError:
            logger.exception("Failed to update post")
            flash("Database error while updating post.", "danger")

    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.image_alt_text.data = post.image_alt_text

    return render_template("edit.html", form=form, post=post)


@posts_bp.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        with session_scope() as session:
            session.delete(post)
        flash("Post deleted.", "success")
    except SQLAlchemyError:
        logger.exception("Failed to delete post")
        flash("Database error while deleting post.", "danger")

    return redirect(url_for("main.index"))


@posts_bp.route("/comment/add/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            post_id=post.id,
            author=sanitize_text(form.author.data) or "Anonymous",
            content=sanitize_text(form.content.data),
        )
        try:
            with session_scope() as session:
                session.add(comment)
            flash("Comment added.", "success")
        except SQLAlchemyError:
            logger.exception("Failed to add comment")
            flash("Database error while adding comment.", "danger")
    else:
        flash("Comment validation failed.", "danger")

    return redirect(url_for("posts.show_post", post_id=post.id))


@posts_bp.route("/comment/delete/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id

    try:
        with session_scope() as session:
            session.delete(comment)
        flash("Comment deleted.", "success")
    except SQLAlchemyError:
        logger.exception("Failed to delete comment")
        flash("Database error while deleting comment.", "danger")

    return redirect(url_for("posts.show_post", post_id=post_id))
