import warnings
from os import path
from tempfile import TemporaryDirectory

from ..helper import deserialize
from .genericoperation import GenericOperation

try:
    import cwltool
    import cwltool.argparser
except ImportError:
    # dependency missing, issue a warning
    warnings.warn("Python package cwltool not found, please install to enable CWL feature.")


class CWL(GenericOperation):
    """Class describing a Common Workflow Language (CWL) command."""

    def run(self) -> None:
        """Run Common Workflow Language (CWL) command.

        This method uses the Python cwltool package to parse the command and infer automatically
        input files, output files, and CWL configuration
        """

        cwltool_parser = cwltool.argparser.arg_parser()

        parsed_arguments = cwltool_parser.parse_args(self._task.split()[1:])
        with TemporaryDirectory() as tmpdir:
            if not parsed_arguments.provenance:
                self._task = (
                    self._task.split()[0]
                    + " --provenance "
                    + tmpdir
                    + " "
                    + " ".join(self._task.split()[1:])
                )
                parsed_arguments = cwltool_parser.parse_args(self._task.split()[1:])

            metadata_path = path.join(
                parsed_arguments.provenance, "metadata", "provenance", "primary.cwlprov.xml"
            )
            super().run()
            deserialize(self._document, metadata_path)
