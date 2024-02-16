import argparse
from flask import Flask, request, jsonify
from db_handler.sqlite_handler import SQLiteHandler
import re
import os
from db_handler.firebase_handler import FirebaseHandler

app = Flask(__name__)


def get_db_handler(database_type):
    """
    Returns the appropriate database handler based on the command-line argument.
    Gets the firebase database name from the environment variable.
    """
    if database_type == 'sqlite':
        return SQLiteHandler('speadsheet.db')
    elif database_type == 'firebase':
        firebase_db_name = os.environ.get('FBASE')
        if not firebase_db_name:
            raise ValueError("Firebase database name not found")
        url = f'https://{firebase_db_name}-default-rtdb.europe-west1.firebasedatabase.app/'
        return FirebaseHandler(url)
    else:
        raise ValueError("Unsupported database type")


def evaluate_cell(cell_id, formula, db_handler):
    """
    Evaluates a cell's formula using recursion, and returns the result.
    :param cell_id: id of the cell
    :param formula: formula of the cell
    :param db_handler: database handler
    """
    # Check if the formula is a simple number
    # BASE CASE
    print('formula: ', formula)
    if formula.isdigit():
        return formula

    # find all the cell ids in the formula
    cell_ids = re.findall(r'[A-Z]+\d+', formula)
    # get the formula for each cell
    for cell in cell_ids:
        # get the formula for the cell
        cell_formula = db_handler.read_cell(cell)
        if cell_formula is None:
            # if reference cell is not found, assume value of 0
            value = '0'
        else:
            # evaluate the cell's formula
            value = evaluate_cell(cell, cell_formula, db_handler)

        # replace the cell id with the value
        formula = formula.replace(cell, value)
    # evaluate the expression
    return str(eval(formula))


def setup_routes(db_handler):
    """
    Sets up the Flask routes using the given database handler.
    :param db_handler: database handler
    """

    @app.route('/cells/<cell_id>', methods=['PUT'])
    def create_or_update_cell(cell_id):
        """
        Creates or updates a cell.
        :param cell_id: id of the cell
        :return: HTTP status code
        """
        data = request.get_json()
        # check if 'id' key is missing in JSON body
        if 'id' not in data:
            return '', 400

        # Extract 'formula' and 'id' from JSON
        formula = data.get('formula')
        json_id = data.get('id')

        # Ensure formula is provided
        if not formula:
            return '', 400

        # check if 'id' in URL does not match 'id' in JSON body
        if cell_id != json_id:
            return '', 400

        # create or update the cell
        try:
            was_created = db_handler.create_cell(cell_id, formula)
            if was_created:
                return '', 201
            else:
                # if the cell was updated
                return '', 204
        except Exception as e:
            return '', 500

    @app.route('/cells/<cell_id>', methods=['GET'])
    def read_cell(cell_id):
        """
        Reads the value of a cell by its ID and evaluates the formula.
        :param cell_id: id of the cell
        :return: JSON Object, HTTP status code
        """

        value = db_handler.read_cell(cell_id)

        # evaluate the formula
        if value is not None:
            value = evaluate_cell(cell_id, value, db_handler)
            return jsonify({"id": cell_id, "formula": value}), 200
        else:
            # if the cell is not found, return 404
            return jsonify({"id": cell_id, "formula": 0}), 404

    @app.route('/cells/<cell_id>', methods=['DELETE'])
    def delete_cell(cell_id):
        """
        Deletes a cell by its ID.
        :param cell_id: id of the cell
        :return: HTTP status code
        """
        # check if the cell exists
        if not db_handler.read_cell(cell_id):
            return '', 404
        # delete the cell
        try:
            db_handler.delete_cell(cell_id)
            return '', 204
        except Exception as e:
            # Internal server error
            return '', 500

    @app.route('/cells', methods=['GET'])
    def list_cells():
        """
        Lists all cell IDs.
        :return: JSON Object, HTTP status code
        """
        try:
            cells = db_handler.list_cells()
            return jsonify(cells), 200
        except Exception as e:
            return '', 500

    # Define other routes...


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='SC Microservice')
    parser.add_argument('-r', '--repository', choices=['sqlite', 'firebase'], required=True,
                        help='Database repository type')
    args = parser.parse_args()

    # Get the database handler
    db_handler = get_db_handler(args.repository)
    setup_routes(db_handler)

    # Run the Flask app
    app.run(host='0.0.0.0', port=3000)
