from models import Comment, Post, db


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_post_and_search(client, app):
    response = client.post(
        "/new",
        data={
            "title": "Hello World",
            "content": "This is valid content for testing post creation.",
            "image_alt_text": "sample image",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        post = Post.query.filter_by(title="Hello World").first()
        assert post is not None

    search = client.get("/?q=Hello")
    assert b"Hello World" in search.data


def test_add_comment(client, app):
    with app.app_context():
        post = Post(title="Post", content="Content long enough for validation")
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.post(
        f"/comment/add/{post_id}",
        data={"author": "tester", "content": "Nice post"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        assert Comment.query.count() == 1


def test_validation_blocks_short_title(client):
    response = client.post(
        "/new",
        data={"title": "ab", "content": "This is valid content for rejection test."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Post created." not in response.data
