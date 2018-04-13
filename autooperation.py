#!/usr/bin/env Python
# coding=utf-8
from flask import Flask, request, render_template, json
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



@app.route('/abnormaltime',methods=['GET', 'POST'])
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
        sql = "select AB_BU BU,count(AB_BU) count FROM \
                    mes1.c_pcassystemabnormal where ABNORMALID IN (SELECT \
                    ABNORMALID FROM mes1.c_pcasabnormaldisposalinfo where \
                    DISPOSASTATUS IN ('T2E3W1','T0E2W1') AND EDITTIME >= \
                    to_date('"+startDate+"080000','yyyy-mm-ddhh24miss') \
                    AND EDITTIME <= to_date('"+endDate+"200000', \
                    'yyyy-mm-ddhh24miss')) group by AB_BU order by count desc"
        cursor = db.cursor()
        result = cursor.execute(sql)
        str_list = result.fetchall()
        return render_template('index.html', str_list=str_list, \
                                startDate=startDate, endDate=endDate)


@app.route('/',methods=['GET', 'POST'])
def autoabnormaltime():
    reload(sys)
    sys.setdefaultencoding('utf8')
    '''
    此處若不加上db = xxx...
    會產生DatabaseError: DPI-1010: not connected異常
    待查明具體原因......
    原因：db連接已被關閉，第二次訪問的時候就會沒有鏈接
    '''
    # db = cx_Oracle.connect('ADMIN/PCAS_ADMIN@10.67.51.174:1521/pcasdb')
    if request.method == 'GET':
        ABSN = request.args.get('ABSN')
        if ABSN:
            print ("ABSN IS NOT None")
            sql = "select * from MES4.R_ABNORMAL_RECORD where ab_sn \
                  = '"+ABSN+"'and starttime >= SYSDATE-3"
            cursor = db.cursor()
            result = cursor.execute(sql)
            if result:
                str_list = result.fetchall()
                if str_list:
                    return render_template('abnormaltime.html', \
                           str_list=str_list)
                return "<script>alert('沒有該筆異常或該筆異常已超過兩天無法修改'); \
                        window.history.go(-1);</script>"
            else:
                return "<script>alert('沒有該筆異常或該筆異常已超過兩天無法修改'); \
                        window.history.go(-1);</script>"

        print ("ABSN is None")
        return render_template('abnormaltime.html')
    else:
        ab_sn = request.form.get('data')
        updateData = None
        if ab_sn:
            print ("------------------------")
            deleteSQL = "delete from MES4.R_ABNORMAL_RECORD where ab_sn \
                        = '"+ab_sn+"'"
            insertSQL = "insert into MES4.R_ABNORMAL_RECORD_DELETE(BU_CODE, \
                            SE_CODE,FL_CODE,LI_CODE,ST_CODE,MODEL_NO,PRODUCT, \
                            WORKORDERNO,DEFECT_ITEM_CODE,DEFECT_TYPE_CODE, \
                            DEFECT_DESC,DEFECT_DESC1,DEFECT_DESC2, \
                            DEFECT_DESC3,FLAG,STARTTIME,ENDTIME,INTERVALTIME, \
                            DEPART,ALARM_FLAG,EDITBY,EDITTIME,AB_SN,ABP, \
                            FACTORYID,OPERATION,WC,ACTIVE_ES,ACTIVE_NS,\
                            EQUIPMENT_NO,PART_NO,DEAL_FUNCTION,STATUS) SELECT \
                            * FROM MES4.R_ABNORMAL_RECORD WHERE AB_SN \
                            = '"+ab_sn+"'"
        else:
            updateData = json.loads(request.form.get('dataTest'))
            print (updateData)
            absncode = updateData['absncode']
            starttime = updateData['starttime']
            endtime = updateData['endtime']
            intervaltime = updateData['intervaltime']
            typecode = updateData['typecode']
            itemcode = updateData['itemcode']
            desc1 = updateData['desc1']
            desc2 = updateData['desc2']
            desc3 = updateData['desc3']
            departcode = updateData['departcode']
            updateSQL = "update mes4.R_ABNORMAL_RECORD set starttime = \
                to_date('"+starttime+"','yyyy-mm-dd hh24:mi:ss'),endtime = \
                to_date('"+endtime+"','yyyy-mm-dd hh24:mi:ss'),intervaltime = \
                '"+intervaltime+"',defect_item_code = '"+itemcode+"', \
                defect_type_code = '"+typecode+"',defect_desc = \
                '"+desc1+"',defect_desc1 = '"+desc2+"',defect_desc2 = \
                '"+desc3+"',depart = '"+departcode+"' where ab_sn = \
                '"+absncode+"'"
            print (updateSQL)
        cursor = db.cursor()
        '''
        先插入歷史表再進行刪除動作,保證數據可恢復
        '''
        if updateData:
            cursor.execute(updateSQL)
        else:
            print ("------------------------")
            cursor.execute(insertSQL)
            cursor.execute(deleteSQL)
        db.commit()
        # cursor.close()
        # db.close()
        return "更新成功"


if __name__ == '__main__':
    app.run()
