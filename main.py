from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Float
import json, string

app = Flask(__name__)

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

jsonfile = open('file.json', 'r')
data = json.load(jsonfile)
values = data['Nutrition Values']
foods = []

for value in values:
    food = value["Food"]
    foods.append(food)

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')



app.config['SECRET_KEY'] = '1856a607f1d8fc35957b1566f7e9030a'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tech-stack.db"
DATABASE_URL = "sqlite:///health-tracker.db"

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    health_score = Column(Integer)
    bmi = Column(Float)

class Nutrition(Base):
    __tablename__ = 'nutrition'
    id = Column(Integer, primary_key=True)
    day = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    protein = Column(Float)
    calories = Column(Float)
    fat = Column(Float)
    Sat_fat = Column(Float)
    carbs = Column(Float)
    fiber = Column(Float)

class Exercise(Base):
    __tablename__ = 'exercise'
    id = Column(Integer, primary_key=True)
    day = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    burnt_calories = Column(Float)
    running = Column(Float)
    cycling = Column(Float)
    pushups = Column(Integer)
    squats = Column(Integer)
    plank = Column(Float)

# Create the table in the database
Base.metadata.create_all(engine)

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                         validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username/Email', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')
        

@app.route("/home", methods=["GET", "POST"])
def home():

    form = SearchForm()
    selected_values = []
    
    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search.data
        filtered_values = [food for food in foods if search_term in food]
        return render_template('home.html', title="Home", form=form, results=filtered_values, selected_values=selected_values)

    return render_template("home.html", title="Home", form=form, results=[], selected_values=selected_values)

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    
    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        users = session.query(Users.username, Users.password, Users.email)
        
        for user in users:
            if(user.username == username or user.email == username):
                if(user.password == password):
                    flash("Login successful!", "success")
                    return redirect(url_for('home', title='Home'))
                else:
                    flash("Incorrect password")
                    return render_template('login.html', form=form, title="Login") 

        flash("User doesn't exist")

        # return redirect(url_for('home'))
    return render_template("login.html", form=form, title='Login')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    form = RegistrationForm()
   
    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data
        email = form.email.data
        print(username)
        users = session.query(Users.username, Users.password, Users.email)
        print(users)
        for user in users:
            if(user.username == username):
                flash("User already exists!!! Try different username")
                return render_template("signup.html", title="Signup")

        new_user = Users(username=username, password=password, email=email)
        session.add(new_user)
        session.commit()
        print(users)
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for('login', title="Home"))
    return render_template("signup.html", form=form, title="Signup")

if(__name__) == "__main__":
    app.run(debug=True)