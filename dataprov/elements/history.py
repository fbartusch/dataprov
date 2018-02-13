import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR
from lxml import etree

class History(GenericElement):
    '''
    This class describes the history element of a dataprov object.
    '''
    
    element_name = "history"
    schema_file = os.path.join(XML_DIR, 'history_element.xsd')
    
    def __init__(self):
        # Empty data attribute
        self.data = defaultdict()
        
        
    def from_xml(self, root):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        #TODO
        for child in root:
            self.data[child.tag] = child.text    
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        Each subclass has to implement itself, because data (defaultdict) elements
        are not ordered.
        '''
        #TODO
        return

