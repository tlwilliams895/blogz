from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
# from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:unreasonable@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "buildsBlogsForFun"


# If blog title is blank/empty, return True
# to render error message to User
def title_error(blog_title):
    if len(blog_title) > 0:
        return False
    else:
        return True


# If blog_body is blank/empty, return True
# to render error message to User
def body_error(blog_body):
    if len(blog_body) > 0:
        return False
    else:
        return True


# create Blog object for db
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    body = db.Column(db.String(800))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog, blogbody, owner):
        self.name = blog
        self.body = blogbody
        self.owner = owner


# create User object for db
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    # signifies a relationship between the blog table and this user
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


# Login and SignUp Section - Enable visitors to the web app to create an account and login
# The Login Page (Red)
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Success! You're logged in!")
            return redirect('/index')
        else:
            flash("Improper User Credentials or Non-Existent User!", 'error')

    return render_template('login.html')


# The SignUp/Register Page (Pink) -
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/index')
        else:
            return '<h1>Duplicate User, Try Again!</h1>'

    return render_template('signup.html')


# The Log-Out page to redirect user to index page (if logged out)
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/index')


# Route User to signup page to access The Login Page,
# if not logged in or registered to app
@app.before_request
def require_login():
    # For blogs and index pages
    user_id = str(request.args.get('user'))
    blog_id = str(request.args.get('id'))

    allowed_routes = ['login', 'blogs', 'signup', 'index']

    # redirect to The Index Page if user not logged in or
    # on an allowed routes page (above)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/index')


# The Index Page (Main/Home Page - blueviolet)
@app.route('/index', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


# Route '/' page to The Index Page (Main/Home)
@app.route('/')
def main():
    return render_template('index.html')


# Displays blog posts filtered/sorted by user_id
@app.route('/blogs', methods=['POST', 'GET'])
def blogs_display():

    user_id = str(request.args.get('user'))
    owner = Blog.query.filter_by(id=user_id).first()

    blog_id = str(request.args.get('id'))
    blogs = Blog.query.filter_by(owner=owner).all()
    myblog = Blog.query.get(blog_id)

    # return redirect('/blogs?blogs=' + str(myblog.id))

    return render_template('blogs.html', blogs=blogs, myblog=myblog)

# New blogs (newpost.html)
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        blog_title = request.form['blog']
        blog_body = request.form['blogbody']
        title_error_msg = ''
        body_error_msg = ''

        if title_error(blog_title):
            title_error_msg = "Enter blog title here"
            return render_template('newpost.html', title_error=title_error_msg, body_error=body_error_msg, blog_body=blog_body)
        if body_error(blog_body):
            body_error_msg = "Input blog content here"
            return render_template('newpost.html', title_error=title_error_msg, body_error=body_error_msg, blog_title=blog_title)

        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blogs?id=' + str(new_post.id))
    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()
