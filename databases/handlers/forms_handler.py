from databases.models import Form, db_session, engine
from helpers.utility import remove_scheme


def db_insert_form(page_url, form_num, method, action, input_num, input_name, input_text):
    page_url = remove_scheme(page_url)
    form = Form(page_url=page_url, form_num=form_num, method=method, action=action, input_num=input_num,
                input_name=input_name, input_text=input_text)
    session = db_session()
    try:
        session.add(form)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def db_get_forms(page_url):
    page_url = remove_scheme(page_url)
    sql = """SELECT page_url, form_num, method, action, input_num, input_name, input_text
                FROM forms WHERE page_url LIKE :page_url"""
    rows = engine.connect().execute(sql, page_url=page_url).fetchall()
    return rows
