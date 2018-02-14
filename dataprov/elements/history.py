import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.operation import Operation
from dataprov.definitions import XML_DIR
from lxml import etree

class History(GenericElement):
    '''
    This class describes the history element of a dataprov object.
    The history consists of a list of operations.
    '''
    
    element_name = "history"
    schema_file = os.path.join(XML_DIR, 'history_element.xsd')
    
    def __init__(self):
        # Empty data attribute
        self.data = defaultdict(list)
        
        
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict(list)
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        for operation_ele in root.findall('operation'):
            new_operation = Operation()
            new_operation.from_xml(operation_ele, validate)
            self.data['operation'].append(new_operation)
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        # Iterate over operations
        for operation in self.data['operation']:
            new_operation_ele = operation.to_xml()
            root.append(new_operation_ele)
        return root

