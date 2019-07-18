import psycopg2
import sys, os
import numpy as np
import pandas as pd
from pandas import DataFrame
import pandas.io.sql as psql
import logging
import pystache
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from string import Template

log = logging.getLogger(__name__)


class Expect:
    TMP_PASSWORD = 's3cr3t_p8ssw0rd'
    
    def __init__ (self, creds):
        conn_string = "host="+ creds['PGHOST'] +" port="+ "5432" +" dbname="+ creds['PGDATABASE'] +" user=" + creds['PGUSER'] \
        +" password="+ creds['PGPASSWORD']
        conn=psycopg2.connect(conn_string)
        log.info("Connected to %s as %s" % (creds['PGDATABASE'],creds['PGUSER']))

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.cursor = conn.cursor()
        self.conn = conn
        self.creds = creds

    def close(self):
        self.cursor.close()
        self.conn.close()

    def expect_success (self, sql):
        self.execute (sql, True)
        log.info("EXPECT -> %s" % "PASSED")

    def execute (self, sql, raise_error=False):
        cursor = self.cursor
        try:
            log.info("Executing %s" % sql)
            cursor.execute(sql)
            try:
                result = cursor.fetchall()

                df = DataFrame(result)
                self.output(df)
            except psycopg2.ProgrammingError:
                log.info(" NO RESULTS")

            log.info("... success")
        except psycopg2.DatabaseError as error:
            if (raise_error):
                raise error
            else:
                log.error(error)

    def expect_execute (self, sql, expected=None):
        try:
            if expected is not None:
                log.info("EXPECT -> %s" % expected)
            self.execute (sql, True)
        except psycopg2.DatabaseError as error:
            not_expected = expected is None or ("%s" % error).find(expected) == -1
            if (not_expected):
                raise error
            log.info("EXPECT -> %s" % "PASSED")
            return

        if expected is not None:
            raise Exception('Expected %s but executed successfully.' % expected)

        log.info("EXPECT -> %s" % "PASSED")
        
    def execute_template (self, template, **args):
        cursor = self.cursor
        log.info("Executing template %s" % template)
        basepath = os.path.dirname(__file__)
        f = open("%s/%s" % (basepath, template), "r")
        c = f.read()
        f.close()

        s = Template(c)
        sql_command = s.substitute(args)

        el = sql_command.splitlines()
        for e in el:
            if (e != ""):
                log.info(" -> %s" % e)

        cursor.execute(sql_command)
        try:
            result = cursor.fetchall()

            df = DataFrame(result)
            self.output(df)
            log.info("... success")
            return df
        except psycopg2.ProgrammingError:
            log.info(" NO RESULTS")
            return None

    def match_results (self, template, result_file, **args):
        df = self.execute_template(template, **args)

        log.info("EXPECT -> MATCH TO %s" % result_file)

        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000, 'display.max_colwidth', 10000):
            basepath = os.path.dirname(__file__)

            if os.path.isfile("%s/%s" % (basepath, result_file)) == False:
                f = open("%s/%s.orig" % (basepath, result_file), "w")
                f.write("%s" % df)
                f.close()
                raise Exception('Expected does not match actual for %s' % result_file)

            f = open("%s/%s" % (basepath, result_file), "r")
            match = f.read()
            f.close()

            if ("%s" % df != match):
                f = open("%s/%s.orig" % (basepath, result_file), "w")
                f.write("%s" % df)
                f.close()
                raise Exception('Expected does not match actual for %s' % result_file)

            log.info("EXPECT -> %s" % "MATCHED")

    def expect_connect(self, db, user, expected=None):
        log.info("EXPECT -> %s for connect to %s as %s" % (expected, db, user))
        try:
            conn_string = "host="+ self.creds['PGHOST'] +" port="+ "5432" +" dbname="+ db +" user=" + user \
            +" password="+ Expect.TMP_PASSWORD
            
            conn=psycopg2.connect(conn_string)

            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except psycopg2.DatabaseError as error:
            not_expected = expected is None or ("%s" % error).find(expected) == -1
            if (not_expected):
                raise error
            log.info("EXPECT -> PASS")
            return
        if expected is not None:
            raise Exception('Expected %s but executed successfully.' % expected)
        
        log.info("EXPECT -> PASS")
        return conn

    def output(self, df):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000, 'display.max_colwidth', 10000):
            el = ("%s" % df).splitlines()
            for e in el:
                if (e != ""):
                    log.info(" : %s" % e)