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

    sql = """
    SELECT 
        id, 
        id_user, 
        id_produk, 
        jenis_produk, 
        jumlah, 
        file_design, 
        file_RAB, 
        is_ihbs, 
        no_pesanan, 
        provinsi, 
        kab_kota,
        kecamatan,
        kelurahan
    FROM 
    tb_keranjang WHERE delete_mark = 0
    """
    # if params is not None:
    #     if params.get('id'):
    #         sql += " AND id =" + params.get('id')

    cur.execute(sql)
    myresult = cur.fetchall()

    allData = []
    for row in myresult:
        menu = {
            "id": row['id'],
            "id_user": row['id_user'],
            "id_produk": row['id_produk'],
            "jenis_produk": row['jenis_produk'],
            "jumlah": row['jumlah'],
            "file_design": row['file_design'],
            "file_RAB": row['file_RAB'],
            "is_ihbs": row['is_ihbs'],
            "no_pesanan": row['no_pesanan'],
            "provinsi": row['provinsi'],
            "kab_kota": row['kab_kota'],
            "kecamatan": row['kecamatan'],
            "kelurahan": row['kelurahan'],
            # "create_by": row[5],
            # "create_date": row[6],
            # "update_by": row[7],
            # "update_date": row[8],
            # "delete_by": row[9],
            # "delete_date": row[10],
            # "delete_mark": row[12]
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
    INSERT INTO `tb_keranjang` (
        id_user, 
        id_produk, 
        jenis_produk, 
        jumlah, 
        file_design, 
        file_RAB, 
        is_ihbs, 
        no_pesanan, 
        provinsi, 
        kab_kota,
        kecamatan,
        kelurahan, 
        create_by, 
        create_date, 
        delete_mark
    ) 
    VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
    """
    cur.execute(sqlInsert, (req['id_user'], req['id_produk'], req['jenis_produk'], req['jumlah'], req['file_design'], req['file_RAB'], req['is_ihbs'],
                req['no_pesanan'], req['provinsi'], req['kab_kota'], req['kecamatan'], req['kelurahan'], vToken['id_user'], datetime.date.today()))
    id = con.insert_id()
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionCreate(), id, '', 'tb_keranjang')

    sql = "SELECT * FROM `tb_keranjang` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "id_user": row['id_user'],
        "id_produk": row['id_produk'],
        "jenis_produk": row['jenis_produk'],
        "jumlah": row['jumlah'],
        "file_design": row['file_design'],
        "file_RAB": row['file_RAB'],
        "is_ihbs": row['is_ihbs'],
        "no_pesanan": row['no_pesanan'],
        "provinsi": row['provinsi'],
        "kab_kota": row['kab_kota'],
        "kecamatan": row['kecamatan'],
        "kelurahan": row['kelurahan']
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
    UPDATE `tb_keranjang` SET  
        id_user=%s, 
        id_produk=%s, 
        jenis_produk=%s, 
        jumlah=%s, 
        file_design=%s, 
        file_RAB=%s, 
        is_ihbs=%s, 
        no_pesanan=%s, 
        provinsi=%s, 
        kab_kota=%s,
        kecamatan=%s,
        kelurahan=%s, 
        update_by=%s, 
        update_date=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['id_user'], req['id_produk'], req['jenis_produk'], req['jumlah'], req['file_design'], req['file_RAB'], req['is_ihbs'],
                req['no_pesanan'], req['provinsi'], req['kab_kota'], req['kecamatan'], req['kelurahan'], vToken['id_user'], datetime.date.today(), id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionEdit(), id, '', 'tb_keranjang')
    con.commit()
    sql = "SELECT * FROM `tb_keranjang` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "id_user": row['id_user'],
        "id_produk": row['id_produk'],
        "jenis_produk": row['jenis_produk'],
        "jumlah": row['jumlah'],
        "file_design": row['file_design'],
        "file_RAB": row['file_RAB'],
        "is_ihbs": row['is_ihbs'],
        "no_pesanan": row['no_pesanan'],
        "provinsi": row['provinsi'],
        "kab_kota": row['kab_kota'],
        "kecamatan": row['kecamatan'],
        "kelurahan": row['kelurahan']
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
    UPDATE `tb_keranjang` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionDelete(), id, '', 'tb_keranjang')
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
