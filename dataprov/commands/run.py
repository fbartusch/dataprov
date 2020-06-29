import logging
import os
import sys
from argparse import Namespace
from typing import List, NoReturn, Set

from prov.model import ProvDocument

from .. import __version__
from ..elements.environment import Environment
from ..elements.executor import Executor
from ..elements.host import Host
from ..elements.operation import Operation
from ..helper import sort

logger = logging.getLogger(__name__)

# Namespaces used in the resulting XML file
NAMESPACES = {
    ("ex", "example"),
    ("web", "https://"),
    ("uuid", "urn:uuid"),
    ("data", "urn:hash::sha1:"),
    ("sha256", "urn:hash::sha256:"),
    ("orcid", "https://orcid.org/"),
    ("github", "https://github.com/"),
    ("linkedin", "https://www.linkedin.com/"),
}


def run(args: Namespace, remaining: List[str]) -> NoReturn:
    """Runs Dataprov with the specified arguments.

    This subcommand executes the command specified by remaining the remaining argument
    as a subprocess and captures provenance metadata for each chosen output file. The output files
    can be chosen individually by the user or can be inferred from the wrapped command.
    Output files can only be inferred, if the wrapped command uses a workflow system supported by
    Dataprov (e.g. Snakemake). If input files are specified (or inferred from the wrapped
    command), their provenance information is included in the provenance files of the results.

    Parameters
    ----------
    args
        User specified command line arguments parsed by the ArgumentParser in the main method.
    remaining
        User specified command that will be run in a subprocess
    """

    # Check if remaining command is empty
    if not remaining:
        logger.info("No command to run specified. Dataprov exits.")
        sys.exit(0)

    # First, check for valid executor file and valid path to the organisation file(s)

    document = ProvDocument()
    for namespace in NAMESPACES:
        document.add_namespace(namespace[0], namespace[1])
    command_output_data_objects: List[str] = []
    command_input_data_objects: List[str] = []
    if args.output:
        command_output_data_objects = args.output
    if args.input:
        command_input_data_objects = args.input
    # logger.basicConfig(level=logging.DEBUG)
    logger.debug(f"This is Dataprov {__version__}")
    logger.debug(
        f"""
    Arguments: {str(args)}
    Remaining: {str(remaining)}
    Personal information: {args.executor}
    Command outputs: {str(command_output_data_objects)}
    Input metadata files: {str(command_input_data_objects)}
    Message: {args.message}"""
    )

    # Get absolute paths to input data files
    input_data_objects: Set[str] = {
        os.path.abspath(input_data_object) for input_data_object in command_input_data_objects
    }
    logger.debug(f"Input files: {input_data_objects}")

    # Get absolute paths to output data files
    output_data_objects: Set[str] = {
        os.path.abspath(output_data_object) for output_data_object in command_output_data_objects
    }
    logger.debug(f"Output files: {output_data_objects}")

    # Load user information
    # TODO what if the executor file is not in a home directory? Then expanduser does not work?
    logger.debug("Get executor information.")
    executor = Executor(document, os.path.expanduser(args.executor))

    # Get information about the host
    logger.debug("Get host information")
    host = Host(document)
    host.actedOnBehalfOf(executor)

    # Get information about the environment
    # - Environment variables
    # - Virtual environments (e.g. conda)
    # - installed python packages(?)
    environment = Environment(document)
    #TODO Which relation btw. environment and activity?


    # Create the operation activity. Link the input entities to it and run the operation.
    # In the end, link input/output files to the activity and add the operation to the document
    logger.debug("Create operation for command: {}".format(" ".join(remaining)))
    operation = Operation(document, input_data_objects, output_data_objects, " ".join(remaining))
    # TODO Maybe we have to divide run also into smaller parts to get the order of inserting
    # element right.
    logger.debug("Run operation.")
    operation.run()
    logger.debug("Link input of operation.")
    operation.link_input()
    logger.debug("Link output of operation")
    operation.link_output()

    if operation.software_agent:
        logger.debug("Add relation: Software agent acted on behalf of executor.")
        operation.software_agent.actedOnBehalfOf(executor)
    logger.debug("Add relation: Operation was associated with host and executor.")
    operation.wasAssociatedWith(host, executor)

    # TODO Check if this is a valid path and we can write there
    provenance_file = os.path.abspath(args.provenance_file)
    logger.info("Writing final provenance file: {}".format(provenance_file))
    export_document = ProvDocument()
    for i in sort(document.records):
        export_document.add_record(i)
    export_document.serialize(provenance_file, format="xml")
    # document.serialize(output_file + ".json", indent=2)
    logger.debug("Export final provenance to plot: {}".format(provenance_file + ".svg"))
    export_document.plot(
        provenance_file + ".svg",
        show_element_attributes=args.show_attributes,
        use_labels=args.hide_labels,
    )
    sys.exit(0)
