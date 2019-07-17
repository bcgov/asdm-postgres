
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

logging.basicConfig(level='INFO',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CLI:
    def info(self, msg, *args, **kwargs):
        if self.quiet == False:
            log.info(msg, *args, **kwargs)

    def __init__ (self, creds, quiet=False):
        self.quiet = quiet
        conn_string = "host="+ creds['PGHOST'] +" port="+ "5432" +" dbname="+ creds['PGDATABASE'] +" user=" + creds['PGUSER'] \
        +" password="+ creds['PGPASSWORD']
        conn=psycopg2.connect(conn_string)
        self.info("Connected to %s as %s" % (creds['PGDATABASE'],creds['PGUSER']))

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.cursor = conn.cursor()
        self.conn = conn

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute (self, sql, raise_error=False):
        cursor = self.cursor
        try:
            self.info("Executing %s" % sql)
            cursor.execute(sql)
            try:
                result = cursor.fetchall()

                df = DataFrame(result)
                self.output(df)
                return df
            except psycopg2.ProgrammingError:
                self.info(" NO RESULTS")

            self.info("... success")
        except psycopg2.DatabaseError as error:
            if (raise_error):
                raise error
            else:
                log.error(error)

    def execute_template (self, template, **args):
        cursor = self.cursor
        self.info("Executing template %s" % template)
        basepath = os.path.dirname(__file__)
        f = open("%s/%s" % (basepath, template), "r")
        c = f.read()
        f.close()

        s = Template(c)
        sql_command = s.substitute(args)

        el = sql_command.splitlines()
        for e in el:
            if (e != ""):
                self.info(" -> %s" % e)

        cursor.execute(sql_command)
        try:
            result = cursor.fetchall()

            df = DataFrame(result)
            self.output(df)
        except psycopg2.ProgrammingError:
            self.info(" NO RESULTS")
        self.info("... success")

    def output(self, df):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000, 'display.max_colwidth', 10000):
            self.info(df)

