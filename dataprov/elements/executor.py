import os
import configparser
from dataprov.elements.dataprov_element import DataprovElement
from dataprov.definitions import XML_DIR
from lxml import etree


class Executor(DataprovElement):
    '''
    Class describing the executor of an operation
    '''
    
    element_name = "executor"
    schema_file = os.path.join(XML_DIR, 'executor.xsd')
    
    def __init__(self, config_file):
        super().__init__()
        # Load data from config file
        self.from_config(config_file)

        
    def from_config(self, config_file):
        '''
        Get Executor data from config file
        '''
        config = configparser.ConfigParser()
        config.read(config_file)
        self.data['title'] = config.get('executor', 'title')
        self.data['firstName'] = config.get('executor', 'firstName')
        self.data['middleName'] = config.get('executor', 'middleName')
        self.data['surname'] = config.get('executor', 'surname')
        self.data['suffix'] = config.get('executor', 'suffix')
        self.data['mail'] = config.get('executor', 'mail')

        # A person can have more than one affiliation
        affiliation_list = []
        affiliations = config.items('affiliations')
        for key, affiliation in affiliations:
            affiliation_list.append(affiliation)
        self.data['affiliation'] = affiliation_list
    

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, "title").text = self.data["title"]
        etree.SubElement(root, "firstName").text = self.data["firstName"]
        etree.SubElement(root, "middleName").text = self.data["middleName"]
        etree.SubElement(root, "surname").text = self.data["surname"]
        etree.SubElement(root, "suffix").text = self.data["suffix"]
        etree.SubElement(root, "mail").text = self.data["mail"]
        # Affiliation(s)
        for affiliation in self.data['affiliation']:
            etree.SubElement(root, "affiliation").text = affiliation
        return root