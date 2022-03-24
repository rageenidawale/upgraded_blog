from flask import Flask, render_template, request
import requests
import smtplib

MY_EMAIL = ""
PASSWORD = ""

posts = requests.get("https://api.npoint.io/710254173db50d6799fb").json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
            print(blog_post["image_url"])
    return render_template("post.html", post=requested_post)


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
