import aiomysql
import aiomysql.cursors
import pymysql.converters

from typing import Optional, Union, Any, List


class Database:
    def __init__(
            self,
            ip_address: str = 'localhost',
            port: int = 3306,
            user: str = "root",
            password: str = "",
            database: str = "",
            charset: str = "utf8"
    ):
        self.ip_address = ip_address
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset

        self.connection: Optional[aiomysql.Connection] = None
        self.is_connect = False
        self.is_commit = False

    @classmethod
    def connect_inject(cls, connection: aiomysql.Connection):
        new_cls = cls(
            ip_address=connection.host,
            port=connection.port,
            user=connection.user,
            password=getattr(connection, "_password"),
            database=connection.db,
            charset=connection.charset
        )
        new_cls.connection = connection
        new_cls.is_connect = True
        return

    async def connect(self) -> aiomysql.Connection:
        connection = self.connection = await aiomysql.connect(
            host=self.ip_address,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            charset=self.charset
        )
        self.is_connect = True
        return connection

    async def close(self, check_commit: bool = True):
        if not self.is_connect:
            return

        if check_commit and not self.is_commit:
            await self.commit()
        self.connection.close()
        self.is_connect = False
        return

    async def commit(self):
        if not self.is_connect:
            return
        await self.connection.commit()
        self.is_commit = True
        return

    async def get_cursor(self, cursor: Any) -> Optional[aiomysql.cursors.Cursor]:
        if not self.is_connect:
            return
        return await self.connection.cursor(cursor)

    @staticmethod
    def _get_table(
            table: Union[type, str]
    ):
        cls = None
        if not isinstance(table, str):
            cls = table
            table = getattr(table, "__tablename__")
        return cls, table

    async def _query_base(
            self,
            table: Union[classmethod, str],
            key_name: str = 'id',
            key: Union[int, str, list, tuple] = None,
            fetch_all: bool = False,
            filter_col: List[str] = None,
            similar: bool = False,
            default: Any = None
    ):
        single_connect = False
        if not self.is_connect:
            await self.connect()
            single_connect = True
        cursor = await self.get_cursor(aiomysql.cursors.DictCursor)
        cls, table = self._get_table(table)

        if filter_col is None:
            _filter_col = "*"
        else:
            _filter_col = ",".join(filter_col)

        if key is None:
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1}".format(_filter_col, table))
            await cursor.execute(sql_command)
        elif isinstance(key, list) or isinstance(key, tuple):
            if not self.is_exist(table=table, key=key, key_name=key_name):
                return default
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE FIND_IN_SET({2}, %s)".format(
                _filter_col, table, key_name
            ))
            await cursor.execute(sql_command, ",".join(key))
        elif similar:
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE {2} LIKE %s".format(
                _filter_col, table, key_name
            ))
            await cursor.execute(sql_command, key)
        else:
            if not self.is_exist(table=table, key=key, key_name=key_name):
                return default
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE {2}=%s".format(
                _filter_col, table, key_name
            ))
            await cursor.execute(sql_command, key)

        if not fetch_all:
            result = await cursor.fetchone()
        else:
            result = await cursor.fetchall()

        if cls is not None:
            if isinstance(result, list):
                return [cls(x) for x in result]
            else:
                return cls(result)
        if single_connect:
            await self.close(check_commit=False)
        return result

    def query(
            self,
            table: Union[classmethod, str],
            key_name: str = 'id',
            key: Union[int, str, list, tuple] = None,
            filter_col: List[str] = None,
            similar: bool = False,
            default: Any = None
    ):
        return self._query_base(
            fetch_all=False,
            table=table,
            key_name=key_name,
            key=key,
            filter_col=filter_col,
            similar=similar,
            default=default
        )

    def query_all(
            self,
            table: Union[classmethod, str],
            key_name: str = 'id',
            key: Union[int, str, list, tuple] = None,
            filter_col: List[str] = None,
            similar: bool = False,
            default: Any = None
    ):
        return self._query_base(
            fetch_all=True,
            table=table,
            key_name=key_name,
            key=key,
            filter_col=filter_col,
            similar=similar,
            default=default
        )

    async def is_exist(
            self,
            table: Union[classmethod, str],
            key: Union[int, str, list, tuple],
            key_name: str = 'id'
    ) -> bool:
        single_connect = False
        if not self.is_connect:
            await self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = await self.get_cursor(aiomysql.cursors.DictCursor)
        if isinstance(key, list) or isinstance(key, tuple):
            sql_command = pymysql.converters.escape_string(
                "SELECT EXISTS (SELECT * FROM {0} WHERE {1} IN (%s)) as success".format(table, key_name)
            )
            await cursor.execute(sql_command, ",".join(key))
        else:
            sql_command = pymysql.converters.escape_string(
                "SELECT EXISTS (SELECT * FROM {0} WHERE {1}=%s) AS success".format(table, key_name)
            )
            await cursor.execute(sql_command, key)
        tf = (await cursor.fetchone()).get('success', False)
        if single_connect:
            await self.close(check_commit=False)
        return bool(tf)

    async def insert(
            self,
            table: Union[str, Any],
            value: dict = None
    ):
        single_connect = False
        if not self.is_connect:
            await self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = await self.get_cursor(aiomysql.cursors.DictCursor)
        if isinstance(table, str) and value is None:
            return TypeError("Insert data class or data in value")

        if value is None:
            value = table.__dict__

        setup = [name for name in value.keys()]
        args = []
        for d in value.keys():
            args.append(value.get(d))

        sql_command = pymysql.converters.escape_string(
            "INSERT INTO {0}({1}) VALUE ({2})".format(table, ', '.join(setup), ', '.join(["%s" * len(args)]))
        )
        await cursor.execute(sql_command, tuple(args))
        self.is_commit = False
        if single_connect:
            await self.close(check_commit=True)
        return

    async def update(
            self,
            table: Union[str, Any],
            key: Union[int, str, list, tuple],
            key_name: str = 'id',
            value: dict = None
    ):
        single_connect = False
        if not self.is_connect:
            await self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = await self.get_cursor(aiomysql.cursors.DictCursor)
        if isinstance(table, str) and value is None:
            return TypeError("Insert data class or data in value")

        if not self.is_exist(table, key, key_name):
            value[key_name] = key
            await self.insert(table, value)
        else:
            if value is None:
                value = table.__dict__

            setup = [f"{name}=%s" for name in value.keys()]
            args = []
            for d in value.keys():
                args.append(value.get(d))
            args.append(key)
            sql_command = pymysql.converters.escape_string(
                "UPDATE {0} SET {1} WHERE {2}=%s".format(table, ",".join(setup), key_name)
            )
            await cursor.execute(sql_command, tuple(args))
        self.is_commit = False
        if single_connect:
            await self.close(check_commit=True)
        return

    async def delete(
            self,
            table: str,
            key: Union[int, str, list, tuple] = None,
            key_name: str = 'id',
            force_delete: bool = False
    ):
        single_connect = False
        if not self.is_connect:
            await self.connect()
            single_connect = True
        cursor = await self.get_cursor(aiomysql.cursors.DictCursor)
        if key is None:
            sql_command = pymysql.converters.escape_string("DELETE FROM {0}".format(table))
            await cursor.execute(sql_command)
        elif isinstance(key, list) or isinstance(key, tuple):
            sql_command = pymysql.converters.escape_string("DELETE FROM {0} WHERE FIND_IN_SET({1}, %s)".format(
                table, key_name
            ))
            if not self.is_exist(table=table, key=key, key_name=key_name) and not force_delete:
                return
            await cursor.execute(sql_command, ",".join(key))
        else:
            sql_command = pymysql.converters.escape_string("DELETE FROM {0} WHERE {1}=%s".format(table, key_name))
            if not self.is_exist(table=table, key=key, key_name=key_name) and not force_delete:
                return
            await cursor.execute(sql_command, key)
        self.is_commit = False
        if single_connect:
            await self.close(check_commit=True)
        return
