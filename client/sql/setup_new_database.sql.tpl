REVOKE ALL ON SCHEMA public FROM public; -- CREATE and USAGE
REVOKE ALL ON SCHEMA pg_catalog FROM public; -- CREATE and USAGE
REVOKE ALL ON SCHEMA information_schema FROM public; -- CREATE and USAGE
REVOKE ALL ON ALL TABLES IN SCHEMA pg_catalog FROM public;
REVOKE ALL ON ALL TABLES IN SCHEMA information_schema FROM public;
