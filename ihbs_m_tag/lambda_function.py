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
    SELECT id, nama_tag, is_use, status FROM tb_master_tag WHERE delete_mark = 0
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
            "nama_tag": row['nama_tag'],
            "is_use": row['is_use'],
            "status": row['status'],
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
    INSERT INTO `tb_master_tag` (  nama_tag, is_use, status, create_by, create_date, delete_mark) VALUES 
    (%s, %s, %s, %s, %s, 0)
    """
    cur.execute(sqlInsert, (req['nama_tag'], req['is_use'], req['status'], vToken['id_user'], datetime.date.today()))
    id = con.insert_id()
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionCreate(), id, '', 'tb_master_tag')

    sql = "SELECT * FROM `tb_master_tag` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "nama_tag": row['nama_tag'],
        "is_use": row['is_use'],
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
    UPDATE `tb_master_tag` SET  nama_tag=%s, is_use=%s, status=%s, update_by=%s, update_date=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['nama_tag'], req['is_use'], req['status'], vToken['id_user'], datetime.date.today(), id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionEdit(), id, '', 'tb_master_tag')
    con.commit()
    sql = "SELECT * FROM `tb_master_tag` WHERE id = %s"
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "nama_tag": row['nama_tag'],
        "is_use": row['is_use'],
        "status": row['status']
    }

    cur.close()
    return send_response(data, 200)     
    
# =============================== FUNCTION DELETE
def functionDelete(con, event):
    cur = con.cursor()
    #req = json.loads(event['body])
    params = event['queryStringParameters']
    vToken = event['data_user']
    id = params['id']

    sqlUpdate = """
    UPDATE `tb_master_tag` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionDelete(), id, '', 'tb_master_tag')
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