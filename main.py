from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Float, Date
import json, string
import time

app = Flask(__name__)

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

jsonfile1 = open('static/nutrients.json', 'r')
data_food = json.load(jsonfile1)


jsonfile2 = open('static/exercise.json', 'r')
data_exercise = json.load(jsonfile2)


from wtforms import SelectMultipleField, widgets
from markupsafe import Markup
 
 
class BootstrapListWidget(widgets.ListWidget):
 
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))
 
 
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# class SearchForm(FlaskForm):
#     __items = []
#     i = 0
#     for food_dict in data['Nutrition Values']:
#         __items.append((i,food_dict['Food']))
#         i+=1
#     items = MultiCheckboxField('Food Items', choices=__items, option_widget=None)
#     submit = SubmitField('Submit')

class NutritionForm(FlaskForm):
    food_items = TextAreaField("food-items", validators=[DataRequired()])
    submit = SubmitField('Submit')

app.config['SECRET_KEY'] = '1856a607f1d8fc35957b1566f7e9030a'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tech-stack.db"
DATABASE_URL = "sqlite:///health-tracker.db"

class ExerciseForm(FlaskForm):
    exercise_items = TextAreaField("exercise-items", validators=[DataRequired()])
    submit = SubmitField('Submit')


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

    def __str__(self):
        return f'{self.id}, Day={self.day}, Wt={self.weight}, Ht={self.height}, Protein={self.protein}, Cal={self.calories}, fat={self.fat}, SAt={self.Sat_fat}, carb={self.carbs}, fib={self.fiber})'

class Exercise(Base):
    __tablename__ = 'exercise'
    id = Column(Integer, primary_key=True)
    day = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    burnt_calories = Column(Float)

class NutritionSearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


class ExerciseSearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


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
    # remember = BooleanField('Remember me')
    submit = SubmitField('Log In')
        

@app.route("/home", methods=["GET", "POST"])
def home():
    __food_items = []
    _food_dict = {}
    i = 0
    for food_dict in data_food['Nutrition Values']:
        __food_items.append((i,food_dict['Food']))
        _food_dict[food_dict['Food']] = i
        i+=1
    form = NutritionForm()
    # selected_items = request.form.getlist('items')
    # print(selected_items)
    # print('hi')
    if request.method == 'POST':
        # push to database
        # print('hi')
        flash(f'Selcected Food Items: {", ".join(form.food_items.data)}', 'success')
        print(form.food_items.data)
        protein = 0
        calories = 0
        fat = 0
        Sat_fat = 0
        carbs = 0
        fiber = 0
        for i in form.food_items.data.split('; '):
            _i = i.split('(x')[0]
            print(type(_i))
            print(_i)
            food = data_food['Nutrition Values'][_food_dict[_i]]
            # print(food)
            protein += float(food['Protein'].replace(',','')) if food['Protein']!='t' else 0
            fat += float(food['Fat'].replace(',','')) if food['Fat']!='t' else 0
            Sat_fat += float(food['Sat.Fat'].replace(',','')) if food['Sat.Fat']!='t' else 0
            carbs += float(food['Carbs'].replace(',','')) if food['Carbs']!='t' else 0
            fiber += float(food['Fiber'].replace(',','')) if food['Fiber']!='t' else 0
            calories += float(food['Calories'].replace(',','')) if food['Calories']!='t' else 0
            
        nutrition_obj = Nutrition(
            day = time.localtime().tm_yday,
            protein = protein,
            calories = calories,
            fat = fat,
            Sat_fat = Sat_fat,
            carbs = carbs,
            fiber = fiber
        )
        print(nutrition_obj)
        session.add(nutrition_obj)
        session.commit()
        return redirect(url_for('home'))

    return render_template("home.html", title="Home", form=form, data=__food_items)

@app.route("/home2", methods=['GET', 'POST'])
def home2():
    __exercises_items = []
    _exercises_dict = {}
    i = 0
    for exercise in data_exercise["Exercise Values"]:
        e = exercise["Activity, Exercise or Sport (1 hour)"]
        __exercises_items.append((i,e))
        _exercises_dict[e] = i
        i+=1
    
    form = ExerciseForm()
    weight = 60
    if request.method == "POST":
        flash(f'Selcected Exercise Items: {", ".join(form.exercise_items.data)}', 'success')
        print(form.exercise_items)
        burnt_calories = 0
        for i in form.exercise_items.data.split('; '):
            _i = i.split('(x')[0]
            exercise = data_exercise['Exercise Values'][_exercises_dict[_i]]
            burnt_calories = float(weight)*float(exercise["Calories per kg"])
        
        exercise_obj = Exercise(
            day = time.localtime().tm_yday,
            burnt_calories = burnt_calories,
        )
        print(exercise_obj)
        session.add(exercise_obj)
        session.commit()
        return redirect(url_for('home2'))
    return render_template("home2.html", title="Home", form=form, data=__exercises_items)


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
                    return redirect(url_for('health', title='Home'))
                else:
                    flash("Incorrect password")
                    return render_template('login.html', form=form, title="Login") 

        flash("User doesn't exist")

        # return redirect(url_for('home'))
    return render_template("login.html", form=form, title='Login')

@app.route("/health", methods=["GET", "POST"])
def health():
    return render_template("health.html")

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