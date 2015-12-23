# coding:utf8
import os

import torndb
from util.Util import Config



def connectMYSQL(mysqlIP,mysqlDATABASE,mysqlUSERNAME,mysqlPASSWORD):
    try:
        print u'尝试连接数据库 %s ,数据库：%s，用户名：%s，密码：%s' % (mysqlIP, mysqlDATABASE, mysqlUSERNAME, mysqlPASSWORD)
        db = torndb.Connection(mysqlIP, mysqlDATABASE, user=mysqlUSERNAME, password=mysqlPASSWORD)
        print u'连接数据库successed'
        return db
    except:
        print u'connect mysql faiuled'


# 添加任务到mysql 返回当前任务是第N条。
def addTask(db, symptom, datetime, lat, lon, patient_tel, patient_name, doctor_tel, doctor_name):
    sql = r"INSERT INTO detailtask (symptom, datetime,lat, lon, patient_tel, patient_name, doctor_tel, doctor_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    r = db.insert(sql, symptom, datetime, lat, lon, patient_tel, patient_name, doctor_tel, doctor_name)
    return r


# db torndb.Connection() 连接成功后返回的db实例
# patient 字典格式的数据实体
# return r 返回操作影响条数
def mysqlAddPatient(db, patient):
    sql = r'INSERT INTO handinhand_patient (tel,pic,name,gender,age,treatment_count,collection_list_id) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    r = db.insert(sql, patient['tel'], patient['password'], patient['pic'], patient['name'], patient['gender'],
                  patient['age'],
                  patient['treatment_count'], patient['collection_list_id'])
    return r


# tel 病人电话号
# return r 如果电话号不存在返回 False 存在 则返回 tel对应实体 list
def isExistsPatient(db, tel):
    sql = r'select tel,password,pic,name,gender,age,treatment_count,collection_list_id FROM handinhand_patient where tel = %s' % tel
    r = db.query(sql)
    print os.path.dirname(__file__), type(r)
    if len(r) == 0:
        return False
    else:
        return r


if __name__ == "__main__":
    db = connectMYSQL()
    print db
    r = isExistsPatient('13187551089')
    if r != False:
        print r[0]['tel']
    else:
        print 'nothing'
