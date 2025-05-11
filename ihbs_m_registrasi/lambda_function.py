import json
import hashlib
import datetime
import valid_token
import pymysql.cursors
import database_connection


def lambda_handler(event, context):
    # return send_response(event, 200)

    httpMethod = event['httpMethod']
    headers = event['headers']
    user_token = headers.get('token')
    con = database_connection.database_connection_read()

    if httpMethod == 'POST':
        return getHttpMethod(con, httpMethod, event)
    else:
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

# =============================== START FUNCTION

# =============================== FUNCTION POST


def functionPost(con, event):
    cur = con.cursor(pymysql.cursors.DictCursor)
    req = json.loads(event['body'])

    sqlInsertPengguna = """
    INSERT INTO `tb_master_pengguna` (nama_lengkap, no_telp, create_date, delete_mark) VALUES (%s, %s, %s, 0)
    """
    cur.execute(sqlInsertPengguna, (str(req['nama_lengkap']), str(
        req['no_telp']), datetime.date.today()))
    id_pengguna = con.insert_id()

    sqlInsert = """
    INSERT INTO tb_alamat_pengguna (`id_pengguna`, `create_date`, `delete_mark`) VALUES (%s, %s, 0)
    """
    cur.execute(sqlInsert, (str(id_pengguna), datetime.date.today()))

    sqlInsert = """
    INSERT INTO `tb_user` 
    (id_pengguna, email, kata_sandi, jenis_user, jenis_rekanan, status_aktif, kode_referal, create_date, delete_mark) 
    VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, 0)
    """

    cur.execute(sqlInsert, (str(id_pengguna), str(req['email']), hashlib.md5(str(req['kata_sandi']).encode('utf-8')).hexdigest(),
                            str(req['jenis_user']), str(req['jenis_rekanan']), str(req['status_aktif']), str(req['kode_referal']), datetime.date.today()))
    id = con.insert_id()

    sql = """
    SELECT
        akun.id,
    	akun.email,
    	usr.nama_lengkap,
    	akun.jenis_user,
    	akun.jenis_rekanan,
    	akun.status_aktif
	FROM
	    tb_user AS akun 
	    LEFT JOIN tb_master_pengguna AS usr ON (usr.id=akun.id_pengguna)
	WHERE 
	    akun.id = %s
	"""
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "jenis_user": row['jenis_user'],
        "nama_lengkap": row['nama_lengkap']
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
    id_pengguna = params['id_pengguna']

    sqlUpdate = """
    UPDATE `tb_user` 
    SET email=%s, update_by=%s, update_date=%s 
    WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['email'],
                vToken['id_user'], datetime.date.today(), id))
    con.commit()

    sqlUpdate = """
    UPDATE `tb_master_pengguna` 
    SET nama_lengkap=%s, jenis_kelamin=%s, tanggal_lahir=%s, no_telp=%s, update_by=%s, update_date=%s 
    WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['nama_lengkap'], req['jenis_kelamin'], req['tanggal_lahir'],
                req['no_telp'], vToken['id_user'], datetime.date.today(), id_pengguna))
    con.commit()

    sqlUpdate = """
    UPDATE `tb_alamat_pengguna` 
    SET provinsi=%s, kab_kota=%s, kecamatan=%s, kelurahan=%s, detail=%s, update_by=%s, update_date=%s 
    WHERE id=%s
    """
    cur.execute(sqlUpdate, (str(req['provinsi']), str(req['kab_kota']), str(req['kecamatan']), str(
        req['kelurahan']), req['detail'], vToken['id_user'], datetime.date.today(), id_pengguna))
    con.commit()
    sql = """
    SELECT 
        usr.nama_lengkap, 
        usr.jenis_kelamin, 
        usr.tanggal_lahir,
        usr.no_telp,
        akun.email,
        almt.provinsi,
        almt.kab_kota,
        almt.kecamatan,
        almt.kelurahan,
        almt.detail
    FROM 
        tb_master_pengguna as usr 
        LEFT JOIN tb_alamat_pengguna as almt ON (usr.id = almt.id_pengguna)
        LEFT JOIN tb_user as akun ON (usr.id = akun.id_pengguna)
    WHERE 
        usr.id = %s"""
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "nama_lengkap": row['nama_lengkap'],
        "jenis_kelamin": row['jenis_kelamin'],
        "tanggal_lahir": row['tanggal_lahir'],
        "email": row['email'],
        "no_telp": row['no_telp'],
        "provinsi": row['provinsi'],
        "kab_kota": row['kab_kota'],
        "kecamatan": row['kecamatan'],
        "kelurahan": row['kelurahan'],
        "detail": row['detail']
    }

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
