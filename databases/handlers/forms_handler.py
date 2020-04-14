from databases.database_handler import Database
from helpers.utility import remove_scheme


def db_insert_form(page_url, form_num, method, action, input_num, input_name, input_text):
    page_url = remove_scheme(page_url)
    sql = """INSERT INTO forms (page_url, form_num, method, action, input_num, input_name, input_text) 
                VALUES (?, ?, ?, ?, ?, ?, ?)"""
    try:
        Database().conn.cursor().execute(
            sql, (page_url, form_num, method, action, input_num, input_name, input_text))
    except Exception:
        pass


def db_get_forms(page_url):
    page_url = remove_scheme(page_url)
    sql = """SELECT page_url, form_num, method, action, input_num, input_name, input_text
                FROM forms WHERE page_url LIKE ?"""
    cur = Database().conn.cursor().execute(sql, (page_url,))
    rows = cur.fetchall()
    return rows
