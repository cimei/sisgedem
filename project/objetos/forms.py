"""

.. topic:: objetos (formulários)

   O formulário do módulo *objetos* recebe dados informados pelo usuário para o registro
   de um novo objeto e é o mesmo utilizado quando da atualização de dados de um objeto já existente.

   * objetoForm: registrar ou atualizar dados de um objeto.
   * ListaForm: escolher unidade

**Campos definidos no formulário (todos são obrigatórios):**

"""

# forms.py dentro de objetos

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Regexp, Optional

# form para inclusão ou alteração de um objeto
class objetoForm(FlaskForm):

    coord        = SelectField('Unidade:',validators=[DataRequired(message="Informe a unidade!")])
    nome         = StringField('Título:',validators=[DataRequired(message="Informe um título para o objeto!")])
    contraparte  = StringField('Contraparte:')
    sei          = StringField('Processo:',validators=[DataRequired(message="Informe um número para o processo!")]) 
    data_inicio  = DateField('Data de início:',format='%Y-%m-%d', validators=(Optional(),))
    data_fim     = DateField('Data de término:',format='%Y-%m-%d', validators=(Optional(),))
    descri       = TextAreaField('Descrição:',validators=[DataRequired(message="Informe a descrição!")])
    valor        = StringField('Valor alocado:',default='0')

    submit       = SubmitField('Registrar')

#
# form para escolher a coordenação na lista de objetos
class ListaForm(FlaskForm):

    coord        = SelectField('Unidade:')
    submit       = SubmitField('Filtrar por unidade')
