from imports import *
from classes import *
from helpers import *

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
                quantity = 1
                if(len(i.split('(x'))>1):
                  quantity = float(i.split('(x')[1].split(')')[0])
                
                food = data_food['Nutrition Values'][_food_dict[_i]]
                print(food)
                protein += (float(food['Protein'])*50*quantity)/float(food['Grams']) if food['Protein']!='t' else 0
                fat += (float(food['Fat'])*50*quantity)/float(food['Grams']) if food['Fat']!='t' else 0
                Sat_fat += (float(food['Sat.Fat'])*50*quantity)/float(food['Grams']) if food['Sat.Fat']!='t' else 0
                carbs += (float(food['Carbs'])*50*quantity)/float(food['Grams']) if food['Carbs']!='t' else 0
                fiber += (float(food['Fiber'])*50*quantity)/float(food['Grams']) if food['Fiber']!='t' else 0
                calories += (float(food['Calories'])*50*quantity)/float(food['Grams']) if food['Calories']!='t' else 0

            day = date.today()
            # user = db_session.query(Users).filter_by(username=username).first()
            nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()
            # exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()

            if(nutrition_data):
                # print(nutrition_data)
                protein += nutrition_data.protein
                protein = round(protein,2)
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
                    protein = round(protein,2),
                    calories = round(calories,2),
                    fat = round(fat,2),
                    Sat_fat = round(Sat_fat,2),
                    carbs = round(carbs,2),
                    fiber = round(fiber,2)
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
                # duration = form.duration.data
                burnt_calories = 0
                exercise_names = ""
                for i in form.exercise_items.data.split('; '):
                    _i = i.split('(x')[0]
                    exercise = data_exercise['Exercise Values'][_exercises_dict[_i]]
                    burnt_calories = float(weight)*float(exercise["Calories per kg"])/12
                    exercise_names += _i +"; "
                
                day = date.today()
                exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).first()
                # nutrition_data = db_session.query(Nutrition).filter_by(username=username, day=day).first()

                if(exercise_data):
                    burnt_calories += exercise_data.burnt_calories
                    burnt_calories = round(burnt_calories,2)
                    exercise_names += exercise_data.exercise_names
                    # duration += exercise_data.duration
                    exercise_data = db_session.query(Exercise).filter_by(username=username, day=day).update({"burnt_calories": burnt_calories, "exercise_names": exercise_names})
                    print(exercise_data)

                    
                    db_session.commit()

                    update_health(username, day, is_nutrition_changed=False, is_exercise_changed=True)
                    
                    update_plots()
                    return redirect(url_for('health'))
                    
                else:
                    exercise_obj = Exercise(
                        username = username,
                        day = day,
                        burnt_calories = round(burnt_calories,2),
                        # duration = duration,
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

@app.route("/logout", methods=['GET'])
def logout():

    username = session['username']
    pics = [
        f'static/images/{username}_Calories.png',
        f'static/images/{username}_Nutrients.png',
        f'static//images/{username}_Health.png',
        f'static//images/{username}_BMI.png',
        f'static//images/{username}_Protein.png'
    ]
    for i in pics:
        os.remove(i)
    return redirect(url_for('login'))

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
    health_score = 0
    if health_data:
        health_score = round(health_data.health_score,2)
    db_session.query(Health).filter_by(username=username, day=day).update({'health_score': health_score})
    db_session.commit()
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
                return render_template("signup.html", title="Signup", form=form)

        new_user = Users(username=username, password=password, email=email, bmi=round((weight*weight)/height,2), height=height, weight=weight)
        db_session.add(new_user)
        db_session.commit()
        new_user = Nutrition(username=username, day=date.today(), protein=0, calories=0, fat=0, Sat_fat=0, carbs=0, fiber=0)
        db_session.add(new_user)
        db_session.commit()
        new_user = Exercise(username=username, day=date.today(), burnt_calories=0, exercise_names='')
        db_session.add(new_user)
        db_session.commit()
        new_user = Health(username=username, day=date.today(), health_score=0)
        db_session.add(new_user)
        db_session.commit()
        print(users)
        # flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for('login', title="login"))
    return render_template("signup.html", form=form, title="Signup")