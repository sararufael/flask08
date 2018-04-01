from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from config import *
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
app.config['UPLOAD_FOLDER'] = '/tmp/'
db = SQLAlchemy(app)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route('/add')
def add():
    return render_template("form.html")


@app.route('/processform', methods=['GET', 'POST'])
def processform():
    content = request.form['content']
    f = request.files['image']

    filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
    f.save(filename)

    res = cloudinary.uploader.upload_large(filename, resource_type="auto")
    img_url = res['secure_url']
    post = Post(content, img_url)

    db.session.add(post)
    db.session.commit()

    # cleanup
    os.remove(filename)

    return redirect(url_for('index'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50))
    image = db.Column(db.String(50))

    def __init__(self, content, image):
        self.content = content
        self.image = image


if __name__ == '__main__':
    db.create_all()
    app.run()