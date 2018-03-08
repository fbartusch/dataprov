import os
import shutil
import subprocess
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file_list import FileList
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
        self.data['inputFiles'] = None
        self.data['outputFiles'] = None
        
        self.input_files = []
        self.output_files = []        
        
        if remaining is not None:
            # Command
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


    
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        if root_tag is not None:
            root.tag = root_tag
        etree.SubElement(root, 'command').text = self.data['command']
        etree.SubElement(root, 'toolPath').text = self.data['toolPath']
        etree.SubElement(root, 'toolVersion').text = self.data['toolVersion']
        if self.data['inputFiles'] is not None:
            input_files_ele = self.data['inputFiles'].to_xml("inputFiles")
            root.append(input_files_ele)
        if self.data['outputFiles'] is not None:
            output_files_ele = self.data['outputFiles'].to_xml("outputFiles")    
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
            input_files = FileList()
            input_files.from_xml(input_files_ele, validate)
            self.data['inputFiles'] = input_files
        else:
            self.data['inputFiles'] = None
        if output_files_ele is not None:
            output_files = FileList()
            output_files.from_xml(output_files_ele, validate)
            self.data['outputFiles'] = output_files
        else:
            self.data['outputFiles'] = None


    def set_command(self, command):
        '''
        Set a command as well as toolPath and toolVersion
        '''
        self.data['command'] = command
        tool = command.split()[0]
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

    
    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        # Generate file elements for input files
        self.data['inputFiles'] = FileList(self.input_files)
        # Generate file elements for output files
        self.data['outputFiles'] = FileList(self.output_files)

        
    def get_input_files(self):
        '''
        Get input files specified by the wrapped command
        (e.g. from CWL input bindings)
        '''
        return self.input_files


    def get_output_files(self):
        '''
        Get output files specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        return self.output_files