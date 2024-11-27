#! /usr/bin/python
# -*- coding: UTF-8 -*-
import configparser
import os.path
import sys

import pymysql
from dbutils.pooled_db import PooledDB



class DB_MySQL_Pool():
    __pool = None
    __MAX_CONNECTIONS = 100  # 创建连接池的最大数量
    __MIN_CACHED = 10  # 连接池中空闲连接的初始数量
    __MAX_CACHED = 20  # 连接池中空闲连接的最大数量
    __MAX_SHARED = 10  # 共享连接的最大数量
    __BLOCK = True  # 超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
    __MAX_USAGE = 100  # 单个连接的最大重复使用次数
    __CHARSET = 'utf8' # 连接字符集
    '''
        setsession: optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        reset: how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
    '''
    __RESET = True
    __SET_SESSION = ['SET AUTOCOMMIT = 1']  # 设置自动提交

    def __init__(self, host, port, user, password, database):
        if not self.__pool:
            self.__class__.__pool = PooledDB(creator=pymysql, host=host, port=port, user=user, password=password, database=database,
                                             maxconnections=self.__MAX_CONNECTIONS,
                                             mincached=self.__MIN_CACHED,
                                             maxcached=self.__MAX_CACHED,
                                             maxshared=self.__MAX_SHARED,
                                             blocking=self.__BLOCK,
                                             maxusage=self.__MAX_USAGE,
                                             setsession=self.__SET_SESSION,
                                             reset=self.__RESET,
                                             charset=self.__CHARSET)

    def get_connect(self):
        return self.__pool.connection()


class DB_MySQL:
    def __init__(self, host='192.168.1.117', user='root', password=None, port=3306, db='sx815v'):
        if password is None:
            config = configparser.ConfigParser()
            # 读取配置文件
            if getattr(sys, 'frozen', False):
                # 打包后的程序
                root_dir = sys._MEIPASS
            else:
                # 正常的脚本运行
                root_dir = os.path.dirname(os.path.abspath(__file__))
            config.read(os.path.join(root_dir ,'config.ini'))
            password = config.get('database', 'password')
            host = config.get('database', 'host')
            # port = config.get('database', 'port')
            user = config.get('database', 'user')
            db = config.get('database', 'db')
            # print("数据库密码为：", password)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = db
        self.connects_pool = DB_MySQL_Pool(
            host=self.__host, port=self.__port, user=self.__user, password=self.__password, database=self.__database)

    def __enter__(self):
        connect = self.connects_pool.get_connect()
        cursor = connect.cursor(pymysql.cursors.DictCursor)
        self._connect = connect
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        if exc_info[0]:
            self._connect.rollback()  # 发生异常时回滚事务
        else:
            self._connect.commit()  # 正常提交事务
        self._cursor.close()
        self._connect.close()

    def begin_transaction(self):
        self._connect.begin()

    def commit_transaction(self):
        self._connect.commit()

    def rollback_transaction(self):
        self._connect.rollback()

    def create_table(self, table_name, columns ,is_add_columns = False):
        """
        创建表
        :param table_name: 表名
        :param columns: 列名及其类型列表，例如 [('name', 'VARCHAR(255)'), 'age', 'grade']
        :param is_add_columns: 是否更新列名,不删除列民
        :return: None
        """
        # 默认列类型为 FLOAT
        default_type = 'FLOAT'

        # 生成列定义
        column_definitions = []
        for col in columns:
            if isinstance(col, tuple):
                column_definitions.append(f"{col[0]} {col[1]}")
            else:
                column_definitions.append(f"{col} {default_type}")

        # 插入主键定义
        column_definitions.insert(0, "id INT AUTO_INCREMENT PRIMARY KEY")

        # 拼接列定义字符串
        columns_str = ", ".join(column_definitions)

        # 构建 SQL 语句
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"

        # 执行 SQL 语句
        self._cursor.execute(sql)

        if is_add_columns:
            self._is_add_columns(table_name, columns)

    def _is_add_columns(self, table_name, columns):
        """
        更新表的列名
        :param table_name: 表名
        :param columns: 列名及其类型列表
        :return: None
        """
        default_type = 'FLOAT'  # 定义默认类型
        # 获取现有列名
        self._cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        existing_columns = {col['Field'] for col in self._cursor.fetchall()}

        # 生成期望的列名集合
        expected_columns = set()
        for col in columns:
            if isinstance(col, tuple):
                expected_columns.add(col[0])
            else:
                expected_columns.add(col)

        # 计算需要添加和删除的列
        columns_to_add = expected_columns - existing_columns
        columns_to_rename = existing_columns - expected_columns

        # 添加缺失的列
        for col in columns:
            if col[0] in columns_to_add:
                if isinstance(col, tuple):
                    self._cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col[0]} {col[1]}")
                else:
                    self._cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {default_type}")
        #
        # # 重命名列
        # for col in columns:
        #     if col[0] in columns_to_rename:
        #         new_col_name = col[0]
        #         old_col_name = next((c for c in existing_columns if c not in expected_columns), None)
        #         if old_col_name:
        #             col_type = col[1] if isinstance(col, tuple) else default_type
        #             self._cursor.execute(f"ALTER TABLE {table_name} CHANGE COLUMN {old_col_name} {new_col_name} {col_type}")


    # def insert_data(self, table_name, data):
    #     """
    #     插入数据
    #     :param table_name: 表名
    #     :param data: 数据字典，例如 {'name': 'Alice', 'age': 30}
    #     :return: 插入的行数
    #     """
    #     columns = ', '.join(data.keys())
    #     values = ', '.join(['%s'] * len(data))
    #     sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    #     self._cursor.execute(sql, tuple(data.values()))
    #     return self._cursor.rowcount
    def get_table_columns(self, table_name):
        """
        获取表的所有列名
        :param table_name: 表名
        :return: 列名列表
        """
        self._cursor.execute(f"DESCRIBE {table_name}")
        columns = [column['Field'] for column in self._cursor.fetchall()]
        return columns
    def add_column(self, table_name, column_name, column_type):
        """
        添加列
        :param table_name: 表名
        :param column_name: 列名
        :param column_type: 列类型
        """
        self._cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    def insert_data(self, table_name, data):
        """
        插入数据
        :param table_name: 表名
        :param data: 数据字典，例如 {'name': 'Alice', 'age': 30}
        :return: 插入的行数
        """
        existing_columns = self.get_table_columns(table_name)
        for column in data.keys():
            if column not in existing_columns:
                # 动态添加缺失的列，默认类型为 VARCHAR(255)
                self.add_column(table_name, column, 'VARCHAR(255)')
                existing_columns.append(column)

        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self._cursor.execute(sql, tuple(data.values()))
        return self._cursor.rowcount

    def bulk_insert_data(self, table_name, data_list, use_parameterized_query=True):
        """
        批量插入数据
        :param table_name: 表名
        :param data_list: 数据列表，例如 [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 35}]
        :param use_parameterized_query: 是否使用参数化查询，默认为 True
        :return: 插入的行数
        """
        if not data_list:
            return 0

        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        values = [tuple(d.values()) for d in data_list]
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        if use_parameterized_query:
            self._cursor.executemany(sql, values)
        else:
            for value in values:
                self._cursor.execute(sql, value)

        return self._cursor.rowcount

    def delete_data(self, table_name, condition):
        """
        删除数据
        :param table_name: 表名
        :param condition: 删除条件，例如 "id = 1"
        :return: 删除的行数
        """
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        self._cursor.execute(sql)
        return self._cursor.rowcount

    def update_data(self, table_name, data, condition):
        """
        更新数据
        :param table_name: 表名
        :param data: 更新的数据字典，例如 {'name': 'Bob', 'age': 35}
        :param condition: 更新条件，例如 "id = 1"
        :return: 更新的行数
        """
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self._cursor.execute(sql, tuple(data.values()))
        return self._cursor.rowcount

    def select_data(self, table_name, columns='*', condition=None, order_by_id=True):
        """
        查询数据
        :param table_name: 表名
        :param columns: 需要查询的列，默认为 '*'
        :param condition: 查询条件，例如 "id = 1"
        :param order_by_id: 是否按 id 排序，默认为 False
        :return: 查询结果列表
        """
        if isinstance(columns, list):
            columns = ', '.join(columns)

        sql = f"SELECT {columns} FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        if order_by_id:
            sql += " ORDER BY id"

        self._cursor.execute(sql)
        return self._cursor.fetchall()


    def get_last_record(self, table_name):
        """
        获取表中的最新记录
        :param table_name: 表名
        :return: 最新记录的字典
        """
        sql = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1"
        self._cursor.execute(sql)
        return self._cursor.fetchone()

    def truncate_table(self, table_name):
        """
        清空表
        :param table_name: 表名
        :return: None
        """
        sql = f"TRUNCATE TABLE {table_name}"
        self._cursor.execute(sql)

    @property
    def cursor(self):
        return self._cursor



if __name__ == "__main__":
    db = DB_MySQL()
    with db:
        # 创建表
        columns = [
            ('name', 'VARCHAR(255)'),
            'age',
            'grade'  # 这里没有指定类型，默认为 FLOAT
        ]
        db.create_table('test',columns)

        # # 插入数据
        # db.insert_data('test', {'a': 30, 'b': 30})
        # db.insert_data('test', {'a': 40, 'b': 40})
        #
        # # 删除数据
        # db.delete_data('test', 'a = 30')
        #
        # # 更新数据
        # db.update_data('test', {'a': 30, 'b': 30}, 'id = 1')
        #
        # # 查询所有数据
    with db:
        result = db.select_data('test')
        print(result)
