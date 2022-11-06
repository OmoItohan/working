import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ContactForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd

# Route from the Home page
@app.route("/")
@app.route("/home")
def home():
    # Gets all the Posts in the dtatbade
    posts = Post.query.all()
    return render_template('home.html', posts=posts)



# Route for the about Page
@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About' )




# Route for the Contact Page
@app.route("/contactus", methods=["GET","POST"])
def get_contact():
    form = ContactForm()
    # here, if the request type is a POST we get the data on contact
    #forms and save them else we return the contact forms html page
    if request.method == 'POST':
        name =  request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        res = pd.DataFrame({'name':name, 'email':email, 'subject':subject ,'message':message}, index=[0])
        res.to_csv('./contactusMessage.csv')
        print(res)
        return redirect(url_for('home'))
    else:
        return render_template('contact.html', form=form)

# Route for the register form
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Converts password to unreadbale string of characters
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Creates user data
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # ADDING THE USER DATA TO THE DATABASE
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # CHECK THAT USER IS AUTHENTICATED
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Find a user based on their email
        user = User.query.filter_by(email=form.email.data).first()
        # confirm that the useremail and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Rute to logout user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture ,path):
    # Generates random text  strin gin hexadecimal
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, path, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Checks that an image is coming from the form
        if form.picture.data:
            # saves and updates the image 
            picture_file = save_picture(form.picture.data, 'static/profile_pics')
            current_user.profile_img = picture_file
            # updates other inputs coming from the form
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_img = url_for('static', filename='profile_pics/' + current_user.profile_img)
    return render_template('account.html', title='Account',
                           profile_img=profile_img, form=form)


# Form to create new post on server
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
      
        if form.picture.data:
         picture_file = save_picture(form.picture.data, 'static/uploads')
         current_user.image_file = picture_file
         print(picture_file)
        flash('Image successfully uploaded and displayed below')
        post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=picture_file)
        db.session.add(post)
        db.session.commit()
        # flash('Your post has been created!', 'success')
        return redirect(url_for('post', post_id=post.id))

        
  
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post' ,)

# Craetes new post on server
@app.route("/post/<int:post_id>")
def post(post_id):
    # Geta all post in database
    posts =Post.query.all()
    # Gets all post based on the id
    post = Post.query.get_or_404(post_id)
    image_file = url_for('static', filename='uploads/' + post.image_file)
    # print(image_file)
    return render_template('post.html', title=post.title, post=post, posts=posts, image_file=image_file )

# Updates Post on Server
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if(form.picture.data):
         picture_file = save_picture(form.picture.data, 'static/uploads')
         post.image_file = picture_file
        post.title = form.title.data
        post.content = form.content.data
      
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')



# Deletes Post on server
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))