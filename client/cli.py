
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
from client.log import log

class CLI:
    def info(self, msg, *args, **kwargs):
        if self.quiet == False:
            log.info(msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        if self.quiet == False:
            log.error(msg, *args, **kwargs)

    def __init__ (self, creds, quiet=False):
        self.quiet = quiet
#        conn_string = "host="+ creds['PGHOST'] +" port="+ creds['PGPORT'] +" dbname="+ creds['PGDATABASE'] +" user=" + creds['PGUSER']  \
#        +" password="+ creds['PGPASSWORD']
#        conn_string = "user=" + creds['PGUSER']
        conn_string = ""
        if "PGDATABASE" in creds:
            conn_string = "%s dbname=%s" % (conn_string, creds["PGDATABASE"])
        conn=psycopg2.connect(conn_string)
        self.info("Connected")

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
                self.log_error(error)

    def execute_template (self, template, **args):
        cursor = self.cursor
        self.info("Executing template %s" % template)
        basepath = os.path.dirname(__file__)
        f = open("%s/%s" % (basepath, template), "r")
        c = f.read()
        f.close()

        s = Template(c)
        sql_command = s.substitute(args)

        lines = []
        current = ""
        el = sql_command.splitlines()
        for e in el:
            if (e != ""):
                # self.info(" -> %s" % e)
                current = "%s%s\n" % (current, e)
                if ';' in current:
                   # self.info(" -> LINE BREAK")
                   lines.append(current)
                   current = ""

        for line in lines:
          if line.startswith('--'):
              continue
          self.info(" -> EXECUTE")
          self.output_pretty(line)
          cursor.execute(line)
          try:
            result = cursor.fetchall()

            df = DataFrame(result)
            self.output(df)
          except psycopg2.ProgrammingError:
            self.info(" NO RESULTS")
          self.info("... success")

    def output(self, df):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 10000, 'display.max_colwidth', 10000):
            el = ("%s" % df).splitlines()
            for e in el:
                if (e != ""):
                    self.info(" : %s" % e)

    def output_pretty (self, text):
        el = str(text).splitlines()
        for e in el:
          if (e != ""):
            self.info(" ->   %s" % e)

    def get_databases (self):
        sql = "SELECT datname FROM pg_database WHERE datistemplate = false"
        return self.get_list(sql)

    def get_users (self):
        sql = "SELECT usename FROM pg_user"
        return self.get_list(sql)

    def get_list (self, sql):
        cursor = self.cursor
        cursor.execute(sql)
        result = cursor.fetchall()

        data = []
        df = DataFrame(result)
        for index, row in df.iterrows():
            data.append(row[0])

        return data