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

    cur.execute(
        """
    UPDATE quests
    SET completed = '%s'
    WHERE id = %s;
    """, (completion, quest_id))
    conn.commit()
    cur.close()
    conn.close()


def retrieve_quest_data(pg_connection, value_id, value_tier, value_creator):
    conn = psycopg2.connect(
        dbname=pg_connection['database'],
        user=pg_connection['user'],
        password=pg_connection['password'],
        host=pg_connection['host'])
    cur = conn.cursor()

    query = """
    SELECT id, tier, creator, description
    FROM quests
    WHERE
    completed = 'f' AND
    (%(value_id)s is null or id = %(value_id)s) AND
    (%(value_tier)s is null or tier = %(value_tier)s) AND
    (%(value_creator)s is null or creator = %(value_creator)s)
    """
    cur.execute(query,
                {'value_id': value_id,
                 'value_tier': value_tier,
                 'value_creator': value_creator}
    )

    print(value_id)
    print(value_tier)
    print(value_creator)
    print(query)
    results = list(cur.fetchall())

    cur.close()
    conn.close()
    return results
