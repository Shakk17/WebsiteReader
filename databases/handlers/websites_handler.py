from datetime import datetime

from databases.models import Website, db_session, engine


def db_insert_website(domain):
    """
    This method inserts a website into the websites table of the database.
    :param domain: The domain of the website to insert in the database.
    """
    website = Website(domain=domain, last_crawled_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    session = db_session()
    session.add(website)
    session.commit()
    session.close()


def db_delete_website(domain):
    domain = f"%{domain}"
    sql = "DELETE FROM websites WHERE domain LIKE :domain;"
    engine.connect().execute(sql, domain=domain)


def db_last_time_crawled(domain):
    """
    This method returns the timestamp of the last crawl on a website, if it has already been crawled.
    :param domain: A string representing the domain of the website to search.
    :return: The timestamp of the last crawl (if it has been crawled), None otherwise.
    """
    sql = "SELECT * FROM websites WHERE domain LIKE :domain LIMIT 1"
    rows = engine.connect().execute(sql, domain=domain).fetchone()
    # Returns True is it has been crawled, False otherwise.
    if rows is not None:
        return rows[1]
