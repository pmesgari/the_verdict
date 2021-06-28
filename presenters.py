import json
import csv
from pathlib import Path


class JsonPresenter:
    def __init__(self, pretty=True):
        self._formatted_data = []
        self.pretty = pretty

    def present(self, data):
        if self.pretty:
            self._formatted_data.append(json.dumps([verdict.to_json() for verdict in [data]], indent=4))
        else:
            self._formatted_data.append(son.dumps([verdict.to_json() for verdict in [data]]))

    def end(self):
        print(self._formatted_data)

    def get_presented_data(self):
        return self._formatted_data


class CsvPresenter:
    def __init__(self, folder):
        self._output_path = Path(folder) / "output.csv"
        self._formatted_data = []

    def present(self, data):
        self._formatted_data.append(data.to_json())

    def end(self):
        fieldnames = ['network_id', 'name', 'serial', 'branch_id', 'verdict', 'errors']
        with open(self._output_path, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in self._formatted_data:
                writer.writerow(data)

    def get_presented_data(self):
        return self._formatted_data
