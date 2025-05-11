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
    SELECT id, id_pengguna, id_bidang_usaha FROM tb_bidang_usaha_pengguna
    """
    if params is not None:
        if params.get('id'):
            sql += " AND id =" + params.get('id')

    cur.execute(sql)
    myresult = cur.fetchall()

    allData = []
    for row in myresult:
        menu = {
            "id": row['id'],
            "id_pengguna": row['id_pengguna'],
            "id_bidang_usaha": row['id_bidang_usaha']
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
    INSERT INTO `tb_bidang_usaha_pengguna` (id_pengguna, id_bidang_usaha) VALUES 
    (%s, %s)
    """
    cur.execute(sqlInsert, (req['id_pengguna'], req['id_bidang_usaha']))
    id = con.insert_id()

    sql = "SELECT * FROM `tb_bidang_usaha_pengguna` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "id_pengguna": row['id_pengguna'],
        "id_bidang_usaha": row['id_bidang_usaha']
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
