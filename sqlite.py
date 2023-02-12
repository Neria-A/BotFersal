import sqlite3
from datetime import datetime
from Shovar import Shovar
import appSettings
import os.path
from os import path


def insert_to_table_string(table_name):
    return f"""INSERT INTO {table_name}(code, amount, expiry_date, is_used, date_added, date_used) VALUES(?, ?, ?, ?, ?, ?);"""


def create_db(db_name):
    try:
        sqlite_connection = sqlite3.connect(db_name)
        print(f"Connected to SQLite {db_name}")
        return sqlite_connection
    except sqlite3.Error as error:
        print("Failed to connect to SQLite", error)


def create_cursor(sqlite_connection):
    try:
        cursor = sqlite_connection.cursor()
        return cursor
    except sqlite3.Error as error:
        print("Failed to create SQLite cursor", error)


def create_table(cursor, table_name):
    try:
        cursor.execute(f"CREATE TABLE {table_name}(code INTEGER NOT NULL UNIQUE, amount, expiry_date, is_used, date_added, date_used)")
        print("SQLite table has created")
    except sqlite3.Error as error:
        print("Failed to create SQLite table", error)


def insert_one(sqlite_connection, cursor,  shovar, table_name):
    data_tuple = convert_shovar_to_data_tuple(shovar)
    try:
        cursor.execute(insert_to_table_string(table_name), data_tuple)
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Failed to insert row to SQLite table", error)


def convert_shovar_to_data_tuple(shovar):
    return shovar.code, shovar.amount, shovar.expiry_date, shovar.is_used, datetime.now(), shovar.expiry_date


def insert_many(sqlite_connection, cursor, table_name, shovar_list):
    try:
        cursor.executemany(insert_to_table_string(table_name), shovar_list)
        sqlite_connection.commit()
        print(f"multiple rows added to {table_name} table")
    except sqlite3.Error as error:
        print(f"Failed to insert multiple rows to SQLite {table_name} table", error)


def print_all_rows(cursor, table_name):
    for row in cursor.execute(f"SELECT * FROM {table_name}"):
        print(row)


def close_cursor(cursor):
    if cursor:
        cursor.close()
        print("The cursor is closed")
    else:
        print("No active cursor")


def close_sqlite_connection(sqlite_connection):
    if sqlite_connection:
        sqlite_connection.close()
        print("The SQLite connection is closed")
    else:
        print("No active SQLite Connection")


def close_cursor_and_connection(cursor, sqlite_connection):
    close_cursor(cursor)
    close_sqlite_connection(sqlite_connection)


if __name__ == "__main__":
    shovar_list = []
    shovar1 = Shovar(12312, 1212312341, 40, datetime.now(), False, datetime.now(), datetime.now())
    shovar2 = Shovar(12312, 12112354123, 40, datetime.now(), False, datetime.now(), datetime.now())
    shovar3 = Shovar(12312, 12123123415, 40, datetime.now(), False, datetime.now(), datetime.now())
    shovar_list.append(convert_shovar_to_data_tuple(shovar1))
    shovar_list.append(convert_shovar_to_data_tuple(shovar2))
    shovar_list.append(convert_shovar_to_data_tuple(shovar3))

    new_db = create_db(appSettings.sqlite_db_name)
    cursor = create_cursor(new_db)
    create_table(cursor, "shovar")
    insert_many(new_db, cursor, "shovar", shovar_list)
    print_all_rows(cursor, "shovar")
    close_cursor_and_connection(cursor, new_db)


