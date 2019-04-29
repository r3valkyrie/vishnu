"""
PostgreSQL module for vishnu.
"""

import yaml
import asyncpg
import datetime

config = yaml.safe_load(open("config.yaml"))


class pgSQLManagement:

    async def connect(self):
        pg_connection = config['pg_connection']
        username = pg_connection['user']
        password = pg_connection['password']
        host = pg_connection['host']
        database = pg_connection['database']
        self.conn = await asyncpg.connect(
            database=database,
            user=username,
            password=password,
            host=host)
        self.tr = self.conn.transaction()
        await self.tr.start()

    async def create_tables(self):
        """
        Creates the tables.
        """

        await self.connect()

        # Make the table if it doesn't exist.

        await self.conn.execute("""
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

        await self.tr.commit()

    async def retrieve_group_info(self,
                                  group_id):
        """
        Takes a given group ID and returns
        info about said group.
        """

        await self.connect()

        group = list(await self.conn.fetch("""
        SELECT id, max_users, members, creator
        FROM groups
        WHERE id = $1""", int(group_id)))

        return group

    async def join_group(self,
                         group_id,
                         author,
                         new_max):
        """
        Allows a member to join a group if it's not full.
        """

        await self.connect()

        await self.conn.execute("""
        UPDATE groups
        SET members =
        array_append(members, $1)
        WHERE id = $2;
        """, author, int(group_id))

        await self.conn.execute("""
        UPDATE groups
        SET max_users = $1
        WHERE id = $2;
        """, new_max, int(group_id))

        await self.tr.commit()

    async def import_group_data(self,
                                creator,
                                start_date,
                                max_users,
                                group_notes="None"):
        """
        Takes input from app.py and imports it into the groups table.
        """

        await self.connect()

        # Convert date string to datetime
        date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

        group_id = await self.conn.fetchval("""
        INSERT INTO groups(creator, start_date, max_users, notes)
        VALUES ($1::varchar, $2::date, $3::varchar, $4::varchar)
        RETURNING id;
        """, creator, date, "0/{}".format(max_users), group_notes)

        await self.tr.commit()

        return """
        Created group with ID of {} starting on {}.
        """.format(group_id, start_date), group_id

    async def retrieve_group_list(self,
                                  value_id,
                                  value_creator):
        """
        Takes a group ID, creator, or neither and returns
        a list of matched groups.
        """

        await self.connect()

        results = list(await self.conn.fetch("""
        SELECT id, creator, start_date, max_users, notes
        FROM groups
        WHERE
        ($1::integer is null or id = $1::integer) AND
        ($2::varchar is null or creator = $2::varchar);
        """, value_id, value_creator))

        return results

    async def delete_group(self,
                           group_id):
        """
        Allows a DM to delete a group from
        the database after closing it.
        """

        await self.connect()

        await self.conn.execute("""
        DELETE FROM groups
        WHERE id = $1;
        """, int(group_id))

        await self.tr.commit()

    async def import_quest_data(self, quest_tier, quest_desc, creator):
        """
        Takes input from app.py and imports it into the quests table.
        """

        await self.connect()

        await self.conn.execute(
            """
        INSERT INTO quests (tier, description, creator, completed)
        VALUES ($1, $2, $3, False);
        """, quest_tier, quest_desc, creator)

        await self.tr.commit()

    async def delete_quest(self, quest_id):
        """
        Deletes a quest from the quests table.
        """

        await self.connect()

        await self.conn.execute("""
        DELETE FROM quests
        WHERE id = $1;""", int(quest_id))

        await self.tr.commit()

    async def complete_quest(self, quest_id, completion):
        """
        Sets a quest as "complete"
        """

        await self.connect()

        await self.conn.execute(
            """
        UPDATE quests
        SET completed = $1::bool
        WHERE id = $2::integer;
        """, completion, int(quest_id))

        await self.tr.commit()

    async def retrieve_quest_data(self, value_id, value_tier, value_creator):
        """
        Retrieves information about a quest based on user input.
        """

        await self.connect()

        if value_id is not None:
            id = int(value_id)
        else:
            id = None

        results = list(await self.conn.fetch("""
        SELECT id, tier, creator, description
        FROM quests
        WHERE
        completed = 'f' AND
        ($1::integer is null or id = $1::integer) AND
        ($2::varchar is null or tier = $2::varchar) AND
        ($3::varchar is null or creator = $3::varchar)
        """, id, value_tier, value_creator))

        return results
