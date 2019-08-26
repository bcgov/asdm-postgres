import sys, os
import logging
from unittest import TestCase
from client.cli import CLI
from tests.expect import Expect

log = logging.getLogger(__name__)

logging.basicConfig(level=os.environ['LOG_LEVEL'],
                    format='%(asctime)s - %(levelname)s - %(message)s')


creds = {
    "PGHOST" : os.environ['PGHOST'],
    "PGPORT" : os.environ['PGPORT'],
    "PGUSER" : os.environ['PGUSER'],
    "PGPASSWORD" : os.environ['PGPASSWORD'],
    "PGDATABASE" : os.environ['PGDATABASE']
}

class TestSuite(TestCase):

    # def tearDown(self):

    def setUp(self):
        self.clean()
        self.prepare_test_db()
        self.prepare()

    def clean(self):
        admin = CLI(creds, True)

        db = "test_db"

        admin.execute("DROP DATABASE IF EXISTS %s;" % db, False)

        databases = ["orig_db", "orig_db_2"]
        for rdb in databases:
            admin.execute("DROP DATABASE %s;" % rdb, False)
            admin.execute("DROP ROLE %s_admin;" % rdb, False)
            admin.execute("DROP ROLE %s_user;" % rdb, False)
            admin.execute("DROP ROLE %s_enduser;" % rdb, False)
            admin.execute("DROP ROLE %s_contribute;" % rdb, False)
            admin.execute("DROP ROLE %s_readonly;" % rdb, False)

        for n in range(1):
            rdb = "project_%s" % (n + 1)
            admin.execute("DROP DATABASE %s;" % rdb, False)
            admin.execute("DROP ROLE %s_contribute;" % rdb, False)
            admin.execute("DROP ROLE %s_readonly;" % rdb, False)
            admin.execute("DROP ROLE %s_min_public;" % rdb, False)
            for u in range(1):
                user = "%s_user_%s" % (rdb, (u + 1))
                admin.execute("DROP ROLE %s;" % user, False)

        admin.execute("DROP ROLE %s;" % 'user_x', False)
        admin.execute("DROP ROLE %s;" % 'tmp_user', False)
        admin.execute("DROP ROLE %s;" % 'tmp_user_incremental', False)

        admin.execute("DROP DATABASE temp_db;", False)
        admin.execute("DROP ROLE %s;" % 'i_test_user', False)

        for n in range(10):
            admin.execute("DROP ROLE user_%s;" % n, False)
        admin.execute("DROP OWNED BY %s_contribute;" % db, False)
        admin.execute("DROP ROLE %s_contribute;" % db, False)
        admin.execute("DROP OWNED BY %s_readonly;" % db, False)
        admin.execute("DROP ROLE %s_readonly;" % db, False)
        admin.execute("DROP OWNED BY %s_min_public;" % db, False)
        admin.execute("DROP ROLE %s_min_public;" % db, False)

        admin.close()
        return self

    def prepare_test_db(self):
        admin = CLI(creds, True)
        db = "test_db"
        
        try:
            admin.execute("CREATE DATABASE %s;" % db, True)
            admin.execute_template("sql/new_database.sql.tpl", APP_DATABASE=db)

            user = "user_x"

            admin_on_db = CLI({**creds, **{"PGDATABASE":db}}, True)
            admin_on_db.execute_template("sql/setup_new_database.sql.tpl")
            admin_on_db.execute_template("sql/setup_roles.sql.tpl", WORKSPACE=db)

            admin_on_db.execute_template("sql/user.sql.tpl", USER=user, PASSWORD=Expect.TMP_PASSWORD)
            admin_on_db.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=db, USER=user)
            admin_on_db.execute_template("sql/setup_user.sql.tpl", WORKSPACE=db, USER=user)
            admin_on_db.execute_template("sql/setup_user_2.sql.tpl", WORKSPACE=db, USER=user)

            for n in range(10):
                admin_on_db.execute_template("sql/user.sql.tpl", USER="user_%s" % n, PASSWORD=Expect.TMP_PASSWORD)
                admin_on_db.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=db, USER="user_%s" % n)

        finally:
            admin.close()

    def prepare(self):
        admin = CLI(creds, True)

        try:

            for n in range(1):
                rdb = "project_%s" % (n + 1)
                admin.execute("CREATE DATABASE %s;" % rdb, True)
                admin.execute_template("sql/new_database.sql.tpl", APP_DATABASE=rdb)

                admin_on_db = CLI({**creds, **{"PGDATABASE":rdb}}, True)
                admin_on_db.execute_template("sql/setup_new_database.sql.tpl")
                admin_on_db.execute_template("sql/setup_roles.sql.tpl", WORKSPACE=rdb)

                for u in range(1):
                    user = "%s_user_%s" % (rdb, (u + 1))
                    admin_on_db.execute_template("sql/user.sql.tpl", USER=user, PASSWORD=Expect.TMP_PASSWORD)
                    admin_on_db.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=rdb, USER=user)
                    admin_on_db.execute_template("sql/setup_user.sql.tpl", WORKSPACE=rdb, USER=user)
                    admin_on_db.execute_template("sql/setup_user_2.sql.tpl", WORKSPACE=rdb, USER=user)
                admin_on_db.close()
        finally:
            admin.close()
        return self


    def test_simple_user_creating_database(self):
        admin = Expect(creds)

        try:
            user = 'i_test_user'
            admin.execute('show search_path')
            admin.execute_template("sql/original_db_prep.sql", POSTGRES_APP_USERNAME=user, POSTGRES_APP_PASSWORD=Expect.TMP_PASSWORD)

            admin.execute("ALTER USER %s CREATEDB" % user, True)

            enduser_on_db = Expect({**creds, **{"PGUSER": user, "PGPASSWORD": Expect.TMP_PASSWORD}})

            db = "temp_db"
            try:
                enduser_on_db.execute("CREATE DATABASE %s" % db, True)
            finally:
                enduser_on_db.execute("DROP ROLE %s_contribute" % db, False)
                enduser_on_db.execute("DROP ROLE %s_readonly" % db, False)
                enduser_on_db.execute("DROP DATABASE %s" % db, False)
            enduser_on_db.close()
        finally:
            admin.close()

    def test_set_search_path(self):
        admin = Expect(creds)

        try:
            databases = ['orig_db']
            for db in databases:
                admin.execute("CREATE DATABASE %s;" % db, True)
                admin.execute_template("sql/original_db_prep.sql", APP_DATABASE=db, POSTGRES_APP_USERNAME='%s_admin' % db, POSTGRES_APP_PASSWORD=Expect.TMP_PASSWORD)
    
                admin_on_db = Expect({**creds, **{"PGDATABASE":db}})

                admin_on_db.execute_template("sql/original_db_setup.sql", APP_DATABASE=db, WORKSPACE=db, POSTGRES_APP_PASSWORD=Expect.TMP_PASSWORD)
                admin_on_db.execute_template("sql/original_db_user_setup.sql", WORKSPACE=db, USER='%s_enduser' % db, PASSWORD=Expect.TMP_PASSWORD)
                admin_on_db.close()

                admin.execute("ALTER DATABASE %s SET search_path = working_data" % db, True)

                enduser_on_db = Expect({**creds, **{"PGDATABASE":db, "PGUSER": "%s_enduser" % db, "PGPASSWORD": Expect.TMP_PASSWORD}})
                enduser_on_db.match_results('sql/query_search_path.sql', 'results/test_set_search_path/results.txt')
                enduser_on_db.close()

        finally:
            admin.close()

    # def test_original_verify_permissions(self):
    #     admin = Expect(creds)
    #     admin.execute('grant all on database template1 to public', True)

    #     try:
    #         databases = ['orig_db', 'orig_db_2']
    #         for db in databases:
    #             admin.execute("CREATE DATABASE %s;" % db, True)
    #             admin.execute_template("sql/original_db_prep.sql", APP_DATABASE=db, POSTGRES_APP_USERNAME='%s_admin' % db, POSTGRES_APP_PASSWORD=Expect.TMP_PASSWORD)
    
    #             admin_on_db = Expect({**creds, **{"PGDATABASE":db}})
    #             admin_on_db.execute("REVOKE ALL ON SCHEMA public FROM public", True)
    #             #admin_on_db.execute('GRANT ALL ON SCHEMA public to public', True)

    #             admin_on_db.execute_template("sql/original_db_setup.sql", APP_DATABASE=db, WORKSPACE=db, POSTGRES_APP_PASSWORD=Expect.TMP_PASSWORD)
    #             admin_on_db.execute("ALTER ROLE %s_contribute SET search_path = working_data" % db, True)
    #             admin_on_db.execute_template("sql/original_db_user_setup.sql", WORKSPACE=db, USER='%s_enduser' % db, PASSWORD=Expect.TMP_PASSWORD)
    #             #admin_on_db.execute("CREATE USER %s WITH ENCRYPTED PASSWORD '%s'" % ("%s_enduser" % db, Expect.TMP_PASSWORD))
    #             admin_on_db.close()

    #             #admin.execute("ALTER DATABASE %s SET search_path = working_data" % db, True)

    #             enduser_on_db = Expect({**creds, **{"PGDATABASE":db, "PGUSER": "%s_enduser" % db, "PGPASSWORD": Expect.TMP_PASSWORD}})
    #             enduser_on_db.execute('show search_path')
    #             enduser_on_db.execute_template("sql/original_db_tables.sql", TABLE='test_table_1')
    #             enduser_on_db.execute_template("sql/original_db_tables.sql", TABLE='test_table_2')

    #             enduser_on_db.close()

    #         for db in databases:
    #             admin_db = Expect({**creds, **{"PGDATABASE":db}})

    #             for user in databases:
    #                 admin_db.match_results("sql/query_permissions.sql.tpl", "results/test_original_verify_permissions/perms_%s_enduser_in_%s.txt" % (user,db), USER='%s_enduser' % user)

    #             #admin_db.match_results("sql/query_grants.sql", "results/test_original_verify_permissions/grants_%s.txt" % (db))
    #             #admin_db.match_results("sql/query_database.sql", "results/test_original_verify_permissions/access_%s.txt" % (db))

    #             admin_db.close()

    #         db = 'orig_db'
    #         enduser_on_db = Expect({**creds, **{"PGDATABASE":db, "PGUSER": "%s_enduser" % 'orig_db_2', "PGPASSWORD": Expect.TMP_PASSWORD}})
    #         enduser_on_db.expect_execute("select * from test_table_1", 'permission denied for relation test_table_1')
    #         enduser_on_db.close()

    #         enduser_on_db = Expect({**creds, **{"PGDATABASE":db, "PGUSER": "%s_user" % 'orig_db_2', "PGPASSWORD": Expect.TMP_PASSWORD}})
    #         enduser_on_db.expect_execute("select * from test_table_1", 'permission denied for relation test_table_1')
    #         enduser_on_db.close()

    #         # REVOKE ALL ON DATABASE template1 FROM public;
    #         # REVOKE ALL ON DATABASE hostdb FROM public;

    #         admin_db = CLI({**creds, **{"PGDATABASE":db}})
    #         df = admin_db.execute('SELECT datname FROM pg_database WHERE datistemplate = false')
    #         admin_db.close()

    #         admin_on_db = Expect({**creds, **{"PGDATABASE":db}})
    #         admin_on_db.execute_template('sql/query_defaults.sql')
    #         admin_on_db.execute_template('sql/query_roles.sql')
    #         admin_on_db.close()

    #     finally:
    #         admin.close()



    def test_simple(self):
        admin = CLI(creds)
        db = "test_db"

        admin.execute("SELECT current_user", True)


    def test_user_connect_access(self):
        admin = CLI(creds)

        try:
            user = "tmp_user"
            db = "test_db"

            userdb = Expect(creds)

            admin.execute_template("sql/user.sql.tpl", USER=user, PASSWORD=Expect.TMP_PASSWORD)

            userdb.expect_connect(db, user, 'FATAL:  permission denied for database')

            admin.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=db, USER=user)

            userdb.expect_connect(db, user)

            admin_on_test_db = Expect({**creds, **{"PGDATABASE":db}})
            admin_on_test_db.match_results("sql/query_permissions.sql.tpl", "results/test_user_connect_access/perms.txt", USER='user_x')
            admin_on_test_db.close()

            userdb.close()

        finally:
            admin.close()

    def test_single_project(self):
        admin = CLI(creds)

        try:
            db = "test_db"

            prep_db = Expect({**creds, **{"PGDATABASE":db}})
            prep_db.execute_template("sql/test_data_project.sql.tpl")
            prep_db.close()

            user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})

            user.expect_execute("SELECT * from pg_settings", 'permission denied for relation pg_settings')

            user.expect_success("SELECT * from protected_data.table_1")

            user.expect_execute("CREATE TABLE protected_data.table_2 (name varchar(20));", 'permission denied for schema protected_data')

            user.expect_success("CREATE TABLE working_data.table_2 (name varchar(20));")

            admin_on_test_db = Expect({**creds, **{"PGDATABASE":db}})
            admin_on_test_db.match_results("sql/query_permissions.sql.tpl", 'results/test_single_project/perms.txt', USER='user_x')
            admin_on_test_db.close()

            user.close()

        finally:
            admin.close()

    def test_cross_project_connect_to_database(self):
        admin = Expect(creds)

        try:
            admin.expect_connect('test_db', 'project_1_user_1', 'User does not have CONNECT privilege.')
            admin.expect_connect('project_1', 'project_1_user_1')
        finally:
            admin.close()
        return self

    def test_no_existing_table(self):
        con = Expect({**creds, **{"PGUSER":'project_1_user_1', "PGDATABASE":'project_1', "PGPASSWORD":Expect.TMP_PASSWORD}})

        try:
            con.expect_execute("SELECT * from protected_data.table_1", 'relation "protected_data.table_1" does not exist')
        finally:
            con.close()

        return self

    def test_cross_project_attempt_to_grant_usage(self):
        admin = CLI(creds)

        db = "test_db"

        try:
            hacker_user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})
            hacker_user.execute_template("sql/test_data_force_grant_1.sql.tpl", WORKSPACE=db, USER='project_1_user_1')

            con = Expect({**creds, **{"PGUSER":'project_1_user_1', "PGDATABASE":'project_1', "PGPASSWORD":Expect.TMP_PASSWORD}})
            con.expect_execute("SELECT * from test_db.protected_data.table_1", 'cross-database references are not implemented')

            con.close()
            hacker_user.close()
        finally:
            admin.close()
        return self

    def test_cross_project_granting_access_without_connect(self):
        con = Expect(creds)

        try:
            con.expect_connect('test_db', 'project_1_user_1', 'User does not have CONNECT privilege')
        finally:
            con.close()
        return self

    def test_hacker_granting_access_with_connect(self):

        db = "test_db"

        admin_on_test_db = CLI({**creds, **{"PGDATABASE":db}})

        try:
            hacker_user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})
            hacker_user.execute_template("sql/test_data_force_grant_1.sql.tpl", WORKSPACE=db, USER='project_1_user_1')

            # grant user connect
            admin_on_test_db.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=db, USER='project_1_user_1')

            con = Expect({**creds, **{"PGUSER":'project_1_user_1', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})
            con.expect_execute("SELECT * from protected_data.table_1", 'permission denied for schema protected_data')

            admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='project_1_user_1')

            con.close()
            admin_on_test_db.close()

        finally:
            admin_on_test_db.close()
        return self

    def test_hacker_trying_to_grant_role_to_another_user(self):

        db = "test_db"

        hacker_user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})

        try:
            hacker_user.expect_execute("GRANT %s_contribute TO %s;" % (db,'project_1_user_1'), 'must have admin option on role "test_db_contribute"')
        finally:
            hacker_user.close()
        return self

    def test_hacker_trying_to_create_schema(self):

        db = "test_db"

        admin_on_test_db = CLI({**creds, **{"PGDATABASE":db}})

        try:
            # Create tables
            admin_on_test_db.execute("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pg_catalog TO " + "user_x")

            hacker_user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})
            hacker_user.execute_template("sql/test_table.sql.tpl", TABLE='user_x_table')

            admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='user_x')

            hacker_user.expect_execute("CREATE SCHEMA %s;" % 'new_schema', 'permission denied for database test_db')

            hacker_user.close()

        finally:
            admin_on_test_db.close()
        return self

    def test_incremental_user_access(self):

        db = "test_db"

        admin_on_test_db = CLI({**creds, **{"PGDATABASE":db}})

        try:
            prep_db = Expect({**creds, **{"PGDATABASE":db}})
            prep_db.execute_template("sql/test_data_project.sql.tpl")

            user = "tmp_user_incremental"

            admin_on_test_db.execute_template("sql/user.sql.tpl", USER=user, PASSWORD=Expect.TMP_PASSWORD)

            prep_db.expect_connect(db, user, 'User does not have CONNECT privilege.')

            admin_on_test_db.execute_template("sql/user_connect.sql.tpl", APP_DATABASE=db, USER=user)

            user_db = Expect({**creds, **{"PGUSER":user, "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})

            user_db.expect_execute("SELECT * from pg_settings", 'permission denied for relation pg_settings')
            user_db.expect_execute("SELECT * from protected_data.table_1", 'permission denied for schema protected_data')

            admin_on_test_db.execute_template("sql/setup_user.sql.tpl", WORKSPACE=db, USER=user)

            user_db.expect_success("SELECT * from protected_data.table_1")
            user_db.expect_execute("CREATE TABLE protected_data.table_2 (name varchar(20));", 'permission denied for schema protected_data')
            user_db.expect_execute("CREATE TABLE working_data.table_2 (name varchar(20));", 'permission denied for schema pg_catalog')

            admin_on_test_db.execute_template("sql/setup_user_2.sql.tpl", WORKSPACE=db, USER=user)

            user_db.expect_success("CREATE TABLE working_data.table_2 (name varchar(20));")

            prep_db.match_results("sql/query_permissions.sql.tpl", 'results/test_incremental_user_access/perms.txt', USER=user)

            user_db.close()
            prep_db.close()

        finally:
            admin_on_test_db.close()

#    def test_single_project(self):
#         admin = CLI(creds)

#         try:
#             db = "test_db"

#             prep_db = Expect({**creds, **{"PGDATABASE":db}})

#             user = Expect({**creds, **{"PGUSER":'user_x', "PGDATABASE":db, "PGPASSWORD":Expect.TMP_PASSWORD}})

#             user.expect_success("SELECT * from pg_settings")

#             admin_on_test_db = CLI({**creds, **{"PGDATABASE":db}})
#             admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='user_x')
#             admin_on_test_db.execute_template("sql/setup_new_database.sql.tpl")

#             user.expect_execute("SELECT * from pg_settings", 'permission denied for relation pg_settings')

#             admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='user_x')
#             admin_on_test_db.execute_template("sql/setup_schemas.sql.tpl", WORKSPACE=db)

#             prep_db.execute_template("sql/test_data_project.sql.tpl")

#             admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='user_x')

#             user.expect_execute("SELECT * from protected_data.table_1", 'permission denied for schema protected_data')

#             admin_on_test_db.execute_template("sql/setup_user.sql.tpl", WORKSPACE=db, USER='user_x')

#             user.expect_execute("SELECT * from protected_data.table_1")

#             user.expect_execute("CREATE TABLE protected_data.table_2 (name varchar(20));", 'permission denied for schema protected_data')

#             user.expect_execute("CREATE TABLE working_data.table_2 (name varchar(20));", 'permission denied for schema pg_catalog')

#             admin_on_test_db.execute_template("sql/setup_user_2.sql.tpl", WORKSPACE=db, USER='user_x')

#             user.expect_execute("CREATE TABLE working_data.table_2 (name varchar(20));")

#             admin_on_test_db.execute_template("sql/query_permissions.sql.tpl", USER='user_x')

#             user.close()
#             admin_on_test_db.close()

#         finally:
#             admin.close()
