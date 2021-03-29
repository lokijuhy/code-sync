#! python

import argparse
import os
import subprocess

cmd_str = 'watchmedo shell-command --recursive --patterns="{local_dir}*" --command="rsync --filter=\':- .gitignore\' ' \
          '--exclude \'*.ipynb\' --exclude \'.git\' --delete-after -rz --port {port} {local_dir} ' \
          '{target}:{remote_dir}" {local_dir}'

epilog_str = '''
Example for connecting to LeoMed:
    code_sync --local_dir mylocaldir/ --remote_dir myremotedir/ --target medinfmk --port 2222\n

'''


def code_sync(local_dir, remote_dir, target, port=22):
    # clean up slashes
    local_dir = os.path.join(local_dir, '')
    remote_dir = os.path.join(remote_dir, '')

    # subprocess.call()
    cmd = cmd_str.format(local_dir=local_dir, remote_dir=remote_dir, target=target, port=port)
    subprocess.call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_str)
    parser.add_argument('--local_dir', help='the local code directory you want to sync', required=True)
    parser.add_argument('--remote_dir', help='the remote directory you want to sync', required=True)
    parser.add_argument('--target', help='specify which remote machine to connect to', required=True)
    parser.add_argument('--port', type=int, help='ssh port for connecting to remote', default=22)

    args = parser.parse_args()

    code_sync(local_dir=args.local_dir, remote_dir=args.remote_dir, target=args.target, port=args.port)


if __name__ == '__main__':
    main()
