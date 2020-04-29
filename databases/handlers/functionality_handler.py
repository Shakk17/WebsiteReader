from databases.database_handler import Database
from helpers.utility import remove_scheme


def db_insert_functionality_link(page_url, name, link_url, score):
    page_url = remove_scheme(page_url)
    sql = """INSERT INTO functionality (page_url, type, name, link_url, score) 
                VALUES (?, ?, ?, ?, ?)"""
    cur = Database().conn.cursor()
    try:
        cur.execute(sql, (page_url, "link", name, link_url, score))
    except Exception:
        pass
    cur.close()


def db_get_functionality(page_url):
    sql = """SELECT page_url, type, name, link_url, score
                FROM functionality WHERE page_url LIKE ?"""
    cur = Database().conn.cursor()
    cur.execute(sql, (page_url,))
    rows = cur.fetchall()
    cur.close()
    return rows
