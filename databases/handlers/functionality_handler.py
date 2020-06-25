from databases.models import db_session, Functionality, engine
from helpers.utility import remove_scheme


def db_insert_functionality_link(page_url, name, link_url, score):
    page_url = remove_scheme(page_url)
    session = db_session()
    functionality = Functionality(page_url=page_url, type="link", name=name, link_url=link_url, score=score)
    try:
        session.add(functionality)
        session.commit()
    except Exception:
        # Exception if link already present.
        session.rollback()
    finally:
        session.close()


def db_get_functionality(page_url):
    sql = """SELECT page_url, type, name, link_url, score
                FROM functionality WHERE page_url LIKE :page_url"""
    rows = engine.connect().execute(sql, page_url=page_url).fetchall()
    return rows
