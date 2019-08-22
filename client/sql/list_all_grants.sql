
SELECT grantee, table_catalog, table_schema, count(*)
  FROM information_schema.role_column_grants
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, table_catalog, table_schema;

SELECT grantee, specific_catalog, specific_schema, privilege_type, count(*)
  FROM information_schema.role_routine_grants
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, specific_catalog, specific_schema, privilege_type;

SELECT grantee, table_catalog, table_schema, table_name,
      string_agg(privilege_type, ', ') AS privileges
  FROM information_schema.role_table_grants
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, table_catalog, table_schema, table_name;

SELECT grantee, udt_catalog, udt_schema, udt_name, count(*)
  FROM information_schema.role_udt_grants
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, udt_catalog, udt_schema, udt_name;

SELECT grantee, object_catalog, object_schema, object_type, privilege_type, count(*)
  FROM information_schema.role_usage_grants
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, object_catalog, object_schema, object_type, privilege_type;

SELECT grantee, specific_catalog, specific_schema, privilege_type, count(*) 
  FROM information_schema.routine_privileges 
  WHERE grantee IN ('${USER}','PUBLIC')
  GROUP BY grantee, specific_catalog, specific_schema, privilege_type; 

SELECT grantee, table_catalog, table_schema, count(*) 
       FROM information_schema.role_table_grants 
       WHERE grantee IN ('${USER}','PUBLIC')
       GROUP BY grantee, table_catalog, table_schema;


