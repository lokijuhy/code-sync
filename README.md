# code_sync
Python utility for syncing code to a remote machine in the background

## Installation
`pip install code_sync`

## Usage

After installing this package, the `code_sync` tool will be available from the command line.

The `code_sync` script allows you to auto-sync any changes to code in a local directory to a remote machine.
Under the hood, it is running an `rsync` command whenever `watchdog` notices changes to the code.

### Example usage
Assuming you have defined `my_remote_machine` in your ssh config:

`code_sync --local_dir mylocaldir/ --remote_dir myremotedir/ --target my_remote_machine --port 2222`

### Notes
**Starting**
* In order to run `code_sync`, you must have an ssh connection open in another window. Once you've entered your password there, `code_sync` uses that connection.
* When you start this script, nothing will happen  until a file in the `local_dir` is touched. This is normal!

**Stopping**
* You can safely quit `code_sync` with control-c.

**About `code_sync` + `git`**
* The destination directory should not be treated as an active git repo.
The destination dir must exist already, but need not already be empty.
If the destination directory is a git repo already, it will be overwritten with the "git state" of the local git directory.
* **Do not run git commands from the destination terminal** on the destination directory.
The destination dir will have its contents synced to exactly match the local dir, including when you checkout a different branch on local.
* The sync command adheres to any filters set by `.gitignore` files within the specified directories.
It also excludes `.git` and `.ipynb` files.
