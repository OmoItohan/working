from datetime import datetime
from flaskblog import db, login_manager,app
from flask_login import UserMixin

# Tells flask-login how to load a users from an id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User MOdel
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_img = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

# Return a string contaning  printabale representation of the object
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_img}')"
 
    with app.app_context():
      db.create_all()
     
# Posts Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_file = db.Column(db.String(20))
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.image_file}')"
    
    with app.app_context():
         db.create_all()
     