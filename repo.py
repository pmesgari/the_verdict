import csv
from pathlib import Path


class CsvRepository:
    def __init__(self, folder):
        self._networks_path = Path(folder) / 'networks.csv'

    def list_networks(self):
        networks = []
        with open(self._networks_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                networks.append(row)
        return networks
