import mysql.connector
from mysql.connector import Error


class mysql_db:

    def __init__(self, host, user, password, db_name):
        self.conn = mysql.connector.connect(host=host, user=user, password=password)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        self.conn.database = db_name

    def execute_query(self, query, args=None):
        try:
            if args is not None:
                self.cursor.execute(query, args)
            else:
                self.cursor.execute(query)

            # Fetch rows only if the query returns a result set (e.g., SELECT)
            result = self.cursor.fetchall() if self.cursor.with_rows else []
            self.conn.commit()
            return result
        except Error as err:
            self.conn.rollback()
            print(f"Failed executing query: {err}")
            return None

    def create_table(self, table_name, column_names_and_types):
        query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(column_names_and_types)})"
        return self.execute_query(query) is not None

    def write_column(self, table_name, data):
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
        return self.execute_query(query, data) is not None

    def read_column(self, table_name):
        result = self.execute_query(f"SELECT * FROM `{table_name}`")
        return result if result is not None else []

    def close(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    db = mysql_db("localhost", "root", "your_password", "mystore")
    table_name = "users"
    db.create_table(table_name, ["username VARCHAR(50)", "password VARCHAR(100)"])
    db.write_column(table_name, ("test_username", "123456"))

    user = db.execute_query(
        "SELECT * FROM users WHERE username = %s", ("test_username",)
    )
    print(user)

    db.close()