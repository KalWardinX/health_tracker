from imports import *

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

class ExerciseForm(FlaskForm):
    # duration = IntegerField("Exercise Duration", validators=[DataRequired()])
    exercise_items = TextAreaField("exercise-items", validators=[DataRequired()])
    submit = SubmitField('Submit')


class HeightWeightForm(FlaskForm):
    height = FloatField('Height')
    weight = FloatField('Weight')
    submit = SubmitField('Update')

class Base(DeclarativeBase):
    pass

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
    # duration = Column(Integer, default=0)

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

