from project import app
from flask import render_template
import locale
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



if __name__ == '__main__':
  app.run(port = 5003)
