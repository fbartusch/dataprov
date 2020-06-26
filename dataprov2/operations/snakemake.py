import logging
import os
import random
import subprocess
import warnings
from typing import Dict, Optional

from prov.model import ProvDocument, ProvEntity

import dataprov2.elements.operation as op

from ..elements.file import File
from .genericoperation import GenericOperation

try:
    import snakemake
except ImportError:
    # dependency missing, issue a warning
    warnings.warn("Python package snakemake not found, please install to enable Snakemake feature.")

logger = logging.getLogger(__name__)


class Snakemake(GenericOperation):
    """Class describing a Snakemake command."""

    def __init__(self, document: ProvDocument, task: str) -> None:
        super().__init__(document, task)

        # Initialize instance attributes
        self.snakefile: str = ""
        self.configfile: str = ""
        self.configfile_entity: Optional[File] = None
        self.snakefile_entity: Optional[File] = None
        # Workflow execution is described as prov:Plan (an subclass of prov:Entity)
        # TODO Meaningful workflow ID and information
        self.wf_plan: ProvEntity = self._document.entity("ex:wf" + str(random.randint(0, 100)))
        # Array of workflow steps. The key is the step ID, the value is the operation instance
        # associated with the particular step
        self.workflow_steps: Dict[str, op.Operation] = {}

    def pre_run(self) -> None:
        """Get workflow steps from Snakefile and configuration."""

        # Use Snakemake's argument parser to parse the arguments
        logger.debug("Parse snakemake arguments using the Snakemake argument parser.")
        parser = snakemake.get_argument_parser()
        args = parser.parse_args(self._arguments)
        logger.debug("Parsed snakemake arguments: {}".format(args))

        # Get the path to the Snakefile
        logger.debug("Search for Snakefiles ...")
        if args.snakefile:
            self.snakefile = os.path.abspath(args.snakefile)
            logger.debug("Snakefile specified as argument for Snakemake: {}".format(self.snakefile))
        elif os.path.exists("Snakefile"):
            self.snakefile = os.path.abspath("Snakefile")
            logger.debug("Snakefile found at default location: {}".format(self.snakefile))
        else:
            self.snakefile = ""
            logger.debug("No Snakefile found.")

        if self.snakefile:
            self.snakefile_entity = self._document.entity(
                "ex:snakefile" + str(random.randint(0, 100))
            )
        else:
            # TODO Workflow without Snakefile not possible. Throw exception?
            pass
        # The master Snakefile itself itself can include several other Snakefiles
        # TODO implement this

        # Get the path to the (optional) configuration file
        logger.debug("Search for configuration file ...")
        if args.configfile:
            self.configfile = os.path.abspath(args.configfile)
            logger.debug(
                "Configuration file specified as argument for Snakemake: {}".format(self.configfile)
            )
        elif os.path.exists("config.yaml"):
            self.configfile = os.path.abspath("config.yaml")
            logger.debug("Configuration file found at default location: {}".format(self.configfile))
        else:
            self.configfile = ""
            logger.debug("No configuration file found.")

        # Create configuration file entity
        if self.configfile:
            logger.debug("Create entity for configuration file.")
            self.configfile_entity = File(self._document, self.configfile)
        else:
            self.configfile_entity = None

        # The workflow plan depends on the Snakefiles defining the workflow and the configuration,
        # that defines - among others - input and output files.
        # In PROV context, the workflow plan 'isInfluencedBy' these files.
        if self.configfile_entity:
            logger.debug(
                "Create qualified association between snakemake acticity,"
                "workflow plan, and configuration file."
            )
            self._document.influence(self.wf_plan, self.configfile_entity.id)
        if self.snakefile_entity:
            logger.debug(
                "Create qualified association between snakemake acticity,"
                "workflow plan, and Snakefile."
            )
            self._document.influence(self.wf_plan, self.snakefile_entity)

        # Perform a dryrun to get the workflow steps
        logger.info("Perform workflow dryrun.")
        self.perform_snakemake_dryrun()

    def perform_snakemake_dryrun(self) -> None:
        """Perform snakemake workflow dryrun.

        The parameters --printshellcmds and --dryrun are added to the original task. 'snakemake run'
        is then executed and the output gets parsed to infer the individual workflow steps.
        """

        # TODO Use Snakemake API for this?

        # Perform a dry run on that workflow. --printshellcmds will tell us the
        # procise commands executed by the workflow
        dryrun_command = self._task.split()
        dryrun_command.insert(1, "--dryrun")
        dryrun_command.insert(2, "--printshellcmds")
        logger.debug("Dryrun command: {}".format(dryrun_command))
        dryrun_output = subprocess.check_output(dryrun_command).splitlines()

        # Iterate over the lines, create an operation activity with a corresponding software agent
        # for each rule. In PROV context, each rule's activity is has a qualified association
        # with the software agent, that is also linked to the abstract workflow plan
        # by prov:hadPlan.
        logger.debug("Start parsing dry run output.")
        rule_ended = True
        command_next = False
        logger.debug("Dryrun output: {}".format(dryrun_output))
        for line in dryrun_output:
            line_decoded = line.decode("ascii").strip()
            if line_decoded.startswith("rule"):
                # Get the rule name from string: "rule <name>:"
                rule_name = line_decoded.split()[1][:-1]
                logger.debug("Found new rule: {}".format(rule_name))
                if rule_name == "all":
                    break

                # If snakemake was called with rule 'all', 'all' will be the last rule
                # TODO Maybe we can tell from jobid: 0 that we reached the last rule
                rule_ended = False
            elif line_decoded.startswith("input: "):
                # String format: "input: <input1>, <input2>, ..., <inputN>
                step_in_files = {os.path.abspath(i.strip()) for i in line_decoded[7:].split(",")}
                logger.debug("Found rule inputs: {}".format(step_in_files))
            elif line_decoded.startswith("output: "):
                # String format: "output: <output1>, <output2>, ..., <outputN>
                step_out_files = {os.path.abspath(o.strip()) for o in line_decoded[8:].split(",")}
                logger.debug("Found rule outputs: {}".format(step_out_files))
            elif line_decoded.startswith("jobid"):
                # String format: "jobid: <ID>"
                step_jobid = line_decoded[7:].strip()
                logger.debug("Found rule job id: {}".format(step_jobid))
            elif len(line_decoded) == 0 and not rule_ended:
                command_next = True
                rule_ended = True
            elif command_next:
                step_command = line_decoded.strip()
                if len(step_command) == 0:
                    logger.debug("Command empty, do not track this step")
                    continue

                if step_command.startswith("["):
                    # The rule does not have Shell or Python code.
                    # Maybe it uses the script directive. Infer script location from Snakefiles
                    # and add information about the script to provenance information.
                    # TODO Implement
                    step_command = "script directive."

                # We've seen every parameter of the rule. Create the operation describing this
                # workflow step
                logger.debug("Found rule command: {}".format(step_command))
                logger.debug(
                    "Create new operation for this step and add it to workflow step dictionary"
                )
                new_step = op.Operation(self._document, step_in_files, step_out_files, step_command)
                # Add new stop to the dictionary of workflow steps
                self.workflow_steps[step_jobid] = new_step
                command_next = False
                rule_ended = True
        logger.debug("Finished parsing dry run output.")
        logger.debug("Workflow steps: {}".format(self.workflow_steps))

    def run(self) -> None:
        """Overwrite the generic method, because we have to use the snakemake API."""

        # Overwrite the generic method, because we have to use the snakemake API
        logger.debug(
            "Run snakemake.main with the original arguments: {}".format(self.get_arguments())
        )
        try:
            snakemake.main(self.get_arguments())
        except SystemExit:
            # snakemake main wants to exit ... but we want to write the xml files first
            return

    def post_run(self, op_id: str) -> None:
        """Add workflow steps to the provenance document.

        Each workflow step consists of an activity, which has a qualitive association with a
        software agent and the workflow plan. In addition, input/output files of the step are
        associated to the activity.
        """

        # In PROV context, the workflow execution was generated by the 'snakemake run' operation,
        # that is represented by an instance of the Operation class
        logger.debug("Create relation: workflow plan was generated by snakemake operation")
        logger.debug("Snakemake software agent: {}".format(self.id))
        self.wf_plan.wasGeneratedBy(op_id)

        for step_id in self.workflow_steps:
            cur_operation = self.workflow_steps[step_id]
            # Add activity
            # TODO Add also plan. Add this as option to add_to_document
            #  function implemented in Operation.py
            logger.debug(
                "Add Snakemake workflow step to provenance document: {}".format(cur_operation)
            )
            cur_operation.add_to_document(create_association=False)
            logger.debug(
                "Associate current Snakemake workflow step with its operation and software agent."
            )
            self._document.wasAssociatedWith(
                cur_operation.id, cur_operation.software_agent.id, plan=self.wf_plan
            )
            logger.debug("Add input/output files to the current Snakemake workflow step.")
            # Link input/output files
            cur_operation.link_input()
            cur_operation.link_output()
