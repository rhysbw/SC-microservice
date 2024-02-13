import requests
from .base import DatabaseHandler
class FirebaseHandler(DatabaseHandler):
    def __init__(self, base_url):
        self.base_url = base_url

    def create_cell(self, cell_id, formula):
        was_created = False
        print('Create or update cell: ', cell_id, formula)
        url = f"{self.base_url}/cells/{cell_id}.json"
        # check if the cell exists
        cell = self.read_cell(cell_id)
        if cell:
            # update the cell
            response = requests.patch(url, json={"formula": formula})
            print('response code: ', response.status_code)
            was_created = False
            return was_created

        was_created = True
        response = requests.put(url, json={"formula": formula})
        print('response code: ', response.status_code)
        return was_created

    def read_cell(self, cell_id):
        url = f"{self.base_url}/cells/{cell_id}.json"
        response = requests.get(url)
        cell_data = response.json()
        if cell_data:
            # If the cell exists, return just the formula part
            return cell_data.get('formula')
        else:
            # Return None if the cell does not exist
            return None

    def delete_cell(self, cell_id):
        url = f"{self.base_url}/cells/{cell_id}.json"
        response = requests.delete(url)
        print('response for delet: ', response)
        return response.status_code  # 200 for success

    def list_cells(self):
        url = f"{self.base_url}/cells.json"
        response = requests.get(url)
        cells_dict = response.json()
        if cells_dict:
            # Extract and return the cell IDs as a list
            return list(cells_dict.keys())
        else:
            # Return an empty list if no cells are found
            return []


