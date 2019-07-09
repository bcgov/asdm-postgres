SELECT grantee, table_catalog, table_schema, table_name, 
            string_agg(privilege_type, ', ') AS privileges
        FROM information_schema.role_table_grants 
        WHERE grantee IN ('${USER}','PUBLIC')
        GROUP BY grantee, table_catalog, table_schema, table_name;