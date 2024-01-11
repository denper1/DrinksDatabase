import sqlite3
from resources.utils import handle_query
from resources.queries import drop_table_query

db_name = "drinksdb"

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

print("Drop table: drinks.")
handle_query(cursor, drop_table_query.format("drinks"))
print("Drop table: ingredients.")
handle_query(cursor, drop_table_query.format("ingredients"))
print("Drop table: measurements.")
handle_query(cursor, drop_table_query.format("measurements"))

cursor.close()
conn.close()
