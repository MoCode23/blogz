from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'df8f78dsa83mnk'

# creating a class for the blog
class Blog(db.Model):

    # specify the data fields that should go into columns
    id = db.Column(db.Integer, primary_key=True)     # start with primary ID
    # these are both set as Text instead of String so there is not a character limit
    title = db.Column(db.Text)  # blog title
    post = db.Column(db.Text)   # blog post text
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post 
        self.owner = owner

# creating a class for the users
class User(db.Model):

    # specify the data fields that should go into columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

# this will run at the beginning of every request to see if the user is logged in
@app.before_request
def require_login():
    # allowed routes are the function name, not the directory
    allowed_routes = ['login_user', 'show_blog', 'add_user', 'index', 'static']
    # if not in white list, and user not logged in, it will redirect to login page
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    all_users = User.query.distinct()
    return render_template('index.html', list_all_users=all_users)

# DISPLAYS IND BLOG POSTS
@app.route('/blog')
def show_blog():
    post_id = request.args.get('id')
    single_user_id = request.args.get('owner_id')
    if (post_id):
        ind_post = Blog.query.get(post_id)
        return render_template('ind_post.html', ind_post=ind_post)
    else:
        if (single_user_id):
            ind_user_blog_posts = Blog.query.filter_by(owner_id=single_user_id)
            return render_template('singleUser.html', posts=ind_user_blog_posts)
        else:
            # queries database for all existing blog entries
            # post_id = request.args.get('id')
            all_blog_posts = Blog.query.all()
            # first of the pair matches to {{}} in for loop in the .html template, second of the pair matches to variable declared above
            return render_template('blog.html', posts=all_blog_posts)


# VALIDATION FOR EMPTY FORM
def empty_val(x):
    if x:
        return True
    else:
        return False

# THIS HANDLES THE REDIRECT (SUCCESS) AND ERROR MESSAGES (FAILURE)

@app.route('/newpost', methods=['POST', 'GET'])
def add_entry():

    if request.method == 'POST':

        # assigning variable to blog title from entry form
        post_title = request.form['blog_title']
        # assigning variable to blog post from entry form
        post_entry = request.form['blog_post']
        # assigning owner variable to blog post from user signup
        owner = User.query.filter_by(username = session['username']).first()
        # creating a new blog post variable from title and entry
        post_new = Blog(post_title, post_entry, owner)

        # if the title and post entry are not empty, the object will be added
        if empty_val(post_title) and empty_val(post_entry):
            # adding the new post (this matches variable created above) as object 
            db.session.add(post_new)
            # commits new objects to the database
            db.session.commit()
            post_link = "/blog?id=" + str(post_new.id)
            return redirect(post_link)
        else:
            if not empty_val(post_title) and not empty_val(post_entry):
                flash('I aint see not title or post bro', 'error')
                return render_template('new_post.html', post_title=post_title, post_entry=post_entry)
            elif not empty_val(post_title):
                flash('Where is my title son?', 'error')
                return render_template('new_post.html', post_entry=post_entry)
            elif not empty_val(post_entry):
                flash('Aint nothin here to read jack!', 'error')
                return render_template('new_post.html', post_title=post_title)

    # DISPLAYS NEW BLOG ENTRY FORM
    else:
        return render_template('new_post.html')


@app.route('/signup', methods=['POST', 'GET'])
def add_user():

    if request.method == 'POST':

        # - - - - - VARIABLES FOR DATA FROM SIGNUP FORM
        # assigning variable to username from signup form
        user_name = request.form['username']
        # assigning variable to user password from signup form
        user_password = request.form['password']
        # assigning variable to user password from signup form
        user_password_validate = request.form['password_validate']


        # - - - - - USER SIGNUP VALIDATION

        # if the username or password is blank, flash error
        if not empty_val(user_name) or not empty_val(user_password) or not empty_val(user_password_validate):
            flash('All fields must be filled in', 'error')
            return render_template('signup.html')

        # if the password is blank, flash error
        if user_password != user_password_validate:
            flash('Yo password aint da same', 'error')
            return render_template('signup.html')

        if len(user_password) < 3 and len(user_name) < 3:
            flash('Username and password gotta be 3 thangs or more', 'error')
            return render_template('signup.html')

        if len(user_password) < 3:
            flash('At least 3 thangs ma dude', 'error')
            return render_template('signup.html')

        if len(user_name) < 3:
            flash('At least 3 thangs ma guy', 'error')
            return render_template('signup.html')

        
        # - - - - - ADD NEW USER

        # queries db to see if there is an existing user with name username
        # username is coming from class, user_name from variable above
        # TODO - clean up this naming
        existing_user = User.query.filter_by(username=user_name).first()
        # if there are no existing users with same username, creates new user
        if not existing_user: 
            # creating a new user
            user_new = User(user_name, user_password) 
            # adds new user
            db.session.add(user_new)
            # commits new objects to the database
            db.session.commit()
            # adds username to this session so they will stay logged in
            session['username'] = user_name
            flash('New user created', 'success')
            return redirect('/newpost')
        else:
            flash('Some already got dat username, AbeBROham', 'error')
            return render_template('signup.html')

    # DISPLAYS NEW BLOG ENTRY FORM
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        # creates variables for information being passed in login form
        username = request.form['username']
        password = request.form['password']

        # - - - - - LOGIN VALIDATIONS

        if not username and not password:
            flash('Username and password caint be blank dawg', 'error')
            return render_template('login.html')
        if not username:
            flash('Where yo username', 'error')
            return render_template('login.html')
        if not password:
            flash('I aint got no password', 'error')
            return render_template('login.html')
        
        # query matches username to existing username in the db
        # this will net the first result, there should only be one result bc field is unique
        # if there are no users with the same username, the result with be none
        user = User.query.filter_by(username=username).first()

        # - - - - - MORE LOGIN VALIDATIONS

        # checks username, renders error if not correct
        if not user:
            flash('This aint no username I seen bafo', 'error')
            return render_template('login.html')
        # checks password, renders error if incorrect
        if user.password != password:
            flash('Ah Ah Ah, you aint say da magic word', 'error')
            return render_template('login.html')

        # - - - - - LOGIN IN USER

        # "if user" checks to see if user exists
        # "if user.password == password" checks to see if the pw provided matches pw in db
        if user and user.password == password:
            # saves username to session
            session['username'] = username
            return redirect('newpost')

    return render_template('login.html')
        
@app.route('/logout')
def logout():
    del session['username']
    flash('You are logged out', 'success')
    return redirect('/blog')

# only runs when the main.py file run directly
if __name__ == '__main__':
    app.run()