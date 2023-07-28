from project import app
from flask import render_template
import locale

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
