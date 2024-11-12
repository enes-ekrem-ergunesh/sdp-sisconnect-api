from config import config
from pymysql.cursors import DictCursor
import pymysqlpool
from constants import PROD

from colorama import Fore

if not PROD:
    pymysqlpool.logger.setLevel('DEBUG')

connConfig = {
    'host': config.get('HOST'),
    'port': config.get('PORT'),
    'user': config.get('USER'),
    'password': config.get('PASSWORD'),
    'database': config.get('DATABASE'),
    'autocommit': True,
    'cursorclass': DictCursor,
}
print("HOST: ", config.get('HOST'))
pool1 = pymysqlpool.ConnectionPool(size=5, maxsize=15, pre_create_num=5, name='pool1', **connConfig)

def print_pool_status():
    if pool1.maxsize - (pool1.total_num - pool1.available_num) < 3:
        print(Fore.RED + ("X"*100 + "\n")*10 + f"POOL: {pool1.total_num - pool1.available_num}/{pool1.total_num} of {pool1.maxsize}")

def execute_query(query, params=None):
    print_pool_status()
    connection = pool1.get_connection()
    print_pool_status()
    cur = connection.cursor()
    cur.execute(query, params)
    output = cur.fetchall()
    connection.close()
    print(output)
    return output


def execute_query_single(query, params=None):
    print_pool_status()
    connection = pool1.get_connection()
    print_pool_status()
    cur = connection.cursor()
    cur.execute(query, params)
    output = cur.fetchone()
    connection.close()
    return output


def execute_update(query, params=None):
    print_pool_status()
    connection = pool1.get_connection()
    print_pool_status()
    cur = connection.cursor()
    cur.execute(query, params)
    connection.close()


class BaseDAO:
    def __init__(self, table):
        print_pool_status()
        self.table = table

    def get_all(self):
        query = f"SELECT * FROM {self.table}"
        print(query)
        return execute_query(query)

    def get_by_id(self, record_id):
        query = f"SELECT * FROM {self.table} WHERE id = %s"
        return execute_query_single(query, (record_id,))

    def create(self, data):
        print("INSERTED ONCE")
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table} ({keys}) VALUES ({values})"
        execute_update(query, tuple(data.values()))

    def update(self, record_id, data):
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = %s"
        execute_update(query, tuple(data.values()) + (record_id,))

    def delete(self, record_id):
        query = f"DELETE FROM {self.table} WHERE id = %s"
        execute_update(query, (record_id,))

    def soft_delete(self, record_id):
        query = f"UPDATE {self.table} SET deleted_at = NOW() WHERE id = %s"
        execute_update(query, (record_id,))