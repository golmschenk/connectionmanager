"""
Code for managing connections to remote machines.
"""
import sys

from royal_tsx import RoyalTsx
from virtual_machine import VirtualMachine


class ConnectionManager:
    """
    A class for managing connections to remote machines.
    """
    @staticmethod
    def sync_royal_tsx_azure_connections(royal_tsx_document_path):
        """
        Syncs the Royal TSX connections with Azure.

        :param royal_tsx_document_path: The location of Royal TSX document to sync.
        :type royal_tsx_document_path: str
        """
        virtual_machines = VirtualMachine.list_from_azure()
        royal_tsx = RoyalTsx(royal_tsx_document_path)
        royal_tsx.sync(virtual_machines)

if __name__ == '__main__':
    connection_manager = ConnectionManager()
    connection_manager.sync_royal_tsx_azure_connections(sys.argv[1])
