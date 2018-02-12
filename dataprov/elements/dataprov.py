import os
import platform
from dataprov.elements.dataprov_element import DataprovElement
from dataprov.definitions import XML_DIR
from lxml import etree


class Dataprov(DataprovElement):
    '''
    Class describing the whole dataprov element.
    This class handles the parsing of input dataprov metadata files.
    '''
    
    element_name = "dataprov"
    schema_file = os.path.join(XML_DIR, 'dataprov.xsd')
    
    def __init__(self):
        super().__init__()
    
    
    def from_xml(self, xml):
        #TODO
        

     
     
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, "system").text = self.data["system"]
        etree.SubElement(root, "dist").text = self.data["dist"]
        etree.SubElement(root, "version").text = self.data["version"]
        etree.SubElement(root, "codename").text = self.data["codename"]
        etree.SubElement(root, "kernelVersion").text = self.data["kernelVersion"]
        etree.SubElement(root, "machine").text = self.data["machine"]
        etree.SubElement(root, "processor").text = self.data["processor"]
        etree.SubElement(root, "hostname").text = self.data["hostname"]
        return root