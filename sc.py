import argparse
from flask import Flask, request, jsonify
from db_handler.sqlite_handler import SQLiteHandler
import operator
import re
from db_handler.firebase_handler import FirebaseHandler  # Uncomment when FirebaseHandler is implemented

app = Flask(__name__)


# Modify the read_cell method or create a new one that uses evaluate_cell
def get_db_handler(database_type):
    """
    Returns the appropriate database handler based on the command-line argument.
    """
    if database_type == 'sqlite':
        return SQLiteHandler('speadsheet.db')
    elif database_type == 'firebase':
         url = 'https://sc-microservice-default-rtdb.europe-west1.firebasedatabase.app/'
         return FirebaseHandler(url)
    else:
        raise ValueError("Unsupported database type")
def evaluate_cell(cell_id, formula, db_handler):
    """
    Evaluates a cell's formula and returns the result.
    """
    # Check if the formula is a simple number
    if formula.isdigit():
        return formula

    # need to use recursion
    # find all the cell ids in the formula
    cell_ids = re.findall(r'[A-Z]+\d+', formula)
    # get the formula for each cell
    for cell in cell_ids:
        # get the formula for the cell
        cell_formula = db_handler.read_cell(cell)
        # evaluate the formula
        value = evaluate_cell(cell, cell_formula, db_handler)
        # replace the cell id with the value
        formula = formula.replace(cell, value)
    # evaluate the formula
    return str(eval(formula))




def setup_routes(db_handler):
    """
    Sets up the Flask routes using the given database handler.
    """

    @app.route('/cells/<cell_id>', methods=['PUT'])
    def create_or_update_cell(cell_id):
        data = request.get_json()
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
        try:
            was_created = db_handler.create_cell(cell_id, formula)
            if was_created:
                return '', 201
            else:
                return '', 204
        except Exception as e:
            return '', 500

    @app.route('/cells/<cell_id>', methods=['GET'])
    def read_cell(cell_id):
        """
        Reads and returns the value of a cell.
        """
        try:
            value = db_handler.read_cell(cell_id)

            # evaluate the formula
            if value:
                value = evaluate_cell(cell_id, value, db_handler)
                return jsonify({"id": cell_id, "formula": value}), 200
            else:
                return jsonify({"error": "Cell not found"}), 404
        except Exception as e:
            return '', 500

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
            return '', 500

    # Define other routes...


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SC Microservice')
    parser.add_argument('-r', '--repository', choices=['sqlite', 'firebase'], required=True,
                        help='Database repository type')
    args = parser.parse_args()

    db_handler = get_db_handler(args.repository)
    setup_routes(db_handler)
    app.run(host='0.0.0.0', port=3000)
