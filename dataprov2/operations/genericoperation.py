import logging
import os
import shutil
import subprocess
import sys
from typing import List, Optional, Set

from fluent_prov import Agent
from prov.constants import PROV_LABEL, PROV_LOCATION, PROV_VALUE
from prov.model import ProvDocument

from ..helper import class_name, hash_file


class GenericOperation(Agent):
    """Class describing a generic operation (software agent).

    In PROV context, a software agent is an agent. A software agent consists of a command,
    that itself is made up by an executable and further arguments.
    The generic software agent is described by the executable, the executable's version.
    The generic software agent runs the command in a subprocess.
    There are several child classes implementing functions of these class in order to handle
    more complex software and commands.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, document: ProvDocument, task: str) -> None:
        """Infer information about th executable and run the code.

        It is assumed, that the executable is the first word of the 'task' argument.
        The path to the executable is inferred by the 'which' command.
        The executable version is inferred by executing the executable with the
        option --version first. If --version is not implemented, -v will be tried.
        Most well written software return a meaningful value for on of these two options.
        Special functionalities should be added to the functions pre_run(), run(), and post_run().

        Parameters
        ----------
        document
            The resulting document, to which the software agent metadata will be added.
        task
            The command to execute.
        """

        self._document = document

        # Get the executable and its path
        self._task = task
        self._executable = self.get_executable()
        self._arguments = self.get_arguments()
        self._executable_path = self.get_executable_path()
        (_, sha_256) = hash_file(self._executable_path)
        sha_256_uuid = "sha256:" + sha_256

        # Get the executable's version
        self._executable_version = self.get_executable_version()

        # Additional input/output files
        self._input_files: Set[str] = set()
        self._output_files: Set[str] = set()

        # Add executable's information to the provenance document
        super().__init__(
            document,
            uuid=sha_256_uuid,
            other_attributes={
                PROV_LOCATION: self._executable_path,
                PROV_LABEL: class_name(self) + self._executable_path,
                PROV_VALUE: self._executable,
                "ex:version": self._executable_version,
            },
        )

    def pre_run(self) -> None:
        """Do things before running the command.

        Subclasses can implement this function to perform actions before running the actual command.
        """

    def run(self) -> None:
        """Run the command as subprocess.

        The subprocess is run via bash -c 'command'. The bash allows for command chaining and
        piping. The standard output and standard error of the subprocess will be written to the log.
        Most of the child classes will implement their own run function.
        """
        logging.info(
            "===================================OUTPUT======================================="
        )
        task = ["bash", "-c", self._task]
        logging.debug(task)
        process = subprocess.Popen(task, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logging.info(
            "===================================OUTPUT======================================="
        )
        logging.info(stdout.decode("utf-8"))
        logging.warning(stderr.decode("utf-8"))

    def post_run(self, op_id: str) -> None:
        """Do things after running the command.

        Subclasses can implement this function to perform actions before running the actual command.

        Parameters
        ----------
        op_id
            ID of the operator to which this agent belongs. The op_id is used to create custom
            relations to the operation, depending on the particular software agent. For example,
            Snakemake software agent creates a workflow plan entity that should be 'generatedBy'
            the operation.
        """

    def get_executable(self) -> str:
        """'Get the executable's name

        It is assumend, that the executable name is the first word of the command.
        """

        return self._task.split()[0]

    def get_arguments(self) -> List[str]:
        """The the arguments

        It is assumend, that the arguments are everything but the first world of the command.
        """

        return self._task.split()[1:]

    def get_executable_path(self) -> str:
        """Get path to the executable

        The output of 'which' is used to get the executable's path. If the output is not meaningful,
        Dataprov will exit with error code 1.
        """

        executable_path = shutil.which(self._executable)
        if not executable_path:
            logging.error("Command not found {}".format(executable_path))
            sys.exit(1)
        return executable_path

    def get_executable_version(self) -> Optional[str]:
        """Get version of the executable

        The function checks the output of
        <executable> --version and <executable> -v
        for version information. It is assumend, that the first line of the output is the
        version number.
        """

        executable_version = ""
        dev_null = open(os.devnull, "w")
        executable_version_output = None
        try:
            executable_version_output = subprocess.check_output(
                [self._executable_path, "--version"], stderr=dev_null
            )
        except subprocess.CalledProcessError:
            pass
        try:
            executable_version_output = subprocess.check_output(
                [self._executable_path, "-v"], stderr=dev_null
            )
        except subprocess.CalledProcessError:
            pass
        if executable_version_output:
            executable_version = executable_version_output.splitlines()[0].decode()

        return executable_version

    def get_input_files(self) -> Set[str]:
        """Get set of input files.

        Some software agent implementations will infer additional input files.

        Returns
        -------
        A set of absolute paths to input files.
        """
        return self._input_files

    def set_input_files(self, files: List[str]) -> None:
        """Set input files used by this operation.

        The input files will be in a 'used' relation to this activity.

        Parameters
        ----------
        files
            List of absolute paths to input files.
        """

    def get_output_files(self) -> Set[str]:
        """Get set of output files.

        Some software agent implementations will infer additional output files.

        Returns
        -------
        A set of absolute paths to output files.
        """
        return self._output_files
