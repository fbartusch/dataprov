import warnings

from fluent_prov import Entity
from prov.constants import PROV_LABEL, PROV_TYPE, PROV_VALUE
from prov.model import ProvDocument

from ..helper import class_name

try:
    from docker.models.images import Image
except ImportError:
    # dependency missing, issue a warning
    warnings.warn("Python package docker not found, please install to enable Docker feature.")


class DockerImage(Entity):
    """Class describing a Docker image."""

    def __init__(self, document: ProvDocument, image: Image):  # type: ignore
        """Describe a Docker image by its ID and image tag.

        Parameters
        ----------
        document
            The resulting document, to which the Docker image metadata will be added.
        image
            Docker image name.
        """

        image_tag = image.attrs["RepoTags"][0]
        super().__init__(
            document,
            {
                PROV_LABEL: class_name(self) + image_tag,
                PROV_VALUE: image_tag,
                PROV_TYPE: "docker:image",
            },
            uuid=image.attrs["Id"],
        )
