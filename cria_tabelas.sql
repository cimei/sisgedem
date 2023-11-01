
    -- Table: sistema

    -- DROP TABLE IF EXISTS sistema;

    CREATE TABLE IF NOT EXISTS sistema
    (
        id INTEGER NOT NULL ,
        nome_sistema VARCHAR  NOT NULL,
        descritivo TEXT  NOT NULL,
        versao VARCHAR ,
        CONSTRAINT sistema_pkey PRIMARY KEY (id)
    )


    -- Table: users

    -- DROP TABLE IF EXISTS users;

    CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER NOT NULL,
        profile_image VARCHAR  DEFAULT 'default_profile.png',
        email VARCHAR ,
        username VARCHAR ,
        password_hash VARCHAR ,
        despacha INTEGER DEFAULT 0,
        email_confirmation_sent_on DATETIME,
        email_confirmed INTEGER,
        email_confirmed_on DATETIME,
        registered_on DATETIME,
        last_logged_in DATETIME,
        current_logged_in DATETIME,
        role VARCHAR  DEFAULT 'USER',
        coord VARCHAR ,
        despacha2 INTEGER DEFAULT 0,
        ativo INTEGER DEFAULT 1,
        cargo_func VARCHAR ,
        despacha0 INTEGER DEFAULT 0,
        CONSTRAINT users_pkey PRIMARY KEY (id),
        CONSTRAINT users_email_key UNIQUE (email),
        CONSTRAINT users_username_key UNIQUE (username)
    )





    -- Table: coords

    -- DROP TABLE IF EXISTS coords;

    CREATE TABLE IF NOT EXISTS coords
    (
        id INTEGER NOT NULL ,
        sigla VARCHAR ,
        desc VARCHAR ,
        id_pai INTEGER,
        id_chefe INTEGER,
        id_chefe_subs INTEGER,
        CONSTRAINT coords_pkey PRIMARY KEY (id)
    )



    -- Table: plano_trabalho

    -- DROP TABLE IF EXISTS plano_trabalho;

    CREATE TABLE IF NOT EXISTS plano_trabalho
    (
        id INTEGER NOT NULL ,
        atividade_sigla VARCHAR ,
        atividade_desc VARCHAR ,
        natureza VARCHAR ,
        meta REAL,
        situa VARCHAR  DEFAULT 'Ativa',
        unidade VARCHAR ,
        CONSTRAINT plano_trabalho_pkey PRIMARY KEY (id)
    )


    -- Table: tipos_demanda

    -- DROP TABLE IF EXISTS tipos_demanda;

    CREATE TABLE IF NOT EXISTS tipos_demanda
    (
        id INTEGER NOT NULL ,
        tipo VARCHAR  NOT NULL,
        relevancia INTEGER,
        unidade VARCHAR ,
        CONSTRAINT tipos_demanda_pkey PRIMARY KEY (id)
    )


    -- Table: passos_tipos

    -- DROP TABLE IF EXISTS passos_tipos;

    CREATE TABLE IF NOT EXISTS passos_tipos
    (
        id INTEGER NOT NULL ,
        tipo_id INTEGER NOT NULL,
        ordem INTEGER NOT NULL,
        passo VARCHAR  NOT NULL,
        desc VARCHAR  NOT NULL,
        CONSTRAINT passos_tipos_pkey PRIMARY KEY (id),
        CONSTRAINT passos_tipos_tipo_id_fkey FOREIGN KEY (tipo_id)
            REFERENCES tipos_demanda (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE
    )


    -- Table: Objeto

    -- DROP TABLE IF EXISTS Objeto;

    CREATE TABLE IF NOT EXISTS Objeto
    (
        id INTEGER NOT NULL,
        coord VARCHAR ,
        nome VARCHAR ,
        sei VARCHAR  NOT NULL,
        contraparte VARCHAR ,
        data_inicio DATETIME,
        data_fim DATETIME,
        valor REAL,
        descri TEXT ,
        CONSTRAINT objeto_pkey PRIMARY KEY (id),
        CONSTRAINT objeto_sei_key UNIQUE (sei)
    )

    -- Table: demandas

    -- DROP TABLE IF EXISTS demandas;

    CREATE TABLE IF NOT EXISTS demandas
    (
        id INTEGER NOT NULL ,
        atividade_id INTEGER,
        sei VARCHAR ,
        tipo VARCHAR ,
        data DATETIME,
        user_id INTEGER NOT NULL,
        titulo VARCHAR ,
        desc TEXT ,
        necessita_despacho INTEGER,
        conclu VARCHAR ,
        data_conclu DATETIME,
        necessita_despacho_cg INTEGER DEFAULT 0,
        urgencia INTEGER DEFAULT 3,
        data_env_despacho date,
        nota INTEGER DEFAULT -1,
        data_verific DATETIME,
        CONSTRAINT demandas_pkey PRIMARY KEY (id),
        CONSTRAINT demandas_user_id_fkey FOREIGN KEY (user_id)
            REFERENCES users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )


    -- Table: providencias

    -- DROP TABLE IF EXISTS providencias;

    CREATE TABLE IF NOT EXISTS providencias
    (
        id INTEGER NOT NULL ,
        demanda_id INTEGER NOT NULL,
        data DATETIME NOT NULL,
        TEXTo TEXT  NOT NULL,
        user_id INTEGER NOT NULL,
        duracao INTEGER,
        programada INTEGER,
        passo VARCHAR ,
        CONSTRAINT providencias_pkey PRIMARY KEY (id),
        CONSTRAINT providencias_demanda_id_fkey FOREIGN KEY (demanda_id)
            REFERENCES demandas (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE
    )

    -- Table: despachos

    -- DROP TABLE IF EXISTS despachos;

    CREATE TABLE IF NOT EXISTS despachos
    (
        id INTEGER NOT NULL ,
        data DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        demanda_id INTEGER NOT NULL,
        TEXTo TEXT  NOT NULL,
        passo VARCHAR ,
        CONSTRAINT despachos_pkey PRIMARY KEY (id),
        CONSTRAINT despachos_demanda_id_fkey FOREIGN KEY (demanda_id)
            REFERENCES demandas (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE,
        CONSTRAINT despachos_user_id_fkey FOREIGN KEY (user_id)
            REFERENCES users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    -- Table: log_auto

    -- DROP TABLE IF EXISTS log_auto;

    CREATE TABLE IF NOT EXISTS log_auto
    (
        id INTEGER NOT NULL,
        data_hora DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        demanda_id INTEGER,
        registro TEXT  NOT NULL,
        atividade INTEGER,
        duracao INTEGER DEFAULT 0,
        CONSTRAINT log_auto_pkey PRIMARY KEY (id),
        CONSTRAINT log_auto_user_id_fkey FOREIGN KEY (user_id)
            REFERENCES users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE
    )


    -- Table: msgs_recebidas

    -- DROP TABLE IF EXISTS msgs_recebidas;

    CREATE TABLE IF NOT EXISTS msgs_recebidas
    (
        id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        data_hora DATETIME NOT NULL,
        demanda_id INTEGER NOT NULL,
        msg TEXT  NOT NULL,
        CONSTRAINT msgs_recebidas_pkey PRIMARY KEY (id)
    )

    -- Table: ativ_usu

    -- DROP TABLE IF EXISTS ativ_usu;

    CREATE TABLE IF NOT EXISTS ativ_usu
    (
        id INTEGER NOT NULL,
        atividade_id INTEGER,
        user_id INTEGER,
        nivel VARCHAR  NOT NULL,
        CONSTRAINT ativ_usu_pkey PRIMARY KEY (id),
        CONSTRAINT ativ_usu_atividade_id_fkey FOREIGN KEY (atividade_id)
            REFERENCES plano_trabalho (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE,
        CONSTRAINT ativ_usu_user_id_fkey FOREIGN KEY (user_id)
            REFERENCES users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

