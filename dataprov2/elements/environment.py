import os
import distro
import platform
import random
import subprocess

from typing import Dict, Optional
from prov.constants import PROV_LABEL
from prov.model import ProvDocument, ProvEntity

#TODO Function creating conda environments from captured metadata
#TODO Function creating pip environment from captured metadata
#TODO Function returning kind of sourcable ~/.bashrc recreating the environment
#TODO Function returning basic information about very basic system information like compiler, glibc
# etc


class Environment(ProvEntity):
    """Class describing the environment in which an operation is performed.

    In the PROV context, the environment is an entity. Among others, the environment influences
    the outcome of an operation via environment variables.
    Also virtual environments (e.g. conda), loaded environment modules, installed system packages,
    and installed modules for programming languages like Python or Perl are important for the
    operation.
    """

    def __init__(self, document: ProvDocument) -> None:
        """Capture information from the environment.

        Parameters
        ----------
        document
            The resulting document, to which the environment information will be added.
        """

        super().__init__(document, "ex:12345")

        # The underlying operating system
        self.os = OperatingSystem(document)

        # All environment variables
        self.env_variables = EnvironmentVariables(document)

        # Add operating system entity, environment variables, etc as members of the environment
        # collection entity
        self.hadMember(self.os)
        self.hadMember(self.env_variables)

        # Get a list of all installed system packages and their versions
        # Complete list of reliable IDs returned by distro.id():
        # https://distro.readthedocs.io/en/latest/#distro.id
        # self.system_packages = {}
        # dist = distro.id()
        # if dist == "centos":
        #     self.system_packages = self.yum_get_packages()
        # elif dist == "ubuntu":
        #     pass
        # elif dist == "debian":
        #     pass
        # elif dist == "rhel":
        #     self.system_packages = self.yum_get_packages()
        # elif dist == "fedora":
        #     pass
        # elif dist == "sles":
        #     pass
        # elif dist == "opensuse":
        #     pass
        # elif dist == "amazon":
        #     pass
        # elif dist == "arch":
        #     pass
        # elif dist == "cloudlinux":
        #     pass
        # elif dist == "exherbo":
        #     pass
        # elif dist == "gentoo":
        #     pass
        # elif dist == "ibm_powerkvm":
        #     pass
        # elif dist == "kvmibm":
        #     pass
        # elif dist == "kvmibm":
        #     pass
        # elif dist == "linuxmint":
        #     pass
        # elif dist == "mageia":
        #     pass
        # elif dist == "mandriva":
        #     pass
        # elif dist == "parallels":
        #     pass
        # elif dist == "pidora":
        #     pass
        # elif dist == "raspbian":
        #     pass
        # elif dist == "oracle":
        #     pass
        # elif dist == "scientific":
        #     self.system_packages = self.yum_get_packages()
        # elif dist == "slackware":
        #     pass
        # elif dist == "xenserver":
        #     pass
        # elif dist == "openbsd":
        #     pass
        # elif dist == "netbsd":
        #     pass
        # elif dist == "freebsd":
        #     pass
        #
        # super().__init__(document)
        # def __init__(self, bundle, identifier, attributes=None):
        #
        # # Get a list of all installed Python packages
        #
        # # Check if the process runs in an activated conda environment
        #
        # # Check if there are loaded environment modules
        #
        #
        # def yum_get_packages():
        #     process = subprocess.Popen(["yum", "-q", "list", "installed"], stdout=subprocess.PIPE)
        #     packages = process.stdout.readlines()
        #     # Skip first line 'Installed Packages'
        #     packages.pop(0)
        #     for line in packages:
        #         line_decoded = line.decode('ascii').split()
        #
        #
        #     #TODO parse sdtout
        #
        #     >> > for i in stdout:
        #         ...
        #         print(i)
        #     ...
        #     b'Installed Packages\n'
        #     b'GConf2.x86_64                      3.2.6-8.el7                         @anaconda\n'
        #     b'GeoIP.x86_64                       1.5.0-13.el7                        @base    \n'
        #     b'ImageMagick.x86_64                 6.7.8.9-16.el7_6                    @updates \n'
        #     b'ImageMagick-c++.x86_64             6.7.8.9-16.el7_6                    @updates \n'
        #     b'Judy.x86_64                        1.0.5-8.el7                         @epel    \n'
        #     b'LibRaw.x86_64                      0.14.8-5.el7.20120830git98d925      @anaconda\n'


class OperatingSystem(ProvEntity):
    """Class describing the operation system."""

    def __init__(self, document: ProvDocument) -> None:

        # Get information about the operating system
        self.os_attributes: Dict[str, Optional[str]] = dict()
        self.os_attributes["ex:name"] = distro.name(pretty=False)
        self.os_attributes["ex:codename"] = distro.codename()
        self.os_attributes["ex:version"] = distro.version(pretty=False, best=True)
        self.os_attributes["ex:kernelVersion"] = platform.release()

        # The id consists of the string formed by the four attributes
        # name-codename-version-kernel_version
        # Two operating systems are considered similar, iff their id is similar
        os_id = "ex:" + self.os_attributes["ex:name"] + "-" + self.os_attributes["ex:codename"] + "-" + self.os_attributes["ex:version"] + "-" + self.os_attributes["ex:kernelVersion"]

        super().__init__(document, os_id, attributes=self.os_attributes)


class EnvironmentVariables(ProvEntity):
    """Class describing the set of environment variables"""

    def __init__(self, document: ProvDocument) -> None:

        # Get all environment variables as dictionary
        self.env_variables = dict(os.environ)

        env_variables_id = "ex:" + str(random.randrange(0,100))
        super().__init__(document, env_variables_id)

        # Create an entity for each environment variable
        i = 0
        for key, value in self.env_variables.items():
            i = i + 1
            # Create new entity describing this variable
            var_id = "ex:env_var_" + str(i)
            cur_env_var = EnvironmentVariable(document, var_id, key, value)

            # Add the variable to this collection
            self.hadMember(cur_env_var)


class EnvironmentVariable(ProvEntity):
    """Class describing one environment variable."""

    def __init__(self, document:ProvDocument, var_id:str, variable_name:str, variable_value:str) -> None:

        super().__init__(document, var_id)
        self.add_attributes([("prov:label", variable_name),
                             ("prov:value", variable_value)])