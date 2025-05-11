import pymysql
import json
import datetime
import hashlib
import string
import random
import database_connection


def lambda_handler(event, context):
    # # TODO implement
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
    con = database_connection.database_connection_write()

    return functionLogin(con, event)

# =============================== START FUNCTION

# =============================== FUNCTION LOGIN


def functionLogin(con, event):
    # return send_response(event, 200)

    cur = con.cursor()
    req = json.loads(event['body'])
    # req = event

    password = hashlib.md5(req['password'].encode('utf-8')).hexdigest()
    username = req['nama_user']

    sql = """
    SELECT
    	COUNT( u.email ),
    	u.id,
    	u.id_pengguna,
    	p.nik,
    	p.nama_lengkap,
    	p.no_telp,
    	u.email
    FROM
    	`tb_user` u
    	LEFT JOIN tb_master_pengguna p ON (p.id=u.id_pengguna)
    WHERE
    	u.email = %s 
    	AND u.kata_sandi = %s
    	AND u.delete_mark = 0
	"""
    cur.execute(sql, (username, password))
    row = cur.fetchone()

    if row[0] == 0:
        data = {
            "message": "User tidak ditemukan!"
        }
        return send_response(data, 404)
    else:
        id_user = row[1]
        id_pengguna = row[2]
        nik = row[3]
        nama_lengkap = row[4]
        no_telp = row[5]
        email = row[6]
        token_user = expiredToken(id_user, cur)

        con.commit()
        cur.close()

        data = {
            "message": "Login Success!",
            "token": token_user,
            "id_user": id_user,
            "id_pengguna": id_pengguna,
            "nik": nik,
            "nama_lengkap": nama_lengkap,
            "no_telp": no_telp,
            "email": email,
            "foto": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
        }
        return send_response(data, 200)

# =============================== FUNCTION GENERATE TOKEN


def generateToken(chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(50))


# =============================== FUNCTION CEK EXPIRED TOKEN
def expiredToken(id_user, cur):
    token = generateToken()

    sqlCek = "SELECT COUNT(id_user), token, id_user FROM `tb_token` WHERE id_user = %s AND expired_date >= CURDATE()"
    cur.execute(sqlCek, (id_user))
    rowCek = cur.fetchone()

    if rowCek[0] == 0:
        sqlDelete = "DELETE FROM `tb_token` WHERE id_user = %s"
        cur.execute(sqlDelete, (id_user))

        sqlInsert = "INSERT INTO `tb_token` (token, id_user, expired_date) VALUES (%s, %s, %s)"
        cur.execute(sqlInsert, (token, id_user, datetime.date.today()))

        # token_user = token + "-" + str(id_user)
        token_user = token

    else:
        # token_user = rowCek[1] + "-" + str(id_user)
        token_user = rowCek[1]

    return token_user

# =============================== END FUNCTION

# function for response


def send_response(data, status_code):
    response = {
        "status": status_code,
        "data": data
    }
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*'
            # 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
