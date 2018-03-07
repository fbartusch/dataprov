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
            self.data['command'] = ' '.join(remaining)
            # Tool Path
            tool = remaining[0].split()[0]
            toolPath = shutil.which(tool)
            self.data['toolPath'] = toolPath
            # Tool Version
            FNULL = open(os.devnull, 'w')
            try:
                toolVersion1 = subprocess.check_output([tool,  '--version'], stderr=FNULL)
            except:
                toolVersion1 = None
            try:
                toolVersion2 = subprocess.check_output([tool,  '-v'], stderr=FNULL)
            except:
                toolVersion2 = None
            if toolVersion1 is not None:
                self.data['toolVersion'] = toolVersion1
            elif toolVersion2 is not None:
                self.data['toolVersion'] = toolVersion2
            else:
                self.data['toolVersion'] = 'unknown'
            # Input files and output files cannot be determined from a general command line command
            self.data['inputFiles'] = None
            self.data['outputFiles'] = None

    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'wrappedCommand').text = self.data['wrappedCommand']
        etree.SubElement(root, 'toolPath').text = self.data['toolPath']
        etree.SubElement(root, 'toolVersion').text = self.data['toolVersion']
        if self.data['inputFiles'] is not None:
            input_files_ele = self.data['inputFiles'].to_xml()
            root.append(input_files_ele)
        if self.data['outputFiles'] is not None:
            output_files_ele = self.data['outputFiles'].to_xml()    
            root.append(output_files_ele)
        return root


    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('command').text
        self.data['toolPath'] = root.find('toolPath').text
        self.data['toolVersion'] = root.find('toolVersion').text
        input_files_ele = root.find('inputFiles')
        output_files_ele = root.find('outputFiles')
        if input_files_ele is not None:
            self.data['inputFiles'] = input_files_ele.from_xml()
        if output_files_ele is not None:
            self.data['outputFiles'] = output_files_ele.from_xml()