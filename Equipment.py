# 改版的
import sqlite3
from flask import g, render_template, request, Blueprint
from datetime import datetime
from datetime import date

equipment_router = Blueprint("equipment_router", __name__)
SQLITE_DB_PATH = 'gym.db'


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db


@equipment_router.route('/my_equip', methods=['POST'])
def my_equip():
    db = get_db()
    # cur = db.cursor()
    Today = date.today()
    Today = str(Today)

    userID = request.form.get('userID')
    print(userID)
    sql = """
        SELECT
            type,
            dateBorrow,
            timeBorrow,
            count(type)
        FROM
            schedule
        WHERE
            personID = ? AND
            dateBorrow >= ?
        GROUP BY
            type,
            DateBorrow,
            timeBorrow
    """

    data = db.execute(sql, (userID, Today)).fetchall()
    equip_data = []

    for d in data:
        equip_data.append({
            'type': d[0],
            'dateBorrow': d[1],
            'timeBorrow': d[2] + ":00",
            'amount': d[3]
        })
    print(equip_data)

    return render_template(
        'my_equip.html',
        userID=userID,
        equip_data=equip_data
    )


@equipment_router.route(
    '/equipment_router/<username>',
    methods=['GET', 'POST']
)
def start_equip(username):
    # print(username)
    Today = date.today()
    currentDateAndTime = datetime.now()
    Hour = currentDateAndTime.hour + 1
    # print("Today's date:", Today)

    return render_template('e2.html', userID=username, today=Today, hour=Hour)


# 顯示可借的
# @equipment_router.route('/search/<username>')
@equipment_router.route('/search', methods=['POST'])
def equipment():
    db = get_db()
    cur = db.cursor()

    Today = date.today()
    currentDateAndTime = datetime.now()
    Hour = currentDateAndTime.hour+1

    userID = request.form.get('userID')

    date_value = request.form.get('date')
    Date_value = datetime.strptime(date_value, '%Y-%m-%d').strftime('%Y-%m-%d')
    Date_parm = str(Date_value)

    TimeS = request.form.get('TimeS')
    TimeS_parm = str(TimeS)

    sql = """
        SELECT
            type,
            count(type)
        FROM
            equipment
        WHERE
            NOT EXISTS (
                SELECT
                    *
                FROM
                    schedule
                WHERE
                    dateBorrow = ? AND
                    timeBorrow = ? AND
                    equipment.equipmentID = schedule.equipmentID
            )
        GROUP BY
            type
    """
    # cur.execute(sql)
    cur.execute(sql, (Date_parm, TimeS_parm))
    data = cur.fetchall()
    equipment_data = []

    for d in data:
        equipment_data.append({
            'Equipment': d[0],
            'count': d[1],
            'dateBorrow': date_value,
            'timeBorrow': TimeS
        })

    db.commit()

    return render_template(
        'e2.html',
        userID=userID,
        equipment_data=equipment_data,
        today=Today,
        hour=Hour,
        dateBorrow=date_value,
        timeBorrow=TimeS + ':00'
    )


# @equipment_router.route('/borrow/<username>',methods=['POST'])
@equipment_router.route('/borrow', methods=['POST'])
def borrow():
    db = get_db()
    cur = db.cursor()

    Today = date.today()
    currentDateAndTime = datetime.now()
    Hour = currentDateAndTime.hour+1

    userID = request.form.get('userID')

    DateBorrow = request.form.get('DateBorrow')
    Date_parm = str(DateBorrow)
    # print(DateBorrow_parm)
    # print(123)
    TimeS = request.form.get('TimeBorrow')
    TimeS_parm = str(TimeS)
    # print(TimeS_parm)

    Equipment = request.form.get('Equipment')
    Equipment_parm = str(Equipment)

    Quantity = request.form.get('Quantity')
    Quantity_parm = str(Quantity)

    sql = """
        SELECT
            equipmentID
        FROM
            Equipment
        WHERE
            NOT EXISTS (
                SELECT
                    *
                FROM
                    schedule
                WHERE
                    dateBorrow = ? AND
                    timeBorrow = ? AND
                    equipment.equipmentID = schedule.equipmentID
                ) AND
            type Like ?
        LIMIT ?
    """
    cur.execute(sql, (Date_parm, TimeS_parm, Equipment_parm, Quantity_parm))
    data = cur.fetchall()

    equipment_ID = []

    for d in data:
        equipment_ID.append({
            d[0],
        })

    # print(equipment_ID)
    # print(userID)

    for d in data:
        insert_sql = """
            INSERT INTO schedule
                (equipmentID, type, dateBorrow, timeBorrow,personID)
            VALUES
                (?, ?, ?, ?, ?)
        """
        cur.execute(
            insert_sql,
            (d[0], Equipment_parm, Date_parm, TimeS_parm, userID)
        )

    # 更新時顯示每一個equipment
    sql = """
        SELECT
            type,
            count(type)
        FROM
            equipment
        WHERE
            NOT EXISTS (
                SELECT
                    *
                FROM
                    schedule
                WHERE
                    dateBorrow=? AND
                    timeBorrow=? AND
                    equipment.equipmentID=schedule.equipmentID
            )
        GROUP BY
            type
    """
    # cur.execute(sql)
    cur.execute(sql, (Date_parm, TimeS_parm))
    data = cur.fetchall()
    equipment_data = []

    for d in data:
        equipment_data.append({
            'Equipment': d[0],
            'count': d[1],
            'dateBorrow': DateBorrow,
            'timeBorrow': TimeS
        })

    db.commit()
    db.close()

    return render_template(
        'e2.html',
        userID=userID,
        equipment_data=equipment_data,
        today=Today,
        hour=Hour,
        dateBorrow=DateBorrow,
        timeBorrow=TimeS + ':00'
    )

# @equipment_router.route('/showmem',methods=['POST'])
# def showmem():
#     db = get_db()
#     cur = db.cursor()

#     userID = request.form.get('userID')


# @equipment_router.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    equipment_router.run(debug=True)
