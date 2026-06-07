from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileSize
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=120)])
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=10, max=5000)])
    image = FileField("Image", validators=[Optional(), FileSize(max_size=4 * 1024 * 1024)])
    image_alt_text = StringField("Image description", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Save")


class CommentForm(FlaskForm):
    author = StringField("Name", validators=[Optional(), Length(max=60)])
    content = TextAreaField("Comment", validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField("Add comment")
