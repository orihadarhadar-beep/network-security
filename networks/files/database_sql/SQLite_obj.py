import sqlite3


class SQLite:

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, column_names_and_types):
        try:
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_names_and_types)})"
            )
            self.conn.commit()
        except sqlite3.Error as err:
            print(f"Failed creating table: {err}")
            return False
        return True

    def write_column(self, table_name, data):
        try:
            placeholders = ", ".join(["?"] * len(data))
            self.cursor.execute(
                f"INSERT INTO {table_name} VALUES ({placeholders})", data
            )
            self.conn.commit()
        except sqlite3.Error as err:
            print(f"Failed writing data: {err}")
            return False
        return True

    def read_column(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except sqlite3.Error as err:
            print(f"Failed reading data: {err}")
            return []

    def execute_query(self, query, args=None):
        try:
            if args is not None:
                result = self.cursor.execute(query, args).fetchall()
            else:
                result = self.cursor.execute(query).fetchall()
            self.conn.commit()
            return result
        except sqlite3.Error as err:
            print(f"Failed executing query: {err}")
            return None
    
    def close(self):
        self.conn.commit()
        self.conn.close()


if __name__ == "__main__":
    db = SQLite("mystore.db")
    table_name = "users"
    db.create_table(table_name, ["username TEXT", "password TEXT"])
    db.write_column(table_name, ("test_username", "123456"))
    data = db.read_column(table_name)
    print(data)
    db.close()
