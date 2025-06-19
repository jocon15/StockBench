import os
import sys
import subprocess
from subprocess import Popen, PIPE, CalledProcessError

DIST_PATH = 'dist/release'
DIST_RESOURCES = f"{DIST_PATH}/resources"
DIST_RESOURCES_WILDCARD = os.path.join(DIST_PATH, 'resources', '*')


def main():
    branch_name = run_command(['git', 'branch', '--show-current'])

    if "/" not in branch_name:
        print('WARNING: You must checkout a branch in format {release_type}/{X.X.X}')
        sys.exit()

    version = branch_name.split('/')[1]

    with open(os.path.join('resources', 'version.txt'), 'w') as file:
        file.write(f'Version: {version}')

    version_commas = version.replace('.', ', ')

    # Read data from template file
    fin = open("version_template.YAML", "rt")
    data = fin.read()
    data = data.replace('filevers=(78, 0, 3904, 108)',
                        'filevers=(' + version_commas + ')')
    data = data.replace('prodvers=(78, 0, 3904, 108)',
                        'prodvers=(' + version_commas + ')')
    data = data.replace("u'FileVersion', u'78, 0, 3904, 108'",
                        "u'FileVersion', u'" + version + "'")
    data = data.replace("u'ProductVersion', u'78, 0, 3904, 108'",
                        "u'ProductVersion', u'" + version + "'")
    fin.close()

    # Write the data to new output file
    fin = open("version_spec.YAML", "wt")
    fin.write(data)
    fin.close()

    # FIXME: this is commented out until we can get the bottom working
    # run_long_command(['pyinstaller', 'main.py', '--name', 'StockBench', '--onefile', '--windowed', '--noconfirm',
    #                   '--distpath=dist/release', '--icon=resources/images/candle.ico',
    #                   '--version-file=version_spec.YAML'])

    # FIXME: we need to replace this with shutil, the filepaths for dist just are not working
    #   delete resources in dist if it exists
    #   copy/paste resources into dist

    if os.path.exists(DIST_RESOURCES):
        run_command(['del', '/f', '/s', '/q', f'"{DIST_RESOURCES}"'])
    run_command(['rmdir', '/s', '/q', f'"{DIST_RESOURCES}"'])
    run_command(['mkdir', f'"{DIST_RESOURCES}"'])
    run_command(['xcopy', f'"{DIST_RESOURCES}"', f'"{DIST_RESOURCES_WILDCARD}"', '/E', '/H', '/C', '/I', '/Y'])


def run_command(args: list) -> str:
    try:
        # Run the command and capture its output
        # capture_output=True captures stdout and stderr
        # text=True decodes the output as text (UTF-8 by default)
        result = subprocess.run(args, capture_output=True, text=True, shell=True, check=True)

        # Access the standard output
        print("Standard Output:")

        # Access the standard error (if any)
        if result.stderr:
            print("\nStandard Error:")
            print(result.stderr)

        return result.stdout

    except subprocess.CalledProcessError as e:
        # Handle errors if the command returns a non-zero exit code
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        sys.exit()
    except FileNotFoundError:
        print("Error: Command not found. Make sure the command is in your system's PATH.")
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit()


def run_long_command(args: list):
    with Popen(args, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


if __name__ == '__main__':
    main()
