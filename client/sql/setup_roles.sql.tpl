CREATE SCHEMA protected_data;
CREATE SCHEMA working_data;

-- Contributor Role;

CREATE ROLE ${WORKSPACE}_contribute NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOLOGIN;
GRANT USAGE ON SCHEMA protected_data TO ${WORKSPACE}_contribute;
GRANT SELECT ON ALL TABLES IN SCHEMA protected_data TO ${WORKSPACE}_contribute;
GRANT ALL ON ALL TABLES IN SCHEMA working_data TO ${WORKSPACE}_contribute;
GRANT CREATE, USAGE ON SCHEMA working_data TO ${WORKSPACE}_contribute;
ALTER DEFAULT PRIVILEGES IN SCHEMA protected_data GRANT SELECT ON TABLES TO ${WORKSPACE}_contribute;
ALTER DEFAULT PRIVILEGES IN SCHEMA working_data GRANT ALL ON TABLES TO ${WORKSPACE}_contribute;

-- Read Only Role;
CREATE ROLE ${WORKSPACE}_readonly NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA protected_data TO ${WORKSPACE}_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA working_data TO ${WORKSPACE}_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA protected_data GRANT SELECT ON TABLES TO ${WORKSPACE}_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA working_data GRANT SELECT ON TABLES TO ${WORKSPACE}_readonly;

-- Minimal pg_catalog permissions;
CREATE ROLE ${WORKSPACE}_min_public NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOLOGIN;
GRANT USAGE ON SCHEMA pg_catalog TO ${WORKSPACE}_min_public; -- CREATE | USAGE
REVOKE ALL ON ALL TABLES IN SCHEMA pg_catalog FROM ${WORKSPACE}_min_public;

ALTER ROLE ${WORKSPACE}_contribute SET search_path TO working_data;
