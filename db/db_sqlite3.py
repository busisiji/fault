# !/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sqlite3
import configparser

from lib.data import adapt_JSON

import pymysql
import traceback
from time import sleep

'''
数据库操作简易封装
'''


class MySqlite3():
    def __init__(self, db_name=None):
        """
        创建数据集

        :param db_name: 数据库名称
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name if db_name else 'database.db',check_same_thread=False)
        self.cursor = self.conn.cursor()
        # print("初始化打开数据库成功")
    def tolist(self,names):
        '""转换为list类型的数据'
        try:
            if not isinstance(names, list):
                names = [names]
            return names
        except:
            return None

    def create_tables(self, table_name: str, field_list: list) -> bool:
        """
        创建表格

        :param table_name: 表名
        :param field_list: 字段列表,例如：["name","age","gender"]
        :return:
        """
        try:
            fields = ",".join([field + " TEXT" for field in field_list])
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields});"
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            print("创建表出错，错误信息：", str(ex))
            return False

    def create_table_majorkey(self, table_name: str, name:str,field_list: list) -> bool:
        """
        创建表格,主键自增

        :param table_name: 表名
        :param name: 自增主键名
        :param field_list: 字段列表,例如：["age","gender"]
        :return:
        """
        try:
            fields = ",".join([field + " TEXT" for field in field_list])
            # sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields});"
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({name} INTEGER PRIMARY KEY AUTOINCREMENT, {fields});"
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            print("创建表出错，错误信息：", str(ex))
            return False

    def create_table_primary(self, table_name: str,field_list: list=['name'],name:str='id') -> bool:
        """
        创建表格,设置主键

        :param table_name: 表名
        :param name: 主键名
        :param field_list: 字段列表,例如：["age","gender"]
        :return:
        """
        try:
            fields = ",".join([field + " TEXT" for field in field_list])
            # sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields});"
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({name} INTEGER PRIMARY KEY, {fields});"
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            print("创建表出错，错误信息：", str(ex))
            return False

    # def create_table_cascade(self, table_name: str,main_table_name:str,field_list: list=['name'],name:str='id',main_name:str='id') -> bool:
    #     """
    #     创建表格,设置外键与主键级联
    #
    #     :param table_name: 表名
    #     :param main_table_name: 主表名
    #     :param field_list: 字段列表,例如：["age","gender"]
    #     :param name: 外键名
    #     :param main_name: 主表主键名
    #     :return:
    #     """
    #     try:
    #         fields = ",".join([field + " TEXT" for field in field_list])
    #         sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields} , {name} INTEGER PRIMARY KEY , FOREIGN KEY ({name}) REFERENCES {main_table_name}({main_name}) ON UPDATE CASCADE);"
    #         self.cursor.execute(sql)
    #         # sql = f"CREATE TRIGGER 更新{table_name} AFTER UPDATE OF {name} ON 主表 BEGIN UPDATE {table_name} SET {name} = NEW.{main_name} WHERE {name} = OLD.{main_name}"
    #         # self.cursor.execute(sql)
    #         self.conn.commit()
    #         return True
    #     except Exception as ex:
    #         print("创建表出错，错误信息：", str(ex))
    #         return False

    def update_table_name(self,table_name,new_table_name):
        """更改表名"""
        try:
            sql = f'ALTER TABLE {table_name} RENAME TO {new_table_name}'
            self.cursor.execute(sql)
        except Exception as ex:
            print("更改表名出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()


    def add_column(self,table_name,names):
        """增加新列"""
        try:
            if isinstance(names, list):
                for name in names:
                    # 序列化要插入单元格的列表
                    name = adapt_JSON(name)
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {name} TEXT"
                    self.cursor.execute(sql)
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {names} TEXT"
                self.cursor.execute(sql)
        except Exception as ex:
            print("增加列出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()

    def insert_data(self, table_name: str, data:str, key:str = "name" ) -> bool:
        '''
        插入数据，根据传入的数据类型进行判断，自动选者插入方式

        :param table_name: 表名
        :param data: 要插入的数据 list/dict
        :param key: 主键
        '''
        try:
            if isinstance(data, list):
                for item in data:
                    # 同名行更新
                    if key in item:
                        result = self.query_colum(table_name, item[key], key)
                        if result:
                            self.update_data_row(table_name, item[key], item,key)
                            continue

                    keys = ",".join(list(item.keys()))
                    values = ",".join([f'"{x}"'  for x in list(item.values())])
                    sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values});"
                    self.cursor.execute(sql)
            elif isinstance(data, dict):
                # 同名行更新
                if key in data:
                    result = self.query_colum(table_name, data[key], key)
                    if result:
                        self.update_data_row(table_name, data[key], data,key)
                        return True
                # 序列化要插入单元格的列表
                for key in data.keys():
                    data[key] = adapt_JSON(data[key])
                # keys = ",".join(list(data.keys()))
                # values = ",".join([f'"{x}"' for x in list(data.values())])
                # sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values});"
                # self.cursor.execute(sql)

                # INSERT
                sql = f'INSERT INTO {table_name} '
                keys = ",".join(list(data.keys()))
                string = "(" + ", ".join(["?"] * len(list(data.keys()))) + ")"
                sql += f'({keys}) VALUES {string}'
                # INSERT
                self.cursor.execute(sql, list(data.values()))
            return True
        except Exception as ex:
            print("插入数据出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()

    def update_data_row(self, table_name: str, name:str, data, key:str = "name" ,isUpKey=False) -> bool:
        '''
        更新行数据，根据传入的数据类型进行判断，自动选者插入方式

        :param table_name: 表名
        :param name: 主键值
        :param data: 要更新的数据 list/dict
        :param key : 主键
        '''
        try:
            # if not isinstance(name, str):
            #     return False
            newdata = ''

            if isinstance(data, list):
                name = "'" + name + "'"
                for item in data:
                    keys = list(item.keys())
                    values = list(item.values())
                    for i in range(len(keys)):
                        value = str(values[i])
                        newdata = newdata + '"' + str(keys[i]) + '" = "' + value + '"'
                        if i != len(keys) - 1:
                            newdata = newdata + ' , '
                    sql = f"UPDATE {table_name} SET {newdata} WHERE {key} = {name};"
                    self.cursor.execute(sql)
            elif isinstance(data, dict):
                # 定义要更新的行的条件
                condition = {key: name}
                # 序列号要插入单元格的列表
                for i in data.keys():
                    data[i] = adapt_JSON(data[i])
                if not isUpKey:
                    del data[key]
                    if not data:
                        return True
                # 构建UPDATE语句
                sql = f'UPDATE {table_name} SET '
                sql += ', '.join([f'{key} = ?' for key in data.keys()])
                sql += ' WHERE '
                sql += ' AND '.join([f'{key} = ?' for key in condition.keys()])
                # 执行UPDATE语句
                self.cursor.execute(sql, list(data.values()) + list(condition.values()))
            return True
        except Exception as ex:
            print("更新数据出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()

    def update_data(self, table_name,keys,datas,newdatas) -> list:
        """
        更新数据
        :param table_name: 表名
        :param key: 键名
        :param data: 原来的数据
        :param newdata: 更新的数据
        :return:
        """
        try:
            sql_set = ""
            sql_where = ""
            datas = self.tolist(datas)
            keys = self.tolist(keys)
            newdatas = self.tolist(newdatas)
            if len(datas) != len(keys) and len(datas) != len(newdatas):
                return False
            for i in range(len(keys)):
                key = str(keys[i])
                newdata = str(newdatas[i])
                newdata = "'" + newdata + "'"
                sql_set = sql_set + f"{key} = {newdata}"
                if i < len(keys) - 1:
                    sql_set = sql_set + "AND"
            for i in range(len(keys)):
                key = str(keys[i])
                data = str(datas[i])
                data = "'" + data + "'"
                sql_where = sql_where + f"{key} = {data}"
                if i < len(keys) - 1:
                    sql_where = sql_where + "AND"
            sql = f"UPDATE {table_name} SET " + sql_set + f" WHERE " + sql_where
            # sql = f"UPDATE {table_name} SET {key} = '{newdata}' WHERE {key} = '{data}';"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as ex:
            return []
        finally:
            self.conn.commit()

    def update_data_if(self, table_name:str,keys:tuple,datas:tuple,sql_where:str) -> list:
        """
        条件更新数据
        :param table_name: 表名
        :param keys: 要更新的列名
        :param datas: 更新的数据
        :param sql_where: 更新的条件
        :return:
        """
        try:
            if isinstance(datas, str) or isinstance(datas, int) or isinstance(datas, list):
                datas = (datas,)
            if isinstance(keys, str) or isinstance(keys, int):
                keys = (keys,)
            datas = self.listIntuple_to_JSON(datas)
            # UPDATE
            sql = f'UPDATE {table_name}'
            sql += ' SET '
            sql += ', '.join([f'{key} = ?' for key in keys])
            sql += ' WHERE '
            sql += sql_where
            self.cursor.execute(sql, datas)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print('数据更新失败',e)
            return []
        finally:
            self.conn.commit()

    # def add_cell_data(self, table_name,key,data,sql_where):
    #     """单元格增加数据"""
    #     try:
    #         if isinstance(data,str):
    #             data = (data,)
    #         if isinstance(key,str):
    #             key = (key,)
    #         data = self.listIntuple_to_JSON(data)
    #         # UPDATE
    #         sql = f'UPDATE {table_name}'
    #         sql += ' SET '
    #         sql += ' key = ? || ?'
    #         sql += ' WHERE '
    #         sql += ' name = ?'
    #         self.cursor.execute(sql, datas)
    #         results = self.cursor.fetchall()
    #         return results
    #     except Exception as ex:
    #         return []
    #     finally:
    #         self.conn.commit()

    def query_data_table(self, table_name:str) -> list:
        """
        查询表格的数据

        :param table_name: 要从中检索数据的表名
        """
        try:
            sql = f"SELECT * FROM {table_name}"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as ex:
            return []
        finally:
            self.conn.commit()

    def query_colum(self, table_name:str, datas:tuple, keys:tuple = ('name',), column:tuple = '*') -> list:
        """
        列查询

        :param table_name: 要从中检索数据的表名
        :param datas: 列数据
        :param keys: 列名
        :param column: 要检索的列名 (column1, column2, ...)
        """
        try:
            if isinstance(datas,str) or isinstance(datas,int):
                datas = (datas,)
            if isinstance(keys,str) or isinstance(keys,int) :
                keys = (keys,)
            # 列表数据序列化
            datas = self.listIntuple_to_JSON(datas)
            # 构建SELECT语句
            sql = f'SELECT {column} FROM {table_name}'
            sql += ' WHERE '
            sql += ' AND '.join([f'{key} = ?' for key in keys])
            # sql = f"SELECT {column} FROM {table_name} where {column_name} = ?"
            self.cursor.execute(sql,datas)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print(e)
            return []
        finally:
            self.conn.commit()

    def execute_sql(self, sql: str) -> list:
        """数据库操作"""
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print("数据集操作失败:", str(e))
            return []
        finally:
            self.conn.commit()

    def delete_cell(self,table_name,row_name,row_data,column_name):
        """
        删除单元格

        :param table_name: 表名
        :param row_name: 行名
        :param row_data: 行数据
        :param column_name: 列名
        :return:
        """
        try:
            sql = f'UPDATE FROM {table_name} SET {column_name} = NULL WHERE {row_name} = ?'
            self.cursor.execute(sql, (row_data,))
        except Exception as ex:
            print("删除数据出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()

    def delete_row(self,table_name,key,data):
        """删除行"""
        try:
            # if isinstance(data,str):
            #     data = '"' + data + '"'
            sql = f'DELETE FROM {table_name} WHERE {key} = "{data}"'
            self.cursor.execute(sql)
        except Exception as ex:
            print("删除数据出错，错误信息：", str(ex))
            return False
        finally:
            self.conn.commit()

    def delete_row_if(self, table_name, condition="name = 1"):
        """
        条件删除行

        :param table_name: 表名
        :param condition: 条件 例如"name = 1"
        :return:
        """
        # 构造DELETE语句
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            # 执行DELETE语句
            self.cursor.execute(sql)
            print("删除成功")
        except Exception as e:
            print("删除失败:", str(e))
        finally:
            self.conn.commit()

    def clear(self,table_name):
        """
        删除所有行

        :param table_name: 表名
        :return:
        """

        # 构造DELETE语句
        sql = f"DELETE FROM {table_name}"
        try:
            # 执行DELETE语句
            self.cursor.execute(sql)
            print("清空成功")
        except Exception as e:
            print("清空失败:", str(e))
        finally:
            self.conn.commit()

    def clear_column(self,table_name,key):
        """
        删除列

        :param table_name: 表名
        :param key: 列名
        :return:
        """

        # 构造DELETE语句
        sql = f"UPDATE {table_name} SET {key} = NULL"
        try:
            # 执行DELETE语句
            self.cursor.execute(sql)
            print("清空成功")
        except Exception as e:
            print("清空失败:", str(e))
        finally:
            self.conn.commit()

    def close(self):
        '''
        关闭数据库连接
        '''
        try:
            self.cursor.close()
            self.conn.close()
        except sqlite3.Error as e:
            # 捕获sqlite3模块抛出的任何错误，表明连接可能已断开或无效
            print(f"捕获sqlite3模块抛出的任何错误，表明连接可能已断开或无效: {e}")
            return False

    def restart(self,db):
        """
        重启数据库
        """
        self.close()
        db_name = self.db_name
        db = MySqlite3(db_name)  # 主数据库

    def listIntuple_to_JSON(self,datas):
        # 元组中的列表数据序列化
        data_list = []
        for i in range(len(datas)):
            data_list.append(adapt_JSON(datas[i]))
        datas = tuple(data_list)
        return datas


class PyMySQL(object):
    create_table = """
        CREATE TABLE stu (   
            id INT not null PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            age INT, 
            sex VARCHAR(255)
        ) DEFAULT CHARSET = utf8
    """
    select = 'SELECT * FROM stu'
    update = 'UPDATE stu SET name = %s WHERE id=%s'
    delete = 'DELETE FROM stu WHERE id=%s'
    insert = 'INSERT INTO stu(name, age, sex) VALUES(%s, %s, %s)'

    def __init__(self, host='192.168.1.117', user='root', passwd=None, port=3306, db='sx815v'):
        if passwd is None:
            config = configparser.ConfigParser()
            passwd = config.get('database', 'password')
            print(passwd)
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, port=port, db=db, charset='utf8')
        self.cursor = self.conn.cursor()
        print("数据库连接成功!")

    def closeAll(self):
        self.conn.close()
        self.cursor.close()
        print("资源释放完毕!")

    def create_table_func(self):
        self.cursor.execute("DROP TABLE IF EXISTS stu")
        self.cursor.execute(PyMySQL.create_table)
        print('数据表创建完毕')

    def insert_date(self):
        try:
            self.cursor.execute(PyMySQL.insert, ('小明', 2, "男"))
            self.conn.commit()
            print("数据插入成功!")
        except Exception as e:
            print(traceback.format_exc())
            self.conn.rollback()
            print("数据插入失败!")

    def update_data(self):
        try:
            self.cursor.execute(PyMySQL.update, ("明明", 2))
            self.conn.commit()
            print("数据更新成功!")
        except Exception as e:
            print(traceback.format_exc())
            self.conn.rollback()
            print("数据更新失败!")

    def delete_data(self):
        try:
            self.cursor.execute(PyMySQL.delete, (9,))
            self.conn.commit()
            print("数据删除成功!")
        except Exception as e:
            print(traceback.format_exc())
            self.conn.rollback()
            print("数据删除失败!")

    def select_data(self):
        self.cursor.execute(PyMySQL.select)
        all_data = self.cursor.fetchall()
        for i in all_data:
            print('查询结果为：{}'.format(i))



if __name__ == '__main__':
    my = PyMySQL()
    my.create_table_func()
    my.insert_date()
    my.update_data()
    my.delete_data()
    my.select_data()
    my.closeAll()

# data=[
#     {"name":"张三","age":"23"},
#     {"name":"丽莎","age":"23"},
#     {"name":"卢卡斯","mytest":"as"}
# ]
# db=DB(db_name="mytest.db")
# db.create_tables("stu",['name', 'age'])
# db.insert_data("stu",data)
# item = db.query_data("SELECT  age FROM stu") if db.query_data("SELECT  age FROM stu") else ''
# print(',,,',item)
# print(db.query_data_column("stu","age",'23'))
# db.add_column("stu",['mytest'])
# db.add_column("stu",['mytest'])
# db.close()

# db_path = DB(Globals.db_main_path)
# db_data = DB(Globalsjson.db_data_path)

