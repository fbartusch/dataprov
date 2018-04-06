import os
import shutil
import subprocess
from collections import defaultdict
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.file_list import FileList
from dataprov.elements.data_object import DataObject
from dataprov.elements.data_object_list import DataObjectList
from lxml import etree
from dataprov.definitions import XML_DIR

class CommandLine(GenericOp):
    '''
    This class describes a command line tool. .
    '''
    
    element_name = "commandLine"
    schema_file = schema_file = os.path.join(XML_DIR, 'commandLine_element.xsd')
    
    def __init__(self, remaining=None):
        super().__init__()
        
        self.remaining = remaining
        self.data['inputDataObjects'] = None
        self.data['outputDataObjects'] = None    
        
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
        if self.data['inputDataObjects'] is not None:
            input_data_objects_ele = self.data['inputDataObjects'].to_xml("inputDataObjects")
            root.append(input_data_objects_ele)
        if self.data['outputDataObjects'] is not None:
            output_data_objects_ele = self.data['outputDataObjects'].to_xml("outputDataObjects")    
            root.append(output_data_objects_ele)
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
        input_data_objects_ele = root.find('inputDataObjects')
        output_data_objects_ele = root.find('outputDataObjects')
        if input_data_objects_ele is not None:
            input_data_objects = DataObjectList()
            input_data_objects.from_xml(input_data_objects_ele, validate)
            self.data['inputDataObjects'] = input_data_objects
        else:
            self.data['inputDataObjects'] = None
        if output_data_objects_ele is not None:
            output_data_objects = DataObjectList()
            output_data_objects.from_xml(output_data_objects_ele, validate)
            self.data['outputDataObjects'] = output_data_objects
        else:
            self.data['outputDataObjects'] = None

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