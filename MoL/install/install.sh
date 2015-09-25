#!/bin/sh


echo -e "============\n1. Install PostgreSQL, Python3, python3-pip"

echo -e "============\n2. Initialize PostgreSQL"
postgres -D /usr/local/var/postgres
createdb mol

cat << ESQL | psql
create user mol with password 'molpassword';
grant all privileges on database mol to mol;
CREATE TABLE users
(
  uid uuid NOT NULL,
  username text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  password text COLLATE pg_catalog."en_US.UTF-8" NOT NULL,
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

INSERT INTO users(uid, username, password, role) VALUES ('ddcb16a4-c813-4a8d-9724-d0df4e905f0c', 'bigbrother', 'qwerty', true);

CREATE TABLE profiles
(
  profileid uuid NOT NULL,
  name text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  lastname text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  city text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  birthdate date NOT NULL,
  mobile text COLLATE pg_catalog."ru_RU.UTF-8",
  marital boolean DEFAULT false,
  crimes bigint[],
  userpic integer,
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
  name text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  article text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  city text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  country text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  crimedate date NOT NULL,
  description text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  participants uuid[],
  judgement text COLLATE pg_catalog."ru_RU.UTF-8" NOT NULL,
  closed boolean DEFAULT false,
  public boolean DEFAULT true,
  CONSTRAINT crimeid PRIMARY KEY (crimeid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE crimes
  OWNER TO mol;

ESQL

cat users.sql | psql mol


echo -e "============\n3. Install requirements"
pip install tornado momoko


