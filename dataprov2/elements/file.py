import os

from fluent_prov import Entity
from prov.constants import PROV_LABEL, PROV_LOCATION, PROV_VALUE
from prov.model import ProvDocument

from ..helper import class_name, hash_file


class File(Entity):
    """Class describing a file in Dataprov.

    In the PROV context, a file is an entity. File entities are consumed and created by operations.
    File entities describing input files are in a 'used' relation with an operation.
    File entities describing output files are in a 'generated' relation with an operation.
    A file is described by their location in the file system, name, and hashsum.
    """

    def __init__(self, document: ProvDocument, filepath: str) -> None:
        """Describe a file by its path and hashsum.

        Parameters
        ----------
        document
            The resulting document, to which the file metadata will be added.
        filepath
            Path to the file on the file system.
        """

        self.sha_1: str = ""
        self.sha_256: str = ""

        # Check if the file exists. If the file does not exist, still record some information,
        # as it could be an important file (for example a temporary file deleted by Snakemake after
        # workflow execution)
        if os.path.exists(filepath):
            (self.sha_1, self.sha_256) = hash_file(filepath)
            self.sha_1_uuid = "data:" + self.sha_1
            self.sha_256_uuid = "sha256:" + self.sha_256

            super().__init__(
                document,
                {
                    PROV_LOCATION: filepath,
                    PROV_LABEL: class_name(self) + filepath,
                    PROV_VALUE: os.path.basename(filepath),
                    "ex:sha256": self.sha_256,
                    "ex:sha1": self.sha_1,
                },
                uuid=self.sha_256_uuid,
            )
            # self._document.alternate(self.sha_256_uuid, self.sha_1_uuid)
            # self._document.alternate(self.sha_1_uuid, self.sha_256_uuid)
        else:
            super().__init__(
                document,
                {
                    PROV_LOCATION: filepath,
                    PROV_LABEL: class_name(self) + filepath,
                    PROV_VALUE: os.path.basename(filepath),
                },
                # TODO Placeholder
                uuid="data:" + os.path.basename(filepath),
            )
