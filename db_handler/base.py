from abc import ABC, abstractmethod


class DatabaseHandler(ABC):
    """
    Abstract base class for database operations.
    """

    @abstractmethod
    def create_cell(self, cell_id, formula):
        """
        Create or update a cell.
        """
        pass


    # Define other abstract methods (read_cell, delete_cell, list_cells)
