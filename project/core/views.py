"""
.. topic:: Core (views)

    Este é o módulo inicial do sistema.

.. topic:: Ações relacionadas aos bolsistas

    * Tela inicial: index
    * Tela de informações: info



"""

# core/views.py

from flask import render_template,url_for,flash, redirect,request,Blueprint
from flask_login import login_required, current_user

from project import db, app
from project.models import Sistema

from project.demandas.views import registra_log_auto

from datetime import datetime as dt
from threading import Thread


core = Blueprint("core",__name__)



@core.route('/')
def index():
    """
    +---------------------------------------------------------------------------------------+
    |Ações quando o aplicativo é colocado no ar.                                            |
    +---------------------------------------------------------------------------------------+
    """
    sistema = db.session.query(Sistema).first()

        
    return render_template ('index.html',sistema=sistema) 

@core.route('/inicio')
def inicio():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela inicial do aplicativo.                                                |
    +---------------------------------------------------------------------------------------+
    """
    sistema = db.session.query(Sistema).first()

    return render_template ('index.html',sistema=sistema)    

@core.route('/info')
def info():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de informações do aplicativo.                                         |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('info.html')

