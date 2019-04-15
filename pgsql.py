"""
PostgreSQL module for vishnu.
"""

import yaml, psycopg2


def create_tables(pg_connection):

    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    # Make the table if it doesn't exist.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vishnu_quests
    (id SERIAL PRIMARY KEY, tier INTEGER, description VARCHAR, creator VARCHAR, completed BOOLEAN);
    """)
    conn.commit()
    cur.close()
    conn.close()

def import_quest_data(pg_connection, quest_tier, quest_desc, creator):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO vishnu_quests (tier, description, creator, completed)
    VALUES (%s, %s, %s, False);
    """,
    (quest_tier, quest_desc, creator)
    )
    conn.commit()
    cur.close()
    conn.close()

def retrieve_quest_data(pg_connection, quest_id):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM vishnu_quests
    WHERE id = %s and completed = 'f';
    """, quest_id)

    results = list(cur.fetchall()[0])

    cur.close()
    conn.close()
    return results

def retrieve_all_quests(pg_connection):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM vishnu_quests
    WHERE completed = 'f';
    """)

    results = cur.fetchall()

    cur.close()
    conn.close()
    return results
