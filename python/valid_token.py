import database_connection


def validationToken(token_user):
    con = database_connection.database_connection_read()

    cur = con.cursor()
    
    sql = "SELECT id_user FROM `tb_token` WHERE token = %s"
    cur.execute(sql, (token_user))
    row = cur.fetchone()

    cur.close()
    if row[0] is None:
        return "false"
    else:
        return {
            "id_user": row[0]
        }