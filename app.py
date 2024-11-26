from imports import *
from classes import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

jsonfile1 = open('static/nutrients.json', 'r')
data_food = json.load(jsonfile1)

jsonfile2 = open('static/exercise.json', 'r')
data_exercise = json.load(jsonfile2)

app.config['SECRET_KEY'] = '1856a607f1d8fc35957b1566f7e9030a'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tech-stack.db"
DATABASE_URL = "sqlite:///health-tracker.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db_session = Session()

# Create the table in the database
Base.metadata.create_all(engine)
