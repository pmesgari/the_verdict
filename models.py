from enum import Enum


class MigrationColor(Enum):
    GREEN = 'Go for migration'
    RED = 'No go for migration'


class Verdict:
    def __init__(self, network: dict, color: MigrationColor):
        self.network = network
        self.color = color
        self.errors = []

    @property
    def has_error(self):
        return len(self.errors) > 0

    @property
    def message(self):
        msg = " ".join([f"{err.get('parameter')}: {err.get('message')}"
                         for err in self.errors])
        return msg

    @classmethod
    def go(cls, network: dict):
        return Verdict(network=network, color=MigrationColor.GREEN)

    @classmethod
    def no_go(cls, network: dict):
        return Verdict(network=network, color=MigrationColor.RED)

    def add_error(self, parameter: str, message: str):
        self.errors.append({'parameter': parameter, 'message': message})

    def to_json(self):
        return {
            'network_id': self.network.get('network_id'),
            'name': self.network.get('name'),
            'serial': self.network.get('serial'),
            'branch_number': self.network.get('branch_number'),
            'company': self.network.get('company'),
            'verdict': self.color.value,
            'errors': self.message
        }
