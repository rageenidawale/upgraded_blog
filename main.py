from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from typing import Callable
import requests
import smtplib
import datetime

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

MY_EMAIL = ""
PASSWORD = ""

posts = requests.get("https://api.npoint.io/710254173db50d6799fb").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class SQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Text: Callable


db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def home():
    all_posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=all_posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    return render_template("post.html", post=requested_post)


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        x = datetime.datetime.now()
        date = f"{x.strftime('%B')} {x.strftime('%d')}, {x.strftime('%Y')}"
        new_blog_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=date,
            body=form.body.data,
            author=form.author.data,
            img_url=form.img_url.data
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("make-post.html", form=form)


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.author = form.author.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for("show_post", index=post.id))
    return render_template("make-post.html", form=form, isEdit=True)


@app.route("/delete")
def delete():
    post_id = request.args.get('post_id')

    # DELETE A RECORD BY ID
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    is_message_sent = False
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        is_message_sent = True
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg=f"Subject:New Message\n\nName: {name} \nEmail: {email} \nPhone: {phone} \nMessage: {message}"
            )
    return render_template("contact.html", is_message_sent=is_message_sent)


if __name__ == "__main__":
    app.run(debug=True)
