CREATE SCHEMA protected_data;
CREATE SCHEMA working_data;

CREATE ROLE ${WORKSPACE}_contribute;
GRANT USAGE ON SCHEMA protected_data TO ${WORKSPACE}_contribute;
GRANT SELECT ON ALL TABLES IN SCHEMA protected_data TO ${WORKSPACE}_contribute;
GRANT ALL ON ALL TABLES IN SCHEMA working_data TO ${WORKSPACE}_contribute;
GRANT CREATE, USAGE ON SCHEMA working_data TO ${WORKSPACE}_contribute;
ALTER DEFAULT PRIVILEGES IN SCHEMA protected_data GRANT SELECT ON TABLES TO ${WORKSPACE}_contribute;
ALTER DEFAULT PRIVILEGES IN SCHEMA working_data GRANT ALL ON TABLES TO ${WORKSPACE}_contribute;

CREATE ROLE ${WORKSPACE}_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA protected_data TO ${WORKSPACE}_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA working_data TO ${WORKSPACE}_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA protected_data GRANT SELECT ON TABLES TO ${WORKSPACE}_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA working_data GRANT SELECT ON TABLES TO ${WORKSPACE}_readonly;

-- CREATE USER ${WORKSPACE}_user WITH ENCRYPTED PASSWORD '${POSTGRES_APP_PASSWORD}';
-- GRANT ${WORKSPACE}_contribute TO ${WORKSPACE}_user;

-- ALTER ROLE ${WORKSPACE}_contribute IN DATABASE ${APP_DATABASE} SET search_path TO working_data, public;
