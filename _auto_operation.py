#!/usr/bin/env Python
# coding=utf-8
from flask import Flask, request, render_template
from sqlalchemy import create_engine
from sqlalchemy import text
import cx_Oracle
import sys
import os

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

app = Flask(__name__)
db = cx_Oracle.connect('user/password@ip/dbname')
#db = create_engine('oracle://user:password@ip/dbname?charset=utf-8',echo=True)
#db = create_engine('oracle://user:password@ip/dbname',echo=True)
#db = create_engine('oracle+cx_oracle://user:password@dbname',echo=True)
#db = create_engine('oracle://user:password@ip/dbname?charset=utf-8',echo=True)



@app.route('/',methods=['GET', 'POST'])
def index():
    reload(sys)
    sys.setdefaultencoding('utf8')
    if request.method == 'GET':
        startDate = request.args.get('startDate')
        endDate = request.args.get('endDate')
        if startDate is None:
            startDate = '20160707'
        if endDate is None:
            endDate = '20170101'
        print "----"
        print startDate
        print endDate
        sql = "select AB_BU BU,count(AB_BU) count FROM mes1.c_pcassystemabnormal " \
                " where ABNORMALID IN (SELECT ABNORMALID FROM mes1.c_pcasabnormaldisposalinfo " \
                " where DISPOSASTATUS IN ('T2E3W1','T0E2W1') " \
                " AND EDITTIME >= to_date('"+startDate+"080000','yyyy-mm-ddhh24miss') " \
                " AND EDITTIME <= to_date('"+endDate+"200000','yyyy-mm-ddhh24miss')) " \
                " group by AB_BU order by count desc"
        cursor = db.cursor()
        result = cursor.execute(sql)
        str_list = result.fetchall()
        return render_template('index.html', str_list=str_list, startDate=startDate, endDate=endDate)


if __name__ == '__main__':
    app.run()
