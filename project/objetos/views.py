"""
.. topic:: objetos (views)

    Os objetos são objetos que a coordenação necessita de um registro mínimo para referência em demandas.

    Um objeto tem atributos que são registrados no momento de sua criação. Todos são obrigatórios:

    * Título
    * Contraparte
    * Número do processo SEI
    * Data de início
    * Data de término
    * Valor associado
    * Descrição

.. topic:: Ações relacionadas aos objetos

    * Listar objetos: lista_objetos
    * Atualizar/visualizar dados de um objeto: update
    * Registrar um objeto no sistema: cria_objeto
    * Listar demandas de um determinado objeto: objeto_demandas

"""

# views.py na pasta objetos

from flask import render_template,url_for,flash, redirect,request,Blueprint
from flask_login import current_user,login_required
from sqlalchemy import func, distinct, cast, Integer
from sqlalchemy.sql import label
from project import db
from project.models import User, Demanda, Coords, Objeto
from project.objetos.forms import objetoForm, ListaForm
from project.demandas.views import registra_log_auto

import locale
from datetime import datetime, date
from dateutil.rrule import rrule, MONTHLY

objetos = Blueprint('objetos',__name__,
                            template_folder='templates/objetos')

#
def none_0(a):
    '''
    DOCSTRING: Transforma None em 0.
    INPUT: campo a ser trandormado.
    OUTPUT: 0, se a entrada for None, caso contrário, a entrada.
    '''
    if a == None:
        a = 0
    return a


@objetos.route('/<lista>/<coord>/lista_objetos', methods=['GET', 'POST'])
def lista_objetos(lista,coord):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista dos objetos.                                                       |
    |                                                                                       |
    |O objeto é algo tratado pela área técnica que justifica um registro específico.        |
    |Um contratao é um exemplo de objeto.                                                   |
    |                                                                                       |
    |No topo da tela há a opção de se inserir um novo objeto e o número sequencial          |
    |de cada objeto (#), ao ser clicado, permite que seus dados possam ser editados.        |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    hoje = datetime.today().date()

    form = ListaForm()
    
    coords = db.session.query(Coords.id,Coords.sigla)\
                       .order_by(Coords.sigla).all()
    lista_coords = [(c.id,c.sigla) for c in coords]
    lista_coords.insert(0,('',''))
    
    form.coord.choices = lista_coords

    if form.validate_on_submit():

        coord = form.coord.data

        if coord == '' or coord == None:
            coord = '*'

        return redirect(url_for('objetos.lista_objetos',lista=lista,coord=coord))

    else:

        if coord == '*':

            form.coord.data = ''

            coordenacao = db.session.query(Coords.id,
                                           Coords.sigla)\
                                    .subquery()

        else:

            form.coord.data = coord

            coordenacao = db.session.query(Coords.id,
                                           Coords.sigla)\
                                    .filter(Coords.id == cast(coord,Integer))\
                                    .subquery()

        if lista == 'todos':
            objetos_v = db.session.query(Objeto.id,
                                         Objeto.coord,
                                         Objeto.nome,
                                         Objeto.contraparte,
                                         Objeto.sei,
                                         Objeto.descri,
                                         Objeto.data_inicio,
                                         Objeto.data_fim,
                                         Objeto.valor,
                                         coordenacao.c.sigla)\
                                  .join(coordenacao, coordenacao.c.id == cast(Objeto.coord,Integer))\
                                  .order_by(Objeto.nome).all()

        elif lista == 'em execução':
            objetos_v = db.session.query(Objeto.id,
                                              Objeto.coord,
                                              Objeto.nome,
                                              Objeto.contraparte,
                                              Objeto.sei,
                                              Objeto.descri,
                                              Objeto.data_inicio,
                                              Objeto.data_fim,
                                              Objeto.valor,
                                              coordenacao.c.sigla)\
                                       .join(coordenacao, coordenacao.c.id == cast(Objeto.coord,Integer))\
                                       .filter(Objeto.data_fim >= hoje,
                                               Objeto.data_inicio <= hoje)\
                                       .order_by(Objeto.data_fim,Objeto.nome).all()

        quantidade = len(objetos_v)

        # objetos = []

        # for objeto in objetos_v:
        #     # ajusta formatos para data e dinheiro
        #     if objeto.data_inicio is not None:
        #         início = objeto.data_inicio.strftime('%x')
        #     else:
        #         início = None

        #     if objeto.data_fim is not None:
        #         fim = objeto.data_fim.strftime('%x')
        #         dias = (objeto.data_fim - hoje).days
        #     else:
        #         fim = None
        #         dias = 999

        #     valor = locale.currency(objeto.valor, symbol=False, grouping = True)

        #     objetos.append([objeto.id,
        #                          objeto.sigla,
        #                          objeto.nome,
        #                          objeto.contraparte,
        #                          objeto.sei,
        #                          início,
        #                          fim,
        #                          valor,
        #                          dias,
        #                          objeto.descri])

        return render_template('lista_objetos.html', objetos=objetos_v,quantidade=quantidade,lista=lista,form=form)


### ATUALIZAR objeto

@objetos.route("/<int:objeto_id>/update", methods=['GET', 'POST'])
@login_required
def update(objeto_id):
    """
    +---------------------------------------------------------------------------------------+
    |Permite atualizar os dados de um objeto selecionado na tela de consulta.          |
    |                                                                                       |
    |Recebe o ID do objeto como parâmetro.                                             |
    +---------------------------------------------------------------------------------------+
    """

    objeto = Objeto.query.get_or_404(objeto_id)

    form = objetoForm()

    if form.validate_on_submit():

        objeto.coord       = form.coord.data
        objeto.nome        = form.nome.data
        objeto.sei         = form.sei.data
        objeto.contraparte = form.contraparte.data
        objeto.data_inicio = form.data_inicio.data
        objeto.data_fim    = form.data_fim.data
        objeto.valor       = float(form.valor.data.replace('.','').replace(',','.'))
        objeto.descri      = form.descri.data

        db.session.commit()

        registra_log_auto(current_user.id,None,'itm')

        flash('objeto atualizado!')
        return redirect(url_for('objetos.lista_objetos',lista='todos',coord = '*'))
    # traz a informação atual do objeto
    elif request.method == 'GET':
        form.coord.data        = objeto.coord
        form.nome.data         = objeto.nome
        form.sei.data          = objeto.sei
        form.contraparte.data  = objeto.contraparte
        form.data_inicio.data  = objeto.data_inicio
        form.data_fim.data     = objeto.data_fim
        form.valor.data        = locale.currency( objeto.valor, symbol=False, grouping = True )
        form.descri.data       = objeto.descri

    return render_template('add_objeto.html', title='Update',
                           form=form, id=objeto_id)

### CRIAR objeto

@objetos.route("/criar", methods=['GET', 'POST'])
@login_required
def cria_objeto():
    """
    +---------------------------------------------------------------------------------------+
    |Permite registrar os dados de um objeto.                                               |
    +---------------------------------------------------------------------------------------+
    """

    form = objetoForm()
    
    coords = db.session.query(Coords.id,Coords.sigla)\
                       .order_by(Coords.sigla).all()
    lista_coords = [(c.id,c.sigla) for c in coords]
    lista_coords.insert(0,('',''))
    
    form.coord.choices = lista_coords

    if form.validate_on_submit():
        objeto = Objeto(coord       = form.coord.data,
                        nome        = form.nome.data,
                        contraparte = form.contraparte.data,
                        sei         = form.sei.data,
                        data_inicio = form.data_inicio.data,
                        data_fim    = form.data_fim.data,
                        valor       = float(form.valor.data.replace('.','').replace(',','.')),
                        descri      = form.descri.data)

        db.session.add(objeto)
        db.session.commit()

        registra_log_auto(current_user.id,None,'Objeto registrado!')

        flash('Objeto registrado!')
        return redirect(url_for('objetos.lista_objetos',lista='todos',coord = '*'))


    return render_template('add_objeto.html', form=form, id=0 )


# lista das demandas relacionadas a um objeto

@objetos.route('/<objeto_id>/objeto_demandas')
def objeto_demandas (objeto_id):
    """+--------------------------------------------------------------------------------------+
       |Mostra as demandas relacionadas a um objeto quando seu NUP é selecionado em uma  |
       |lista de objetos.                                                                |
       |Recebe o id do objeto como parâmetro.                                            |
       +--------------------------------------------------------------------------------------+
    """

    objeto_SEI = db.session.query(Objeto.sei,Objeto.nome).filter_by(id=objeto_id).first()

    SEI = objeto_SEI.sei
    SEI_s = str(SEI).replace('/','_')

    demandas_count = Demanda.query.filter(Demanda.sei.like('%'+SEI+'%')).count()

    demandas = Demanda.query.filter(Demanda.sei.like('%'+SEI+'%'))\
                            .order_by(Demanda.data.desc()).all()

    autores=[]
    for demanda in demandas:
        autores.append(str(User.query.filter_by(id=demanda.user_id).first()).split(';')[0])

    dados = [objeto_SEI.nome,SEI_s,'0','0']

    return render_template('SEI_demandas.html',demandas_count=demandas_count,demandas=demandas,sei=SEI, autores=autores,dados=dados)

#
#removendo uma atividade do plano de trabalho

@objetos.route('/<int:objeto_id>/delete', methods=['GET','POST'])
@login_required
def delete_objeto(objeto_id):
    """+----------------------------------------------------------------------+
       |Permite que o chefe, se logado, a remova um um objeto.           |
       |                                                                      |
       |Recebe o ID do objeto como parâmetro.                            |
       +----------------------------------------------------------------------+

    """
    if current_user.ativo == 0 or (current_user.despacha0 == 0 and current_user.despacha == 0 and current_user.despacha2 == 0):
        abort(403)

    objeto = Objeto.query.get_or_404(objeto_id)

    db.session.delete(Objeto)
    db.session.commit()

    registra_log_auto(current_user.id,None,'xtm')

    flash ('objeto excluído!','sucesso')

    return redirect(url_for('objetos.lista_objetos',lista='todos',coord = '*'))
