import os
from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR

class CWLWorkflow(GenericElement):
    '''
    This class describes a CWLWorkflow element.
    '''
    
    element_name = "cwlWorkflow"
    schema_file = os.path.join(XML_DIR, 'cwl/cwlWorkflow_element.xsd')
    
    def __init__(self, cwl_tool=None, job_order_object=None, outdir=None):
        # Empty data attribute
        self.data = defaultdict()
        
        
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
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
        root = etree.Element(self.element_name)
        #etree.SubElement(root, "name").text = self.data["name"]
        return root
        
            

