from __future__ import absolute_import, division, print_function
import os
import platform
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR
from lxml import etree


class Host(GenericElement):
    '''
    Class describing the host system of an operation
    '''
    
    element_name = "host"
    schema_file = os.path.join(XML_DIR, 'host_element.xsd')
    
    def __init__(self):
        super(Host, self).__init__()
        # Get information about host and populate the data dictionary
        dist = platform.linux_distribution()
        uname = platform.uname()
        self.data["system"] = platform.system()
        self.data["dist"] = dist[0]
        self.data["version"] = dist[1]
        self.data["codename"] = dist[2]
        self.data["kernelVersion"] = uname[2]
        self.data["machine"] = platform.machine()
        self.data["processor"] = platform.processor()
        self.data["hostname"] = uname[1]
         
    
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