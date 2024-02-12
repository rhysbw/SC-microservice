import argparse
from flask import Flask, request, jsonify
from db_handler.sqlite_handler import SQLiteHandler
import operator
import re
# from db_handler.firebase_handler import FirebaseHandler  # Uncomment when FirebaseHandler is implemented

app = Flask(__name__)


# Modify the read_cell method or create a new one that uses evaluate_cell
def get_db_handler(database_type):
    """
    Returns the appropriate database handler based on the command-line argument.
    """
    if database_type == 'sqlite':
        return SQLiteHandler('speadsheet.db')
    # elif database_type == 'firebase':
    #     return FirebaseHandler()
    else:
        raise ValueError("Unsupported database type")


def setup_routes(db_handler):
    """
    Sets up the Flask routes using the given database handler.
    """

    @app.route('/cells/<cell_id>', methods=['PUT'])
    def create_or_update_cell(cell_id):
        data = request.get_json()  # force=True to ensure you get JSON even if Content-Type header is missing

        # For Test 8: Check if 'id' key is missing in JSON body
        if 'id' not in data:
            return '', 400

        # Extract 'formula' and 'id' from JSON
        formula = data.get('formula')
        json_id = data.get('id')

        # Ensure formula is provided
        if not formula:
            return '', 400

        # For Test 9: Check if 'id' in URL does not match 'id' in JSON body
        if cell_id != json_id:
            return '', 400

        # Insert or update logic here...
        try:
            # Assuming db_handler.create_cell() exists and handles the DB operation
            was_created = db_handler.create_cell(cell_id, formula)
            print('this ran')
            return '', 201 if was_created else '', 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/cells/<cell_id>', methods=['GET'])
    def read_cell(cell_id):
        """
        Reads and returns the value of a cell.
        """
        try:
            value = db_handler.read_cell(cell_id)
            if value is None:
                return jsonify({"error": "Cell not found"}), 404
            return jsonify({"id": cell_id, "formula": value}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/cells/<cell_id>', methods=['DELETE'])
    def delete_cell(cell_id):
        """
        Deletes a cell by its ID.
        """
        try:
            db_handler.delete_cell(cell_id)
            return '', 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/cells', methods=['GET'])
    def list_cells():
        """
        Lists all cell IDs.
        """
        try:
            cells = db_handler.list_cells()
            return jsonify(cells), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Define other routes...


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SC Microservice')
    parser.add_argument('-r', '--repository', choices=['sqlite', 'firebase'], required=True,
                        help='Database repository type')
    args = parser.parse_args()

    db_handler = get_db_handler(args.repository)
    setup_routes(db_handler)
    app.run(host='0.0.0.0', port=3000)
