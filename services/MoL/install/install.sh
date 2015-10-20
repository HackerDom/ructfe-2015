#!/bin/bash -e

echo -e "============\n1. Install dependencies"
aptitude update 
aptitude install -y postgresql python3 python3-pip libpq-dev
pip3 install momoko

echo -e "============\n2. Add user"
useradd -m mol

echo -e "============\n3. Initialize PostgreSQL"
#postgres -D /usr/local/var/postgres
sudo="su - postgres -c "

$sudo "createdb mol"

$sudo "cat << ESQL | psql mol
create user mol with password 'molpassword';
grant all privileges on database mol to mol;
CREATE TABLE users
(
  uid uuid NOT NULL,
  username text  NOT NULL,
  password text  NOT NULL,
  role boolean NOT NULL DEFAULT false,
  profile uuid,
  CONSTRAINT uid PRIMARY KEY (uid),
  CONSTRAINT users_username_key UNIQUE (username)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users
  OWNER TO mol;

INSERT INTO users(uid, username, password, role) VALUES ('ddcb16a4-c813-4a8d-9724-d0df4e905f0c', 'bigbrother', 'd8578edf8458ce06fbc5bb76a58c5ca4', true);

CREATE TABLE profiles
(
  profileid uuid NOT NULL,
  name text  NOT NULL,
  lastname text  NOT NULL,
  city text  NOT NULL,
  birthdate date NOT NULL,
  mobile text ,
  marital boolean DEFAULT false,
  userpic integer,
  crimes bigint[],
  CONSTRAINT profileid PRIMARY KEY (profileid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE profiles
  OWNER TO mol;


CREATE TABLE crimes
(
  crimeid bigint NOT NULL,
  name text  NOT NULL,
  article text  NOT NULL,
  city text  NOT NULL,
  country text  NOT NULL,
  crimedate date NOT NULL,
  description text  NOT NULL,
  participants uuid[],
  judgement text ,
  closed boolean DEFAULT false,
  public boolean DEFAULT true,
  author uuid,
  CONSTRAINT crimeid PRIMARY KEY (crimeid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE crimes
  OWNER TO mol;

ESQL"

cat users.sql | $sudo "psql mol"

echo -e "============\n4. Register in systemd"
cat << SYSTEMD > /etc/systemd/system/multi-user.target.wants/mol.service
[Unit]
    Description=Ministry of Love
    After=network.target postgresql.service

[Service]
    ExecStart=/usr/bin/env python3 main.py
    WorkingDirectory=/home/mol/service
    User=mol
    Group=mol
    Restart=always
    PIDFile=/var/run/mol.pid
    RestartSec=500ms

[Install]
    WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
