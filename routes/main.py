from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from sqlalchemy import or_

from forms import CommentForm
from models import Post


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    query_text = request.args.get("q", "").strip()
    date_filter = request.args.get("date", "").strip()
    page = request.args.get("page", default=1, type=int)

    query = Post.query.order_by(Post.created_at.desc())

    if query_text:
        like = f"%{query_text}%"
        query = query.filter(or_(Post.title.ilike(like), Post.content.ilike(like)))

    if date_filter:
        try:
            day = datetime.strptime(date_filter, "%Y-%m-%d")
            next_day = day + timedelta(days=1)
            query = query.filter(Post.created_at >= day, Post.created_at < next_day)
        except ValueError:
            pass

    pagination = query.paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)

    return render_template(
        "index.html",
        posts=pagination.items,
        pagination=pagination,
        q=query_text,
        date=date_filter,
        comment_form=CommentForm(),
    )
