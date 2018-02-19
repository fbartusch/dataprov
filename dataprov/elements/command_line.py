import os
import shutil
import subprocess
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from lxml import etree
from dataprov.definitions import XML_DIR

class CommandLine(GenericElement):
    '''
    This class describes a command line tool. .
    This class provides basic functionalities to read/write the dataprov element.
    '''
    
    element_name = "commandLine"
    schema_file = schema_file = os.path.join(XML_DIR, 'commandLine_element.xsd')
    
    def __init__(self, remaining=None):
        # Empty data attribute
        self.data = defaultdict()
        
        if remaining is not None:
            # Wrapped command
            self.data['wrappedCommand'] = ' '.join(remaining)
            # Tool Path
            tool = remaining[0].split()[0]
            toolPath = shutil.which(tool)
            self.data['toolPath'] = toolPath
            # Tool Version
            try:
                toolVersion1 = subprocess.check_output([tool,  '--version'])
            except:
                toolVersion1 = None
            try:
                toolVersion2 = subprocess.check_output([tool,  '-v'])
            except:
                toolVersion2 = None
            if toolVersion1 is not None:
                self.data['toolVersion'] = toolVersion1
            elif toolVersion2 is not None:
                self.data['toolVersion'] = toolVersion2
            else:
                self.data['toolVersion'] = 'unknown'

    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'wrappedCommand').text = self.data['wrappedCommand']
        etree.SubElement(root, 'toolPath').text = self.data['toolPath']
        etree.SubElement(root, 'toolVersion').text = self.data['toolVersion']
        return root
        