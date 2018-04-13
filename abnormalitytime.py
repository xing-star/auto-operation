#!/usr/bin/env Python
# coding=utf-8
from autooperation import app,db
from flask import request, render_template
from sqlalchemy import create_engine
from sqlalchemy import text
import cx_Oracle
import sys


@app.route('/abnormaltime',methods=['GET', 'POST'])
def autoabnormaltime():
    reload(sys)
    sys.setdefaultencoding('utf8')
    if request.method == 'GET':
        return render_template('abnormaltime.html')
