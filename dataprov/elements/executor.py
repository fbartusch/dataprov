import codecs
import configparser
import logging
import os
import sys
from typing import Dict, List, Optional, cast

from fluent_prov import Agent
from prov.constants import PROV_LABEL
from prov.model import ProvDocument

from ..helper import class_name, config_file, ostr, ostr_
from .organisation import Organisation


class Executor(Agent):
    """Class describing the person executing a command.

    In the PROV context, the executor is an agent. The executor bears responsibility for
    the executed operation. Therefore the operation activity and the executor agent are
    connected by an 'acted on behalf of' relation.
    """

    valid_keys: Dict[str, List[str]] = {
        "executor": ["title", "firstname", "middlename", "surname", "suffix", "mail", "orcid"],
        "affiliations": [],
    }
    """Class variable defining valid section and keys of the executor ini-file.

     This is the single source of truth for the allowed executor ini-file content.
     valid_keys is a dictionary, whose keys are section names. A value is a list of strings,
     that define the valid keys of the section.
     The keys in the 'affiliations' section can be chosen by the user.
     The values in this section is a path to an ini-file describing the organisation
     the executor is affiliated to. See the affiliation class for the conventions of the
     organisation ini-file.
     Every function should use this dictionary when reading and writing ini-files.
     """

    def __init__(
        self,
        document: ProvDocument,
        path_to_config: Optional[str] = None,
        other_attributes: Optional[Dict[str, Optional[str]]] = None,
        uuid: Optional[str] = None,
        affiliations: Optional[List[Agent]] = None,
    ) -> None:
        """Get executor information from a ini-file and add provenance data to the document.

        The information about the command executor is taken from an ini-file.
        The default location is ~/.dataprov/executor.ini, but the user can also specify a path
        to another ini-file upon dataprov invocation.
        The ini-file has to contain UTF-8 coded characters.
        This function will exit with return code 1, if the executor ini-file does not exist.

        Parameters
        ----------
        document
            The resulting document, to which the executor metadata will be added.
        path_to_config
            Path to the executor's ini-file
        other_attributes
            Other attributes describing the executor
        uuid
            UUID of the executor. If an ORCiD iD is specified in the ini-file,
            the ORCiD iD is used as UUID
        affiliations
            Affiliations of the executor
        """

        self.executor_attributes: Optional[Dict[str, Optional[str]]] = dict()

        # Check if executor ini-file exists.
        if not path_to_config:
            super().__init__(document, other_attributes, uuid=uuid)
            if affiliations:
                self.actedOnBehalfOf(*affiliations)
        else:
            if not os.path.exists(path_to_config):
                create_empty_executor_config(path_to_config)
                sys.exit(1)

            # Parse the executor ini-file
            config = configparser.ConfigParser(allow_no_value=True, delimiters="=")
            config.read_file(codecs.open(path_to_config, "r", "utf8"))

            # A person can have more than one affiliation
            _affiliations = config.items("affiliations")
            base_dir = os.path.dirname(path_to_config)
            affiliations = [
                Organisation(document, os.path.join(base_dir, affiliation + ".ini"))
                for affiliation, _ in _affiliations
            ]
            # TODO what happens if no ORCiD iD is specified? How to build the uuid then?
            if config["executor"]["ORCiD"]:
                uuid = "orcid:" + config["executor"]["ORCiD"]

            # TODO add more checks for malformed ini-files and ini-files with missing information
            executor_attributes = cast(Dict[str, Optional[str]], config["executor"])

            # Check for invalid (e.g. unsupported) keys in the ini-file.
            # Do not consider invalid keys and print print a warning to the log
            for key in executor_attributes.keys():
                if key not in Executor.valid_keys["executor"]:
                    logging.warning("Key in executor ini-file not supported: {}".format(key))
                    # Remove invalid key from dictionary
                    executor_attributes.pop(key)
                    logging.warning("Removed key from executor attributes: {}".format(key))

            name = (
                ostr_(executor_attributes["title"])
                + ostr_(executor_attributes["firstName"])
                + ostr_(executor_attributes["middleName"])
                + ostr_(executor_attributes["surname"])
                + ostr(executor_attributes["suffix"])
            )
            self.executor_attributes = {"ex:" + k: v for k, v in executor_attributes.items()}
            self.executor_attributes[PROV_LABEL] = class_name(self) + name
            self.uuid = uuid
            self.id = Executor(
                document,
                other_attributes=self.executor_attributes,
                uuid=self.uuid,
                affiliations=affiliations,
            ).id


def create_empty_executor_config(path: str) -> None:
    """Create an empty executor ini-file.

    The created empty ini-file will container fields for all fields supported by Dataprov.

    Parameters
    ----------
    path
        Path to the created ini-file
    """

    print(
        "No personal information found at:",
        path,
        "\nAn empty personal information file will be created at:",
        path,
        "\nPlease fill this file with your personal information and try again.\n",
    )

    # A simple, empty configuration
    config = configparser.ConfigParser()
    config["executor"] = {
        "title": "",
        "firstName": "",
        "middleName": "",
        "surname": "",
        "suffix": "",
        "mail": "",
        "ORCiD": "",
    }
    config["affiliations"] = {"organisationFile": ""}
    config_file.create(path, config)


# def is_executor_file_valid(path: str) -> bool:
#    """
#    :param path: absolute path to the
#    :return:
#    """
