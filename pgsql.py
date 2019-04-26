"""
PostgreSQL module for vishnu.
"""

import yaml
import psycopg2

config = yaml.safe_load(open("config.yaml"))


class pgSQLManagement:

    def __init__(self):
        pg_connection = config['pg_connection']
        username = pg_connection['user']
        password = pg_connection['password']
        host = pg_connection['host']
        database = pg_connection['database']
        self.conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=host)
        self.cur = self.conn.cursor()

    def create_tables(self):
        """
        Creates the tables.
        """

        # Make the table if it doesn't exist.

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS quests
        (id SERIAL PRIMARY KEY, tier VARCHAR,
        description VARCHAR, creator VARCHAR,
        completed BOOLEAN);

        CREATE TABLE IF NOT EXISTS groups
        (id SERIAL PRIMARY KEY,
        creator VARCHAR NOT NULL,
        start_date DATE NOT NULL,
        max_users VARCHAR NOT NULL,
        notes VARCHAR,
        members VARCHAR[] );
        """)

        self.conn.commit()

    def retrieve_group_info(self,
                            group_id):
        """
        Takes a given group ID and returns
        info about said group.
        """

        self.cur.execute("""
        SELECT id, max_users, members
        FROM groups
        WHERE id = %s;
        """, group_id)

        return self.cur.fetchall()

    def import_group_data(self,
                          creator,
                          start_date,
                          max_users,
                          group_notes="None"):
        """
        Takes input from app.py and imports it into the groups table.
        """

        self.cur.execute("""
        INSERT INTO groups(creator, start_date, max_users, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """, (creator, start_date, "0/{}".format(max_users), group_notes))

        group_id = self.cur.fetchone()[0]
        self.conn.commit()

        return """
        Created group with ID of {} starting on {}.
        """.format(group_id, start_date), group_id

    def retrieve_group_list(self,
                            value_id,
                            value_creator):
        """
        Takes a group ID, creator, or neither and returns
        a list of matched groups.
        """

        self.cur.execute("""
        SELECT id, creator, start_date, max_users, notes
        FROM groups
        WHERE
        (%(value_id)s is null or id = %(value_id)s) AND
        (%(value_creator)s is null or creator = %(value_creator)s);
        """,
                         {
                            'value_id': value_id,
                            'value_creator': value_creator
                         })

        results = list(self.cur.fetchall())
        return results

    def import_quest_data(self, quest_tier, quest_desc, creator):
        """
        Takes input from app.py and imports it into the quests table.
        """

        self.cur.execute(
            """
        INSERT INTO quests (tier, description, creator, completed)
        VALUES (%s, %s, %s, False);
        """, (quest_tier, quest_desc, creator))
        self.conn.commit()

    def delete_quest(self, quest_id):
        """
        Deletes a quest from the quests table.
        """
        conn = psycopg2.connect(
            dbname=self['database'],
            user=self['user'],
            password=self['password'],
            host=self['host'])
        self.cur = self.conn.cursor()

        self.cur.execute("""
        DELETE FROM quests
        WHERE id = %s;""", quest_id)
        self.conn.commit()

    def complete_quest(self, quest_id, completion):
        """
        Sets a quest as "complete"
        """

        self.cur.execute(
            """
        UPDATE quests
        SET completed = '%s'
        WHERE id = %s;
        """, (completion, quest_id))
        self.conn.commit()

    def retrieve_quest_data(self, value_id, value_tier, value_creator):
        """
        Retrieves information about a quest based on user input.
        """

        self.cur.execute("""
        SELECT id, tier, creator, description
        FROM quests
        WHERE
        completed = 'f' AND
        (%(value_id)s is null or id = %(value_id)s) AND
        (%(value_tier)s is null or tier = %(value_tier)s) AND
        (%(value_creator)s is null or creator = %(value_creator)s)
        """,
                         {'value_id': value_id,
                          'value_tier': value_tier,
                          'value_creator': value_creator})

        results = list(self.cur.fetchall())

        return results
