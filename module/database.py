import pymysql
import pymysql.cursors
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

        self.connection: Optional[pymysql.Connection] = None
        self.is_connect = False
        self.is_commit = False

    def connect(self) -> pymysql.Connection:
        connection = self.connection = pymysql.connect(
            host=self.ip_address, port=self.port, user=self.user, password=self.password, database=self.database,
            charset=self.charset
        )
        self.is_connect = True
        return connection

    def close(self, check_commit: bool = True):
        if not self.is_connect:
            return

        if check_commit and not self.is_commit:
            self.commit()
        self.connection.close()
        self.is_connect = False
        return

    def commit(self):
        if not self.is_connect:
            return
        self.connection.commit()
        self.is_commit = True
        return

    def get_cursor(self, cursor: Any) -> Optional[pymysql.cursors.Cursor]:
        if not self.is_connect:
            return
        return self.connection.cursor(cursor)

    @staticmethod
    def _get_table(
            table: Union[type, str]
    ):
        cls = None
        if not isinstance(table, str):
            cls = table
            table = getattr(table, "__tablename__")
        return cls, table

    def _query_base(
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
            self.connect()
            single_connect = True
        cursor = self.get_cursor(pymysql.cursors.DictCursor)
        cls, table = self._get_table(table)

        if filter_col is None:
            _filter_col = "*"
        else:
            _filter_col = ",".join(filter_col)

        if key is None:
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1}".format(_filter_col, table))
            cursor.execute(sql_command)
        elif isinstance(key, list) or isinstance(key, tuple):
            if not self.is_exist(table=table, key=key, key_name=key_name):
                return default
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE FIND_IN_SET({2}, %s)".format(
                _filter_col, table, key_name
            ))
            cursor.execute(sql_command, ",".join(key))
        elif similar:
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE {2} LIKE %s".format(
                _filter_col, table, key_name
            ))
            cursor.execute(sql_command, key)
        else:
            if not self.is_exist(table=table, key=key, key_name=key_name):
                return default
            sql_command = pymysql.converters.escape_string("SELECT {0} FROM {1} WHERE {2}=%s".format(
                _filter_col, table, key_name
            ))
            cursor.execute(sql_command, key)

        if not fetch_all:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

        if cls is not None:
            if isinstance(result, list):
                return [cls(x) for x in result]
            else:
                return cls(result)
        if single_connect:
            self.close(check_commit=False)
        return result

    def query(self, **kwargs):
        return self._query_base(
            fetch_all=False, **kwargs
        )

    def query_all(self, **kwargs):
        return self._query_base(
            fetch_all=True, **kwargs
        )

    def is_exist(
            self,
            table: Union[classmethod, str],
            key: Union[int, str, list, tuple],
            key_name: str = 'id'
    ) -> bool:
        single_connect = False
        if not self.is_connect:
            self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        if isinstance(key, list) or isinstance(key, tuple):
            sql_command = pymysql.converters.escape_string(
                "SELECT EXISTS (SELECT * FROM {0} WHERE {1} IN (%s)) as success".format(table, key_name)
            )
            cursor.execute(sql_command, ",".join(key))
        else:
            sql_command = pymysql.converters.escape_string(
                "SELECT EXISTS (SELECT * FROM {0} WHERE {1}=%s) AS success".format(table, key_name)
            )
            cursor.execute(sql_command, key)
        tf = cursor.fetchone().get('success', False)
        if single_connect:
            self.close(check_commit=False)
        return bool(tf)

    def insert(
            self,
            table: Union[str, Any],
            value: dict = None
    ):
        single_connect = False
        if not self.is_connect:
            self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
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
        cursor.execute(sql_command, tuple(args))
        self.is_commit = False
        if single_connect:
            self.close(check_commit=True)
        return

    def update(
            self,
            table: Union[str, Any],
            key: Union[int, str, list, tuple],
            key_name: str = 'id',
            value: dict = None
    ):
        single_connect = False
        if not self.is_connect:
            self.connect()
            single_connect = True
        cls, table = self._get_table(table)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        if isinstance(table, str) and value is None:
            return TypeError("Insert data class or data in value")

        if not self.is_exist(table, key, key_name):
            value[key_name] = key
            self.insert(table, value)
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
            cursor.execute(sql_command, tuple(args))
        self.is_commit = False
        if single_connect:
            self.close(check_commit=True)
        return

    def delete(
            self,
            table: str,
            key: Union[int, str, list, tuple] = None,
            key_name: str = 'id',
            force_delete: bool = False
    ):
        single_connect = False
        if not self.is_connect:
            self.connect()
            single_connect = True
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        if key is None:
            sql_command = pymysql.converters.escape_string("DELETE FROM {0}".format(table))
            cursor.execute(sql_command)
        elif isinstance(key, list) or isinstance(key, tuple):
            sql_command = pymysql.converters.escape_string("DELETE FROM {0} WHERE FIND_IN_SET({1}, %s)".format(
                table, key_name
            ))
            if not self.is_exist(table=table, key=key, key_name=key_name) and not force_delete:
                return
            cursor.execute(sql_command, ",".join(key))
        else:
            sql_command = pymysql.converters.escape_string("DELETE FROM {0} WHERE {1}=%s".format(table, key_name))
            if not self.is_exist(table=table, key=key, key_name=key_name) and not force_delete:
                return
            cursor.execute(sql_command, key)
        self.is_commit = False
        if single_connect:
            self.close(check_commit=True)
        return
