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
    CREATE TABLE IF NOT EXISTS quests
    (id SERIAL PRIMARY KEY, tier VARCHAR, description VARCHAR, creator VARCHAR, completed BOOLEAN);
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

    cur.execute(
        """
    INSERT INTO quests (tier, description, creator, completed)
    VALUES (%s, %s, %s, False);
    """, (quest_tier, quest_desc, creator))
    conn.commit()
    cur.close()
    conn.close()


def delete_quest(pg_connection, quest_id):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM quests
    WHERE id = %s;""", quest_id)
    conn.commit()
    cur.close()
    conn.close()

def complete_quest(pg_connection, quest_id, completion):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    UPDATE quests
    SET completed = '%s'
    WHERE id = %s;
    """, (completion, quest_id))
    conn.commit()
    cur.close()
    conn.close()

def retrieve_quest_data(pg_connection, idformat, tierformat, creatorformat):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    cur.execute("""
    SELECT id, tier, creator, description FROM quests
    WHERE completed = 'f'
    %s
    %s
    %s;
    """, (idformat, tierformat, creatorformat))

    results = list(cur.fetchall())

    cur.close()
    conn.close()
    return results
