import os.path

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


if os.path.isfile(args.scripts):
    eml_files = handle_file(args.scripts)

    if args.output:
        output = args.output
    else:
        output = os.path.dirname(args.scripts)

    name_pattern = os.path.basename(args.scripts)
    name_pattern = name_pattern.split(".")[0:-1]
    name_pattern = ".".join(name_pattern)
    name_pattern = "{}.{}.eml".format(name_pattern, "{}")
    for index, eml_file in enumerate(eml_files):
        name = name_pattern.format(index)
        with open(os.path.join(output, name), "wb") as output_file:
            output_file.write(eml_file.as_bytes())

if os.path.isdir(args.scripts):
    root_dir = os.path.dirname(args.scripts)
    for root, dirs, files in os.walk(args.scripts):
        yaml_files = [file for file in files if file.endswith(".yml")]
        print("yaml files", root_dir, root, yaml_files)
