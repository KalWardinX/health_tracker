from flask import Flask, render_template, flash, redirect, url_for, request, session
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
from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import LoginManager
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
import pandas as pd

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

class NutritionForm(FlaskForm):
    food_items = TextAreaField("food-items", validators=[DataRequired()])
    submit = SubmitField('Submit')

app.config['SECRET_KEY'] = '1856a607f1d8fc35957b1566f7e9030a'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tech-stack.db"
DATABASE_URL = "sqlite:///health-tracker.db"

class ExerciseForm(FlaskForm):
    duration = IntegerField("Exercise Duration", validators=[DataRequired()])
    exercise_items = TextAreaField("exercise-items", validators=[DataRequired()])
    submit = SubmitField('Submit')


class HeightWeightForm(FlaskForm):
    height = FloatField('Height')
    weight = FloatField('Weight')
    submit = SubmitField('Update')

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db_session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    bmi = Column(Float)
    weight = Column(Float)
    height = Column(Float)

class Nutrition(Base):
    __tablename__ = 'nutrition'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"))
    day = Column(String)
    protein = Column(Float, default=0.0)
    calories = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    Sat_fat = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    
    def __str__(self):
        return f'{self.id}, Day={self.day}, Protein={self.protein}, Cal={self.calories}, fat={self.fat}, SAt={self.Sat_fat}, carb={self.carbs}, fib={self.fiber})'

class Exercise(Base):
    __tablename__ = 'exercise'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"))
    day = Column(String)
    burnt_calories = Column(Float, default=0.0)
    exercise_names = Column(String)
    duration = Column(Integer, default=0)

class Health(Base):
    __tablename__ = 'health'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"))
    day = Column(String)
    health_score = Column(Integer, default=0)

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
    height = FloatField('Height', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username/Email', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
        
###########################
# ** HELPER FUNCTIONS **  #
###########################

# UPDATE Health Table
def update_health(username, day, is_nutrition_changed, is_exercise_changed):
    # nutrition score calculation
    nutrition_score = 0
    if is_nutrition_changed:
        nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()
        nutrition_score = 0.25*nutrition_data.protein + 0.1*nutrition_data.calories + 0.15*nutrition_data.fat + 0.1*nutrition_data.Sat_fat + 0.2*nutrition_data.carbs + 0.2*nutrition_data.fiber

    # exercise score calculation
    exercise_score = 0
    if is_exercise_changed:
        exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()
        exercise_score = exercise_data.burnt_calories

    # health score calculation
    health_score = round(0.7*nutrition_score + 0.3*exercise_score,2)
    
    # commit health score
    health_data = db_session.query(Health).filter_by(username=username, day=day).first()
    
    if (health_data):
        health_score += health_data.health_score
        db_session.query(Health).filter_by(username=username, day=day).update({"health_score":health_score})
    else:
        health_obj = Health(
            username = username,
            day = day,
            health_score = health_score
        )
        db_session.add(health_obj)
    
    db_session.commit()

# GET LEADERBOARD data
def get_top_10(day):
    leaderboard = []
    user_health_data = db_session.query(Health).filter_by(day=day).order_by(Health.health_score.desc()).limit(10).all()
    for i in range(min(10, len(user_health_data))):
        leaderboard.append({
            'username': user_health_data[i].username,
            'health_score': round(user_health_data[i].health_score, 2)
        })
    return leaderboard

# GET EXERCISE Data
def get_exercises(username, day):
    exercises_list = []
    exercises = db_session.query(Exercise).filter_by(username=username, day=day).first()
    if(exercises):
        exercises = exercises.exercise_names
        i = 0
        for exercise in exercises.split('; '):
            if(i==10):
                break
            if ( exercise != '' ):
                exercises_list.append(exercise)
                i+=1

    return exercises_list

# UPDATE HEIGHT
def update_height(username, height):
    db_session.query(Users).filter_by(username = username).update({'height': height})
    db_session.commit()

# UPDATE WEIGHT
def update_weight(username, weight):
    db_session.query(Users).filter_by(username = username).update({'weight': weight})
    db_session.commit()

# UPDATE BMI
def update_bmi(username):
    height = db_session.query(Users).filter_by(username = username).first().height
    weight = db_session.query(Users).filter_by(username = username).first().weight
    bmi = round((weight**2)/height, 2)
    db_session.query(Users).filter_by(username = username).update({'bmi': bmi})
    db_session.commit()

# CONVERT TO DF
def convert_to_df(data, tuple_length):
    
    i = len(data)
    array = []

    for j in range(i):
        temp = []
        for y in range(tuple_length):
            temp.append(data[j][y])
        array.append(temp)

    df = pd.DataFrame(data)

    return df

# MAKE PLOTS AND SAVE THEM AS .png
def make_plots(df, username, title):

    width = 0.2
    # CALORIE PLOT
    if(title == "Calories"):
 
        calories_burnt = range(len(df['Date'])) 
        calories_intake = [pos + width for pos in calories_burnt]

        plt.figure(figsize=(5, 5))

        plt.bar(df['Date'], df['Calories Burnt'], width=width, label='Calories Burnt', color='lightgreen', edgecolor='black')
        plt.bar(calories_intake, df['Calories Consumed'], width=width, label='Calories Consumed', color='skyblue', edgecolor='black')

        plt.xticks([pos + width / 2 for pos in calories_burnt], df['Date'], fontsize=10)  
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Amount (kcal)', fontsize=12)
        plt.title('Calories Burnt vs Consumed Over Time', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1500)
        plt.clf()

    # Nutrient plot
    elif(title == "Nutrients"):
       
        protein = range(len(df['Date'])) 
        fat = [x + width for x in protein]
        Sat_fat = [x + width for x in fat]
        carbs = [x + width for x in Sat_fat]
        fiber = [x + width for x in carbs]

        plt.figure(figsize=(7, 5))

        plt.bar(df['Date'], df['protein'], width=width, label='Protein', color='red', edgecolor='black')
        plt.bar([pos for pos in fat], df['fat'], width=width, label='Fat', color='yellow', edgecolor='black')
        plt.bar([pos for pos in Sat_fat], df['Sat_fat'], width=width, label='Sat_fat', color='salmon', edgecolor='black')
        plt.bar([pos for pos in carbs], df['carbs'], width=width, label='Carbs', color='skyblue', edgecolor='black')
        plt.bar([pos for pos in fiber], df['fiber'], width=width, label='Fiber', color='lightgreen', edgecolor='black')


        plt.xticks([pos + width*2 for pos in protein], df['Date'], fontsize=10)  
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Amount (gm)', fontsize=12)
        plt.title('Nutrients Consumed Over Time', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1500)
        plt.clf()

    # HEALTH_SCORE PLOT    
    else:

        health = range(len(df['Date'])) 

        plt.figure(figsize=(5, 5))

        plt.bar(df['Date'], df['health_score'], width=width, label='Health Score', color='darkblue', edgecolor='black')

        plt.xticks([pos for pos in health], df['Date'], fontsize=10)  
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Health Score', fontsize=12)
        plt.title('Health Score vs Time', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1500)
        plt.clf()

def make_plot_line(df, username, title):
    
    plt.plot(df['Date'], df['health_score'], color='darkblue', marker='X', linewidth=2)
    plt.xlabel("Date")
    plt.ylabel("Health Score")
    plt.title(title)
    plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1500)
    plt.clf()

def update_plots():
    username = session['username']

    health_score = db_session.query(Health.day, Health.health_score).filter_by(username=username).order_by(Health.day.desc()).all()
    calorie_burnt = db_session.query(Exercise.day, Exercise.burnt_calories).filter_by(username=username).order_by(Exercise.day.desc()).all()
    calorie_intake = db_session.query( Nutrition.day, Nutrition.calories).filter_by(username=username).order_by(Nutrition.day.desc()).all()
    
    other_nutrients = db_session.query(Nutrition.day, Nutrition.protein, Nutrition.fat, Nutrition.Sat_fat, Nutrition.carbs, Nutrition.fiber).filter_by(username=username).order_by(Nutrition.day).all()
    
    health_score_df = convert_to_df(health_score, 2)
    calorie_burnt_df = convert_to_df(calorie_burnt, 2)
    calorie_intake_df = convert_to_df(calorie_intake, 2)
    other_nutrients_df = convert_to_df(other_nutrients,5)
    # print(health_score_df)
    calorie_plot_df = pd.merge(calorie_burnt_df, calorie_intake_df, on='day')
    calorie_plot_df = calorie_plot_df.rename(columns={'day': 'Date', 'burnt_calories': 'Calories Burnt', 'calories': 'Calories Consumed'})
    other_nutrients_df = other_nutrients_df.rename(columns={'day':'Date'})
    health_score_df = health_score_df.rename(columns={'day':'Date'})
    
    make_plots(calorie_plot_df.head(10), username, "Calories")
    make_plots(other_nutrients_df.head(10), username, "Nutrients")
    make_plots(health_score_df.head(10), username, "Health")
    make_plot_line(health_score_df, username, "Health_overall")

def make_pie(parameter, limit, username, title):

    colors = ['lightgreen', 'whitesmoke']
    remaining = limit - parameter
    data = [parameter, remaining]

    if title == "Protein":
        
        if limit*2 < parameter:
            remaining = parameter - limit
            data = [limit*2, remaining]
            # labels = [f"{limit} gm", f"{limit*2} gm", f"{parameter} gm"]
            limit = parameter
            colors = ['lightgreen','red']
        
        elif limit < parameter:
            remaining = limit*2 - parameter
            data = [parameter, remaining]
            # labels = [f"{limit} gm", f"{parameter} gm", f"{limit*2} gm"]
            limit *= 2
        
        else:
            data = [parameter, limit*2]
            limit *= 2
    else:
        if limit < parameter:
            limit = parameter
            remaining = limit - parameter
            data = [parameter, remaining]
            colors=['Red', 'lightgreen']

    plt.figure(figsize=(4, 4))  
    plt.pie(
        data,
        startangle=0,
        colors=colors,
        wedgeprops={'edgecolor': 'whitesmoke', 'width':0.5}
    )

    plt.text(0, 0, f"0-{limit}", ha='center', va='center', color='white', fontsize=14, fontweight='bold')
    # plt.axis('equal')
    # plt.title(title, fontsize=14)
    plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=300)
    plt.clf()

###########################
# ** ROUTES **            #
###########################

@app.route('/nutrition', methods=["GET", "POST"])
def nutrition():
    __food_items = []
    _food_dict = {}
    i = 0
    for food_dict in data_food['Nutrition Values']:
        __food_items.append((i,food_dict['Food']))
        _food_dict[food_dict['Food']] = i
        i+=1
    form = NutritionForm()
 

    if request.method == 'POST':
        
        if 'username' in session:
            username = session['username']
            print(username)

            protein = 0
            calories = 0
            fat = 0
            Sat_fat = 0
            carbs = 0
            fiber = 0
            for i in form.food_items.data.split('; '):
                _i = i.split('(x')[0]
                
                food = data_food['Nutrition Values'][_food_dict[_i]]
           
                protein += float(food['Protein'].replace(',',''))/100 if food['Protein']!='t' else 0
                fat += float(food['Fat'].replace(',',''))/100 if food['Fat']!='t' else 0
                Sat_fat += float(food['Sat.Fat'].replace(',',''))/100 if food['Sat.Fat']!='t' else 0
                carbs += float(food['Carbs'].replace(',',''))/100 if food['Carbs']!='t' else 0
                fiber += float(food['Fiber'].replace(',',''))/100 if food['Fiber']!='t' else 0
                calories += float(food['Calories'].replace(',',''))/100 if food['Calories']!='t' else 0

            day = date.today()
            # user = db_session.query(Users).filter_by(username=username).first()
            nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()
            # exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()

            if(nutrition_data):
                print(nutrition_data)
                protein += nutrition_data.protein
                calories += nutrition_data.calories
                calories = round(calories,2)
                fat += nutrition_data.fat
                fat = round(fat,2)
                Sat_fat += nutrition_data.Sat_fat
                Sat_fat = round(Sat_fat,2)
                carbs += nutrition_data.carbs
                carbs = round(carbs,2)
                fiber += nutrition_data.fiber
                fiber = round(fiber,2)
                nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).update({ "protein": protein, "calories" : calories, "fat": fat, "Sat_fat": Sat_fat, "carbs": carbs, "fiber": fiber})
                db_session.commit()
                update_health(username, day, is_nutrition_changed=True, is_exercise_changed=False)

                update_plots()
                return redirect(url_for('health'))
                
            else:
                nutrition_obj = Nutrition(
                    username = username,
                    day = day,
                    protein = protein,
                    calories = calories,
                    fat = fat,
                    Sat_fat = Sat_fat,
                    carbs = carbs,
                    fiber = fiber
                )

                db_session.add(nutrition_obj)
                db_session.commit()
                update_health(username, day, is_nutrition_changed=True, is_exercise_changed=False)
                
                update_plots()
                return redirect(url_for('health'))

    return render_template("nutrition.html", title="Home", form=form, data=__food_items)

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    __exercises_items = []
    _exercises_dict = {}
    i = 0
    for exercise in data_exercise["Exercise Values"]:
        e = exercise["Activity, Exercise or Sport (1 hour)"]
        __exercises_items.append((i,e))
        _exercises_dict[e] = i
        i+=1

    form = ExerciseForm()    
    if request.method == 'POST':
        
        if 'username' in session:
            username = session['username']

            user = db_session.query(Users).filter_by(username=username).first()
            weight = user.weight

            if request.method == "POST":
                duration = form.duration.data
                burnt_calories = 0
                exercise_names = ""
                for i in form.exercise_items.data.split('; '):
                    _i = i.split('(x')[0]
                    exercise = data_exercise['Exercise Values'][_exercises_dict[_i]]
                    burnt_calories = float(weight)*float(exercise["Calories per kg"])*(float(duration)/60)
                    exercise_names += _i +"; "
                
                day = date.today()
                exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()
                # nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()

                if(exercise_data):
                    burnt_calories += exercise_data.burnt_calories
                    burnt_calories = round(burnt_calories,2)
                    exercise_names += exercise_data.exercise_names
                    duration += exercise_data.duration
                    exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).update({"burnt_calories": burnt_calories, "exercise_names": exercise_names, "duration": duration})
                    print(exercise_data)

                    
                    db_session.commit()

                    update_health(username, day, is_nutrition_changed=False, is_exercise_changed=True)
                    
                    update_plots()
                    return redirect(url_for('health'))
                    
                else:
                    exercise_obj = Exercise(
                        username = username,
                        day = day,
                        burnt_calories = burnt_calories,
                        duration = duration,
                        exercise_names = exercise_names
                    )
                    
                    print(exercise_obj)
                    db_session.add(exercise_obj)
                    db_session.commit()
                    update_health(username, day, is_nutrition_changed=False, is_exercise_changed=True)
                    update_plots()
                    return redirect(url_for('health'))
                
    return render_template("exercise.html", title="Home", form=form, data=__exercises_items)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    
    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        users = db_session.query(Users.username, Users.password, Users.email, Users.id, Users.bmi,  Users.height, Users.weight)
        
        for user in users:
            if(user.username == username or user.email == username):
                if(user.password == password):
                    # flash("Login successful!", "success") 
                    session['username'] = username
                    print(username)
                    return redirect(url_for('health'))
                else:
                    flash("Incorrect password")
                    return render_template('login.html', form=form, title="Login") 

        flash("User doesn't exist")

        # return redirect(url_for('nutrition'))
    return render_template("login.html", form=form, title='Login')

@app.route("/health", methods=["GET", "POST"])
def health():

    form = HeightWeightForm()
    username = session['username']
    day = date.today()

    if request.method == 'POST':
        if form.height.data:
            update_height(username, form.height.data)
            update_bmi(username)
        if form.weight.data:
            update_weight(username, form.weight.data)
            update_bmi(username)
            
        return redirect(url_for('health'))

    user = db_session.query(Users).filter_by(username=username).first()
    nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()
    exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()
    health_data = db_session.query(Health).filter_by(username=username, day=day).first()

    leaderboard = get_top_10(day)
    exercises = get_exercises(username, day)    
    
    update_plots()
    make_pie(user.bmi, 25, username, "BMI")
    if nutrition_data:
        make_pie(nutrition_data.protein, user.weight, username, "Protein")
    else:
        make_pie(0, user.weight, username, "Protein")

    user_data = {
        "user": user, 
        "nutrition_data":nutrition_data, 
        "exercise_data":exercise_data,
        "health_data": health_data,
        "exercises": exercises,
        "calories_png": f'static/images/{username}_Calories.png',
        "nutrients_png": f'static/images/{username}_Nutrients.png',
        "health_png": f'static//images/{username}_Health.png',
        "bmi_png": f'static//images/{username}_BMI.png',
        "protein_png": f'static//images/{username}_Protein.png',
        "health2_png": f'static//images/{username}_Health_overall.png'
    }
    return render_template("health.html", user_data=user_data, form = form, leaderboard=leaderboard)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    form = RegistrationForm()
   
    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data
        email = form.email.data
        height = form.height.data
        weight = form.weight.data

        print(username)
        users = db_session.query(Users.username, Users.password, Users.email)
        print(users)
        for user in users:
            if(user.username == username):
                # flash("User already exists!!! Try different username")
                return render_template("signup.html", title="Signup")

        new_user = Users(username=username, password=password, email=email, bmi=round((weight*weight)/height,2), height=height, weight=weight)
        db_session.add(new_user)
        db_session.commit()
        new_user = Nutrition(username=username, day=date.today(), protein=0, calories=0, fat=0, Sat_fat=0, carbs=0, fiber=0)
        db_session.add(new_user)
        db_session.commit()
        new_user = Exercise(username=username, day=date.today(), burnt_calories=0, exercise_names='', duration = 0)
        db_session.add(new_user)
        db_session.commit()
        new_user = Health(username=username, day=date.today(), health_score=0)
        db_session.add(new_user)
        db_session.commit()
        print(users)
        # flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for('login', title="login"))
    return render_template("signup.html", form=form, title="Signup")

if(__name__) == "__main__":
    app.run(debug=True)