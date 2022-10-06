"""
.. topic:: Acordos (views)

    Os Acordos são instrumentos de parceria entre o CNPq e Entidades Parceiras Estaduais - EPEs onde
    não há repasse direto de recursos entre as partes.

    O CNPq custeia as bolsas dos contemplados em processos seletivos organizados pelas EPEs
    e estas, a título de contrapartida, custeiam outras despesas dos projetos.

    Toda bolsa é implementada por meio de um processo de bolsa (processo filho), que, por sua vez, deve estar vinculado a
    um processo mãe.

    Em princípio, é no processo mãe que são definidos a quantidade máxima de bolsas que poderão ser implementadas no projeto,
    pois o processo mãe tem um valor de concessão definido, bem como uma vigência que limita as vigências dos processos filho.

    A indicação dos bolsisstas  é feita pela EPE em plataforma específica do CNPq e este módulo trabalha com os
    dados fornecidos por este sistema, via planilha excel enviada pela COSAO, sob demanda da COPES.

    Um acordo tem atributos que são registrados no momento de sua criação. Todos são obrigatórios:

    * Edição do programa ao qual ele está vinculado
    * Número do processo SEI
    * Sigla da EPE
    * Unidade da Federação da EPE
    * Data de início
    * Data de término
    * Valor alocado pelo CNPq
    * Valor alocado pela EPE

    Os valores pagos são calculados pela soma de todos os pagamentos registrados para cada processo filho da planilha COSAO.
    Da mesma forma, é feito o cálculo da quantidade de mensalides pagas.

    Os valores a pagar consistem da multiplicação da quantidade de meses entre a data de referência (data de geração da
    planilha COSAO) e o fim de vigência de cada processo-filho pelo valor da respectiva memsalidade do nível de bolsa no
    qual o bolsista foi enquadrado. Da mesma forma, é feito o cálculo da quantidade de mensalides a pagar.

.. topic:: Ações relacionadas aos acordos

    * Listar acordos por edição do programa: lista_acordos
    * Atualizar dados de um acordo: update
    * Registrar um acordo no sistema: cria_acordo
    * Deletar o registro de um acordo: deleta_acordo
    * Listar demandas de um determinado acordo: acordo_demandas
    * Registrar um programa do CNPq no sistema: cria_programa_cnpq
    * Listar programas do CNPq: lista_programa_cnpq
    * Atualizar programas do CNPq: atualiza_programa_cnpq
    * Lista processos mãe de um acordo: lista_processos_mae_por_acordo
    * Alterada dados de processo_mãe: altera_mae
    * Associar processos mãe a um acordo: processo_mae_acordo
    * Desassociar processo mãe de um acordo: deleta_processo_mae
    * Listar processos filho de um processo mãe: lista_processos_filho
    * Listar bolsistas (cpf) de um processo mãe: lista_bolsistas
    * Listar os processos filho de um acordo: lista_processos_filho_por_acordo
    * Carregar situações de arquivo do sigef: carrega_sit_sigef
    * Listar bolsistas (cpf) de um acordo: lista_bolsistas_acordo
    * Acordos por Programa: resumo_acordos
    * Acordos por UF: brasil_acordos
    * Edições de cada programa: edic_programa
    * Gasto mensal por acordo: gasto_mes
    * Listar projetos ou bolsistas homologados: homologados

"""

# views.py na pasta acordos

from re import I
from flask import render_template,url_for,flash, redirect,request,Blueprint,send_from_directory
from flask_login import current_user,login_required
from sqlalchemy import func, distinct
from sqlalchemy.sql import label
from project import db
from project.models import Acordo, RefCargaPDCTR, PagamentosPDCTR, Processo_Mae, Bolsa, User, Demanda,\
                           Chamadas, Programa_CNPq, Acordo_ProcMae, Processo_Filho
from project.acordos.forms import AcordoForm, Programa_CNPqForm, func_ProcMae_Acordo, ListaForm, ArquivoForm, Altera_proc_mae_Form
from project.demandas.views import registra_log_auto

import locale
import datetime
from datetime import datetime as dt
from dateutil.rrule import rrule, MONTHLY
import xlrd
import tempfile
from werkzeug.utils import secure_filename
import os
from folium import Map, Circle, Popup
import csv

acordos = Blueprint('acordos',__name__,
                            template_folder='templates/acordos')

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

def cargaSit(entrada):

    print ('\n')
    print ('<<',dt.now().strftime("%x %X"),'>> ',' Carga de arquivo de situações de processos-filho iniciada...')

    book = xlrd.open_workbook(filename=entrada,ragged_rows=True)
    planilha = book.sheet_by_index(0)

    linha_cabeçalho = planilha.row_values(0, start_colx=0, end_colx=None)

    print ('Planilha: SIGEF')
    print (f'Cabeçalho original: {len(linha_cabeçalho)} campos')
    print (f'Quantidade de registros na planilha: {planilha.nrows - 1 }')
    print ('\n')

    qtd_linhas = planilha.nrows - 1

    for i in range(qtd_linhas):

        linha_base = planilha.row_values(i + 1, start_colx=0, end_colx=None)

        proc = planilha.cell_value(i + 1, linha_cabeçalho.index('Processo'))
        sit  = planilha.cell_value(i + 1, linha_cabeçalho.index('Situação'))

        processo_filho = db.session.query(Processo_Filho).filter(Processo_Filho.processo == proc).all()

        for p in processo_filho:

            if p.situ_filho != sit:
                p.situ_filho = sit

        db.session.commit()

        pag_PDCTR = db.session.query(PagamentosPDCTR).filter(PagamentosPDCTR.processo == proc).all()

        for p in pag_PDCTR:

            if p.situ_filho != sit:
                p.situ_filho = sit

        db.session.commit()

    print ('Carga finalizada!')
    print ('\n')

#
def cria_csv(arq,linha,tabela):
  '''Recebe caminho do arquivo como string, campos da tabela como lista e a tabela propriamente dita'''
  with open(arq,'w',encoding='UTF8',newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(linha)
        writer.writerows(tabela)

@acordos.route('/<lista>/<coord>/lista_acordos', methods=['GET', 'POST'])
def lista_acordos(lista,coord):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista dos acordos por edição do programa.                                |
    |                                                                                       |
    |Ao varrer a tabela de acordos, resgatando os cadastrados na edição consultada, são     |
    |feitas consultas aos dados envidados pela COSAO e também aos                           |
    |dados sobre os respectivos processos-mãe relacionados a cada acordo para que se        |
    |calcule a quantidade de bolsistas contemplados (CPFs), a quantidade de bolsas          |
    |implementadas (processos-filho), a quantidade de mensalidades pagas, o valor pago,     |
    |o valor a pagar e o saldo (valor alocado pelo CNPq no acordo - valor pago - valor a    |
    |pagar).                                                                                |
    |                                                                                       |
    |No topo da tela há a opção de se inserir um novo acordo e o número sequencial de cada  |
    |acordo (#), ao ser clicado, permite que seus dados possam ser editados.                |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    hoje = dt.today()

    form = ListaForm()

    if form.validate_on_submit():

        coord = form.coord.data

        if coord == '' or coord == None:
            coord = '*'

        return redirect(url_for('acordos.lista_acordos',lista=lista,coord=coord))

    else:

        if coord == '*':

            form.coord.data = ''

            programa = db.session.query(Programa_CNPq.SIGLA_PROGRAMA,
                                        Programa_CNPq.COD_PROGRAMA,
                                        Programa_CNPq.COORD,
                                        Programa_CNPq.ID_PROGRAMA)\
                                        .subquery()
        else:

            form.coord.data = coord

            programa = db.session.query(Programa_CNPq.SIGLA_PROGRAMA,
                                        Programa_CNPq.COD_PROGRAMA,
                                        Programa_CNPq.COORD,
                                        Programa_CNPq.ID_PROGRAMA)\
                                        .filter(Programa_CNPq.COORD == coord)\
                                        .subquery()


        #situ_filho_retirados = ['17','40','41','61','62','63','66']

        if lista == 'todos':
            acordos_v = db.session.query(Acordo.id,
                                       Acordo.nome,
                                       Acordo.sei,
                                       Acordo.epe,
                                       Acordo.uf,
                                       Acordo.data_inicio,
                                       Acordo.data_fim,
                                       Acordo.valor_cnpq,
                                       Acordo.valor_epe,
                                       Acordo.programa_cnpq,
                                       Acordo.situ,
                                       programa.c.SIGLA_PROGRAMA,
                                       programa.c.COORD,
                                       programa.c.ID_PROGRAMA)\
                                       .join(programa, programa.c.COD_PROGRAMA == Acordo.programa_cnpq)\
                                       .order_by(Acordo.programa_cnpq, Acordo.epe).all()

        elif lista == 'em execução':
            acordos_v = db.session.query(Acordo.id,
                                       Acordo.nome,
                                       Acordo.sei,
                                       Acordo.epe,
                                       Acordo.uf,
                                       Acordo.data_inicio,
                                       Acordo.data_fim,
                                       Acordo.valor_cnpq,
                                       Acordo.valor_epe,
                                       Acordo.programa_cnpq,
                                       Acordo.situ,
                                       programa.c.SIGLA_PROGRAMA,
                                       programa.c.COORD,
                                       programa.c.ID_PROGRAMA)\
                                       .join(programa, programa.c.COD_PROGRAMA == Acordo.programa_cnpq)\
                                       .filter(Acordo.data_fim >= datetime.date.today())\
                                       .order_by(Acordo.data_fim,Acordo.epe).all()
        elif lista[:8] == 'programa':
            acordos_v = db.session.query(Acordo.id,
                                       Acordo.nome,
                                       Acordo.sei,
                                       Acordo.epe,
                                       Acordo.uf,
                                       Acordo.data_inicio,
                                       Acordo.data_fim,
                                       Acordo.valor_cnpq,
                                       Acordo.valor_epe,
                                       Acordo.programa_cnpq,
                                       Acordo.situ,
                                       programa.c.SIGLA_PROGRAMA,
                                       programa.c.COORD,
                                       programa.c.ID_PROGRAMA)\
                                       .join(programa, programa.c.COD_PROGRAMA == Acordo.programa_cnpq)\
                                       .filter(Acordo.programa_cnpq == lista[8:])\
                                       .order_by(Acordo.epe).all()
    #
        elif lista[:4] == 'edic':
            acordos_v = db.session.query(Acordo.id,
                                       Acordo.nome,
                                       Acordo.sei,
                                       Acordo.epe,
                                       Acordo.uf,
                                       Acordo.data_inicio,
                                       Acordo.data_fim,
                                       Acordo.valor_cnpq,
                                       Acordo.valor_epe,
                                       Acordo.programa_cnpq,
                                       Acordo.situ,
                                       programa.c.SIGLA_PROGRAMA,
                                       programa.c.COORD,
                                       programa.c.ID_PROGRAMA)\
                                       .join(programa, programa.c.COD_PROGRAMA == Acordo.programa_cnpq)\
                                       .filter(Acordo.nome == lista[4:])\
                                       .order_by(Acordo.epe).all()
        #
        elif lista[:2] == 'uf':
            acordos_v = db.session.query(Acordo.id,
                                   Acordo.nome,
                                   Acordo.sei,
                                   Acordo.epe,
                                   Acordo.uf,
                                   Acordo.data_inicio,
                                   Acordo.data_fim,
                                   Acordo.valor_cnpq,
                                   Acordo.valor_epe,
                                   Acordo.programa_cnpq,
                                   Acordo.situ,
                                   programa.c.SIGLA_PROGRAMA,
                                   programa.c.COORD,
                                   programa.c.ID_PROGRAMA)\
                                   .join(programa, programa.c.COD_PROGRAMA == Acordo.programa_cnpq)\
                                   .filter(Acordo.programa_cnpq == lista[4:], Acordo.uf == lista[2:4])\
                                   .order_by(Acordo.epe).all()

        quantidade = len(acordos_v)

        acordos = []

        for acordo in acordos_v:
            # ajusta formatos para data e dinheiro
            if acordo.data_inicio is not None:
                início = acordo.data_inicio.strftime('%x')
            else:
                início = None

            if acordo.data_fim is not None:
                fim = acordo.data_fim.strftime('%x')
                dias = (acordo.data_fim - hoje).days
            else:
                fim = None
                dias = 999

            valor_cnpq = locale.currency(acordo.valor_cnpq, symbol=False, grouping = True)
            valor_epe  = locale.currency(acordo.valor_epe, symbol=False, grouping = True)

            # pega quantidade de mães, filhos do acordo e totaliza o que foi pago
            procs_mae = db.session.query(Acordo_ProcMae.proc_mae_id,
                                         Processo_Mae.proc_mae,
                                         Processo_Mae.inic_mae,
                                         Processo_Mae.term_mae,
                                         Processo_Mae.situ_mae)\
                                  .join(Processo_Mae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                                  .filter(Acordo_ProcMae.acordo_id == acordo.id).all()

            qtd_proc_mae = len(procs_mae)
            l_procs_mae = [p.proc_mae for p in procs_mae]

            cpfs_banco = db.session.query(Processo_Filho.cpf)\
                             .filter(Processo_Filho.proc_mae.in_(l_procs_mae))\
                             .group_by(Processo_Filho.cpf)\
                             .all()
            qtd_cpfs = len(cpfs_banco)

            qtd_filhos_acordo = 0
            pago_acordo       = 0
            a_pagar           = 0
            mae_em_aberto     = False
            filho_em_aberto   = False

            for proc in procs_mae:

                if str(proc.situ_mae).strip() != '71':
                    mae_em_aberto = True

                filho_sit = db.session.query(Processo_Filho.situ_filho).filter(Processo_Filho.proc_mae == proc.proc_mae).all()

                for sit in filho_sit:
                    if str(sit.situ_filho).strip() != '71':
                        filho_em_aberto = True

                filhos = db.session.query(label('qtd_filhos',func.count(Processo_Filho.processo)),
                                          label('pago',func.sum(Processo_Filho.pago_total)),
                                          label('apagar',func.sum(Processo_Filho.valor_apagar)))\
                                          .filter(Processo_Filho.proc_mae == proc.proc_mae)

                qtd_filhos_acordo += int(filhos[0][0])
                if filhos[0][1] == None:
                    pago_acordo += 0
                else:
                    pago_acordo += float(filhos[0][1])
                if filhos[0][2] == None:
                    a_pagar += 0
                else:
                    a_pagar += float(filhos[0][2])

            #
            # verifica ser o acordo tem demandas de indicação de bolsisstas
            indic = 0
            indic = db.session.query(Demanda.tipo).filter(Demanda.sei == acordo.sei, Demanda.tipo == 'Bolsistas - Indicação na PICC').count()

            #verificar se situação do acordo pode ser modificada

            situ = acordo.situ
            alterar_sit = False

            if acordo.data_fim != None and acordo.data_fim != '':
                if situ != 'Vigente' and qtd_proc_mae > 0 and acordo.data_fim >= hoje:
                    situ = 'Vigente'
                    alterar_sit = True
                if situ[0:8] != 'Expirado' and situ != 'Não executado' and acordo.data_fim < hoje:
                    situ = 'Expirado (sem RTF)'
                    alterar_sit = True
                if situ == 'Expirado' and acordo.data_fim < hoje:
                    situ = 'Expirado (sem RTF)'
                    alterar_sit = True
                if (situ == 'Expirado (RTF aprovado)' or situ == 'Expirado (RTF APROVADO!)') and (mae_em_aberto or filho_em_aberto):
                    situ = 'RTF aprovado, mas há processo(s) à finalizar'
                    alterar_sit = True
                if (situ[0:8] == 'Expirado' or situ == 'Vigente' or situ == 'Preparação' or situ == 'Esquecido' or situ == '' or situ == 'Consta indicação de bolsista') and\
                            qtd_proc_mae == 0 and acordo.data_fim > hoje and indic == 0 and\
                            (acordo.data_inicio+datetime.timedelta(days=90)) >= hoje:
                    situ = 'Assinado'
                    alterar_sit = True
                if (situ[0:8] == 'Expirado' or situ == 'Vigente' or situ == 'Assinado' or situ == 'Preparação' or situ == '' or situ == 'Consta indicação de bolsista') and\
                            qtd_proc_mae == 0 and acordo.data_fim > hoje and indic == 0 and\
                            (acordo.data_inicio+datetime.timedelta(days=90)) < hoje:
                    situ = 'Esquecido'
                    alterar_sit = True
                if (situ[0:8] == 'Assinado' or situ == 'Esquecido' or situ == 'Aguarda Folha' or situ == 'Bolsas foram indicadas') and indic > 0:
                    situ = 'Consta indicação de bolsista'
                    alterar_sit = True
            else:
                if situ != 'Preparação' and situ != "Não executado":
                    situ = 'Preparação'
                    alterar_sit = True

            if alterar_sit:
                acordo_alterar_sit = Acordo.query.get_or_404(acordo.id)
                acordo_alterar_sit.situ = situ
                db.session.commit()
            #
            acordos.append([acordo.id,
                            acordo.SIGLA_PROGRAMA,
                            acordo.nome, acordo.sei, acordo.epe, acordo.uf,
                            início,
                            fim,
                            valor_epe,
                            valor_cnpq,
                            qtd_proc_mae,
                            qtd_filhos_acordo,
                            locale.currency(pago_acordo, symbol=False, grouping = True),
                            locale.currency(a_pagar, symbol=False, grouping = True),
                            locale.currency(acordo.valor_cnpq - pago_acordo - a_pagar, symbol=False, grouping = True),
                            acordo.COORD,
                            dias,
                            acordo.ID_PROGRAMA,
                            qtd_cpfs,
                            situ])

        cria_csv('/app/project/static/acordos.csv',
                 ['id','prog','nome','sei','epe','uf','ini','fim','valor_epe','valor_cnpq','qtd_proc_mae','qtd_filhos','pago','a_pagar','saldo','coord','dias','id_prog','qtd_cpfs','situ'],
                 acordos)    

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', 'acordos.csv')                     

        return render_template('lista_acordos.html', acordos=acordos,quantidade=quantidade,lista=lista,form=form)


### VISUALIZAR E ATUALIZAR detalhes de Acordo

@acordos.route("/<int:acordo_id>/<lista>/update", methods=['GET', 'POST'])
@login_required
def update(acordo_id,lista):
    """
    +---------------------------------------------------------------------------------------+
    |Permite ver e atualizar os dados de um acordo selecionado na tela de consulta.         |
    |                                                                                       |
    |Recebe o ID do acordo como parâmetro.                                                  |
    +---------------------------------------------------------------------------------------+
    """

    chamadas_s = []

    acordo = Acordo.query.get_or_404(acordo_id)

    procs_mae = db.session.query(Processo_Mae.proc_mae,
                                 Processo_Mae.inic_mae,
                                 Processo_Mae.term_mae)\
                          .join(Acordo_ProcMae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                          .filter(Acordo_ProcMae.acordo_id == acordo_id)\
                          .order_by(Processo_Mae.term_mae.desc()).all()

    form = AcordoForm(programa_cnpq=acordo.programa_cnpq)

    programa = db.session.query(Programa_CNPq.SIGLA_PROGRAMA)\
                            .filter(Programa_CNPq.COD_PROGRAMA == acordo.programa_cnpq)\
                            .first()

    chamadas = db.session.query(Chamadas.id,
                                Chamadas.chamada,
                                Chamadas.qtd_projetos,
                                Chamadas.vl_total_chamada,
                                Chamadas.doc_sei,
                                Chamadas.obs).filter(Chamadas.sei == acordo.sei).all()
    qtd_chamadas = len(chamadas)                            

    valor_cnpq = locale.currency(acordo.valor_cnpq, symbol=False, grouping = True)
    valor_epe  = locale.currency(acordo.valor_epe, symbol=False, grouping = True)

    chamadas_s = []
    chamadas_tot = 0
    qtd_proj = 0
    for chamada in chamadas:
        chamadas_s.append([chamada.id,chamada.chamada,chamada.qtd_projetos,
                            locale.currency(chamada.vl_total_chamada, symbol=False, grouping = True),
                            chamada.doc_sei,chamada.obs])
        chamadas_tot += chamada.vl_total_chamada
        qtd_proj += chamada.qtd_projetos
    
    try:
        sei = str(acordo.sei).split('/')[0]+'_'+str(acordo.sei).split('/')[1]
    except:
        sei = acordo.sei

    if form.validate_on_submit():

        acordo.nome             = form.nome.data
        acordo.sei              = form.sei.data
        acordo.epe              = form.epe.data
        acordo.uf               = form.uf.data
        acordo.data_inicio      = form.data_inicio.data
        acordo.data_fim         = form.data_fim.data
        acordo.valor_cnpq       = float(form.valor_cnpq.data.replace('.','').replace(',','.'))
        acordo.valor_epe        = float(form.valor_epe.data.replace('.','').replace(',','.'))
        acordo.programa_cnpq    = form.programa_cnpq.data
        acordo.situ             = form.situ.data

        db.session.commit()

        # atualiza demandas associadas em caso de alteração do SEI do acordo.
        if form.sei.data != acordo.sei:
            demandas = db.session.query(Demanda).filter(Demanda.sei == acordo.sei).all()
            for demanda in demandas:
                demanda.sei = form.sei.data
            db.session.commit()

        registra_log_auto(current_user.id,None,'aco')

        flash('Acordo atualizado!','sucesso')
        return redirect(url_for('acordos.update', acordo_id=acordo_id, lista=lista))

    # traz a informação atual do acordo
    elif request.method == 'GET':

        form.nome.data             = acordo.nome
        form.sei.data              = acordo.sei
        form.epe.data              = acordo.epe
        form.uf.data               = acordo.uf
        form.data_inicio.data      = acordo.data_inicio
        form.data_fim.data         = acordo.data_fim
        form.valor_cnpq.data       = locale.currency( acordo.valor_cnpq, symbol=False, grouping = True )
        form.valor_epe.data        = locale.currency( acordo.valor_epe, symbol=False, grouping = True )
        form.situ.data             = acordo.situ


    return render_template('add_acordo.html', title='Update',
                            chamadas=chamadas_s,
                            qtd_chamadas=qtd_chamadas,
                            qtd_proj=qtd_proj,
                            chamadas_tot=locale.currency(chamadas_tot, symbol=False, grouping = True),
                            acordo_id=acordo_id,
                            sei=sei,
                            prog=programa.SIGLA_PROGRAMA,
                            edic=acordo.nome,
                            epe=acordo.epe,
                            uf=acordo.uf,
                            procs_mae=procs_mae,
                            qtd_procs_mae=len(procs_mae),
                            form=form)

### CRIAR Acordo

@acordos.route("/criar", methods=['GET', 'POST'])
@login_required
def cria_acordo():
    """
    +---------------------------------------------------------------------------------------+
    |Permite registrar os dados de um acordo.                                               |
    +---------------------------------------------------------------------------------------+
    """

    form = AcordoForm()

    if form.validate_on_submit():
        acordo = Acordo(nome             = form.nome.data,
                        sei              = form.sei.data,
                        epe              = form.epe.data,
                        uf               = form.uf.data,
                        data_inicio      = form.data_inicio.data,
                        data_fim         = form.data_fim.data,
                        valor_cnpq       = float(form.valor_cnpq.data.replace('.','').replace(',','.')),
                        valor_epe        = float(form.valor_epe.data.replace('.','').replace(',','.')),
                        programa_cnpq    = form.programa_cnpq.data,
                        situ             = form.situ.data)

        db.session.add(acordo)
        db.session.commit()

        registra_log_auto(current_user.id,None,'aco')

        flash('Acordo criado!','sucesso')
        return redirect(url_for('acordos.resumo_acordos'))


    return render_template('add_acordo.html',
                            acordo_id=0,
                            form=form)

## Deletar um acordo

@acordos.route("/<int:acordo_id>/deleta_acordo", methods=['GET', 'POST'])
@login_required
def deleta_acordo(acordo_id):
    """
    +---------------------------------------------------------------------------------------+
    |Permite deletar o registro de um acordo.                                               |
    +---------------------------------------------------------------------------------------+
    """

    acordo = Acordo.query.get_or_404(acordo_id)

    db.session.delete(acordo)
    db.session.commit()

    registra_log_auto(current_user.id,None,'ade')

    flash ('Acordo deletado!','sucesso')

    return redirect(url_for('acordos.lista_acordos',lista='em execução',coord='*'))


# lista das demandas relacionadas a um acordo

@acordos.route('/<acordo_id>/acordo_demandas')
def acordo_demandas (acordo_id):
    """+--------------------------------------------------------------------------------------+
       |Mostra as demandas relacionadas a um acordo quando seu NUP é selecionado em uma       |
       |lista de acordos.                                                                     |
       |Recebe o id do acordo como parâmetro.                                                 |
       +--------------------------------------------------------------------------------------+
    """

    acordo_SEI = db.session.query(Acordo.sei,Acordo.nome).filter_by(id=acordo_id).first()

    SEI = acordo_SEI.sei
    SEI_s = str(SEI).split('/')[0]+'_'+str(SEI).split('/')[1]

    demandas_count = Demanda.query.filter(Demanda.sei.like('%'+SEI+'%')).count()

    demandas = Demanda.query.filter(Demanda.sei.like('%'+SEI+'%'))\
                            .order_by(Demanda.data.desc()).all()

    autores=[]
    for demanda in demandas:
        autores.append(str(User.query.filter_by(id=demanda.user_id).first()).split(';')[0])

    dados = [acordo_SEI.nome,SEI_s,'0','0']

    return render_template('SEI_demandas.html',demandas_count=demandas_count,demandas=demandas,sei=SEI, autores=autores,dados=dados)

#
### CRIAR programa do CNPq

@acordos.route("/cria_programa_cnpq", methods=['GET', 'POST'])
@login_required
def cria_programa_cnpq():
    """
    +---------------------------------------------------------------------------------------+
    |Permite registrar os dados de um programa do CNPq.                                     |
    +---------------------------------------------------------------------------------------+
    """

    form = Programa_CNPqForm()

    if form.validate_on_submit():

        last_programa_cnpq = db.session.query(Programa_CNPq).order_by(Programa_CNPq.ID_PROGRAMA.desc()).first()

        programa_cnpq = Programa_CNPq(ID_PROGRAMA    = last_programa_cnpq.ID_PROGRAMA + 1,
                                      COD_PROGRAMA   = form.cod_programa.data,
                                      NOME_PROGRAMA  = form.nome_programa.data,
                                      SIGLA_PROGRAMA = form.sigla_programa.data,
                                      COORD          = form.coord.data)

        db.session.add(programa_cnpq)
        db.session.commit()

        registra_log_auto(current_user.id,None,'pac')

        flash('Programa do CNPq registrado!','sucesso')
        return redirect(url_for('acordos.lista_programa_cnpq'))

    return render_template('cria_programa_cnpq.html', form=form)

#
#
### LISTAR programas do CNPq

@acordos.route("/lista_programa_cnpq")
def lista_programa_cnpq():
    """
    +---------------------------------------------------------------------------------------+
    |Permite listar os programas do CNPq.                                                   |
    +---------------------------------------------------------------------------------------+
    """

    programas = []

    programas_cnpq = Programa_CNPq.query.order_by(Programa_CNPq.NOME_PROGRAMA).all()

    quantidade = Programa_CNPq.query.count()

    for prog in programas_cnpq:

        prog_dt_ult_pag = db.session.query(label('max_ult_pag',func.max(Processo_Filho.dt_ult_pag)))\
                                    .filter(Processo_Filho.cod_programa == prog.COD_PROGRAMA).first()

        programas.append([prog.ID_PROGRAMA,prog.COD_PROGRAMA,prog.NOME_PROGRAMA,prog.SIGLA_PROGRAMA,prog.COORD,prog_dt_ult_pag.max_ult_pag])

    return render_template('lista_programa_cnpq.html',programas=programas, quantidade=quantidade)

#
### ATUALIZAR programa do CNPq

@acordos.route("/<int:id>/atualiza_programa_cnpq", methods=['GET', 'POST'])
@login_required
def atualiza_programa_cnpq(id):
    """
    +---------------------------------------------------------------------------------------+
    |Permite atualizar os dados de um programa do CNPq selecionado na tela de consulta.     |
    |                                                                                       |
    |Recebe o ID do programa como parâmetro.                                                |
    +---------------------------------------------------------------------------------------+
    """

    programa_cnpq = Programa_CNPq.query.get_or_404(id)

    form = Programa_CNPqForm()

    if form.validate_on_submit():

        programa_cnpq.COD_PROGRAMA   = form.cod_programa.data
        programa_cnpq.NOME_PROGRAMA  = form.nome_programa.data
        programa_cnpq.SIGLA_PROGRAMA = form.sigla_programa.data
        programa_cnpq.COORD          = form.coord.data

        db.session.commit()

        registra_log_auto(current_user.id,None,'pac')

        flash('Programa do CNPq atualizado!','sucesso')
        return redirect(url_for('acordos.lista_programa_cnpq'))
    # traz a informação atual do programa CNPq
    elif request.method == 'GET':
        form.cod_programa.data   = programa_cnpq.COD_PROGRAMA
        form.nome_programa.data  = programa_cnpq.NOME_PROGRAMA
        form.sigla_programa.data = programa_cnpq.SIGLA_PROGRAMA
        form.coord.data          = programa_cnpq.COORD

    return render_template('cria_programa_cnpq.html', title='Update', form=form)

#
### LISTAR processos mãe de um acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/lista_processos_mae_por_acordo")
def lista_processos_mae_por_acordo(acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista os processos mãe vinculados a um acordo.                                         |
    +---------------------------------------------------------------------------------------+
    """

    procs_mae = db.session.query(Acordo_ProcMae.proc_mae_id,
                                 Processo_Mae.proc_mae,
                                 Processo_Mae.coordenador,
                                 Processo_Mae.inic_mae,
                                 Processo_Mae.term_mae,
                                 Processo_Mae.situ_mae)\
                          .join(Processo_Mae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                          .filter(Acordo_ProcMae.acordo_id == acordo_id).all()

    qtd_maes = len(procs_mae)

    maes = []

    for proc in procs_mae:

        qtd_filhos_mae = 0
        pago_mae       = 0
        a_pagar_mae    = 0

        filhos = db.session.query(label('qtd_filhos',func.count(Processo_Filho.processo)),
                                  label('pago',func.sum(Processo_Filho.pago_total)),
                                  label('apagar',func.sum(Processo_Filho.valor_apagar)),
                                  label('cpfs',func.count(distinct(Processo_Filho.cpf))),
                                  label('max_ult_pag',func.max(Processo_Filho.dt_ult_pag)))\
                                  .filter(Processo_Filho.proc_mae == proc.proc_mae)

        qtd_filhos_mae = int(filhos[0][0])
        if filhos[0][1] == None:
            pago_mae = 0
        else:
            pago_mae = float(filhos[0][1])
        if filhos[0][2] == None:
            a_pagar_mae = 0
        else:
            a_pagar_mae = float(filhos[0][2])
        qtd_cpfs = int(filhos[0][3])

        maes.append([proc.proc_mae_id,
                     proc.proc_mae, proc.inic_mae, proc.term_mae,
                     qtd_filhos_mae,
                     locale.currency(pago_mae, symbol=False, grouping = True),
                     locale.currency(a_pagar_mae, symbol=False, grouping = True),
                     qtd_cpfs,
                     filhos[0][4].strftime("%x"),
                     proc.coordenador,
                     proc.situ_mae])



    return render_template('lista_processos_mae.html',procs_mae=maes,qtd_maes=qtd_maes,
                                                      acordo_id=acordo_id,prog=prog,
                                                      edic=edic,epe=epe,uf=uf)
#
### Alterar dados de um processos_mãe de um acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/<proc_mae>/altera_mae", methods=['GET', 'POST'])
def altera_mae(acordo_id,prog,edic,epe,uf,proc_mae):
    """
    +---------------------------------------------------------------------------------------+
    |Alterar dados de um processos_mãe de um acordo.                                        |
    +---------------------------------------------------------------------------------------+
    """

    processo_mae = db.session.query(Processo_Mae).filter(Processo_Mae.proc_mae == proc_mae.replace('_','/')).first()

    form = Altera_proc_mae_Form()

    if form.validate_on_submit():

        processo_mae.coordenador = form.coordenador.data
        processo_mae.situ_mae    = form.situ_mae.data

        db.session.commit()

        registra_log_auto(current_user.id,None,'mae')

        flash('Dados de processo-mãe atualizados manualmente!','sucesso')
        return redirect(url_for('acordos.lista_processos_mae_por_acordo',acordo_id=acordo_id,prog=prog,edic=edic,epe=epe,uf=uf))

    elif request.method == 'GET':

        form.coordenador.data = processo_mae.coordenador
        form.situ_mae.data   = processo_mae.situ_mae


    return render_template('altera_mae.html', form=form,acordo_id=acordo_id,prog=prog,edic=edic,epe=epe,uf=uf,proc_mae=proc_mae)

### ASSOCIAR UM processo mãe a um acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/processo_mae_acordo", methods=['GET', 'POST'])
@login_required
def processo_mae_acordo(acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    | Apesar da planilha COSAO trazer, em tese, os processos mãe aos quais os bolsistas     |
    | estão vinculados, é necessário fazer aconexão destes dados com os dados dos acordos   |
    | celebrados.                                                                           |
    |                                                                                       |
    | Permite associar um processos mãe a um acordo.                                        |
    |                                                                                       |
    | Recebe o ID do acodo como parâmetro.                                                  |
    +---------------------------------------------------------------------------------------+
    """

    programa = db.session.query(Acordo.programa_cnpq).filter(Acordo.id == acordo_id)

    form = func_ProcMae_Acordo(programa)

    if form.validate_on_submit():

        for proc in form.proc_mae.data:
            acordo_procmae = Acordo_ProcMae(acordo_id   = acordo_id,
                                            proc_mae_id = proc)
            db.session.add(acordo_procmae)

        db.session.commit()

        registra_log_auto(current_user.id,None,'ass')

        flash('Processo Mãe relacionado ao Acordo!','sucesso')
        return redirect(url_for('acordos.lista_processos_mae_por_acordo',acordo_id=acordo_id,prog=prog,edic=edic,epe=epe,uf=uf))

    return render_template('associa_processo_mae_acordo.html', form=form,acordo_id=acordo_id,prog=prog,edic=edic,epe=epe,uf=uf)

#
### DELETAR processo MÃE de um ACORDO

@acordos.route('/<int:id>/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/deleta_processo_mae',methods=['GET','POST'])
def deleta_processo_mae(id,acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Deleta a associação de um processo mãe com um acordo.                                  |
    |                                                                                       |
    |Recebe o id da associação como parâmetro.                                              |
    +---------------------------------------------------------------------------------------+
    """

    acordo_procmae = db.session.query(Acordo_ProcMae.id).filter(Acordo_ProcMae.proc_mae_id==id)

    assoc = Acordo_ProcMae.query.get_or_404(acordo_procmae[0][0])

    db.session.delete(assoc)
    db.session.commit()

    registra_log_auto(current_user.id,None,'ass')

    flash ('Associação Processo Mãe - Acordo desfeita!','sucesso')

    return redirect(url_for('acordos.lista_processos_mae_por_acordo',acordo_id=acordo_id,prog=prog,edic=edic,epe=epe,uf=uf))


### LISTAR processos filho de um processo mãe

@acordos.route("/<proc_mae>/<prog>/<edic>/<epe>/<uf>/lista_processos_filho")
def lista_processos_filho(proc_mae,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista os processos filho de um determinado processo mãe.                               |
    +---------------------------------------------------------------------------------------+
    """
    lista = 'mae'

    filhos_banco = db.session.query(Processo_Filho.processo,
                              Processo_Filho.nome,
                              Processo_Filho.cpf,
                              Processo_Filho.modalidade,
                              Processo_Filho.nivel,
                              Processo_Filho.situ_filho,
                              Processo_Filho.inic_filho,
                              Processo_Filho.term_filho,
                              Processo_Filho.mens_pagas,
                              Processo_Filho.pago_total,
                              Processo_Filho.mens_apagar,
                              Processo_Filho.valor_apagar,
                              Processo_Filho.dt_ult_pag)\
                       .filter(Processo_Filho.proc_mae == proc_mae.replace('_','/'))\
                       .order_by(Processo_Filho.situ_filho,Processo_Filho.nome).all()

    qtd_filhos = len(filhos_banco)

    ult_pag = [filho.dt_ult_pag for filho in filhos_banco]

    max_ult_pag = max(ult_pag)

    filhos = []

    for filho in filhos_banco:

        filhos.append([filho.processo,
                       filho.nome,
                       filho.cpf,
                       filho.modalidade,
                       filho.nivel,
                       filho.situ_filho,
                       filho.inic_filho.strftime("%x"),
                       filho.term_filho.strftime("%x"),
                       filho.mens_pagas,
                       locale.currency(filho.pago_total, symbol=False, grouping = True),
                       filho.mens_apagar,
                       locale.currency(filho.valor_apagar, symbol=False, grouping = True)])



    return render_template('lista_processos_filho.html',proc_mae=proc_mae,filhos=filhos,
                                                   qtd_filhos=qtd_filhos,lista=lista,
                                                   prog=prog,edic=edic,epe=epe,uf=uf,max_ult_pag=max_ult_pag.strftime("%m/%Y"))
#

@acordos.route("/<proc_mae>/<prog>/<edic>/<epe>/<uf>/carrega_sit_sigef", methods=['GET', 'POST'])
def carrega_sit_sigef(proc_mae,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Carrega situações dos processos-filho obtidas de uma planilha gerada via sigef         |
    +---------------------------------------------------------------------------------------+
    """

    form =  ArquivoForm()

    if form.validate_on_submit():

        tempdirectory = tempfile.gettempdir()

        f = form.arquivo.data
        fname = secure_filename(f.filename)
        arq_sigef = os.path.join(tempdirectory, fname)
        f.save(arq_sigef)

        print ('\n')
        print ('***  ARQUIVO ***',arq_sigef)

        cargaSit(arq_sigef)

        registra_log_auto(current_user.id,None,'car')

        return redirect(url_for('acordos.lista_processos_filho', proc_mae=proc_mae, prog=prog, edic=edic, epe=epe, uf=uf))

    return render_template('grab_file.html',form=form,data_ref="sigef")

#
### LISTAR bolsistas (cpf) de um processo mãe

@acordos.route("/<proc_mae>/<prog>/<edic>/<epe>/<uf>/lista_bolsistas")
def lista_bolsistas(proc_mae,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista bolsistas (cpfs) de um determinado processo mãe.                                 |
    +---------------------------------------------------------------------------------------+
    """

    cpfs_banco = db.session.query(Processo_Filho.nome,
                              Processo_Filho.cpf,
                              Processo_Filho.modalidade,
                              Processo_Filho.nivel,
                              Processo_Filho.situ_filho,
                              label('min_inic_filho',func.min(Processo_Filho.inic_filho)),
                              label('max_term_filho',func.max(Processo_Filho.term_filho)),
                              label('mens_p',func.sum(Processo_Filho.mens_pagas)),
                              label('pago',func.sum(Processo_Filho.pago_total)),
                              label('mens_ap',func.sum(Processo_Filho.mens_apagar)),
                              label('apagar',func.sum(Processo_Filho.valor_apagar)))\
                       .filter(Processo_Filho.proc_mae == proc_mae.replace('_','/'))\
                       .group_by(Processo_Filho.cpf,
                                 Processo_Filho.nome,
                                 Processo_Filho.modalidade,
                                 Processo_Filho.nivel,
                                 Processo_Filho.situ_filho)\
                       .order_by(Processo_Filho.nome).all()

    qtd_cpfs = len(cpfs_banco)

    cpfs = []

    for cpf in cpfs_banco:

        cpfs.append([cpf.nome,
                       cpf.cpf,
                       cpf.modalidade,
                       cpf.nivel,
                       cpf.situ_filho,
                       cpf.min_inic_filho.strftime("%x"),
                       cpf.max_term_filho.strftime("%x"),
                       cpf.mens_p,
                       locale.currency(cpf.pago, symbol=False, grouping = True),
                       cpf.mens_ap,
                       locale.currency(cpf.apagar, symbol=False, grouping = True)])



    return render_template('lista_bolsistas.html',proc_mae=proc_mae,cpfs=cpfs,
                                                   qtd_cpfs=qtd_cpfs,
                                                   prog=prog,edic=edic,epe=epe,uf=uf)
#
### LISTAR processos filhos de um acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/lista_processos_filho_por_acordo")
def lista_processos_filho_por_acordo(acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista os processos filhos vinculados a um acordo.                                      |
    +---------------------------------------------------------------------------------------+
    """
    lista = 'acordo'

    procs_mae = db.session.query(Processo_Mae.proc_mae)\
                          .join(Acordo_ProcMae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                          .filter(Acordo_ProcMae.acordo_id == acordo_id).all()

    qtd_maes = len(procs_mae)

    filhos = []
    qtd_filhos = 0
    ultimo_pag = []

    for proc in procs_mae:

        filhos_banco = db.session.query(Processo_Filho.processo,
                                  Processo_Filho.nome,
                                  Processo_Filho.cpf,
                                  Processo_Filho.modalidade,
                                  Processo_Filho.nivel,
                                  Processo_Filho.situ_filho,
                                  Processo_Filho.inic_filho,
                                  Processo_Filho.term_filho,
                                  Processo_Filho.mens_pagas,
                                  Processo_Filho.pago_total,
                                  Processo_Filho.mens_apagar,
                                  Processo_Filho.valor_apagar,
                                  Processo_Filho.dt_ult_pag)\
                           .filter(Processo_Filho.proc_mae == proc.proc_mae)\
                           .order_by(Processo_Filho.situ_filho,Processo_Filho.nome).all()

        qtd_filhos += len(filhos_banco)

        ult_pag = [filho.dt_ult_pag for filho in filhos_banco]

        ultimo_pag.append(max(ult_pag))


        for filho in filhos_banco:

            filhos.append([filho.processo,
                          filho.nome,
                          filho.cpf,
                          filho.modalidade,
                          filho.nivel,
                          filho.situ_filho,
                          filho.inic_filho.strftime("%x"),
                          filho.term_filho.strftime("%x"),
                          filho.mens_pagas,
                          locale.currency(filho.pago_total, symbol=False, grouping = True),
                          filho.mens_apagar,
                          locale.currency(filho.valor_apagar, symbol=False, grouping = True)])


    max_ult_pag = max(ultimo_pag)

    return render_template('lista_processos_filho.html',filhos=filhos,qtd_maes=qtd_maes,
                                                        qtd_filhos=qtd_filhos,lista=lista,acordo_id=acordo_id,
                                                        prog=prog,edic=edic,epe=epe,uf=uf,max_ult_pag=max_ult_pag.strftime("%m/%Y"))
#

#
### LISTAR bolsistas (cpf) de um acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/lista_bolsistas")
def lista_bolsistas_acordo(acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista bolsistas (cpfs) de um acordo especifico.                                        |
    +---------------------------------------------------------------------------------------+
    """

    lista = 'acordo'

    procs_mae = db.session.query(Processo_Mae.proc_mae)\
                          .join(Acordo_ProcMae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                          .filter(Acordo_ProcMae.acordo_id == acordo_id).all()

    l_procs_mae = [p.proc_mae for p in procs_mae]

    qtd_maes = len(procs_mae)

    filhos = []
    qtd_filhos = 0
    ultimo_pag = []

    cpfs_banco = db.session.query(Processo_Filho.nome,
                              Processo_Filho.cpf,
                              Processo_Filho.modalidade,
                              Processo_Filho.nivel,
                              Processo_Filho.situ_filho,
                              label('min_inic_filho',func.min(Processo_Filho.inic_filho)),
                              label('max_term_filho',func.max(Processo_Filho.term_filho)),
                              label('mens_p',func.sum(Processo_Filho.mens_pagas)),
                              label('pago',func.sum(Processo_Filho.pago_total)),
                              label('mens_ap',func.sum(Processo_Filho.mens_apagar)),
                              label('apagar',func.sum(Processo_Filho.valor_apagar)))\
                       .filter(Processo_Filho.proc_mae.in_(l_procs_mae))\
                       .group_by(Processo_Filho.cpf,
                                 Processo_Filho.nome,
                                 Processo_Filho.modalidade,
                                 Processo_Filho.nivel,
                                 Processo_Filho.situ_filho)\
                       .order_by(Processo_Filho.nome).all()

    qtd_cpfs = len(cpfs_banco)

    cpfs = []

    for cpf in cpfs_banco:

        cpfs.append([cpf.nome,
                       cpf.cpf,
                       cpf.modalidade,
                       cpf.nivel,
                       cpf.situ_filho,
                       cpf.min_inic_filho.strftime("%x"),
                       cpf.max_term_filho.strftime("%x"),
                       cpf.mens_p,
                       locale.currency(cpf.pago, symbol=False, grouping = True),
                       cpf.mens_ap,
                       locale.currency(cpf.apagar, symbol=False, grouping = True)])

    return render_template('lista_bolsistas.html',proc_mae=l_procs_mae,cpfs=cpfs,
                                                   qtd_cpfs=qtd_cpfs,
                                                   prog=prog,edic=edic,epe=epe,uf=uf)
#
## RESUMO acordos

@acordos.route('/resumo_acordos')
def resumo_acordos():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta um resumo dos acordos por programa da coordenação.                           |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    programas = db.session.query(Programa_CNPq.COD_PROGRAMA,
                                 Programa_CNPq.SIGLA_PROGRAMA,
                                 label('vl_cnpq',func.sum(Acordo.valor_cnpq)),
                                 label('vl_epe',func.sum(Acordo.valor_epe)),
                                 label('qtd',func.count(Acordo.id)),
                                 label('qtd_edic',func.count(distinct(Acordo.nome))))\
                                 .join(Acordo,Acordo.programa_cnpq==Programa_CNPq.COD_PROGRAMA)\
                                 .group_by(Programa_CNPq.SIGLA_PROGRAMA,Programa_CNPq.COD_PROGRAMA)\
                                 .all()
#
    programas_s = []

    for prog in programas:

        maes_filhos   = db.session.query(label('qtd_maes',func.count(distinct(Processo_Filho.proc_mae))),
                                         label('qtd_filhos',func.count(distinct(Processo_Filho.processo))),
                                         label('qtd_cpfs',func.count(distinct(Processo_Filho.cpf))),
                                         label('pago',func.sum(Processo_Filho.pago_total)),
                                         label('apagar',func.sum(Processo_Filho.valor_apagar)))\
                                         .filter(Processo_Filho.cod_programa==prog[0])\
                                         .all()

        prog_s = list(prog)

        prog_s[2] = locale.currency(prog_s[2], symbol=False, grouping = True)
        prog_s[3] = locale.currency(prog_s[3], symbol=False, grouping = True)
        prog_s.append(maes_filhos[0][0])
        prog_s.append(maes_filhos[0][1])
        prog_s.append(maes_filhos[0][2])
        if maes_filhos[0][3] == None:
            prog_s.append(locale.currency(0, symbol=False, grouping = True))
        else:
            prog_s.append(locale.currency(maes_filhos[0][3], symbol=False, grouping = True))
        if maes_filhos[0][4] == None:
            prog_s.append(locale.currency(0, symbol=False, grouping = True))
        else:
            prog_s.append(locale.currency(maes_filhos[0][4], symbol=False, grouping = True))

        programas_s.append(prog_s)

    maes_sem_acordo = db.session.query(Processo_Mae.cod_programa,
                                       Processo_Mae.proc_mae)\
                                       .outerjoin(Acordo_ProcMae,Acordo_ProcMae.proc_mae_id==Processo_Mae.id)\
                                       .filter(Acordo_ProcMae.proc_mae_id == None)\
                                       .order_by(Processo_Mae.cod_programa,Processo_Mae.proc_mae)

    qtd_maes_sem_acordo = len(list(maes_sem_acordo))

    return render_template('resumo_acordos.html',programas=programas_s,
                                                 maes_sem_acordo=maes_sem_acordo,
                                                 qtd_maes_sem_acordo=qtd_maes_sem_acordo)

#
## RESUMO edições dos programas (acordos)

@acordos.route('/<cod_programa>/<sigla>/edic_programa')
def edic_programa(cod_programa,sigla):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta as edições de um determinado programa (acordos).                             |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    edics = db.session.query(Acordo.nome,
                               func.count(Acordo.id),
                               func.sum(Acordo.valor_cnpq),
                               func.sum(Acordo.valor_epe))\
                               .filter(Acordo.programa_cnpq == cod_programa)\
                               .group_by(Acordo.nome)\
                               .order_by(Acordo.nome.desc()).all()
#
    edics_s = []

    for edic in edics:

        maes_edic = db.session.query(Processo_Mae.proc_mae)\
                                    .join(Acordo_ProcMae,Acordo_ProcMae.proc_mae_id==Processo_Mae.id)\
                                    .join(Acordo,Acordo.id==Acordo_ProcMae.acordo_id)\
                                    .filter(Acordo.nome==edic[0])

        qtd_maes        = len(list(maes_edic))
        qtd_filhos_edic = 0
        qtd_cpfs_edic   = 0
        pago_edic       = 0
        apagar_edic     = 0

        if len(list(maes_edic)) != 0:

            for mae in maes_edic:
                filhos_edic   = db.session.query(label('qtd_filhos',func.count(Processo_Filho.processo)),
                                                 label('qtd_cpfs',func.count(Processo_Filho.cpf)),
                                                 label('pago',func.sum(Processo_Filho.pago_total)),
                                                 label('apagar',func.sum(Processo_Filho.valor_apagar)))\
                                                 .filter(Processo_Filho.proc_mae==mae.proc_mae)

                qtd_filhos_edic += none_0(filhos_edic[0].qtd_filhos)
                qtd_cpfs_edic   += none_0(filhos_edic[0].qtd_cpfs)
                pago_edic       += none_0(filhos_edic[0].pago)
                apagar_edic     += none_0(filhos_edic[0].apagar)

        edic_s = list(edic)

        edic_s[2] = locale.currency(edic_s[2], symbol=False, grouping = True)
        edic_s[3] = locale.currency(edic_s[3], symbol=False, grouping = True)
        edic_s.append(qtd_maes)
        edic_s.append(qtd_filhos_edic)
        edic_s.append(qtd_cpfs_edic)
        edic_s.append(locale.currency(pago_edic, symbol=False, grouping = True))
        edic_s.append(locale.currency(apagar_edic, symbol=False, grouping = True))

        edics_s.append(edic_s)


    return render_template('edic_programa.html',edics=edics_s,sigla=sigla)

#
#
## acordos  no mapa do Brasil

@acordos.route('/brasil_acordos')
def brasil_acordos():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta um mapa onde se pode verificar os acordos e encomendas por UF.               |
    +---------------------------------------------------------------------------------------+
    """

    gps = {'AC':[-9.977916,-67.826068],
           'AL':[-9.649433,-35.709335],
           'AM':[-3.074759,-60.028723],
           'AP':[0.052334,-51.070093],
           'BA':[-13.008304,-38.512027],
           'CE':[-3.795849,-38.497930],
           'DF':[-15.710702,-47.911077],
           'ES':[-20.276832,-40.300442],
           'GO':[-16.680903,-49.250701],
           'MA':[-2.501711,-44.284316],
           'MG':[-19.884511,-43.915749],
           'MS':[-20.447545,-54.603542],
           'MT':[-15.566057,-56.072258],
           'PA':[-1.454934,-48.475778],
           'PB':[-7.205724,-35.921335],
           'PE':[-8.060426,-34.901544],
           'PI':[-5.096300,-42.798928],
           'PR':[-25.446918,-49.245448],
           'RJ':[-22.904571,-43.173827],
           'RN':[-5.829595,-35.212017],
           'RO':[-8.625350,-63.844920],
           'RR':[2.930872,-60.672953],
           'RS':[-30.028724,-51.228277],
           'SC':[-27.571250,-48.509038],
           'SE':[-10.909057,-37.050032],
           'SP':[-23.536390,-46.714247],
           'TO':[-10.182099,-48.331027]}

    programas = db.session.query(Programa_CNPq.SIGLA_PROGRAMA,
                                 Programa_CNPq.COD_PROGRAMA,
                                 Programa_CNPq.COORD,
                                 Programa_CNPq.ID_PROGRAMA,
                                 Acordo.uf,
                                 Acordo.epe,
                                 label('qtd_acordos',func.count(Acordo.id)))\
                          .join(Acordo, Acordo.programa_cnpq == Programa_CNPq.COD_PROGRAMA)\
                          .order_by(Programa_CNPq.SIGLA_PROGRAMA)\
                          .group_by(Acordo.uf,
                                    Programa_CNPq.SIGLA_PROGRAMA,
                                    Programa_CNPq.COD_PROGRAMA,
                                    Programa_CNPq.COORD,
                                    Programa_CNPq.ID_PROGRAMA,
                                    Acordo.epe)

    m = Map(location=[-15.7, -47.9],
            tiles='OpenStreetMap',
            control_scale = True,
            zoom_start = 2,
            min_zoom=2)

    m.fit_bounds([[-34,-74],[3,-34]])

    for uf in gps:
        qtd_na_uf = 0
        cor = 'blue'
        pop = '<b>Acordos - '+uf+':</b><br>'
        for p in programas:
            if p.uf == uf:
                tip = '<b>'+uf+'</b><br>EPE: '+p.epe
                pop += '<p>'+p.SIGLA_PROGRAMA+' ('+str(p.qtd_acordos)+')</p>'
                qtd_na_uf += p.qtd_acordos
        if pop == '<b>Acordos - '+uf+':</b><br>':
            tip = '<b>'+uf+'</b>'
            pop = 'N&atilde;o h&aacute; Acordos celebrados com <b>'+uf+'</b>.'

        #Circulos com raios em metros
        Circle(location = [float(gps[uf][0]), float(gps[uf][1])],
               radius = 18000 + qtd_na_uf*8000,
               tooltip = tip,
               popup = Popup(pop,max_width=150),
               fill = True,
               fill_opacity = 0.2,
               weight = 1,
               color=cor).add_to(m)


    return render_template('brasil_convenios.html', m = m._repr_html_())
#
### gasto mês por acordo

@acordos.route("/<int:acordo_id>/<prog>/<edic>/<epe>/<uf>/gasto_mes")
def gasto_mes(acordo_id,prog,edic,epe,uf):
    """
    +---------------------------------------------------------------------------------------+
    |Lista os gastos mensais por acordo.                                                    |
    +---------------------------------------------------------------------------------------+
    """

    gastos = []

    procs_mae = db.session.query(Acordo_ProcMae.proc_mae_id,
                                 Processo_Mae.proc_mae,
                                 Processo_Mae.inic_mae,
                                 Processo_Mae.term_mae)\
                          .join(Processo_Mae, Processo_Mae.id == Acordo_ProcMae.proc_mae_id)\
                          .filter(Acordo_ProcMae.acordo_id == acordo_id).all()

    for proc in procs_mae:

        pags_proc_mae = db.session.query(label('vl_pago',func.sum(PagamentosPDCTR.valor_pago)),
                                         label('qtd',func.count(PagamentosPDCTR.valor_pago)),
                                         PagamentosPDCTR.data_pagamento)\
                                  .group_by(PagamentosPDCTR.data_pagamento)\
                                  .filter(PagamentosPDCTR.proc_mae == proc.proc_mae).all()

        #datas com dias trocados para evita problemas com rrule
        strt_dt = datetime.date(proc.inic_mae.year,proc.inic_mae.month,1)
        end_dt  = datetime.date(proc.term_mae.year,proc.term_mae.month,28)

        dates = [dt for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]

        for d in dates:

            d1 = datetime.date(d.year,d.month,1)

            p = 0
            q = 0
            for pag in pags_proc_mae:
                #if pag.data_pagamento == d1:
                if pag.data_pagamento.year == d.year and pag.data_pagamento.month == d.month:
                    p = pag.vl_pago
                    q = pag.qtd

            gastos.append((d1,p,q))

    datas = set([x[0] for x in gastos])

    lista = []
    for d in datas:
        v = 0
        qtd = 0
        for g in gastos:
            if g[0] == d:
                v += g[1]
                qtd += g[2]
        lista.append((d,v,qtd))

    lista.sort(key = lambda x: x[0])

    gastos = [ (x[0].year,x[0].month,locale.currency(x[1], symbol=False, grouping = True),x[2]) for x in lista ]

    return render_template('gasto_mes.html',gastos=gastos,qtd_meses=len(gastos),
                                                   prog=prog,edic=edic,epe=epe,uf=uf)

#
