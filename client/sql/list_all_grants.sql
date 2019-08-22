
SELECT * FROM information_schema.role_column_grants WHERE grantee IN ('${USER}','PUBLIC');
SELECT * FROM information_schema.role_routine_grants WHERE grantee IN ('${USER}','PUBLIC');
SELECT * FROM information_schema.role_table_grants WHERE grantee IN ('${USER}','PUBLIC');
SELECT * FROM information_schema.role_udt_grants WHERE grantee IN ('${USER}','PUBLIC');
SELECT * FROM information_schema.role_usage_grants WHERE grantee IN ('${USER}','PUBLIC');
-- SELECT grantee, specific_catalog, specific_schema, privilege_type, count(*) FROM information_schema.routine_privileges GROUP BY grantee, specific_catalog, specific_schema, privilege_type; 
SELECT grantee, table_catalog, table_schema, count(*) 
       FROM information_schema.role_table_grants 
       WHERE grantee IN ('${USER}','PUBLIC')
       GROUP BY grantee, table_catalog, table_schema;


