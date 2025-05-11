import json
import datetime
import valid_token
import database_connection
import pymysql.cursors
import string
import random


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
        no_proyek, 
        nama_proyek, 
        desc_proyek, 
        nilai_proyek, 
        provinsi, 
        kab_kota, 
        kecamatan, 
        kelurahan, 
        alamat_detail, 
        nama_pemilik_proyek, 
        no_telp_proyek 
    FROM 
        tb_unggah_proyek WHERE delete_mark = 0
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
            "no_proyek": row['no_proyek'],
            "nama_proyek": row['nama_proyek'],
            "desc_proyek": row['desc_proyek'],
            "nilai_proyek": row['nilai_proyek'],
            "provinsi": row['provinsi'],
            "kab_kota": row['kab_kota'],
            "kecamatan": row['kecamatan'],
            "kelurahan": row['kelurahan'],
            "alamat_detail": row['alamat_detail'],
            "nama_pemilik_proyek": row['nama_pemilik_proyek'],
            "no_telp_proyek": row['no_telp_proyek'],
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

    # get kode proyek
    idProyek = id_generator(6)

    sqlInsert = """
    INSERT INTO `tb_unggah_proyek` ( 
        no_proyek, 
        nama_proyek, 
        desc_proyek, 
        nilai_proyek, 
        provinsi, 
        kab_kota, 
        kecamatan, 
        kelurahan, 
        alamat_detail, 
        nama_pemilik_proyek, 
        no_telp_proyek,
        create_by, 
        create_date, 
        delete_mark) 
    VALUES 
        ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
    """
    cur.execute(sqlInsert, (idProyek,
                            req['nama_proyek'],
                            req['desc_proyek'],
                            req['nilai_proyek'],
                            req['provinsi'],
                            req['kab_kota'],
                            req['kecamatan'],
                            req['kelurahan'],
                            req['alamat_detail'],
                            req['nama_pemilik_proyek'],
                            req['no_telp_proyek'],
                            vToken['id_user'],
                            datetime.date.today()))
    id = con.insert_id()

    sql = "SELECT * FROM `tb_unggah_proyek` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "no_proyek": row['no_proyek'],
        "nama_proyek": row['nama_proyek'],
        "desc_proyek": row['desc_proyek'],
        "nilai_proyek": row['nilai_proyek'],
        "provinsi": row['provinsi'],
        "kab_kota": row['kab_kota'],
        "kecamatan": row['kecamatan'],
        "kelurahan": row['kelurahan'],
        "alamat_detail": row['alamat_detail'],
        "nama_pemilik_proyek": row['nama_pemilik_proyek'],
        "no_telp_proyek": row['no_telp_proyek']
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
    UPDATE `tb_unggah_proyek` SET 
        nama_proyek=%s, 
        desc_proyek=%s, 
        nilai_proyek=%s, 
        provinsi=%s, 
        kab_kota=%s, 
        kecamatan=%s, 
        kelurahan=%s, 
        alamat_detail=%s, 
        nama_pemilik_proyek=%s, 
        no_telp_proyek=%s, 
        update_by=%s, 
        update_date=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['nama_proyek'], req['desc_proyek'], req['nilai_proyek'], req['provinsi'], req['kab_kota'], req['kecamatan'],
                req['kelurahan'], req['alamat_detail'], req['nama_pemilik_proyek'], req["no_telp_proyek"], vToken['id_user'], datetime.date.today(), id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionEdit(), id, '', 'tb_unggah_proyek')
    con.commit()
    sql = "SELECT * FROM `tb_unggah_proyek` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "no_proyek": row['no_proyek'],
        "nama_proyek": row['nama_proyek'],
        "desc_proyek": row['desc_proyek'],
        "nilai_proyek": row['nilai_proyek'],
        "provinsi": row['provinsi'],
        "kab_kota": row['kab_kota'],
        "kecamatan": row['kecamatan'],
        "kelurahan": row['kelurahan'],
        "alamat_detail": row['alamat_detail'],
        "nama_pemilik_proyek": row['nama_pemilik_proyek'],
        "no_telp_proyek": row['no_telp_proyek']
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
    UPDATE `tb_unggah_proyek` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionDelete(), id, '', 'tb_unggah_proyek')
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

# function for generate no proyek


def id_generator(length):
    return_str = ""

    data = string.ascii_uppercase + '0123456789'

    for i in range(length):
        return_str += random.choice(data)

    return return_str
