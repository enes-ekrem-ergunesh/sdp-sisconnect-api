import pymysql
import db.dbConnections as db
from helpers.http_response import http_response


class BaseDao:

    def __init__(self, table_name):
        self.connection = db.get_connection()
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        self.table_name = table_name

    def admin_auth_check(self, admin_id):
        query = "SELECT * FROM users WHERE id = %s AND is_admin = 1"
        self.cursor.execute(query, (admin_id,))
        if not self.cursor.fetchone():
            http_response(403, "Unauthorized")

    def execute_query(self, query, params=None, filters=None):
        try:
            if filters:
                if " WHERE " in query:
                    query += " AND " + " AND ".join(filters)
                else:
                    query += " WHERE " + " AND ".join(filters)
                params = params if params else ()
                params += tuple(filters.values())
            # print(query, params)
            self.cursor.execute(query, params)
            last_row_id = self.cursor.lastrowid
            self.connection.commit()
            return last_row_id
        except Exception as e:
            return http_response(500, str(e))

    def fetch_one(self, query, params=None, filters=None):
        try:
            if filters:
                query += " AND " + " AND ".join(filters)
                params += tuple(filters.values())
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            return http_response(500, str(e))

    def fetch_all(self, query, params=None, filters=None):
        try:
            if filters:
                query += " WHERE " + " AND ".join(filters)
                params += tuple(filters.values())
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            return http_response(500, str(e))

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def get_all(self, filters=None, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        query = f"SELECT * FROM {self.table_name}"
        base_dao = BaseDao(self.table_name)
        result = base_dao.fetch_all(query, filters)
        base_dao.close_connection()
        return result

    def get_by_id(self, _id, filters=None, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        base_dao = BaseDao(self.table_name)
        result = base_dao.fetch_one(query, (_id,), filters)
        base_dao.close_connection()
        return result

    def insert(self, data, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        base_dao = BaseDao(self.table_name)
        result = base_dao.execute_query(query, tuple(data.values()))
        base_dao.close_connection()
        return result

    def update(self, data, _id, filters=None, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        placeholders = ""
        for key in data.keys():
            placeholders += f"{key} = %s, "
        placeholders = placeholders[:-2]
        query = f"UPDATE {self.table_name} SET {placeholders} WHERE id = %s"
        print(query)
        base_dao = BaseDao(self.table_name)
        base_dao.execute_query(query, tuple(data.values()) + (_id,), filters)
        base_dao.close_connection()

    def delete(self, filters, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        query = f"DELETE FROM {self.table_name}"
        base_dao = BaseDao(self.table_name)
        result = base_dao.execute_query(query, None, filters)
        base_dao.close_connection()
        return result

    def soft_delete(self, filters, admin=False, admin_id=None):
        self.admin_auth_check(admin_id) if admin else None
        query = f"UPDATE {self.table_name} SET deleted_at = NOW()"
        base_dao = BaseDao(self.table_name)
        result = base_dao.execute_query(query, None, filters)
        base_dao.close_connection()
        return result
