import os.path
import re
import sys
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from typing import List, Set

import yaml

from lib.script import Script
from argparse import ArgumentParser
from lib.generator import Generator

parser = ArgumentParser()
parser.add_argument(
    "scripts",
    metavar="FILE_OR_DIRECTORY",
    help="Script file to process. If a directory is given, script-to-email will recursively try to process all .yml files",
)
parser.add_argument(
    "-o",
    "--output",
    help="This is where generated email "
    "files will be saved. If a "
    "directory is processed the "
    "directory structure will be "
    "replicated",
)

args = parser.parse_args()


def handle_file(file: str):
    with open(file, "r") as entry_point:
        script_data = yaml.safe_load(entry_point)

    script = Script.deserialize(script_data, entry_point.name)

    generator = Generator(script)

    return generator.generate_emails()


def make_filename(eml: EmailMessage, existing_filenames: Set[str]) -> str:
    parsed_date = parsedate_to_datetime(eml['date'])
    formatted_date = parsed_date.strftime('%Y-%m-%d')

    subject = eml['subject'].replace(':', '_')
    subject = subject.replace('.', '_')
    subject = subject.replace(' ', '-')
    subject = subject.lower()
    subject = re.sub(r'[^a-z0-9_-]', '', subject)

    filename = f'{formatted_date}_{subject}'
    index = 2
    while filename in existing_filenames:
        filename = '_'.join(filename.split('_')[:-1]) + f'_{index}'
        index += 1
        if index > 10:
            print('something went wrong, too many emails with the same name')
            print(filename, existing_filenames)
            sys.exit(1)

    return f'{filename}.eml'


def generate_file(file: str):
    print('WARNING: Output file name generation has been changed. This can be confusing and might need to be changed')
    eml_files = handle_file(file)

    if args.output:
        output = args.output
    else:
        output = os.path.dirname(file)

    existing_filenames: Set[str] = set()

    name_pattern = os.path.basename(file)
    name_pattern = name_pattern.split(".")[0:-1]
    name_pattern = ".".join(name_pattern)
    name_pattern = "{}.{}.eml".format(name_pattern, "{}")
    for index, eml_file in enumerate(eml_files):
        name = name_pattern.format(index)
        name = make_filename(eml_file, existing_filenames)
        existing_filenames.add(name)
        with open(os.path.join(output, name), "wb") as output_file:
            output_file.write(eml_file.as_bytes())


if os.path.isfile(args.scripts):
    generate_file(args.scripts)

if os.path.isdir(args.scripts):
    root_dir = os.path.dirname(args.scripts)
    for root, dirs, files in os.walk(args.scripts):
        yaml_files = [file for file in files if file.endswith(".yml")]
        for file in yaml_files:
            print('generating file {}'.format(os.path.join(root, file)))
            generate_file('{}'.format(os.path.join(root, file)))
