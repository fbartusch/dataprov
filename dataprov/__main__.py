import argparse
import logging
import os
import sys
from typing import List, Tuple

from . import __version__
from .config import globalConfig
from .elements.executor import create_empty_executor_config
from .elements.organisation import create_empty_organisation_config


def get_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Automatic provenance metadata creator."
    )

    parser.add_argument("-d", "--debug", help="use verbose logging to debug.", action="store_true")

    parser.add_argument("-q", "--quiet", help="suppress print output", action="store_true")

    parser.add_argument("-v", "--version", help="print version information", action="store_true")

    parser.add_argument(
        "--show-attributes", help="add element attributes to the svg", action="store_true"
    )

    parser.add_argument("--hide-labels", help="hide labels from the svg", action="store_false")

    parser.add_argument(
        "--hide-class-name", help="hide class name from the svg", action="store_false"
    )

    # Default place for resulting provenance file
    #provenance_file_default = "./provenance.prov.xml"
    parser.add_argument(
        "-p",
        "--provenance-file",
        help="Path to resulting provenance file.",
        default=None,
    )

    # Default place for personal information
    executor_default_config_file = os.path.join(
        os.path.expanduser("~"), ".dataprov", "executor.ini"
    )

    parser.add_argument(
        "-e",
        "--executor",
        help=("personal information about executor added" "to recorded metadata."),
        default=executor_default_config_file,
    )

    # Path to output data object
    # This is the URI of the output data object of the wrapped command
    # If the user uses a workflow manager / workflow engine supported
    # by this tool, the output data objects will be detected automatically
    command_output_data_objects: List[str] = []
    parser.add_argument(
        "-o",
        "--output",
        action="append",
        help=(
            "URI to output data objects (file, directory)."
            "The provenance files with the same name + .prov suffix"
            "will be created beside the output data objects"
        ),
        default=command_output_data_objects,
    )

    # If the used command line tool used one or more input data objects,
    # the user Can specifiy the paths to these objects.
    # If there are dataprov metadata files for the input data objects,
    # it will be incorporated into the resulting provenance metadata
    # If the user uses a workflow manager / workflow engine supported
    # by this tool, the output will be handled automatically
    parser.add_argument(
        "-i",
        "--input",
        action="append",
        help=("path to input data objects (file, directory)" "used by the wrapped command"),
        default=None,
    )

    subparsers = parser.add_subparsers(help="dataprov actions", title="actions", dest="command")

    # Run: This subcommand will run arbitrary command line commands
    subparsers.add_parser(
        "run", help=("Run a command line command and create" "provenance metadata")
    )

    # Message incorporated into metadata
    parser.add_argument("-m", "--message", help="message for operation metadata", default="")
    return parser


def parse_arguments() -> Tuple[argparse.Namespace, List[str]]:
    parser = get_parser()

    return parser.parse_known_args()


def main() -> None:
    """Runs Dataprov with user specified command line arguments.

    The command line arguments are further documented by Dataprov's
    help function (-h).

    Returns
    -------
    err_code : int
        Non-zero value indicates error code, or zero on success.
    """

    # Parse command line arguments
    args, remaining = parse_arguments()
    globalConfig.set("show-class-name", not args.hide_class_name)

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    if args.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)
    if args.version:
        print(f"dataprov {__version__}")
        sys.exit(0)

    # No command -> check for .ini files and create them if needed
    if not args.command:
        if not os.path.exists(args.executor):
            create_empty_executor_config(args.executor)
        orga_default_config_file = os.path.join(
            os.path.expanduser("~"), ".dataprov", "organisation.ini"
        )
        if not os.path.exists(orga_default_config_file):
            create_empty_organisation_config(orga_default_config_file)
        sys.exit(0)

    if args.command == "run":
        from dataprov.commands.run import run
        run(args, remaining)


if __name__ == "__main__":
    main()
