from imports import *
from classes import *
from app import *

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
    health_score = round(health_score,2)
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
        plt.ylabel('Amount (kcal)', fontsize=10)
        plt.title('Calories Burnt vs Consumed Over Time', fontsize=10, fontweight='bold')
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1000)
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
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1000)
        plt.clf()

def make_plot_line(df, username, title):
    
    plt.figure(figsize=(6, 5))

    plt.plot(df['Date'], df['health_score'], color='darkblue', marker='X', linewidth=2)
    plt.xlabel("Date")
    plt.ylabel("Health Score")
    plt.title(title)
    plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=1000)
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
    # make_plots(health_score_df.head(10), username, "Health")
    make_plot_line(health_score_df.head(10), username, "Health")

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
        wedgeprops={'edgecolor': 'black', 'width':0.5}
    )

    plt.text(0, 0, f"0-{limit}", ha='center', va='center', color='black', fontsize=14, fontweight='bold')
    # plt.axis('equal')
    # plt.title(title, fontsize=14)
    plt.savefig(f"static/images/{username}_{title}.png", transparent=True, dpi=300)
    plt.clf()