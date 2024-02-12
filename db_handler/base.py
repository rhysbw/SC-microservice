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

    @abstractmethod
    def read_cell(self, cell_id):
        """
        Read a cell.
        """
        pass

    @abstractmethod
    def delete_cell(self, cell_id):
        """
        Delete a cell.
        """
        pass

    @abstractmethod
    def list_cells(self):
        """
        List all cells.
        """
        pass



