from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
# from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/QLChuyenBay?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)

# login = LoginManager(app)

cloudinary.config(
    cloud_name="ddgxultsd",
    api_key="186632124732842",
    api_secret="iE7EGw6Lk-LMs1CMy7JpcX3fj3A",
    secure=True
)
