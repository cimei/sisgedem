# __init__.py dentro da pasta project

import sys
import os
import locale
import datetime
from flask import Flask,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


from shutil import rmtree
import time
import glob

TOP_LEVEL_DIR = os.path.abspath(os.curdir)

app = Flask (__name__, static_url_path=None, instance_relative_config=True, static_folder='/app/project/static')

app.config.from_pyfile('flask.cfg')

app.static_url_path=app.config.get('STATIC_PATH')

db = SQLAlchemy(app)

mail = Mail(app)

locale.setlocale( locale.LC_ALL, '' )


#################################
## log in - cofigurações

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'users.login'


############################################
## blueprints - registros

from project.core.views import core
from project.users.views import users
from project.demandas.views import demandas
from project.error_pages.handlers import error_pages

from project.objetos.views import objetos

app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(demandas,url_prefix='/demandas')
app.register_blueprint(error_pages)

app.register_blueprint(objetos,url_prefix='/objetos')
