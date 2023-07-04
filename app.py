from project import app
from flask import render_template
from threading import Timer
import locale
import csv
from flask import send_from_directory

from project.core.views import carregaSICONV

# filtro cusomizado para o jinja
#
@app.template_filter('converte_para_real')
def converte_para_real(valor):
  if valor:
    return locale.currency(valor, symbol=False, grouping = True )
  else:
    return valor  

@app.route('/')
def index():
  return render_template('home.html')



if __name__ == '__main__':
  app.run(port = 5003)
