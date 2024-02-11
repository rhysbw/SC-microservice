import argparse
from flask import Flask
from db_handler.sqlite_handler import SQLiteHandler

# from db_handler.firebase_handler import FirebaseHandler  # Uncomment when FirebaseHandler is implemented

app = Flask(__name__)


def get_db_handler(database_type):
    """
    Returns the appropriate database handler based on the command-line argument.
    """
    if database_type == 'sqlite':
        return SQLiteHandler('path_to_your_sqlite_db.db')
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
        # Implementation here
        pass

    # Define other routes...


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SC Microservice')
    parser.add_argument('-r', '--repository', choices=['sqlite', 'firebase'], required=True,
                        help='Database repository type')
    args = parser.parse_args()

    db_handler = get_db_handler(args.repository)
    setup_routes(db_handler)
    app.run(port=3000)
