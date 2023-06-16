#改版的
import csv
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, Blueprint
from datetime import datetime

equipment_router = Blueprint("equipment_router", __name__)
SQLITE_DB_PATH = 'gym.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

@equipment_router.route('/', methods=['GET', 'POST'])
def start_equip():
    return render_template('e2.html')

#顯示可借的
@equipment_router.route('/search',methods=['POST'])
def equipment():
    db = get_db()
    cur = db.cursor()

    date_value=request.form.get('date')
    Date_value = datetime.strptime(date_value, '%Y-%m-%d').strftime('%Y-%m-%d')
    Date_parm=str(Date_value)

    TimeS = request.form.get('TimeS')
    TimeS_parm=str(TimeS)
    
    sql = "SELECT type,count(type) FROM equipment WHERE not exists(SELECT * FROM schedule WHERE dateBorrow=? and timeBorrow=? and equipment.equipmentID=schedule.equipmentID) GROUP BY type"
    #cur.execute(sql)
    cur.execute(sql, (Date_parm,TimeS_parm))
    data=cur.fetchall()
    equipment_data =[]
   
    for d in data :
        equipment_data.append({
            'Equipment':d[0],
            'count':d[1],
            'dateBorrow':date_value,
            'timeBorrow':TimeS
        })

    db.commit()

    return render_template(
        'e2.html',
        equipment_data= equipment_data
    )


#@equipment_router.route('/borrow',methods=['POST'])
def borrow():
    db = get_db()
    cur = db.cursor()

    DateBorrow=request.form.get('DateBorrow')
    Date_parm=str(DateBorrow)
    #print(DateBorrow_parm)

    TimeS=request.form.get('TimeBorrow')
    TimeS_parm=str(TimeS)
    #print(TimeS_parm)

    Equipment = request.form.get('Equipment')
    Equipment_parm=str(Equipment)

    Quantity = request.form.get('Quantity')
    Quantity_parm=str(Quantity)
    
    sql = """SELECT equipmentID 
    FROM Equipment 
    WHERE not exists(
        SELECT * 
        FROM schedule 
        WHERE dateBorrow=? and timeBorrow=? and equipment.equipmentID=schedule.equipmentID) and type Like ? 
        LIMIT ?
    """
    cur.execute(sql, (Date_parm,TimeS_parm,Equipment_parm,Quantity_parm ))
    data=cur.fetchall()

    equipment_ID =[]
    for d in data :
        equipment_ID.append({
            d[0],
        })
    print(equipment_ID)
    
    for d in data :
        insert_sql = "INSERT INTO schedule (equipmentID, type, dateBorrow, timeBorrow,personID) \
                        VALUES (?, ?, ?, ?,?)"
        cur.execute(insert_sql, (d[0],Equipment_parm , Date_parm, TimeS_parm, 'NULL' ))



    #更新時顯示每一個equipment
    sql = "SELECT type,count(type) FROM equipment WHERE not exists(SELECT * FROM schedule WHERE dateBorrow=? and timeBorrow=? and equipment.equipmentID=schedule.equipmentID) GROUP BY type"
    #cur.execute(sql)
    cur.execute(sql, (Date_parm,TimeS_parm))
    data=cur.fetchall()
    equipment_data =[]
   
    for d in data :
        equipment_data.append({
            'Equipment':d[0],
            'count':d[1],
            'dateBorrow':DateBorrow,
            'timeBorrow':TimeS
        })
    
    
    
    db.commit()
    db.close()


   

    return render_template(
        'e2.html',
        equipment_data= equipment_data
    )




#@equipment_router.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
