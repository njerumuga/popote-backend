import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    # Connect to default postgres db
    con = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='0000')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Create the actual project database
    cur.execute('CREATE DATABASE popote_db')
    cur.close()
    con.close()
    print("Database popote_db created successfully!")


if __name__ == "__main__":
    create_database()