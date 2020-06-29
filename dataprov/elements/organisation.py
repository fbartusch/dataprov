import configparser
import os
import sys
from typing import Dict, Optional, cast

from fluent_prov import Agent
from prov.constants import PROV_LABEL
from prov.model import ProvDocument

from ..helper import class_name, config_file


class Organisation(Agent):
    """Class describing an organisation.

    In the PROV context, the organisation is an agent. An executor can has several affiliations.
    Every affiliation agent is in a 'acted on behalf of' relation to the executor. An affiliation
    could be, for example, an academic department, an organization, or a company.
    """

    def __init__(
        self,
        document: ProvDocument,
        path_to_config: str,
        uuid: Optional[str] = None,
        other_attributes: Optional[Dict[str, Optional[str]]] = None,
    ) -> None:
        """Get the affiliation's information from a ini-file.

        A persons affiliations are listed in the 'affiliations' section of an executors ini-file.
        This function will exit with return code 1, if the affiliation ini-file does not exist at
        the specified path.

        Parameters
        ----------
        document
            The resulting document, to which the affiliations metadata will be added.
        path_to_config
            Path to the organisations's ini-file.
        uuid
            UUID of the organisation.
        other_attributes
            Other attributes describing the organisation.
        """

        if not path_to_config:
            super().__init__(document, other_attributes, uuid)
        # Load data from config file
        if not os.path.exists(path_to_config):
            create_empty_organisation_config(path_to_config)
            sys.exit(1)
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(path_to_config)
        if not uuid:
            web = config["organisation"]["Web"]
            github = config["organisation"]["Github"]
            linkedin = config["organisation"]["LinkedIn"]
            if web:
                uuid = "web:" + web
            if linkedin:
                uuid = "linkedin:" + linkedin
            if github:
                uuid = "github:" + github
            organisation_attributes = cast(Dict[str, Optional[str]], config["organisation"])

        if organisation_attributes:
            title = organisation_attributes["title"]
            organisation_attributes = {"ex:" + k: v for k, v in organisation_attributes.items()}
            if title:
                organisation_attributes = {
                    **organisation_attributes,
                    PROV_LABEL: class_name(self) + title,
                }

        self.id = Agent(document, organisation_attributes, uuid).id


def create_empty_organisation_config(path: str) -> None:
    """
    Create an empty organisation ini-file.

    Parameters
    ----------
    path
        Path to the created ini-file
    """

    print(
        "No organisational information found at",
        path,
        "\nAn empty organisational information file will be created at:",
        path,
        "\nIf desired, fill this file with information about your organisation.",
        "\nSpecify then the path to this file in your personal information file\n",
    )

    # A simple, empty configuration
    config = configparser.ConfigParser(allow_no_value=True)
    config["organisation"] = {"title": "", "mail": "", "LinkedIn": "", "Github": "", "Web": ""}
    config_file.create(path, config)
