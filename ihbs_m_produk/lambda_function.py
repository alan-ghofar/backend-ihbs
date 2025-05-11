import json
import datetime
import valid_token
import database_connection
import pymysql.cursors


def lambda_handler(event, context):

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
    SELECT id_produk, kode_produk, nama_produk, id_kategori, id_kriteria, id_merk, ukuran, minimal_beli, tag, img_produk, konten, status FROM tb_master_produk WHERE delete_mark = 0
    """
    if params is not None:
        if params.get('id'):
            sql += " AND id_produk =" + params.get('id')

    cur.execute(sql)
    myresult = cur.fetchall()

    allData = []
    for row in myresult:
        menu = {
            "id_produk": row['id_produk'],
            "kode_produk": row['kode_produk'],
            "nama_produk": row['nama_produk'],
            "id_kategori": row['id_kategori'],
            "id_kriteria": row['id_kriteria'],
            "id_merk": row['id_merk'],
            "ukuran": row['ukuran'],
            "minimal_beli": row['minimal_beli'],
            "tag": row['tag'],
            "img_produk": row['img_produk'],
            "konten": row['konten'],
            "status": row['status']
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
    INSERT INTO `tb_master_produk` (kode_produk, nama_produk, id_kategori, id_kriteria, id_merk, ukuran, minimal_beli, tag, img_produk, konten, status, create_by, create_date, delete_mark) VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
    """
    cur.execute(sqlInsert, (req['kode_produk'], req['nama_produk'], req['id_kategori'], req['id_kriteria'], req['id_merk'], req['ukuran'],
                req['minimal_beli'], req['tag'], req['img_produk'], req['konten'], req['status'], vToken['id_user'], datetime.date.today()))
    id = con.insert_id()

    sql = "SELECT * FROM `tb_master_produk` WHERE id_produk = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id_produk": row['id_produk'],
        "kode_produk": row['kode_produk'],
        "nama_produk": row['nama_produk'],
        "id_kategori": row['id_kategori'],
        "id_kriteria": row['id_kriteria'],
        "id_merk": row['id_merk'],
        "ukuran": row['ukuran'],
        "minimal_beli": row['minimal_beli'],
        "tag": row['tag'],
        "img_produk": row['img_produk'],
        "konten": row['konten'],
        "status": row['status']
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
    UPDATE `tb_master_produk` SET kode_produk=%s, nama_produk=%s, id_kategori=%s, id_kriteria=%s, id_merk=%s, ukuran=%s, minimal_beli=%s, tag=%s, img_produk=%s, konten=%s, status=%s, update_by=%s, update_date=%s WHERE id_produk=%s
    """
    cur.execute(sqlUpdate, (req['kode_produk'], req['nama_produk'], req['id_kriteria'], req['id_kriteria'], req['id_merk'], req['ukuran'],
                req['minimal_beli'], req['tag'], req['img_produk'], req['konten'], req['status'], vToken['id_user'], datetime.date.today(), id))
    con.commit()
    sql = "SELECT * FROM `tb_master_produk` WHERE id_produk = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id_produk": row['id_produk'],
        "kode_produk": row['kode_produk'],
        "nama_produk": row['nama_produk'],
        "id_kategori": row['id_kategori'],
        "id_kriteria": row['id_kriteria'],
        "id_merk": row['id_merk'],
        "ukuran": row['ukuran'],
        "minimal_beli": row['minimal_beli'],
        "tag": row['tag'],
        "img_produk": row['img_produk'],
        "konten": row['konten'],
        "status": row['status']
    }

    cur.close()
    return send_response(data, 200)

# =============================== FUNCTION DELETE


def functionDelete(con, event):
    cur = con.cursor()
    params = event['queryStringParameters']
    vToken = event['data_user']
    id = params['id']

    sqlUpdate = """
    UPDATE `tb_master_produk` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id_produk=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
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
        },
        'body': json.dumps(response, default=str)
    }
