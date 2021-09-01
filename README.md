# code_sync
`code_sync` auto-syncs your code changes in a local directory to a remote machine,
so that you can edit your code in your local editor and instantly run those change on a remote machine.

Under the hood, `code_sync` is running an `rsync` command whenever `watchdog` notices changes to the code.

## Installation
`pip install code_sync`

After installing this package, the `code_sync` tool will be available from the command line.


## Usage

#### Register a project
    code_sync --register <project>
This will prompt you to enter the local directory to sync,
the remote machines to sync to,
and the destination path on the remote to sync the files to.

Once you register a project with `code_sync`, it will remember that configuration.

#### code_sync a registered project
    code_sync <project>
This command will use the configuration you set for the project when you registered it.

#### List all projects registered to code_sync
    code_sync --list

#### Run code_sync with specific parameters
    code_sync --local_dir <mylocaldir/> --remote_dir <myremotedir/> --target <ssh_remote> --port 2222\n

#### Edit or delete a registered project
    code_sync --edit <project>
    code_sync --delete <project>

### Notes
**Starting**
* In order to run `code_sync`, you must have an ssh connection open in another window.
Once you've entered your password there, `code_sync` uses that connection.
* The destination dir must exist already, but need not be empty.

**Stopping**
* You can safely quit `code_sync` with control-c.

**About `code_sync` + `git`**
* `code_sync` does not sync files that are excluded by `.gitignore`, if present in the local directory.
It also does not sync `.git` and `.ipynb` files.
* The destination directory should not be treated as an active git repo.
* **Do not run git commands from the destination terminal** on the destination directory.
The destination dir will have its contents synced to exactly match the local dir, including when you checkout a different branch on local.
