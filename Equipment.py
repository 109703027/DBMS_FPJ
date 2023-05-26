import csv
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
SQLITE_DB_PATH = 'gym.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

#查詢要借的器材
@app.route('/', methods=['GET', 'POST'])
def search():
    return render_template('search_equip.html')
    

#找器材名稱、可借數量傳到前端顯示
@app.route('/equip',methods=['POST'])
def equipment():

    db = get_db()
    Type=request.form.get('Type')
    param1 = ('%' + Type + '%',)

    sql= "SELECT type, Count(*) FROM equipment WHERE type LIKE ? AND usable=1 Order by type"
    data = db.execute(sql, param1).fetchall()
    equipment_data =[]

    for d in data :
        equipment_data.append({
            'Equipment':d[0],
            'count':d[1],
        })
    
    return render_template(
        'equipment.html',
        equipment_data= equipment_data    
    )

#前端輸入的租借資訊，更改在db
@app.route('/modify',methods=['POST'])
def modify():
    db = get_db()
    cur = db.cursor()

    Type = request.form.get('Type')
    param1=str(Type)
   
    date_value = request.form.get('Date')
    Date = datetime.strptime(date_value, '%Y-%m-%d').strftime('%Y-%m-%d')
    param2=str(Date)

    Time_S = request.form.get('Time_S')
    param3=str(Time_S)

    Quantity = request.form.get('Quantity')
    #param3=str(Quantity)
    param4=str(Quantity)
    
    sql = """UPDATE equipment 
    SET dateBorrow = ? , usable = 0, timeBorrow= ?
    WHERE equipmentid IN (
        SELECT equipmentID
        FROM equipment
        WHERE usable = 1 AND type LIKE ?
        LIMIT ?
    )
    """

    cur.execute(sql, (param2,param3,param1,param4))
    db.commit()

    cur.close()
    db.close()

    return render_template('search_equip.html')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
