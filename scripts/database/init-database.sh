#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE DATABASE platform_api_db_test;
	GRANT ALL PRIVILEGES ON DATABASE platform_api_db_test TO sigtunnel;
EOSQL