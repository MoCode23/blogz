from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# creating a persistent class for the database
class Blog(db.Model):

    # data fields that should go into columns
    id = db.Column(db.Integer, primary_key=True)     # start with primary ID
    title = db.Column(db.Text)
    post = db.Column(db.Text)

    def __init__(self, title, post):
        self.title = title
        self.post = post 

# DISPLAYS IND BLOG POSTS
@app.route('/blog')
def show_blog():
    post_id = request.args.get('id')
    if (post_id):
        ind_post = Blog.query.get(post_id)
        return render_template('ind_post.html', ind_post=ind_post)
    else:
        # queries database for all existing blog entries
        # post_id = request.args.get('id')
        all_blog_posts = Blog.query.all()
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

        # THIS CREATES EMPTY STRINGS FOR THE ERROR MESSAGES
        title_error = ""
        blog_entry_error = ""

        # assigning variable to blog title from entry form
        post_title = request.form['blog_title']
        # assigning variable to blog post from entry form
        post_entry = request.form['blog_post']
        # creating a new blog post variable from title and entry
        post_new = Blog(post_title, post_entry)

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
                title_error = "Enter dat title Son!"
                blog_entry_error = "Enter dat text dawg!"
                return render_template('new_post.html', blog_entry_error=blog_entry_error, title_error=title_error)
            elif not empty_val(post_title):
                title_error = "Where's my title bro!"
                return render_template('new_post.html', title_error=title_error, post_entry=post_entry)
            elif not empty_val(post_entry):
                blog_entry_error = "I don't see no text up in hurr!"
                return render_template('new_post.html', blog_entry_error=blog_entry_error, post_title=post_title)

    else:
        return render_template('new_post.html')

@app.route('/')
def index():
    return redirect('/blog')
        
if __name__ == '__main__':
    app.run()