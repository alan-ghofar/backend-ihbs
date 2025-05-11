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
        gal.id,    
        gal.judul,
        gal.id_lokasi,
        gal.id_kategori,
        gal.id_style,
        gal.image_galeri,
        gal.konten,
        gal.`status`
    FROM 
        `tb_galeri` gal  
        LEFT JOIN `tb_master_lokasi` mlok ON ( mlok.id = gal.id_lokasi )
        LEFT JOIN `tb_master_kategori_galeri` mkgal ON ( mkgal.id = gal.id_kategori )
        LEFT JOIN `tb_master_style` mst ON ( mst.id = gal.id_style ) 
    WHERE 
        gal.delete_mark = 0
    """
    if params is not None:
        if params.get('id'):
            sql += " AND gal.id =" + params.get('id')

    cur.execute(sql)
    myresult = cur.fetchall()

    allData = []
    for row in myresult:
        menu = {
            "id": row['id'],
            "judul": row['judul'],
            "id_lokasi": row['id_lokasi'],
            "id_kategori": row['id_kategori'],
            "id_style": row['id_style'],
            "image_galeri": row['image_galeri'],
            "konten": row['konten'],
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
    INSERT INTO `tb_galeri` (  judul, id_lokasi, id_kategori, id_style, image_galeri, konten, status, create_by, create_date, delete_mark) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sqlInsert, (req['judul'], req['id_lokasi'], req['id_kategori'], req['id_style'], req['image_galeri'], req['konten'], 
        req['status'], vToken['id_user'], datetime.date.today(), 0))
    id = con.insert_id()
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionCreate(), id, '', 'tb_galeri')

    sql = """
    SELECT 
        gal.id,    
        gal.judul,
        gal.id_lokasi,
        gal.id_kategori,
        gal.id_style,
        gal.image_galeri,
        gal.konten,
        gal.`status`
    FROM 
        `tb_galeri` gal  
        LEFT JOIN `tb_master_lokasi` mlok ON ( mlok.id = gal.id_lokasi )
        LEFT JOIN `tb_master_kategori_galeri` mkgal ON ( mkgal.id = gal.id_kategori )
        LEFT JOIN `tb_master_style` mst ON ( mst.id = gal.id_style ) 
    WHERE 
        gal.delete_mark = 0 
        AND gal.id = %s
    """
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "judul": row['judul'],
        "id_lokasi": row['id_lokasi'],
        "id_kategori": row['id_kategori'],
        "id_style": row['id_style'],
        "image_galeri": row['image_galeri'],
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
    UPDATE `tb_galeri` SET  judul=%s, id_lokasi=%s, id_kategori=%s, id_style=%s, image_galeri=%s, konten=%s, status=%s, update_by=%s, update_date=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (req['judul'], req['id_lokasi'], req['id_kategori'], req['id_style'], req['image_galeri'], req['konten'], req['status'], vToken['id_user'], datetime.date.today(), id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionEdit(), id, '', 'tb_galeri')
    con.commit()
    sql = """
    SELECT 
        gal.id,    
        gal.judul,
        gal.id_lokasi,
        gal.id_kategori,
        gal.id_style,
        gal.image_galeri,
        gal.konten,
        gal.`status`
    FROM 
        `tb_galeri` gal  
        LEFT JOIN `tb_master_lokasi` mlok ON ( mlok.id = gal.id_lokasi )
        LEFT JOIN `tb_master_kategori_galeri` mkgal ON ( mkgal.id = gal.id_kategori )
        LEFT JOIN `tb_master_style` mst ON ( mst.id = gal.id_style ) 
    WHERE 
        gal.delete_mark = 0
        AND gal.id = %s
    """
    cur.execute(sql, (id))
    row = cur.fetchone()
    data = {
        "id": row['id'],
        "judul": row['judul'],
        "id_lokasi": row['id_lokasi'],
        "id_kategori": row['id_kategori'],
        "id_style": row['id_style'],
        "image_galeri": row['image_galeri'],
        "konten": row['konten'],
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
    UPDATE `tb_galeri` SET delete_by=%s, delete_date=%s, delete_mark=%s WHERE id=%s
    """
    cur.execute(sqlUpdate, (vToken['id_user'], datetime.date.today(), "1", id))
    # inc_db.addAuditMaster(con, gcode_menu(), inc_def.getActionDelete(), id, '', 'tb_galeri')
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