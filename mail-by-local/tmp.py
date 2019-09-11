import pymysql

data = ''
flag = 0
try:
    conn = pymysql.connect(host='10.28.0.8',port=3306,user='root',passwd='00204XGmima@')
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    data = cursor.fetchone()
except:
    pass

if data != '':
    print(data)
    flag = 1

print(flag)
