# Spreadsheet Microservice

This project is a simple spreadsheet microservice implemented in Python using Flask and SQLite.

## Prerequisites

- Python 3.6 or higher
- flask
- requests

## Installation
1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Set the database type by using the `-r` or `--repository` command-line argument. The options are `sqlite` and `firebase`. For example, to use SQLite:
   ```
   python sc.py -r sqlite
   ```
2. The application will start running on port 3000: `http://0.0.0.0:3000`.

## API Endpoints

- `PUT /cells/<cell_id>`: Create or update a cell with a given ID.
- `GET /cells/<cell_id>`: Read the value of a cell with a given ID.
- `DELETE /cells/<cell_id>`: Delete a cell with a given ID.
- `GET /cells`: List all cell IDs.

## Firebase Integration
1. Set the firebase real-time database name as an ENV variable `FBASE`. For example, to use my firebase database `sc-microservice`:
   ```
   export FBASE="sc-microservice"
   ```
2. Run the application with the `-r` or `--repository` command-line argument set to `firebase`:
   ```
    python sc.py -r firebase
    ```