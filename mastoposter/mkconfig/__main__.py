from argparse import ArgumentParser, Namespace
from os.path import exists
from rich.prompt import Confirm
from rich import print

parser = ArgumentParser(
    "mastoposter.mkconfig",
    description="Configuration script for mastoposter",
    epilog="For detailed description of configuration file, "
    "visit https://github.com/hatkidchan/mastoposter",
)

parser.add_argument(
    "-o", dest="output", required=True, help="Path of output file"
)

parser.add_argument(
    "-f", dest="force", action="store_true", help="Force overwrite"
)


def main(args: Namespace):
    if exists(args.output) and not args.force:
        print("[red]File already exists. It will be overwritten in the end")
        if not Confirm.ask("Continue?"):
            return 1

    # TODO


if __name__ == "__main__":
    from sys import argv

    exit(main(parser.parse_args(argv[1:])))
