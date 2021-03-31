from flask import Flask, render_template

'''
"Filters"
safe
capitalize
lower
upper
title
trim
striptags
'''

# Create a Flask Instance
app = Flask(__name__)

# Create a route decorator
@app.route('/')

def index():
	first_name = "Ian"
	stuff = "This is <strong>Bold</strong> Text"
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


	