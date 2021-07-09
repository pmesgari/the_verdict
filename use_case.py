import meraki
from models import Verdict
import json


def read_meraki_network(network_id: str, serial: str, client: meraki.DashboardAPI):
    result = {
        'network_id': '',
        'name': '',
        'serial': ''
    }

    try:
        network = client.networks.getNetwork(networkId=network_id)
        print(network)
        result['network_id'] = network.get('id')
        result['name'] = network.get('name')
    except meraki.APIError:
        pass
    try:
        device = client.devices.getDevice(serial)
        result['serial'] = device.get('serial')
    except meraki.APIError:
        pass
    
    return result


def make_migration_verdict_for(legacy_network: dict, meraki_network: dict):
    no_go_verdict = Verdict.no_go(legacy_network)
    
    if not meraki_network.get('network_id'):
        no_go_verdict.add_error('network_id', 'does not exist in Meraki Dashboard')
        return no_go_verdict
    if legacy_network.get('name') != meraki_network.get('name'):
        no_go_verdict.add_error('network_name', 'does not match')
    if legacy_network.get('serial') != meraki_network.get('serial'):
        no_go_verdict.add_error('serial', 'does not match')

    if no_go_verdict.has_error:
        return no_go_verdict
    return Verdict.go(legacy_network)


class ValidateLegacyNetworkUseCase:
    def __init__(self, client: meraki.DashboardAPI):
        self.client = client

    def execute(self, args):
        network_id = args.get('network_id')
        serial = args.get('serial')
        name = args.get('name')
        branch_number = args.get('branch_number')
        company = args.get('company')
        legacy_network = {
            'network_id': network_id,
            'serial': serial,
            'name': name,
            'branch_number': branch_number,
            'company': company
        }
        meraki_network = read_meraki_network(network_id, serial, self.client)
        verdict = make_migration_verdict_for(legacy_network, meraki_network)
        return verdict

