import asyncio
import datetime
import random
import time

import asyncpg

class Database:
    async def connect(self, **kwargs):
        self.conn = await asyncpg.connect(**kwargs)

    async def new_project(self, pname, slug='', icon='', ratelimit=0,
                            public=False, paused=True, min_pipeline_version=0):

        await self.conn.execute("""
        	INSERT INTO projects (name, slug, icon_uri, ratelimit,
                                    min_pipeline_version, public, paused)
            VALUES($1, $2, $3, $4, $5, $6, $7);
        """, pname, slug, icon, ratelimit, min_pipeline_version,
        public, paused)

    async def queue_item(self, project, item,
                        expected_duration=datetime.timedelta(days=1), priority=1):

        await self.conn.execute("""
        	INSERT INTO items (project, item, status, expected_duration, priority)
            VALUES($1, $2, 'should_handout', $3, $4);
        """, project, str(item), expected_duration, priority)

    async def get_item(self, project, username, script_version):
        async with self.conn.transaction():
            item = dict(await self.conn.fetchrow("""
                SELECT * FROM items WHERE status = 'should_handout'
                AND project = $1
                ORDER BY priority
                LIMIT 1;
            """, project))

            await self.conn.execute("""
                INSERT INTO handouts (item_id, status, username, script_version)
                VALUES($1, 'in_progress', $2, $3);
            """, item['id'], username, script_version)

            await self.conn.execute("""
                UPDATE items
                SET status = 'handed_out'
                WHERE project = $1 AND id = $2;
            """, project, item['id'])

        return (item['item'], item['id'])

    async def heartbeat(self, id):
        await self.conn.execute("""
            UPDATE handouts
            SET last_heartbeat = now()
            WHERE item_id = $1;
        """, id)

    async def set_handout_status(self, id, status):
        async with self.conn.transaction():
            if status == 'abandoned':
                await self.conn.execute("""
                    UPDATE items
                    SET status = 'should_handout'
                    WHERE id = $2;
                """, id)

            if status == 'succeeded':
                await self.conn.execute("""
                    UPDATE items
                    SET status = 'succeeded'
                    WHERE id = $1;
                """, id)

            await self.conn.execute("""
                UPDATE handouts
                SET status = $1
                WHERE item_id = $2;
            """, status, id)


    async def count_items(self, project, status):
        record = await self.conn.fetchrow("""
            SELECT COUNT(*) FROM items
            WHERE project = $1 AND status = $2;
        """, project, status)

        return int(record[0])

    async def create_account(self, username, hash):
        await self.conn.execute("""
            INSERT INTO accounts (username, password_hash)
            VALUES($1, $2);
        """, username, hash)

    async def get_hash(self, username):
        record = await self.conn.fetchrow("""
            SELECT password_hash FROM accounts
            WHERE username = $1;
        """, username)

        return str(record[0])

    async def change_password(self, username, newpass):
        await self.conn.execute("""
            UPDATE accounts
            SET password_hash = $1
            WHERE username = $2;
        """, newpass, username)

    async def delete_account(self, username):
        await self.conn.execute("""
            DELETE FROM accounts
            WHERE username = $1;
        """, username)


async def async_test():
    """Very ugly test to use while getting this working"""

    print('Connecting to db')
    db = Database()
    await db.connect(user='postgres', password='12345',
                database='tracker', host='localhost')

    print('Removing old data')
    await db.conn.execute("""
        DELETE FROM sessions;
        DELETE FROM accounts;
        DELETE FROM handouts;
        DELETE FROM items;
        DELETE FROM projects;
        ALTER SEQUENCE items_id_seq RESTART WITH 1;
    """)

    print('testing db.new_project')
    await db.new_project('test')

    print('testing db.queue_item')
    for i in range(1000):
        await db.queue_item('test', i)

    out_items = []

    print('testing db.get_item')
    for i in range(250):
        item = await db.get_item('test', 'LowLevel_M', 'testver')
        out_items.append(item)

    print('testing db.count_items')
    print(await db.count_items('test', 'handed_out'))

    print('testing db.heartbeat')
    for i in out_items:
        if random.randrange(5) == 3:
            await db.heartbeat(i[1])

    print('testing db.set_handout_status')
    for i in out_items:
        await db.set_handout_status(i[1], 'succeeded')

    print('testing db.create_account')
    await db.create_account('LowLevel_M', 'TestHash')

    print('testing db.get_hash')
    print(await db.get_hash('LowLevel_M'))

    print('testing db.change_password')
    print('Oldpass:', await db.get_hash('LowLevel_M'))
    await db.change_password('LowLevel_M', 'NewTestHash')
    print('Newpass:', await db.get_hash('LowLevel_M'))

    print('testing db.delete_account')
    await db.delete_account('LowLevel_M')


asyncio.run(async_test())
