"""

.. topic:: Instrumentos (formulários)

   O formulário do módulo *Instrumentos* recebe dados informados pelo usuário para o registro
   de um novo instrumento e é o mesmo utilizado quando da atualização de dados de um instrumento já existente.

   * InstrumentoForm: registrar ou atualizar dados de um instrumento.
   * ListaForm: escolher coordenação

**Campos definidos no formulário (todos são obrigatórios):**

"""

# forms.py dentro de instrumentos

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Regexp
from project import db
from project.models import Coords

# form para inclusão ou alteração de um instrumento
class InstrumentoForm(FlaskForm):

    coords = db.session.query(Coords.sigla)\
                      .order_by(Coords.sigla).all()
    lista_coords = [(c[0],c[0]) for c in coords]
    lista_coords.insert(0,('',''))

    coord        = SelectField('Coordenação:',choices= lista_coords)
    nome         = StringField('Título:',validators=[DataRequired(message="Informe um título para o instrumento!")])
    contraparte  = StringField('Contraparte:',validators=[DataRequired(message="Informe a contraparte!")])
    sei          = StringField('Número SEI:',validators=[DataRequired(message="Informe o Programa!")]) # incluir regex para sei
    data_inicio  = DateField('Data de início:',format='%Y-%m-%d',validators=[DataRequired(message="Informe data do início!")])
    data_fim     = DateField('Data de término:',format='%Y-%m-%d',validators=[DataRequired(message="Informe data do término!")])
    descri       = TextAreaField('Descrição:',validators=[DataRequired(message="Informe a descrição!")])
    valor        = StringField('Valor alocado:',validators=[DataRequired(message="Informe o valor!")])

    submit       = SubmitField('Registrar')

#
# form para escolher a coordenação na lista de instrumentos
class ListaForm(FlaskForm):

    coords = db.session.query(Coords.sigla)\
                      .order_by(Coords.sigla).all()
    lista_coords = [(c[0],c[0]) for c in coords]
    lista_coords.insert(0,('',''))

    coord        = SelectField('Coordenação:',choices= lista_coords)
    submit       = SubmitField('Filtrar coordenação')
