import sqlite3
from .base import DatabaseHandler
import os

class SQLiteHandler(DatabaseHandler):
    """
    SQLite's implementation of the DatabaseHandler.
    """

    def __init__(self, db_path):
        """
        Initializes the SQLiteHandler with the path to the database file.
        :param db_path: file path to the SQLite database
        """
        self.db_path = db_path
        self.connection = self._connect_to_db()

    def _connect_to_db(self):
        """
        Connects to the SQLite database.
        :return: the connection object
        """
        # Check if the database file does not exist and create it
        db_exists = os.path.exists(self.db_path)
        connection = sqlite3.connect(self.db_path)
        if not db_exists:
            self._create_schema(connection)
        return connection

    def _create_schema(self, connection):
        """
        Creates the database schema.
        """
        cursor = connection.cursor()
        # Example schema
        cursor.execute('''CREATE TABLE cells (id TEXT PRIMARY KEY, formula TEXT)''')
        connection.commit()

    def create_cell(self, cell_id, formula):
        """
        Creates a new cell or updates an existing one with the provided formula.
        Returns True if a new cell was created, False if an existing cell was updated.
        :param cell_id: id of the cell
        :param formula: formula to be stored
        :return: True if a new cell was created, False if an existing cell was updated
        """
        was_created = False
        try:
            with self._connect_to_db() as conn:
                cursor = conn.cursor()
                # First, try to fetch the cell to determine if it exists
                cursor.execute("SELECT formula FROM cells WHERE id = ?", (cell_id,))
                exists = cursor.fetchone()

                if exists:
                    # Update the existing cell
                    cursor.execute("UPDATE cells SET formula = ? WHERE id = ?", (formula, cell_id))
                else:
                    # Insert a new cell
                    cursor.execute("INSERT INTO cells (id, formula) VALUES (?, ?)", (cell_id, formula))
                    was_created = True

                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")
            raise e  # It's better to raise the exception to handle it in the calling function

        return was_created

    def read_cell(self, cell_id):
        """
        Reads the formula of a cell by its id, by executing SQL queries directly.
        :param cell_id: id of the cell to read
        :return: the formula of the cell, if it exists else None
        """
        try:
            with self._connect_to_db() as conn:
                cursor = conn.cursor()
                # select the cell from the database
                cursor.execute("SELECT formula FROM cells WHERE id=?", (cell_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")

    def delete_cell(self, cell_id):
        """
        Deletes a cell by its id, by executing SQL queries directly.
        :param cell_id: id of the to delete
        """
        try:
            with self._connect_to_db() as conn:
                cursor = conn.cursor()
                # delete the cell from the database
                cursor.execute("DELETE FROM cells WHERE id=?", (cell_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")

    def list_cells(self):
        """
        Lists all cell ids in the database, by executing SQL queries directly.
        :return list of cell ids
        """
        try:
            with self._connect_to_db() as conn:
                cursor = conn.cursor()
                # select all cell ids from the database
                cursor.execute("SELECT id FROM cells")
                list_of_cells = cursor.fetchall()
                return [row[0] for row in list_of_cells]
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")
