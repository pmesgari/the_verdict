import sys
import argparse
import meraki

from repo import CsvRepository
from helpers import unflatten
from use_case import ValidateLegacyNetworkUseCase
from presenters import JsonPresenter, CsvPresenter


def run_validate_legacy_network_use_case(data, client, presenter):
    use_case = ValidateLegacyNetworkUseCase(client)
    result = use_case.execute(data)
    presenter.present(result)


def run_cli(args):
    use_case_args = parse_args(vars(args))

    config = use_case_args.get('config', {})
    data = use_case_args.get('data')
    csv = use_case_args.get('csv', None)
    output_format = use_case_args.get('output', 'json')
    output_folder = use_case_args.get('output_folder', 'data')

    # validate at least csv or data are used
    if not csv and not data:
        raise ValueError('at least csv or data parameter are needed')

    # validate csv and data are not used at the same time
    if csv and data:
        raise ValueError('csv and data parameters can not be used at the same time')

    # validate configuration parameters
    output_log = config.get('OUTPUT_LOG', False)
    api_key = config.get('API_KEY', None)
    if api_key is None:
        raise ValueError('configuration parameter API_KEY is missing')

    client = meraki.DashboardAPI(api_key=api_key, output_log=output_log)

    # decide on the output format
    presenter = JsonPresenter()
    if output_format == 'csv':
        presenter = CsvPresenter(output_folder)

    # determine single or csv run
    if csv:
        repo = CsvRepository(folder=csv)
        run_csv(client=client, repo=repo, presenter=presenter)
    else:
        # validate data parameters
        minimum_data_parameters = {'network_id', 'name', 'serial', 'branch_number'}
        if not minimum_data_parameters.issubset(set(data.keys())):
            raise ValueError('Minimum data parameters are missing, see usage')

        run_validate_legacy_network_use_case(data=data, client=client, presenter=presenter)

    presenter.end()


def run_csv(client, repo, presenter):
    networks = repo.list_networks()
    for network in networks:
        run_validate_legacy_network_use_case(data=network, client=client, presenter=presenter)


class ErrorCatchingArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if status:
            raise KeyError(f'Exiting because of an error: {message}')
        exit(status)


def arguments():
    parser = ErrorCatchingArgumentParser()
    parser.add_argument(
        '--data',
        nargs='+',
        help='legacy network parameters, must include keys network_id, name, serial and branch_number',
        metavar='key=value'
    )
    parser.add_argument(
        '--config',
        nargs='+',
        help='configuration parameters, must include at least the key API_KEY',
        metavar='key=value'
    )
    parser.add_argument(
        '--csv',
        nargs=1,
        help='validate legacy networks in the csv file',
        metavar='folder',
    )
    parser.add_argument(
        '--output',
        nargs=1,
        help='result output format, allowed options are json and csv',
        metavar='option',
    )
    return parser


def parse_value(value):
    if isinstance(value, list):
        adict = {}
        alist = []
        for item in value:
            if '=' in item:
                adict[item.split('=')[0]] = item.split('=')[1]
            else:
                if len(value) == 1:
                    return value[0]
                alist.append(item)
        if len(adict.keys()) > 0:
            return unflatten(adict)
        else:
            return adict
    else:
        return value


def parse_args(args):
    result = {}
    for key, value in args.items():
        if value is not None:
            result[key] = parse_value(value)
    return result


if __name__ == '__main__':
    allowed_args = arguments()
    try:
        cli_args = allowed_args.parse_args(sys.argv[1:])
        run_cli(cli_args)
    except ValueError as err:
        print(err)
    except KeyError as err:
        print(err)