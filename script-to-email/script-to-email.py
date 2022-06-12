import yaml

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('scripts',
                    metavar='FILE_OR_DIRECTORY',
                    help='Script file to process. If a directory is given, script-to-email will recursively try to process all .yml files')

args = parser.parse_args()

with open(args.scripts, 'r') as script_file:
    script = yaml.safe_load(script_file.read())

    print(script)
