import json
import datetime
import valid_token
import database_connection
import pymysql.cursors


def lambda_handler(event, context):
    # # TODO implement
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
    httpMethod = event['httpMethod']
    headers = event['headers']
    user_token = headers.get('token')
    con = database_connection.database_connection_read()

    if user_token is None:
        return send_response("Access Denied", 403)
    else:
        vToken = valid_token.validationToken(user_token)
        if vToken == "false":
            return send_response("Invalid Token", 404)
        event['data_user'] = vToken

    return getHttpMethod(con, httpMethod, event)


def getHttpMethod(con, httpMethod, event):
    if httpMethod == 'GET':
        return functionGet(con, event)
    elif httpMethod == 'POST':
        return functionPost(con, event)
    elif httpMethod == 'PUT':
        return functionPut(con, event)
    elif httpMethod == 'DELETE':
        return functionDelete(con, event)

# =============================== FUNCTION GET


def functionGet(con, event):
    cur = con.cursor(pymysql.cursors.DictCursor)
    params = event['queryStringParameters']
    vToken = event['data_user']

    sql = """
    SELECT
    	p.id,
    	p.nama_lengkap,
    	p.foto_profil,
    	p.tanggal_lahir,
    	p.no_telp,
    	p.nik,
    	p.jenis_kelamin,
    	s.email
    FROM
    	tb_master_pengguna p
    	LEFT JOIN tb_user s ON (p.id=s.id_pengguna)
    WHERE
    	p.delete_mark = 0
    """
    if vToken['id_user'] is not None:
        sql += " AND s.id =" + str(vToken['id_user'])

    cur.execute(sql)
    myresult = cur.fetchall()

    allData = []
    for row in myresult:
        menu = {
            "id": row['id'],
            "nama_lengkap": row['nama_lengkap'],
            "foto_profil": row['foto_profil'],
            "tanggal_lahir": row['tanggal_lahir'],
            "no_telp": row['no_telp'],
            "nik": row['nik'],
            "jenis_kelamin": row['jenis_kelamin'],
            "email": row['email'],
            "foto": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        }
        allData.append(menu)

    cur.close()
    return send_response(allData, 200)

# =============================== FUNCTION POST


def functionPost(con, event):
    cur = con.cursor(pymysql.cursors.DictCursor)
    req = json.loads(event['body'])
    vToken = event['data_user']

    sqlInsert = """
    INSERT INTO `tb_master_pengguna` ( nama_lengkap, foto_profil, tanggal_lahir, no_telp, nik, jenis_kelamin, create_by, create_date, delete_mark) VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, 0)
    """
    cur.execute(sqlInsert, (req['nama_lengkap'], req['foto_profil'], req['tanggal_lahir'],
                req['no_telp'], req['nik'], req['jenis_kelamin'], vToken['id_user'], datetime.date.today()))
    id = con.insert_id()
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionCreate(), id, '', 'tb_master_pengguna')

    sql = "SELECT * FROM `tb_master_pengguna` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "nama_lengkap": row['nama_lengkap'],
        "foto_profil": row['foto_profil'],
        "tanggal_lahir": row['tanggal_lahir'],
        "no_telp": row['no_telp'],
        "nik": row['nik'],
        "jenis_kelamin": row['jenis_kelamin']
    }
    con.commit()
    cur.close()
    return send_response(data, 200)

# =============================== FUNCTION PUT


def functionPut(con, event):
    cur = con.cursor(pymysql.cursors.DictCursor)
    req = json.loads(event['body'])
    params = event['queryStringParameters']
    vToken = event['data_user']
    id = params['id']

    sqlUpdate = """
    UPDATE `tb_master_pengguna` SET nama_lengkap=%s, foto_profil=%s, tanggal_lahir=%s, no_telp=%s, nik=%s, jenis_kelamin=%s, update_by=%s, update_date=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['nama_lengkap'], req['foto_profil'], req['tanggal_lahir'],
                req['no_telp'], req['nik'], req['jenis_kelamin'], vToken['id_user'], datetime.date.today(), id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionEdit(), id, '', 'tb_master_pengguna')
    con.commit()
    sql = "SELECT * FROM `tb_master_pengguna` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "nama_lengkap": row['nama_lengkap'],
        "foto_profil": row['foto_profil'],
        "tanggal_lahir": row['tanggal_lahir'],
        "no_telp": row['no_telp'],
        "nik": row['nik'],
        "jenis_kelamin": row['jenis_kelamin']
    }

    cur.close()
    return send_response(data, 200)

# =============================== FUNCTION DELETE


def functionDelete(con, event):
    cur = con.cursor()
    # req = json.loads(event['body])
    params = event['queryStringParameters']
    vToken = event['data_user']
    id = params['id']

    sqlUpdate = """
    UPDATE `tb_master_pengguna` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionDelete(), id, '', 'tb_master_')
    data = {
        "message": "Deleted!"
    }
    con.commit()
    cur.close()
    return send_response(data, 200)

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
        'body': json.dumps(response, default=str)
    }
