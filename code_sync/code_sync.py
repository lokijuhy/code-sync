#! python

import argparse
import os
from pathlib import Path
import subprocess
import yaml
from typing import Dict, Union


cmd_str = 'watchmedo shell-command --recursive --patterns="{local_dir}*" --command="rsync --filter=\':- .gitignore\' ' \
          '--exclude \'*.ipynb\' --exclude \'.git\' --delete-after -rz --port {port} {local_dir} ' \
          '{target}:{remote_dir}" {local_dir}'

epilog_str = '''
EXAMPLE USAGE
Register a project:
    code_sync --register <project>

code_sync a registered project:
    code_sync <project>

List all projects registered to code_sync:
    code_sync --list

Run code_sync with specific parameters:
    code_sync --local_dir <mylocaldir/> --remote_dir <myremotedir/> --target <ssh_remote> --port 2222\n

'''

CONFIG_FILE_NAME = '.code_sync'


def code_sync(local_dir, remote_dir, target, port=22):
    # clean up slashes
    local_dir = os.path.join(local_dir, '')
    remote_dir = os.path.join(remote_dir, '')

    print("Starting code_sync between {} and {}:{} ...".format(local_dir, target, remote_dir))
    print('(^C to quit)')
    cmd = cmd_str.format(local_dir=local_dir, remote_dir=remote_dir, target=target, port=port)
    subprocess.call(cmd, shell=True)


def load_config() -> Dict:
    """
    Load the code_sync config file. Create a blank one if no file exists.

    Returns:
        The config loaded from the file.
    """

    create_config_if_not_exists()

    config_file_path = Path(Path.home(), CONFIG_FILE_NAME)
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)
    # if config is empty, return an empty dictionary (not None)
    if config is None:
        config = {}
    return config


def init_config() -> None:
    """Create an empty config file."""
    config_path = Path(Path.home(), CONFIG_FILE_NAME)
    open(config_path.__str__(), 'x').close()


def create_config_if_not_exists() -> None:
    """Create the code_sync config if it does not already exist."""
    config_file_path = Path(Path.home(), CONFIG_FILE_NAME)
    if not config_file_path.exists():
        init_config()


def register_project(project: Union[str, None]) -> None:
    """
    Register a project to the code_sync config.

    Args:
        project: The name of the project to register. If None is provided, the user will be asked for a project name.

    Returns:
        None. The result is saved to the code_sync config.

    Raises:
        ValueError if there is already a registered project with the given name.

    """
    if project is None:
        project = input('Project name: ')
    else:
        print("Registering new project '{}'".format(project))

    config = load_config()
    if project in config:
        raise ValueError("Project '{}' is already registered".format(project))

    local_dir = input('Path to code_sync on this local machine: ')
    target = input('Destination machine: ')
    remote_dir = input('Path on the destination machine to sync: ')
    port = int(input('Port number to use (default 22): ') or "22")

    config_entry_data = {
        project: {
            'local_dir': local_dir,
            'target': target,
            'remote_dir': remote_dir,
            'port': port,

        }
    }

    create_config_if_not_exists()
    config_file_path = Path(Path.home(), CONFIG_FILE_NAME)
    with open(config_file_path.__str__(), 'a') as f:
        yaml.dump(config_entry_data, f, default_flow_style=False)

    print("Successfully registered project '{}'".format(project))
    return


def list_projects() -> None:
    """List all projects registered to code_sync."""
    create_config_if_not_exists()
    config = load_config()
    if len(config) == 0:
        print('No projects registered')
    else:
        formatted_keys = ', '.join(list(config.keys()))
        print(formatted_keys)
    return

def identify_code_sync_parameters(args) -> Dict:
    """
    Identify the code_sync parameters. The user may specify a project (which should be registered to the code_sync
        config) or specific all command line arguments.
    Args:
        args: The args object from argparse.

    Returns:
        Dictionary of the parameters to be used for the code_sync command.

    Raises:
        ValueError if the specified project is not registered to the code_sync config.
    """
    if args.project is not None:
        config = load_config()
        if args.project not in config:
            raise ValueError("Project '{}' is not registered".format(args.project))
        parameters = config[args.project]
    else:
        if args.local_dir is None or args.remote_dir is None or args.target is None:
            raise ValueError('Missing argument. If a project is not specified, then local_dir, remote_dir, and target'
                             ' must be specified.')
        parameters = dict()
        parameters['local_dir'] = args.local_dir
        parameters['remote_dir'] = args.remote_dir
        parameters['target'] = args.target
        parameters['port'] = args.local_dir
    return parameters


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_str)
    parser.add_argument('project', nargs='?', default=None)
    parser.add_argument('--register', help='Register a new project to code_sync', required=False)
    parser.add_argument('--list', action='store_true', help='List all registered projects',  required=False)
    parser.add_argument('--local_dir', help='The local code directory you want to sync', required=False)
    parser.add_argument('--remote_dir', help='The remote directory you want to sync', required=False)
    parser.add_argument('--target', help='Specify which remote machine to connect to', required=False)
    parser.add_argument('--port', type=int, help='ssh port for connecting to remote', default=22)
    args = parser.parse_args()

    if args.register is not None:
        register_project(args.register)
    elif args.list:
        list_projects()
    else:
        params = identify_code_sync_parameters(args)
        code_sync(local_dir=params['local_dir'], remote_dir=params['remote_dir'], target=params['target'],
                  port=params['port'])


if __name__ == '__main__':
    main()
