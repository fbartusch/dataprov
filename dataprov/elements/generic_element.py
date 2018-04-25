from __future__ import absolute_import, division, print_function
import os
import lxml
from collections import defaultdict
from lxml import etree
from dataprov.utils.io import prettify
from dataprov.definitions import XML_DIR

class GenericElement(object):
    '''
    This class describes a generic element of a dataprov object.
    This class provides basic functionalities to read/write the dataprov element.
    '''
    
    element_name = "generic"
    schema_file = os.path.join(XML_DIR, 'generic_element.xsd')
    
    def __init__(self):
        # Empty data attribute
        self.data = defaultdict()
        
        
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        This only works for simple elements like Host.
        Validity is not checked if not validate. This can be the case if validity
        is already checked by a superior element (e.g. dataprov vs. history)
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        for child in root:
            self.data[child.tag] = child.text    
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        Each subclass has to implement itself, because data (defaultdict) elements
        are not ordered.
        '''
        return ""
    
    
    def validate_xml(self, root):
        '''
        Validate an lxml object against a the XSD schema of this dataprov element.
        '''
        # Read schema file
        with open(self.schema_file, 'r') as schema_file_handler:
            xml_schema_doc = etree.parse(schema_file_handler)
        # Create XML schema
        try:
            xml_schema = etree.XMLSchema(xml_schema_doc)
        except lxml.etree.XMLSchemaParseError as e:
            print("Cannot parse XML schema: ", self.schema_file)
            print(e)
            exit(1)
        # Validate
        try:
            xml_schema.assertValid(root)
            return True
        except etree.DocumentInvalid as e:#, xml_errors:
            print("XML document is not valid!")
            print(e)
            log = xml_schema.error_log
            error = log.last_error
            print(error.domain_name)
            print(error.type_name)
            return False


    def __str__(self):
        root = self.to_xml()
        return prettify(root)
        
            

