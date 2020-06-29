import json
import platform
from hashlib import sha256
from typing import Dict, Optional

import distro
from fluent_prov import Agent
from prov.constants import PROV_LABEL
from prov.model import ProvDocument

from ..helper import class_name


class Host(Agent):
    """Class describing the host, on which a command is executed.

    In the PROV context, the host is an agent. The host agent bears responsibility for the
    executed operation, as the host machine's properties heavily influence the outcome of
    the commands executed during the operation. Therefore the operation activity and the host
    agent are connected by an 'acted on behalf of' relation.
    """

    def __init__(self, document: ProvDocument) -> None:
        """Get information about the host.

        The information are gathered using the Python distro and platform package.

        Parameters
        ----------
        document
            The resulting document, to which the host metadata will be added.
        """

        self.host_attributes: Dict[str, Optional[str]] = dict()
        """Attributes describing a host machine.

        The following attributes are inferred by the dist.linux_distribution() command:
        istribution name, distribution version, distribution kernel version,
        The following attributes are inferred by the platform package:
        Processor information and hostname
        """

        # Get information about host and populate the data dictionary
        #TODO linux_distribution is deprecated
        dist = distro.linux_distribution()
        uname = platform.uname()
        self.host_attributes["ex:system"] = platform.system()
        self.host_attributes["ex:dist"] = dist[0]
        self.host_attributes["ex:version"] = dist[1]
        self.host_attributes["ex:codename"] = dist[2]
        self.host_attributes["ex:kernelVersion"] = uname[2]
        self.host_attributes["ex:machine"] = platform.machine()
        self.host_attributes["ex:processor"] = platform.processor()
        self.host_attributes["ex:hostname"] = uname[1]
        self.host_attributes[str(PROV_LABEL)] = class_name(self) + uname[1]
        test = json.dumps(self.host_attributes, sort_keys=True)
        sha = "sha256:" + sha256((test.encode())).hexdigest()
        super().__init__(document, other_attributes=self.host_attributes, uuid=sha)
