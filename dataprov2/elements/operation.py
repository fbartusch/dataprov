import html
import logging
from datetime import datetime
from typing import Any, Set

from fluent_prov import Activity
from prov.constants import PROV_LABEL
from prov.model import ProvDocument

from ..helper import class_name
from ..operations.commandline import CommandLine
from ..operations.cwl import CWL
from ..operations.docker import Docker
from ..operations.snakemake import Snakemake
from .file import File

logger = logging.getLogger(__name__)


class Operation(Activity):
    """Class describing an operation.

    In the PROV context, an operation is an activity. The operation can consume, modify,
    and generate input and output files. Thus, these file entities are in a 'used' and 'generated'
    relation with the operation. In the computational context, the operation activity consists of
    a command executed with some arguments. In PROV context, the executed command is a software
    agent, which is in a 'wasAssociatedWith' relation with operation.
    The software agent's implementation is responsible for the command's execution.
    The operation is executed by an executor and influenced by the host machine,
    thus the operation is in an 'acted on behalf of' relation with these agents.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=super-init-not-called

    def __init__(
        self, document: ProvDocument, input_files: Set[str], output_files: Set[str], task: str
    ) -> None:
        """Chooses software agent and captures software independent metadata.

        The software independent metadata is start and end time of the operation. In between,
        the software agent's implementation runs the command and also collects software specific
        provenance metadata.

        Parameters
        ----------
        document
            The resulting document, to which the operation metadata will be added.
        input_files
            Set of input files specified by the user.
            For each input file, Dataprov checks if provenance metadata exists and incorporates
            the input's provenance to the output's provenance files. Some software agents can
            infer input files theirself. These are then added to this set.
        output_files
            Set of output files specified by the user, for which Dataprov will capture
            provenance metadata. Some software agents can infer output files theirself.
            These are then added to this set.
        task
            The command to execute
        """

        self.document = document
        self.input_files = input_files
        self.output_files = output_files
        self.task = task
        self.software_agent: Any
        self.starttime: str = ""
        self.endtime: str = ""

        # Choose the type of software agent to use. (e.g. Docker, Singularity, commandLine, ...)
        # The software agent is responsible for the commands execution and collecting of
        # software specific provenance information
        executable = task.split()[0]
        if executable == "docker":
            self.software_agent = Docker(document, task)
            self.docker_image = self.software_agent.image
        # elif executable == "singularity":
        #    self.singularity_container = Singularity(document, task)
        elif executable == "snakemake":
            self.software_agent = Snakemake(document, task)
        elif executable == "cwltool":
            self.software_agent = CWL(document, task)
        else:
            # Generic command line tool
            self.software_agent = CommandLine(document, task)

    def run(self) -> None:
        """
        Run the command using the software agent

        This is not done via __init__, as sometimes you do not want to run the command.
        This is the case, if the activity is part of a workflow and the workflow runs the steps
        itself (e.g. Snakemake).

        Returns
        -------

        """

        # Maybe the software agent wants to perform some actions before running the software
        logger.info("Call software agent pre_run function.")
        self.software_agent.pre_run()
        logger.info("Returned from software agent pre_run function.")

        # Let software agent run the command
        self.starttime = str(datetime.now())
        logger.info("Call software agent run function")
        self.software_agent.run()
        logger.info("Return from software agent run function")
        self.endtime = str(datetime.now())

        logger.info("Add operation to the provenance document.")
        self.add_to_document()

        # Maybe the software agent wants to perform some actions after running the software
        logger.info("Call software agent post_run function")
        self.software_agent.post_run(self.uuid)
        logger.info("Return from software agent post_run function")

    def add_to_document(self, create_association: bool = True) -> None:
        """Add this operation to the provenance document.

        Returns
        -------

        """
        if self.starttime and self.endtime:
            super().__init__(
                self.document,
                self.starttime,
                self.endtime,
                {
                    PROV_LABEL: class_name(self) + html.escape(self.task),
                    "ex:task": html.escape(self.task),
                },
            )
        else:
            # TODO Start/End time not meaningful. Do not set it.
            super().__init__(
                self.document,
                str(datetime.now()),
                str(datetime.now()),
                {
                    PROV_LABEL: class_name(self) + html.escape(self.task),
                    "ex:task": html.escape(self.task),
                },
            )

        # Some software agents create qualified associations.
        # In this case, this generic association is not needed
        if create_association:
            self.wasAssociatedWith(self.software_agent)

    def link_input(self) -> None:
        """Link input files to the operation activity.

        Returns
        -------

        """

        # Add input files' provenance to the provenance document
        input_file_entities = []
        for input_file in self.input_files:
            input_file_entities.append(File(self.document, input_file))
        #    prov_file = input_file + ".prov.xml"
        #    deserialize(self._document, prov_file)
        self.used(*input_file_entities)
        self.used(*input_file_entities)

    def link_output(self) -> None:
        """Link output files to the operation activity.

        Returns
        -------

        """

        # Add output files to the provenance document
        for output_file in self.output_files:
            # TODO check for duplicates?
            File(self.document, output_file).wasGeneratedBy(self)

        # TODO Make this a method of the software agent.
        #  E.g. linking additional entities to the operation
        # if self.docker_image:
        #    self.used(self.docker_image)
