from flask import Flask
# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_path='', static_url_path='')
app.config.from_object('config')
app.config['SECRET_KEY'] = '123456'  
# db = SQLAlchemy(app)

faces_json_path = r"app/static/json_files/faces_json/"
download_json_path = r"app/static/json_files/download_json/"
gen_json_path = r"app/static/json_files/gen_json/"
saved_pics_path = r"/oss/pics_repo/"
backup_json_path = r"app/static/json_files/backup_json/"

from app import views #, models