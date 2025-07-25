import os
import shutil
import sys
import subprocess
from subprocess import Popen, PIPE, CalledProcessError

SRC_RESOURCES = os.path.join(os.getcwd(), 'resources')
ZIP_PLACEMENT_PATH = os.path.join(os.getcwd(), 'dist')


def main():
    if '-d' in sys.argv:
        print('Building debug app...')
        DIST_PATH = os.path.join(os.getcwd(), 'dist', 'debug')
    else:
        DIST_PATH = os.path.join(os.getcwd(), 'dist', 'release')
    DIST_RESOURCES = os.path.join(DIST_PATH, 'resources')

    print('Extracting branch version...')
    branch_name = run_command(['git', 'branch', '--show-current']).strip()

    if "/" not in branch_name or "." not in branch_name:
        print('WARNING: You must checkout a branch in format {release_type}/{X.X.X}')
        sys.exit()

    version = branch_name.split('/')[1]

    with open(os.path.join('resources', 'version.txt'), 'w') as file:
        file.write(f'Version: {version}')

    version_commas = version.replace('.', ', ') + ", 0"

    print('Creating version config from template...')
    fin = open("version_template.YAML", "rt")
    data = fin.read()
    data = data.replace('filevers=(0, 0, 0, 0)',
                        'filevers=(' + version_commas + ')')
    data = data.replace('prodvers=(0, 0, 0, 0)',
                        'prodvers=(' + version_commas + ')')
    data = data.replace("u'ProductVersion', u'0.0.0'",
                        "u'ProductVersion', u'" + version + "'")
    fin.close()

    # Write the data to new output file
    fin = open("version_spec.YAML", "wt")
    fin.write(data)
    fin.close()

    print('Building application...')
    run_long_command(['pyinstaller', 'main.py', '--name', 'StockBench', '--onefile', '--windowed', '--noconfirm',
                      f'--distpath={DIST_PATH}', '--icon=resources/images/candle.ico',
                      '--version-file=version_spec.YAML'])

    print('Building resource directories...')
    os.makedirs(os.path.dirname(DIST_RESOURCES), exist_ok=True)

    print('Copying resource directories...')
    shutil.copytree(SRC_RESOURCES, DIST_RESOURCES, dirs_exist_ok=True)

    print('Build complete.')

    print('Zipping release...')

    zip_base_filepath = os.path.join(ZIP_PLACEMENT_PATH, f'StochBench{version}')
    zip_type = 'zip'

    shutil.make_archive(zip_base_filepath, zip_type, DIST_PATH)

    print('Zip complete.')


def run_command(args: list) -> str:
    try:
        # Run the command and capture its output
        # capture_output=True captures stdout and stderr
        # text=True decodes the output as text (UTF-8 by default)
        result = subprocess.run(args, capture_output=True, text=True, shell=True, check=True)

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
