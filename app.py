from project import app
from flask import render_template
import locale
import webbrowser
from threading import Timer
from datetime import datetime as dt

# filtro cusomizado para o jinja
#
@app.template_filter('converte_para_real')
def converte_para_real(valor):
  if valor:
    return locale.currency(valor, symbol=False, grouping = True )
  else:
    return valor  
  
@app.template_filter('str_to_date')
def str_to_date(valor):
    if valor == None or valor == '':
        return 0
    else:
        return dt.strptime(valor,'%Y-%m-%dT%H:%M:%S')   

@app.route('/')
def index():
  return render_template('home.html')
  
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5003/')

if __name__ == '__main__':
    Timer(1, open_browser).start();
    app.run(port=5003)
