#! /usr/bin/env python3

import os
import re
import sys
from subprocess import (
    Popen,
    PIPE,
)
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter,
)


PROJECT_ROOT_DIR = os.path.dirname(__file__).split('/src')[0]


# Create CLI interface
parser = ArgumentParser(
    usage="./%(prog)s \n", formatter_class=RawTextHelpFormatter,
    description="Automatically update repo version across 'version', 'pyproject.toml' and 'README.md' files.\n"
                "Interactively adds, commits, tags and pushes in Git using that version.\n",
)


class SubprocessReturnError(Exception):
    pass


class SubprocessCommandError(Exception):
    pass


def run_subprocess(
        command: str | list,
        print_stdout: bool = True,
        print_command: bool = False,
        capture_output: bool = False
) -> list | None:
    """
    Run a command in a subprocess.
    :param command: Command to execute. If string it will be split into a list of words
    :param print_stdout: Print Subprocess stdout ?
    :param print_command: Print Subprocess command and exit code at termination?
    :param capture_output: If True, return a list of non-empty readlines returned
    :raises SubprocessReturnError: If subprocess return code is != 0
    :raises SubprocessCommandError: If command is not a string or list
    """
    # Make sure command is split and constructed as a list for security purposes
    if type(command) is str:
        command = [cmd for cmd in re.split(r'\s+', command) if cmd]
    elif type(command) is list:
        command = [cmd for cmd in command if cmd]
    else:
        raise SubprocessCommandError(f"Command must be of type 'str' or 'list'")

    process_output = []
    with Popen(command, stdout=PIPE) as process:
        while True:
            try:
                # If process has terminated, handle it
                if process.poll() is not None:
                    if process.returncode != 0:
                        raise SubprocessReturnError(f"Failed executing {command}, exit code: {process.returncode}")

                    if print_command:
                        print(f"Subprocess {command} exited with code: {process.returncode}\n")

                    if capture_output:
                        return process_output
                    else:
                        return None

                # Use read1() instead of read() or Popen.communicate() as both blocks until EOF
                # https://docs.python.org/3/library/io.html#io.BufferedIOBase.read1
                text = process.stdout.read1().decode("utf-8")
                if print_stdout:
                    print(text, end='', flush=True)

                if capture_output and text:
                    process_output.append(text)

            except KeyboardInterrupt:
                sys.exit(f"\nProgram Terminated with KeyboardInterrupt")


parser.parse_args()
try:
    print(f">>> Started {os.path.basename(__file__)}")
    last_version = run_subprocess(f"git describe --tags", capture_output=True, print_stdout=False)[0].strip()

    version = input(f">> Latest version is {last_version}. Specify new version: ")

    run_subprocess(f"poetry version {version}")

    # ------------  Update 'README.md' file ---------------------------------------------------------------------------
    with open(f"{PROJECT_ROOT_DIR}/README.md", 'r') as file:
        old_text = file.read()

    old_version = re.findall(r"### version \S*", old_text)[0]

    if old_version:
        # Replace the all target strings
        new_text = re.sub(old_version, f"### version {version}", old_text)

        with open(f"{PROJECT_ROOT_DIR}/README.md", 'w') as file:
            file.write(new_text)
            print(f"--> Updated 'README.md' file to {version}")

    run_subprocess(f"git commit --interactive")
    run_subprocess(f"git tag -a {version} HEAD")
    run_subprocess(f"git push origin {version}")
    run_subprocess(f"git push")

except SubprocessReturnError as ex:
    print(ex)

except KeyboardInterrupt as ex:
    sys.exit("\n>>> KeyboardInterrupt. Closing down.")
