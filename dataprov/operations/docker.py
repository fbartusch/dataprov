import logging
import subprocess
import warnings
from typing import Optional

from ..elements.dockerimage import DockerImage
from .genericoperation import GenericOperation

try:
    import docker
    from docker.models.images import Image
except ImportError:
    # dependency missing, issue a warning
    warnings.warn("Python package docker not found, please install to enable Docker feature.")


class Docker(GenericOperation):
    """Class describing a Docker command.

    Additional information will contain details about the Docker image,
    in which the command is executed.
    """

    image: Optional[Image] = None  # type:ignore
    _docker_and_pipe = False

    def run(self) -> None:
        """Run Docker command.

        The docker command is run. The container ID is inferred from the subprocess output.
        The Python Docker client package is used to get details about the Docker container.
        If there was a '--rm' flag in the original Docker command, we run the command without --rm
        to be able to capture the running container's ID. We remove the container manually after
        the container exited.
        """

        client = docker.from_env()

        if self._task.split()[1] == "run":
            self._docker_and_pipe = (
                self._task.find(">") == -1
                or self._task.find("<") == -1
                or self._task.find("|") == -1
            )
            self._task = self._task.replace("docker run", "docker run -d", 1)
            task = self._task.replace(" --rm ", "", 1)
            logging.debug(task)
            container_id = subprocess.check_output(task.split()).decode("utf-8").strip()
            container = client.containers.get(container_id)
            image_id = container.attrs["Image"]
            self.image = DockerImage(self._document, client.images.get(image_id))
            container.wait()
            logging.info(container.logs().decode("utf-8"))
            if task is not self._task:
                container.remove()

        else:
            super().run()

    def post_run(self, op_id: str) -> None:
        if self._docker_and_pipe:
            logging.warning(
                """
Docker and unix pipe symbols detected.
This command might not have worked as expected.
Fore more information visit https://github.com/fbartusch/dataprov/
"""
            )
