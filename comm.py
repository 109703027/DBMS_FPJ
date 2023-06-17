import sqlite3
from flask import g, render_template, request, Blueprint

comm_router = Blueprint("comm_router", __name__)
SQLITE_DB_PATH = 'gym.db'


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

# @comm_router.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return redirect(url_for('comm_router.commodity', username=request.form.get('username')))

#     return render_template('mem_login.html')


@comm_router.route('/commodity/<username>', methods=['GET', 'POST'])
def commodity(username):
    db = get_db()
    cursor = db.cursor()

    sql1 = "SELECT voucher FROM member WHERE memberID = ?"
    voucher = db.execute(sql1, (username,)).fetchall()[0][0]

    sql2 = "SELECT commodityID, name, cost, store FROM commodity"
    data = db.execute(sql2).fetchall()
    comm_data = []

    for d in data:
        comm_data.append({
            'id': d[0],
            'name': d[1],
            'cost': d[2],
            'store': d[3]
        })

    cursor.close()
    db.close()

    return render_template(
        'comm.html',
        userID=username,
        voucher=voucher,
        comm_data=comm_data
    )


@comm_router.route('/my_comm', methods=['GET', 'POST'])
def my_comm():

    userID = request.form.get('userID')
    db = get_db()
    sql = """
        SELECT
            c.commodityID,
            c.name,
            t.amount
        FROM
            commodity as c,
            transactions as t
        WHERE
            t.memberID = ? AND
            c.commodityID = t.commodityID
    """
    data = db.execute(sql, (userID,)).fetchall()
    comm_data = []

    for d in data:
        comm_data.append({
            'commid': d[0],
            'commname': d[1],
            'amount': d[2]
        })

    return render_template(
        'my_comm.html',
        userID=userID,
        comm_data=comm_data
    )


@comm_router.route('/buy', methods=['GET', 'POST'])
def buy_comm():

    userID = request.form.get('userID')
    buynum = request.form.get('buynum')
    buynum = str(buynum)
    commid = request.form.get('commid')
    commid = str(commid)
    cost = request.form.get('cost')

    db = get_db()
    cursor = db.cursor()

    sql1 = '''
        UPDATE
            commodity
        SET
            store = store - ?
        WHERE
            commodityID = ?
    '''

    cursor.execute(sql1, (buynum, commid))
    db.commit()

    sql2 = "SELECT commodityID, name, cost, store FROM commodity"
    data = db.execute(sql2).fetchall()
    comm_data = []

    for d in data:
        comm_data.append({
            'id': d[0],
            'name': d[1],
            'cost': d[2],
            'store': d[3]
        })

    sql3 = """
        INSERT INTO transactions
            (memberID, commodityID, amount)
        VALUES
            (?, ?, ?)
    """
    cursor.execute(sql3, (userID, commid, buynum))
    db.commit()

    sql4 = '''UPDATE member
            set voucher = voucher - (? * ?)
            where memberID = ?'''

    cursor.execute(sql4, (buynum, cost, userID))
    db.commit()

    sql5 = "SELECT voucher FROM member WHERE memberID = ?"
    voucher = db.execute(sql5, (userID,)).fetchall()[0][0]

    cursor.close()
    db.close()

    return render_template(
        'comm.html',
        userID=userID,
        voucher=voucher,
        comm_data=comm_data
    )


# @comm_router.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    comm_router.run(debug=True)
