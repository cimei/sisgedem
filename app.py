from project import app
from flask import render_template
import webbrowser
from threading import Timer
import locale

# filtro cusomizado para o jinja
#
@app.template_filter('converte_para_real')
def converte_para_real(valor):
  return locale.currency(valor, symbol=False, grouping = True )

@app.route('/')
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port = 5003)
