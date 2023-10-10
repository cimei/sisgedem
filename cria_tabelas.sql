-- Database: dbsisgedem

-- DROP DATABASE IF EXISTS dbsisgedem;

CREATE DATABASE dbsisgedem
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-----------------------------------------------------------------------------------------

-- SCHEMA: dem

-- DROP SCHEMA IF EXISTS dem ;

CREATE SCHEMA IF NOT EXISTS dem
    AUTHORIZATION postgres;

-------------------------------------------------------------------------------------

-- Sequências


-- SEQUENCE: dem.ativ_usu_id_seq

-- DROP SEQUENCE IF EXISTS dem.ativ_usu_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.ativ_usu_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.ativ_usu_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.coords_id_seq

-- DROP SEQUENCE IF EXISTS dem.coords_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.coords_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.coords_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.demandas_id_seq

-- DROP SEQUENCE IF EXISTS dem.demandas_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.demandas_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.demandas_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.despachos_id_seq

-- DROP SEQUENCE IF EXISTS dem.despachos_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.despachos_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.despachos_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.objeto_id_seq

-- DROP SEQUENCE IF EXISTS dem.objeto_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.objeto_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.objeto_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.log_auto_id_seq

-- DROP SEQUENCE IF EXISTS dem.log_auto_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.log_auto_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.log_auto_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.msgs_recebidas_id_seq

-- DROP SEQUENCE IF EXISTS dem.msgs_recebidas_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.msgs_recebidas_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.msgs_recebidas_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.passos_tipos_id_seq

-- DROP SEQUENCE IF EXISTS dem.passos_tipos_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.passos_tipos_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.passos_tipos_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.plano_trabalho_id_seq

-- DROP SEQUENCE IF EXISTS dem.plano_trabalho_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.plano_trabalho_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.plano_trabalho_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.providencias_id_seq

-- DROP SEQUENCE IF EXISTS dem.providencias_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.providencias_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.providencias_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.sistema_id_seq

-- DROP SEQUENCE IF EXISTS dem.sistema_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.sistema_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.sistema_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.tipos_demanda_id_seq

-- DROP SEQUENCE IF EXISTS dem.tipos_demanda_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.tipos_demanda_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.tipos_demanda_id_seq
    OWNER TO postgres;

-- SEQUENCE: dem.users_id_seq

-- DROP SEQUENCE IF EXISTS dem.users_id_seq;

CREATE SEQUENCE IF NOT EXISTS dem.users_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE dem.users_id_seq
    OWNER TO postgres;


------------------------------------------------------------------------------------------


-- Table: dem.sistema

-- DROP TABLE IF EXISTS dem.sistema;

CREATE TABLE IF NOT EXISTS dem.sistema
(
    id integer NOT NULL DEFAULT nextval('dem.sistema_id_seq'::regclass),
    nome_sistema character varying COLLATE pg_catalog."default" NOT NULL,
    descritivo text COLLATE pg_catalog."default" NOT NULL,
    versao character varying COLLATE pg_catalog."default",
    CONSTRAINT sistema_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.sistema
    OWNER to postgres;

-- Table: dem.users

-- DROP TABLE IF EXISTS dem.users;

CREATE TABLE IF NOT EXISTS dem.users
(
    id integer NOT NULL DEFAULT nextval('dem.users_id_seq'::regclass),
    profile_image character varying COLLATE pg_catalog."default" DEFAULT 'default_profile.png'::character varying,
    email character varying COLLATE pg_catalog."default",
    username character varying COLLATE pg_catalog."default",
    password_hash character varying COLLATE pg_catalog."default",
    despacha integer DEFAULT 0,
    email_confirmation_sent_on timestamp without time zone,
    email_confirmed integer,
    email_confirmed_on timestamp without time zone,
    registered_on timestamp without time zone,
    last_logged_in timestamp without time zone,
    current_logged_in timestamp without time zone,
    role character varying COLLATE pg_catalog."default" DEFAULT USER,
    coord character varying COLLATE pg_catalog."default",
    despacha2 integer DEFAULT 0,
    ativo integer DEFAULT 1,
    cargo_func character varying COLLATE pg_catalog."default",
    despacha0 integer DEFAULT 0,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_username_key UNIQUE (username)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.users
    OWNER to postgres;


-- Table: dem.coords

-- DROP TABLE IF EXISTS dem.coords;

CREATE TABLE IF NOT EXISTS dem.coords
(
    id integer NOT NULL DEFAULT nextval('dem.coords_id_seq'::regclass),
    sigla character varying COLLATE pg_catalog."default",
    "desc" character varying COLLATE pg_catalog."default",
    id_pai integer,
    id_chefe integer,
    id_chefe_subs integer,
    CONSTRAINT coords_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.coords
    OWNER to postgres;

-- Table: dem.plano_trabalho

-- DROP TABLE IF EXISTS dem.plano_trabalho;

CREATE TABLE IF NOT EXISTS dem.plano_trabalho
(
    id integer NOT NULL DEFAULT nextval('dem.plano_trabalho_id_seq'::regclass),
    atividade_sigla character varying COLLATE pg_catalog."default",
    atividade_desc character varying COLLATE pg_catalog."default",
    natureza character varying COLLATE pg_catalog."default",
    meta real,
    situa character varying COLLATE pg_catalog."default" DEFAULT 'Ativa'::character varying,
    unidade character varying COLLATE pg_catalog."default",
    CONSTRAINT plano_trabalho_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.plano_trabalho
    OWNER to postgres;

-- Table: dem.tipos_demanda

-- DROP TABLE IF EXISTS dem.tipos_demanda;

CREATE TABLE IF NOT EXISTS dem.tipos_demanda
(
    id integer NOT NULL DEFAULT nextval('dem.tipos_demanda_id_seq'::regclass),
    tipo character varying COLLATE pg_catalog."default" NOT NULL,
    relevancia integer,
    unidade character varying COLLATE pg_catalog."default",
    CONSTRAINT tipos_demanda_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.tipos_demanda
    OWNER to postgres;

-- Table: dem.passos_tipos

-- DROP TABLE IF EXISTS dem.passos_tipos;

CREATE TABLE IF NOT EXISTS dem.passos_tipos
(
    id integer NOT NULL DEFAULT nextval('dem.passos_tipos_id_seq'::regclass),
    tipo_id integer NOT NULL,
    ordem integer NOT NULL,
    passo character varying COLLATE pg_catalog."default" NOT NULL,
    "desc" character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT passos_tipos_pkey PRIMARY KEY (id),
    CONSTRAINT passos_tipos_tipo_id_fkey FOREIGN KEY (tipo_id)
        REFERENCES dem.tipos_demanda (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.passos_tipos
    OWNER to postgres;



-- Table: dem.Objeto

-- DROP TABLE IF EXISTS dem.Objeto;

CREATE TABLE IF NOT EXISTS dem.Objeto
(
    id integer NOT NULL DEFAULT nextval('dem.objeto_id_seq'::regclass),
    coord character varying COLLATE pg_catalog."default",
    nome character varying COLLATE pg_catalog."default",
    sei character varying COLLATE pg_catalog."default" NOT NULL,
    contraparte character varying COLLATE pg_catalog."default",
    data_inicio timestamp without time zone,
    data_fim timestamp without time zone,
    valor real,
    descri text COLLATE pg_catalog."default",
    CONSTRAINT objeto_pkey PRIMARY KEY (id),
    CONSTRAINT objeto_sei_key UNIQUE (sei)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.Objeto
    OWNER to postgres;


-- Table: dem.demandas

-- DROP TABLE IF EXISTS dem.demandas;

CREATE TABLE IF NOT EXISTS dem.demandas
(
    id integer NOT NULL DEFAULT nextval('dem.demandas_id_seq'::regclass),
    atividade_id integer,
    sei character varying COLLATE pg_catalog."default",
    tipo character varying COLLATE pg_catalog."default",
    data timestamp without time zone,
    user_id integer NOT NULL,
    titulo character varying COLLATE pg_catalog."default",
    "desc" text COLLATE pg_catalog."default",
    necessita_despacho integer,
    conclu character varying COLLATE pg_catalog."default",
    data_conclu timestamp without time zone,
    necessita_despacho_cg integer DEFAULT 0,
    urgencia integer DEFAULT 3,
    data_env_despacho date,
    nota integer DEFAULT '-1'::integer,
    data_verific timestamp without time zone,
    CONSTRAINT demandas_pkey PRIMARY KEY (id),
    CONSTRAINT demandas_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES dem.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.demandas
    OWNER to postgres;


-- Table: dem.providencias

-- DROP TABLE IF EXISTS dem.providencias;

CREATE TABLE IF NOT EXISTS dem.providencias
(
    id integer NOT NULL DEFAULT nextval('dem.providencias_id_seq'::regclass),
    demanda_id integer NOT NULL,
    data timestamp without time zone NOT NULL,
    texto text COLLATE pg_catalog."default" NOT NULL,
    user_id integer NOT NULL,
    duracao integer,
    programada integer,
    passo character varying COLLATE pg_catalog."default",
    CONSTRAINT providencias_pkey PRIMARY KEY (id),
    CONSTRAINT providencias_demanda_id_fkey FOREIGN KEY (demanda_id)
        REFERENCES dem.demandas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.providencias
    OWNER to postgres;


-- Table: dem.despachos

-- DROP TABLE IF EXISTS dem.despachos;

CREATE TABLE IF NOT EXISTS dem.despachos
(
    id integer NOT NULL DEFAULT nextval('dem.despachos_id_seq'::regclass),
    data timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    demanda_id integer NOT NULL,
    texto text COLLATE pg_catalog."default" NOT NULL,
    passo character varying COLLATE pg_catalog."default",
    CONSTRAINT despachos_pkey PRIMARY KEY (id),
    CONSTRAINT despachos_demanda_id_fkey FOREIGN KEY (demanda_id)
        REFERENCES dem.demandas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT despachos_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES dem.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.despachos
    OWNER to postgres;


-- Table: dem.log_auto

-- DROP TABLE IF EXISTS dem.log_auto;

CREATE TABLE IF NOT EXISTS dem.log_auto
(
    id integer NOT NULL DEFAULT nextval('dem.log_auto_id_seq'::regclass),
    data_hora timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    demanda_id integer,
    registro text COLLATE pg_catalog."default" NOT NULL,
    atividade integer,
    duracao integer DEFAULT 0,
    CONSTRAINT log_auto_pkey PRIMARY KEY (id),
    CONSTRAINT log_auto_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES dem.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.log_auto
    OWNER to postgres;


-- Table: dem.msgs_recebidas

-- DROP TABLE IF EXISTS dem.msgs_recebidas;

CREATE TABLE IF NOT EXISTS dem.msgs_recebidas
(
    id integer NOT NULL DEFAULT nextval('dem.msgs_recebidas_id_seq'::regclass),
    user_id integer NOT NULL,
    data_hora timestamp without time zone NOT NULL,
    demanda_id integer NOT NULL,
    msg text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT msgs_recebidas_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.msgs_recebidas
    OWNER to postgres;



-- Table: dem.ativ_usu

-- DROP TABLE IF EXISTS dem.ativ_usu;

CREATE TABLE IF NOT EXISTS dem.ativ_usu
(
    id integer NOT NULL DEFAULT nextval('dem.ativ_usu_id_seq'::regclass),
    atividade_id integer,
    user_id integer,
    nivel character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT ativ_usu_pkey PRIMARY KEY (id),
    CONSTRAINT ativ_usu_atividade_id_fkey FOREIGN KEY (atividade_id)
        REFERENCES dem.plano_trabalho (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT ativ_usu_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES dem.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS dem.ativ_usu
    OWNER to postgres;

