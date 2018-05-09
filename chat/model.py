import aiosqlite
import settings
import hashlib

class InitDB():
    def __init__(self):
        self.db_file = settings.DB_FILE

    async def createdb(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                "create table if not exists users "
                "("
                "id integer primary key asc, "
                "username varchar(50), password varchar(50),"
                "email varchar(50)"
                ")"
            )

        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                "create table if not exists msg "
                "("
                "id integer primary key asc, "
                "user_id integer, created_at datetime,"
                "msg text"
                ")"
            )

class User():
    def __init__(self):
        self.db_file = settings.DB_FILE


    async def check_user(self, username):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("select * from users where username = '{}'".format(username))
            rows = await cursor.fetchone()
            await cursor.close()
            return rows

    async def create_user(self, data):
        result = False
        user = await self.check_user(data.get('username'))

        if not user and data.get('username'):
            async with aiosqlite.connect(self.db_file) as db:
                password = hashlib.md5(data.get('password').encode('utf-8')).hexdigest()
                results = await db.execute("insert into users (username, password, email) "
                                           "values (?, ?, ?)",
                                 [data.get('username'), password,
                                  data.get('email')])
                await db.commit()
                if results.lastrowid:
                    result = await self.get_login_user(results.lastrowid)
                await results.close()

        return result

    async def login_user(self, username, password):
        async with aiosqlite.connect(self.db_file) as db:
            password = hashlib.md5(password.encode('utf-8')).hexdigest()
            cursor = await db.execute("select * from users where username = '{0}' "
                                      "and password = '{1}'".format(username, password))

            rows = await cursor.fetchone()
            await cursor.close()
            return rows


    async def get_login_user(self, user_id):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("select * from users where id = {0}".format(user_id))
            rows = await cursor.fetchone()
            await cursor.close()
            return rows

class Message:
    def __init__(self):
        self.db_file = settings.DB_FILE

    async def save_msg(self, data):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("insert into msg (user_id, created_at, msg) "
                             "values (?, ?, ?)",
                             [data.get('user_id'), data.get('created_at'),
                              data.get('msg')])
            await db.commit()

    async def load_msg(self):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("SELECT users.username, msg.created_at, msg.msg FROM users"
                                      " inner join msg ON users.id = msg.user_id limit {0} OFFSET"
                                      " (SELECT COUNT(*) FROM msg)-{0};".format(settings.MAX_MSG))
            rows = await cursor.fetchall()
            await cursor.close()
            return rows
