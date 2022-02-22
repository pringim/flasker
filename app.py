from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

'''
"wtforms field types"
and filters ..see 'flask-values.text'
'''

# Create a Flask Instance
app = Flask(__name__)

ckeditor = CKEditor(app)
# Add Database
# Old SQLite DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pringim1@localhost/our_users'

# Deploy app with Postgres d/b on Heroku -- config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yfmgihlkltyvde:937716bc15f1e617504cca605a56e99af98c82bbb30947a60d731efb926f6e71@ec2-44-199-52-133.compute-1.amazonaws.com:5432/d18dtpgektsbrp'

app.config['SECRET_KEY'] = "sirob"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Pass Data into Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 1:
		return render_template('admin.html')
	else:
		flash('Sorry ! Admin Access Denied')
		return render_template('dashboard.html')

# Create Search Function
@app.route('/search', methods=['POST'])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Get data from submitted form
		post.searched = form.searched.data
		# Query the Database
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()
		return render_template("search.html", form=form, searched=post.searched, posts=posts)

# Create Login Page
@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check the Hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash('Login Successful !')
				return redirect(url_for('dashboard'))
			else:
				flash('Wrong Password..Try Again !')
		else:
			flash('User Not Found..Try Again !')

	return render_template('login.html', form=form)

# Create Logout
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
	logout_user()
	flash("You have Logged Out...Mind how you Go !!")
	return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	return render_template('dashboard.html')

# Delete Posts

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster.id:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()
			flash('Blog Post was Deleted !')
		except:
			flash('Whoops ! There was a Problem Deleting the Post: Try Again..')


	else:
		flash('Whoops ! You are not Authorised to Delete this Post.')

	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)

# Display all posts

@app.route('/posts')
def posts():
	# Grab all the posts from the d/b
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)

# Display individual post
@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)

# Edit individual post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		# post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update Database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated !!")
		return redirect(url_for('post', id=post.id))
		#return redirect(url_for('posts', posts=posts))

	if current_user.id == post.poster.id:
		form.title.data = post.title
		# form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)
	else:
		flash('Whoops ! You are not Authorised to Edit this Post.')
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


# Add Posts Page
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
		# Clear the Form
		form.title.data= ""
		form.content.data= ""
		#form.author.data= ""
		form.slug.data= ""

		# Add to the database
		db.session.add(post)
		db.session.commit()

		flash("Blog Post Submitted Successfully !")
		return redirect(url_for('posts', posts=posts))
	return render_template("add_post.html", form=form)

# Json thing
@app.route('/date')
def get_current_date():
	return {"Date": date.today()}




@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)

		db.session.commit()
		flash("User Deleted Successfully !! ")
		our_users = Users.query.order_by(Users.date_added)
		#return render_template("add_user.html", form=form,
		#name=name, our_users=our_users)

	except:
		flash('Whoops ! There was a probelm deleting User, try again..')
		#return render_template("add_user.html", form=form,
		#name=name, our_users=our_users)
	return render_template("add_user.html", form=form, name=name, our_users=our_users)

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
			name_to_update.name = request.form['name']
			name_to_update.email = request.form['email']
			name_to_update.favorite_color = request.form['favorite_color']
			name_to_update.username = request.form['username']
			name_to_update.about_author = request.form['about_author']
			name_to_update.profile_pic = request.files['profile_pic']

			# Grab Image filename
			pic_filename = secure_filename(name_to_update.profile_pic.filename)
			# Set UUID
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			# Save The Image
			saver = request.files['profile_pic']
			name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
			# Change to string to save to db
			name_to_update.profile_pic = pic_name

			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
				flash("User Updated Successfully !")
				return render_template("update.html", form=form,
					name_to_update=name_to_update, id=id)
			except:
				flash("Error with Update..try again !")
				return render_template("update.html", form=form,
					name_to_update=name_to_update, id=id)
	else:
			return render_template("update.html", form=form,
				name_to_update=name_to_update, id=id )

# Create a route decorator
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			# Hash the password!!!
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
						 favorite_color=form.favorite_color.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.favorite_color.data = ''
		form.password_hash.data = ''

		flash("User Added Successfully!")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html",
		form=form,
		name=name,
		our_users=our_users)

# Create a route decorator
@app.route('/')

def index():
	first_name = "Ian"
	stuff = "This is <strong>Bold</strong>Text"
	fav_food = ["Curry", "Burger king", "Salads", 42]
	return render_template("index.html",
		first_name=first_name, stuff=stuff, fav_food = fav_food)

@app.route('/user/<name>')
# localhost:5000/user/Ian
def user(name):
	return render_template("user.html", user_name=name)

# Create Custom Error Pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	# Validate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''
		# Look up user by email entered
		pw_to_check = Users.query.filter_by(email=email).first()

		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html", email = email,
						   password = password, pw_to_check = pw_to_check, passed = passed, form = form)

@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully !")
	return render_template("name.html", name = name, form = form)

# Create a blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	# author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	favorite_color = db.Column(db.String(120))
	about_author = db.Column(db.Text(), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(120), nullable=True )
	# Do some password stuff!
	password_hash = db.Column(db.String(128))
	# User can have many posts
	posts = db.relationship('Posts', backref='poster')
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute !')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

		# Create A String
	def __repr__(self):
		return '<Name %r>' % self.name
