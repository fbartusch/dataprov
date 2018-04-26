from __future__ import absolute_import, division, print_function
import os
from configparser import ConfigParser
from collections import defaultdict
from dataprov.utils.io import mkdir_p
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR, DATAPROV
from lxml import etree


class Executor(GenericElement):
    '''
    Class describing the executor of an operation
    '''
    
    element_name = DATAPROV + "executor"
    schema_file = os.path.join(XML_DIR, 'executor_element.xsd')
    
    def __init__(self, config_file=None):
        super(Executor, self).__init__()
        # Load data from config file
        if config_file:
            self.from_config(config_file)

        
    def from_config(self, config_file):
        '''
        Get Executor data from config file.
        Create an empty file, if the config file does not exist.
        '''
        if not os.path.exists(config_file):
            print("No personal information found at ", config_file)
            print("An empy personal information file will be created at ", config_file)
            print("Please fill this file with your personal information and try again.")
            self.create_empty_executor_config(config_file)
            exit(0)
        else:
            config = ConfigParser()
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
    
    
    def from_xml(self, root, validate=True):
        '''
        Cannot use the from_xml of the super class, because affiliation is a complex type.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        title_ele = root.find('{Dataprov}title')
        if title_ele is not None:
            self.data['title'] = title_ele.text
        else:
            self.data['title'] = None
        self.data['firstName'] = root.find('{Dataprov}firstName').text
        middle_name_ele = root.find('{Dataprov}middleName')
        if middle_name_ele is not None:
            self.data['middleName'] = middle_name_ele.text
        else:
            self.data['middleName'] = None
        self.data['surname'] = root.find('{Dataprov}surname').text
        suffix_ele = root.find('{Dataprov}suffix')
        if suffix_ele is not None:
            self.data['suffix'] = suffix_ele.text
        else:
            self.data['suffix'] = None
        self.data['mail'] = root.find('{Dataprov}mail').text
        affiliation_list = []
        for affiliation_ele in root.findall('{Dataprov}affiliation'):
            affiliation_list.append(affiliation_ele.text)
        self.data['affiliation'] = affiliation_list
            
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        if self.data['title'] is not None:
            etree.SubElement(root, DATAPROV + "title").text = self.data["title"]
        etree.SubElement(root, DATAPROV + "firstName").text = self.data["firstName"]
        if self.data['middleName'] is not None:
            etree.SubElement(root, DATAPROV + "middleName").text = self.data["middleName"]
        etree.SubElement(root, DATAPROV + "surname").text = self.data["surname"]
        if self.data['suffix'] is not None:
            etree.SubElement(root, DATAPROV + "suffix").text = self.data["suffix"]
        etree.SubElement(root, DATAPROV + "mail").text = self.data["mail"]
        # Affiliation(s)
        for affiliation in self.data['affiliation']:
            etree.SubElement(root, DATAPROV + "affiliation").text = affiliation
        return root
        
    
    def create_empty_executor_config(self, path):
        '''
        Create an empty executor information file.
        '''
        # A simple, empty configuration
        config = ConfigParser()
        config['executor'] = {'title': '',
                              'firstName': '',
                              'middleName': '',
                              'surname': '',
                              'suffix': '',
                              'mail': ''}
        config['affiliations'] = {'affiliation1': ''}

        # Create base directory if needed
        base_dir = os.path.dirname(path)
        mkdir_p(base_dir)
        with open(path, 'w') as configfile:
            config.write(configfile)