#! python

import argparse
import os
from pathlib import Path
import subprocess
import yaml
from typing import Dict


rsync_cmd_str = 'rsync --filter=\':- .gitignore\' ' \
          '--exclude \'*.ipynb\' --exclude \'.git\' --delete-after -rz --port {port} {local_dir} ' \
          '{target}:{remote_dir}'

cmd_str = 'watchmedo shell-command --recursive --patterns="{local_dir}*" --command="{rsync_cmd}" {local_dir}'

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


def code_sync(local_dir, remote_dir, target, port=22, verbose=False):
    # clean up slashes
    local_dir = os.path.expanduser(local_dir)
    local_dir = os.path.join(local_dir, '')
    remote_dir = os.path.join(remote_dir, '')

    print(f"Starting code_sync between {local_dir} and {target}:{remote_dir} ...")
    rsync_cmd = rsync_cmd_str.format(local_dir=local_dir, remote_dir=remote_dir, target=target, port=port)
    print('Running startup sync:')
    if verbose:
        print('Running command: {}'.format(rsync_cmd))
    subprocess.call(rsync_cmd, shell=True)
    print('  ... startup sync complete.')

    watchmedo_cmd = cmd_str.format(rsync_cmd=rsync_cmd, local_dir=local_dir)
    print('Code-sync running')
    if verbose:
        print('Running command: {}'.format(watchmedo_cmd))
    print('(^C to quit)')
    subprocess.call(watchmedo_cmd, shell=True)


def get_config_file_path() -> Path:
    return Path(Path.home(), CONFIG_FILE_NAME)


def load_config() -> Dict:
    """
    Load the code_sync config file. Create a blank one if no file exists.

    Returns:
        The config loaded from the file.
    """

    create_config_if_not_exists()

    config_file_path = get_config_file_path()
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)
    # if config is empty, return an empty dictionary (not None)
    if config is None:
        config = {}
    return config


def init_config() -> None:
    """Create an empty config file."""
    config_path = get_config_file_path()
    open(config_path.__str__(), 'x').close()


def create_config_if_not_exists() -> None:
    """Create the code_sync config if it does not already exist."""
    config_file_path = get_config_file_path()
    if not config_file_path.exists():
        init_config()


def save_config(config: Dict, mode='a') -> None:
    """
    Save the code-sync config to file.

    Args:
        config: The code-sync config dictionary.
        mode: File mode. May be either 'a' for append or 'w' for write.

    Returns: None

    """
    if mode not in ['a', 'w']:
        raise ValueError(f"Config must be edited in mode 'a' or 'w', received '{mode}'")

    create_config_if_not_exists()
    config_file_path = get_config_file_path()
    with open(config_file_path.__str__(), mode) as f:
        yaml.dump(config, f, default_flow_style=False, indent=4)


def get_project_config_from_user() -> Dict:
    """
    Ask the user for the information for the project config.

    Returns: A dictionary with the config for the project, including local_dir, target, remote_dir, and port.

    """
    local_dir = input('Path to code_sync on this local machine: ')
    target = input('Destination machine (name of ssh config entry): ')
    remote_dir = input('Path on the destination machine to sync: ')
    port = int(input('Port number to use (default 22): ') or "22")
    project_details = {
        'local_dir': local_dir,
        'target': target,
        'remote_dir': remote_dir,
        'port': port,
    }
    return project_details


def register_project(project: str) -> None:
    """
    Register a project to the code_sync config.

    Args:
        project: The name of the project to register.

    Returns:
        None. The result is saved to the code_sync config.

    Raises:
        ValueError if there is already a registered project with the given name.

    """
    config = load_config()
    if project in config:
        raise ValueError(f"Project '{project}' is already registered")

    print(f"Registering new project '{project}'")
    project_config = get_project_config_from_user()

    project_config_entry = {
        project: project_config
    }

    save_config(project_config_entry)
    print(f"Successfully registered project '{project}'")
    return


def list_projects() -> None:
    """List all projects registered to code_sync."""
    create_config_if_not_exists()
    config = load_config()
    if len(config) == 0:
        print('No projects registered')
        return

    formatted_keys = ', '.join(list(config.keys()))
    print(formatted_keys)


def delete_project(project_name: str) -> None:
    """Delete the config entry of the registered project."""
    create_config_if_not_exists()
    original_config = load_config()
    if len(original_config) == 0:
        print('No projects registered')
        return
    elif project_name not in original_config:
        raise ValueError(f"Project '{project_name}' does not exist")

    config = original_config.copy()
    config = delete_project_from_config(project_name, config)

    save_config(config, mode='w')
    print(f'Deleted {project_name} from code-sync config.')


def edit_project(project_name: str) -> None:
    """Edit the config entry of the registered project."""
    create_config_if_not_exists()
    original_config = load_config()
    if len(original_config) == 0:
        print('No projects registered')
        return
    elif project_name not in original_config:
        raise ValueError(f"Project '{project_name}' does not exist")

    config = original_config.copy()
    config = edit_project_config(project_name, config)

    save_config(config, mode='w')
    print(f'Updated code-sync config for project {project_name}.')


def delete_project_from_config(project: str, config: Dict) -> Dict:
    """Delete a project entry from the config dictionary."""
    config.pop(project)
    return config


def edit_project_config(project: str, config: Dict) -> Dict:
    """
    Edit the project config entry for a project that already exists in the code-sync config.

    Args:
        project: The project name (key in the code-sync config).
        config: The global code-sync config.

    Returns:

    """
    print(f"Enter details for project '{project}'")
    project_config = get_project_config_from_user()
    config[project] = project_config
    return config


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
            raise ValueError(f"Project '{args.project}' is not registered")
        parameters = config[args.project]
    else:
        if args.local_dir is None or args.remote_dir is None or args.target is None:
            raise ValueError('Missing argument. If a project is not specified, then local_dir, remote_dir, and target'
                             ' must be specified.')
        parameters = dict()
        parameters['local_dir'] = args.local_dir
        parameters['remote_dir'] = args.remote_dir
        parameters['target'] = args.target
        parameters['port'] = args.port
    return parameters


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_str)
    parser.add_argument('project', nargs='?', default=None)
    parser.add_argument('--register', help='Register a new project to code_sync', required=False)
    parser.add_argument('--list', action='store_true', help='List all registered projects',  required=False)
    parser.add_argument('--edit', help='Edit the config for a registered project.',  required=False)
    parser.add_argument('--delete', help='Delete the config for a registered project.',  required=False)
    parser.add_argument('--local_dir', help='The local code directory you want to sync', required=False)
    parser.add_argument('--remote_dir', help='The remote directory you want to sync', required=False)
    parser.add_argument('--target', help='Specify which remote machine to connect to', required=False)
    parser.add_argument('--port', type=int, help='ssh port for connecting to remote', default=22)
    parser.add_argument('--verbose', help='Print verbose output', default=False, action='store_true')
    args = parser.parse_args()

    if args.register is not None:
        register_project(args.register)
    elif args.list:
        list_projects()
    elif args.edit:
        edit_project(args.edit)
    elif args.delete:
        delete_project(args.delete)
    else:
        params = identify_code_sync_parameters(args)
        code_sync(local_dir=params['local_dir'], remote_dir=params['remote_dir'], target=params['target'],
                  port=params['port'], verbose=args.verbose)


if __name__ == '__main__':
    main()
