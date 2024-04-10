from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from sqlalchemy import asc,desc

app = Flask(__name__)
DATABASE = 'site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ranking = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)

class LinkHandle:
    
    def add_url(self, url, name, description):
        new_link = Link(url=url, name=name, description=description)
        db.session.add(new_link)
        db.session.commit()
    
    def upvote(link_id):
        link = Link.query.get(link_id)
        link.ranking += 1
        db.session.commit()

    def downvote(link_id):
        link = Link.query.get(link_id)
        link.ranking -= 1
        db.session.commit()

link_handle = LinkHandle()

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL,
            name TEXT NOT NULL,
            date_added DATE NOT NULL,
            ranking INTEGER NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

    links = Link.query.all()
    if len(links) < 5:
        link_handle.add_url('https://speak-ez.net', 'speak-easy', 'converse with AI in a new , language language language language language language language language language language language ')

@app.route('/')
def index():
    create_table() # Ensure table exists
    links = Link.query.order_by(desc(Link.ranking)).all()
    for link in links:
        link.id = str(link.id)
        link.date_added = str(link.date_added)[:10]
    return render_template('index.html', links=links)

from flask import request

@app.route('/vote/<int:id>', methods=['POST'])
def vote(id):
    if request.form['vote'] == 'up':
        LinkHandle.upvote(id)
    elif request.form['vote'] == 'down':
        LinkHandle.downvote(id)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
