# coding:utf8

import torndb
from util.Util import Config

# 获取配置信息
c = Config()


def connectMYSQL():
    try:
        print u'尝试连接数据库 %s ,数据库：%s，用户名：%s，密码：%s' % (c.mysqlIP, c.mysqlDATABASE, c.mysqlUSERNAME, c.mysqlPASSWORD)
        db = torndb.Connection(c.mysqlIP, c.mysqlDATABASE, user=c.mysqlUSERNAME, password=c.mysqlPASSWORD)
        print u'连接数据库successed'
        return db
    except:
        print u'connect mysql faiuled'


#添加任务到mysql 返回当前任务是第N条。
def addTask(db,symptom, datetime,lat, lon, patient_tel, patient_name, doctor_tel, doctor_name):
    sql = r"INSERT INTO detailtask (symptom, datetime,lat, lon, patient_tel, patient_name, doctor_tel, doctor_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    r = db.insert(sql,symptom, datetime,lat, lon, patient_tel, patient_name, doctor_tel, doctor_name)
    return r

# db torndb.Connection() 连接成功后返回的db实例
# patient 字典格式的数据实体
# return r 返回操作影响条数
def mysqlAddPatient(db,patient):
    sql = r'INSERT INTO handinhand_patient (tel,pic,name,gender,age,treatment_count,collection_list_id) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    r = db.insert(sql,patient['tel'],patient['pic'],patient['name'],patient['gender'],patient['age'],patient['treatment_count'],patient['collection_list_id'])
    return r

def isExistsPatient(tel):
    sql = r'select tel FROM handinhand_patient where tel = %s'%tel
    r = db.query(sql)
    print r


if __name__ == "__main__":
    db = connectMYSQL()
    print db
    r= isExistsPatient('13187551089')
    print r