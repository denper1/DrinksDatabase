import sqlite3
from resources.utils import setup_logger, handle_query
from resources.queries import drop_table_query


def main():
    db_name = "drinksdb"
    log = setup_logger()

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    log.info("Drop table: drinks.")
    handle_query(cursor, drop_table_query.format("drinks"))
    log.info("Drop table: ingredients.")
    handle_query(cursor, drop_table_query.format("ingredients"))
    log.info("Drop table: measurements.")
    handle_query(cursor, drop_table_query.format("measurements"))

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
