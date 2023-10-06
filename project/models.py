"""
.. topic:: Modelos (tabelas nos bancos de dados)

    Os modelos são classes que definem a estrutura das tabelas dos bancos de dados.

    Antes este aplicativo utilizava dois bancos de dados, um para os dados referentes às demandas e o outro para os dados de
    Acordos e Convênios, contudo, na migração para o PosgreSQL, optou-se por juntar tudo em um só.

    Demandas possui os modelos:

    * Tipos_Demanda: tipos de demanda
    * Passos_Tipos: passos que devem ser tomados em cada tipo de demanda
    * Plano_Trabalho: atividades da coordenação por usuário
    * Ativ_Usu: atividades atribuidas a cada usuário
    * Msgs_Recebidas: mensagens recebidas pelo usuário
    * Demanda: dados das demandas.
    * Providencia: dados das proviências tomadas para cada demanda.
    * Despacho: dados dos despachos, ou encaminhamentos, efetuados pela chefia imediata em cada demanda.
    * User: dados dos usuários registrados.

    Acordos e Convênios tem os modelos:

    * RefCargaPDCTR: datas de referência das cargas de dados realizadas, conforme planilhas COSAO.
    * PagamentosPDCTR: dados brutos da planinha COSAO.
    * Bolsa: dados das bolsas utilizada no PDCTR.
    * Programa_CNPq: programas do CNPq, normalmente utilizados nos Acordos.
    * Acordo: dados dos acordos celebrados.
    * ProcessoMae: dados dos processos mãe (projetos) criados para permitir a implemtação de bolsas.
    * Programa_Interesse: programas tratados na coordenação
    * Chamadas: dados das chamadas homologadas pelo CNPq
    * Homologados: projetos ou bolsistas homologados pelo CNPq
    * Programa: programas importados do SICONV a partir de lista de interesse copes
    * Proposta: propostas cadastradas no SICONV a partir dos programas selecionados
    * Convenio: convênios cadastrados no SICONV a partir das propostas selecionadas
    * Pagamento: relação dos pagamento efetuados pela convenente, aqui são armazemados os dados agregados por recebedor
    * Empenho: empenhos realizados conforme o SICONV
    * Desembolso: desembolsost realizados conforme o SICONV
    * Crono_Desemb: cronograma de desembolso dos convênios
    * Plano_Aplic: plano de aplicação das propostas
    * Coords: coordenações técnicas
    * RefSICONV: data da carga SICONV
    * MSG_Siconv: mensagens do siconv
    * objeto: demais objetos

    Abaixo seguem os Modelos e respectivos campos.
"""
# models.py
import locale
from project import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

    ##############################################################################################
    ##  banco demandas                                                                          ##
    ##############################################################################################

#
## tabela das coordenações técnicas
class Coords (db.Model):

    __tablename__ = "coords"
    __table_args__ = {"schema": "dem"} 

    id            = db.Column(db.Integer,primary_key=True)
    sigla         = db.Column(db.String)
    desc          = db.Column(db.String)
    id_pai        = db.Column(db.Integer)
    id_chefe      = db.Column(db.Integer)
    id_chefe_subs = db.Column(db.Integer)

    def __init__ (self,sigla,desc,id_pai,id_chefe,id_chefe_subs):

        self.sigla         = sigla
        self.desc          = desc
        self.id_pai        = id_pai
        self.id_chefe      = id_chefe
        self.id_chefe_subs = id_chefe_subs

    def __repr__ (self):
        return f"{self.sigla};{self.desc}"


class Tipos_Demanda(db.Model):

    __tablename__ = 'tipos_demanda'
    __table_args__ = {"schema": "dem"}

    id         = db.Column(db.Integer, primary_key=True)
    tipo       = db.Column(db.String,nullable=False)
    relevancia = db.Column(db.Integer,nullable=False)
    unidade    = db.Column(db.String)

    def __init__(self, tipo, relevancia, unidade):

        self.tipo       = tipo
        self.relevancia = relevancia
        self.unidade    = unidade

    def __repr__(self):

        return f"{self.tipo};{self.unidade}"

#
class Passos_Tipos(db.Model):

    __tablename__ = 'passos_tipos'
    __table_args__ = {"schema": "dem"}

    id      = db.Column(db.Integer, primary_key=True)
    tipo_id = db.Column(db.Integer, db.ForeignKey('dem.tipos_demanda.id'),nullable=False)
    ordem   = db.Column(db.Integer, nullable=False)
    passo   = db.Column(db.String, nullable=False)
    desc    = db.Column(db.String, nullable=False)

    def __init__(self, tipo_id, ordem, passo, desc):

        self.tipo_id = tipo_id
        self.ordem   = ordem
        self.passo   = passo
        self.desc    = desc

    def __repr__(self):

        return f"{self.tipo_id};{self.ordem};{self.passo};{self.desc}"


class Plano_Trabalho(db.Model):

    __tablename__ = 'plano_trabalho'
    __table_args__ = {"schema": "dem"}

    id              = db.Column(db.Integer, primary_key=True)
    atividade_sigla = db.Column(db.String,nullable=False)
    atividade_desc  = db.Column(db.String,nullable=False)
    natureza        = db.Column(db.String,nullable=False)
    meta            = db.Column(db.Float,nullable=False)
    situa           = db.Column(db.String)
    unidade         = db.Column(db.String)
 
    def __init__(self, atividade_sigla, atividade_desc, natureza, meta, situa, unidade):

        self.atividade_sigla = atividade_sigla
        self.atividade_desc  = atividade_desc
        self.natureza        = natureza
        self.meta            = meta
        self.situa           = situa
        self.unidade         = unidade

    def __repr__(self):

        return f"{self.atividade_sigla};{self.atividade_desc};{self.natureza};{self.meta};{self.situa};{self.unidade}"

#
class Ativ_Usu(db.Model):

    __tablename__ = 'ativ_usu'
    __table_args__ = {"schema": "dem"}

    id           = db.Column(db.Integer, primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('dem.plano_trabalho.id'),nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('dem.users.id'),nullable=False)
    nivel        = db.Column(db.String, nullable=False)


    def __init__(self, atividade_id, user_id, nivel):

        self.atividade_id = atividade_id
        self.user_id      = user_id
        self.nivel        = nivel

    def __repr__(self):

        return f"{self.atividade_id};{self.user_id};{self.nivel}"

#
#
class Msgs_Recebidas(db.Model):

    __tablename__ = 'msgs_recebidas'
    __table_args__ = {"schema": "dem"}

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('dem.users.id'),nullable=False)
    data_hora  = db.Column(db.DateTime,nullable=False,default=datetime.now())
    demanda_id = db.Column(db.Integer, db.ForeignKey('dem.demandas.id'),nullable=False)
    msg        = db.Column(db.String, nullable=False)


    def __init__(self, user_id, data_hora, demanda_id, msg):

        self.user_id    = user_id
        self.data_hora  = data_hora
        self.demanda_id = demanda_id
        self.msg        = msg

    def __repr__(self):

        return f"{self.user_id};{self.data_hora};{self.demanda_id};{self.msg}"


class Demanda(db.Model):

    __tablename__ = 'demandas'
    __table_args__ = {"schema": "dem"}

    id                     = db.Column(db.Integer, primary_key=True)
    programa               = db.Column(db.Integer, nullable=False)
    sei                    = db.Column(db.String, nullable=False)
    convênio               = db.Column(db.String)
    ano_convênio           = db.Column(db.Integer)
    tipo                   = db.Column(db.String,nullable=False)
    data                   = db.Column(db.DateTime,nullable=False,default=datetime.now())
    user_id                = db.Column(db.Integer, db.ForeignKey('dem.users.id'),nullable=False)
    titulo                 = db.Column(db.String(140),nullable=False)
    desc                   = db.Column(db.Text,nullable=False)
    necessita_despacho     = db.Column(db.Integer)
    conclu                 = db.Column(db.String)
    data_conclu            = db.Column(db.DateTime)
    necessita_despacho_cg  = db.Column(db.Integer)
    urgencia               = db.Column(db.Integer,default=3)
    data_env_despacho      = db.Column(db.DateTime)
    nota                   = db.Column(db.Integer)
    data_verific           = db.Column(db.DateTime)

    providencias        = db.relationship('Providencia',backref='demanda',cascade="delete, delete-orphan")
    despachos           = db.relationship('Despacho',backref='demanda',cascade="delete, delete-orphan")


    def __init__(self, programa, sei, convênio, ano_convênio, tipo, data, user_id, titulo, desc, necessita_despacho,\
                 conclu, data_conclu,necessita_despacho_cg,urgencia,data_env_despacho,nota,data_verific):
        self.programa              = programa
        self.sei                   = sei
        self.convênio              = convênio
        self.ano_convênio          = ano_convênio
        self.tipo                  = tipo
        self.data                  = data
        self.user_id               = user_id
        self.titulo                = titulo
        self.desc                  = desc
        self.necessita_despacho    = necessita_despacho
        self.conclu                = conclu
        self.data_conclu           = data_conclu
        self.necessita_despacho_cg = necessita_despacho_cg
        self.urgencia              = urgencia
        self.data_env_despacho     = data_env_despacho
        self.nota                  = nota
        self.data_verific          = data_verific

    def __repr__(self):

        if self.necessita_despacho == '1':
            flag1 = 'Necessida despacho'
        else:
            flag1 = ''
        if self.conclu == '1':
            flag2 = 'Concluído'
        else:
            flag2 = ''
        if self.necessita_despacho_cg == '1':
            flag3 = 'Necessida despacho CG'
        else:
            flag3 = ''

        return f"{self.programa};{self.sei};{self.convênio};{self.ano_convênio};{self.tipo};{self.data};\
                 {self.user_id};{self.titulo};{flag1};{flag2};{flag3};{self.data_conclu};{self.data_verific}"

class Despacho(db.Model):

    __tablename__ = 'despachos'
    __table_args__ = {"schema": "dem"}

    id         = db.Column(db.Integer, primary_key=True)
    data       = db.Column(db.DateTime,nullable=False,default=datetime.now())
    user_id    = db.Column(db.Integer, db.ForeignKey('dem.users.id', ondelete="CASCADE"),nullable=False)
    demanda_id = db.Column(db.Integer, db.ForeignKey('dem.demandas.id', ondelete="CASCADE"),nullable=False)
    texto      = db.Column(db.Text,nullable=False)
    passo      = db.Column(db.String)

    def __init__(self, data, user_id, demanda_id, texto, passo):

        self.data       = data
        self.user_id    = user_id
        self.demanda_id = demanda_id
        self.texto      = texto
        self.passo      = passo


    def __repr__(self):

        return f"{self.data};{self.user_id};{self.demanda_id};{self.texto};{self.passo}"

class Providencia(db.Model):

    __tablename__ = 'providencias'
    __table_args__ = {"schema": "dem"}

    id         = db.Column(db.Integer, primary_key=True)
    data       = db.Column(db.DateTime,nullable=False,default=datetime.now())
    demanda_id = db.Column(db.Integer, db.ForeignKey('dem.demandas.id', ondelete="CASCADE"),nullable=False)
    texto      = db.Column(db.Text,nullable=False)
    user_id    = db.Column(db.Integer, nullable=False)
    duracao    = db.Column(db.Integer)
    programada = db.Column(db.Integer)
    passo      = db.Column(db.String)

    def __init__(self, data, demanda_id, texto, user_id, duracao, programada, passo):

        self.data       = data
        self.demanda_id = demanda_id
        self.texto      = texto
        self.user_id    = user_id
        self.duracao    = duracao
        self.programada = programada
        self.passo      = passo

    def __repr__(self):

        return f"{self.data};{self.demanda_id};{self.texto};{self.passo}"

class User(db.Model, UserMixin):

    __tablename__ = 'users'
    __table_args__ = {"schema": "dem"}

    id                         = db.Column(db.Integer,primary_key=True)
    profile_image              = db.Column(db.String(64),nullable=False,default='default_profile.png')
    email                      = db.Column(db.String(64),unique=True,index=True)
    username                   = db.Column(db.String(64),unique=True,index=True)
    password_hash              = db.Column(db.String(128))
    despacha                   = db.Column(db.Integer)
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed            = db.Column(db.Integer, nullable=True, default=0)
    email_confirmed_on         = db.Column(db.DateTime, nullable=True)
    registered_on              = db.Column(db.DateTime, nullable=True)
    last_logged_in             = db.Column(db.DateTime, nullable=True)
    current_logged_in          = db.Column(db.DateTime, nullable=True)
    role                       = db.Column(db.String, default='user')
    coord                      = db.Column(db.String)
    despacha2                  = db.Column(db.Integer)
    ativo                      = db.Column(db.Integer)
    cargo_func                 = db.Column(db.String)
    despacha0                  = db.Column(db.Integer)


    posts = db.relationship ('Demanda',backref='author',lazy=True)
    desp  = db.relationship ('Despacho',backref='author',lazy=True)

    def __init__(self,email,username,plaintext_password,despacha,coord,despacha2,ativo,cargo_func,\
                 despacha0,email_confirmation_sent_on=None,role='user'):

        self.email                      = email
        self.username                   = username
        self.password_hash              = generate_password_hash(plaintext_password)
        #self.password = plaintext_password
        self.despacha                   = despacha
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed            = 0
        self.email_confirmed_on         = None
        self.registered_on              = datetime.now()
        self.last_logged_in             = None
        self.current_logged_in          = datetime.now()
        self.role                       = role
        self.coord                      = coord
        self.despacha2                  = despacha2
        self.ativo                      = ativo
        self.cargo_func                 = cargo_func
        self.despacha0                  = despacha0

    def check_password (self,plaintext_password):

        return check_password_hash(self.password_hash,plaintext_password)

    def __repr__(self):

        return f"{self.username};{self.despacha};{self.despacha2};{self.cargo_func};{self.despacha0}"
#
## tabela de registro dos principais commits
class Log_Auto(db.Model):

    __tablename__ = 'log_auto'
    __table_args__ = {"schema": "dem"}

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_hora   = db.Column(db.DateTime,nullable=False,default=datetime.now())
    user_id     = db.Column(db.Integer, db.ForeignKey('dem.users.id'),nullable=False)
    demanda_id  = db.Column(db.Integer, db.ForeignKey('dem.demandas.id'))
    atividade   = db.Column(db.Integer,db.ForeignKey('dem.plano_trabalho.id'))
    duracao     = db.Column(db.Integer,default=0)
    registro    = db.Column(db.String)

    def __init__(self, data_hora, user_id, demanda_id, atividade, duracao, registro):

        self.data_hora  = data_hora
        self.user_id    = user_id
        self.demanda_id = demanda_id
        self.atividade  = atividade
        self.duracao    = duracao
        self.registro   = registro

    def __repr__(self):

        return f"{self.data_hora};{self.user_id};{self.demanda_id};{self.registro}"

#
## tabela com dados gerais
class Sistema(db.Model):

    __tablename__ = 'sistema'
    __table_args__ = {"schema": "dem"}

    id            = db.Column(db.Integer, primary_key=True)
    nome_sistema  = db.Column(db.String,nullable=False)
    descritivo    = db.Column(db.Text,nullable=False)
    versao        = db.Column(db.String)


    def __init__(self, nome_sistema, descritivo, versao):

        self.nome_sistema  = nome_sistema
        self.descritivo    = descritivo
        self.versao        = versao

    def __repr__(self):

        return f"{self.nome_sistema};{self.descritivo};{self.versao}"


# dados dos objetos
class Objeto(db.Model):

    __tablename__ = 'objeto'
    __table_args__ = {"schema": "dem"}

    id           = db.Column(db.Integer,primary_key=True)
    coord        = db.Column(db.String)
    nome         = db.Column(db.String)
    sei          = db.Column(db.String,unique=True,index=True)
    contraparte  = db.Column(db.String)
    data_inicio  = db.Column(db.Date)
    data_fim     = db.Column(db.Date)
    valor        = db.Column(db.Float)
    descri       = db.Column(db.String)

    def __init__(self,coord,nome,sei,contraparte,data_inicio,data_fim,valor,descri):
        self.coord            = coord
        self.nome             = nome
        self.sei              = sei
        self.contraparte      = contraparte
        self.data_inicio      = data_inicio
        self.data_fim         = data_fim
        self.valor            = valor
        self.descri           = descri

    def __repr__(self):

        return f"{self.coord};{self.nome};{self.sei};{self.contraparte};{self.data_inicio};{self.data_fim};{self.valor};{self.descri}"
