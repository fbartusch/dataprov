import os
import datetime
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.elements.file_list import FileList
from dataprov.elements.executor import Executor
from dataprov.elements.host import Host
from dataprov.elements.op_class import OpClass
from dataprov.definitions import XML_DIR
from lxml import etree

class Operation(GenericElement):
    '''
    This class describes an operation element of a dataprov object.
    '''
    
    element_name = "operation"
    schema_file = os.path.join(XML_DIR, 'operation_element.xsd')
    
    # Known operation classes
    op_classes = ['CommandLine']
    
    def __init__(self):
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
        # Input Files (minOccurs=0)
        input_files_ele = root.find('inputFiles')
        if input_files_ele is not None:
            input_files = FileList()
            input_files.from_xml(input_files_ele, validate)
            self.data['inputFiles'] = input_files
        else:
            self.data['inputFiles'] = None
        # Target Files
        target_files_ele = root.find('targetFiles')
        target_files = FileList()
        target_files.from_xml(target_files_ele, validate)
        self.data['targetFiles'] = target_files
        # Start time
        start_time_ele = root.find('startTime')
        self.data['startTime'] = start_time_ele.text
        # End time
        end_time_ele = root.find('endTime')
        self.data['endTime'] = end_time_ele.text
        # Executor
        executor_ele = root.find('executor')
        executor = Executor()
        executor.from_xml(executor_ele, validate)
        self.data['executor'] = executor
        # Host
        host_ele = root.find('host')
        host = Host()
        host.from_xml(host_ele, validate)
        self.data['host'] = host
        # Operation class (opClass)
        op_class_ele = root.find('opClass')
        op_class= OpClass()
        op_class.from_xml(op_class_ele, validate)
        self.data['opClass'] = op_class
        # Message
        message_ele = root.find('message')
        self.data['message'] = message_ele.text
        
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        # Input Files
        if self.data['inputFiles']:
            input_files_ele = self.data['inputFiles'].to_xml(root_tag='inputFiles')
            root.append(input_files_ele)
        # Target Files
        root.append(self.data['targetFiles'].to_xml(root_tag='targetFiles'))
        # Start Time
        start_time_ele = etree.SubElement(root, 'startTime')
        start_time_ele.text = self.data['startTime']
        # End Time
        end_time_ele = etree.SubElement(root, 'endTime')
        end_time_ele.text = self.data['endTime']
        # Executor
        root.append(self.data['executor'].to_xml())
        # Host
        root.append(self.data['host'].to_xml())
        # Operation class (opClass)
        op_class_ele = etree.SubElement(root, 'opClass')
        op_class_ele.append(self.data['opClass'].to_xml())
        # Message
        message_ele = etree.SubElement(root, 'message')
        message_ele.text = self.data['message']
        return root
    
    
    def record_input_files(self, input_provenance_data):
        '''
        Record the input files.
        '''
        input_files = FileList()
        if input_provenance_data is not None:
            for input_file,provenance_object in input_provenance_data.items():
                # Check if there is provenance data available
                if provenance_object is not None:
                    input_files.add_file(provenance_object.data['target'])
                else:
                    new_file = File(input_file)
                    input_files.add_file(new_file)
            self.data['inputFiles'] = input_files
        else:
            self.data['inputFiles'] = None
        
    
    def record_target_files(self, files):
        '''
        Record target files
        '''
        # Check which of the specified target files are present
        target_files = FileList()
        for file in files:
            try:
                new_file = File(os.path.abspath(file))
                target_files.add_file(new_file)
            except IOError:
                print("Target file not found: ", file)
                continue
        self.data['targetFiles'] = target_files
            
    
    def record_start_time(self):
        '''
        Record start time in the format:
        YYYY-MM-DDThh:mm:ss
        '''
        start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")
        self.data['startTime'] = start_time
    
    
    def record_end_time(self):
        '''
        Record end time in the format:
        YYYY-MM-DDThh:mm:ss
        '''
        end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")
        self.data['endTime'] = end_time
    
    
    def record_op_class(self, op_class):
        '''
        Record op class.
        '''  
        self.data['opClass'] = op_class
        
        
    def record_wrapped_command(self, wrapped_command):
        '''
        Record wrapped command
        '''
        self.data['wrappedCommand'] = wrapped_command
        
    
    def record_host(self):
        '''
        Record host system
        '''
        host = Host()
        self.data['host'] = host


    def record_executor(self, executor):
        '''
        Record executor
        '''
        self.data['executor'] = executor
    
    
    def record_message(self, message):
        '''
        Record message
        '''
        self.data['message'] = message
    
    
    def get_target_file(self, target_file):
        '''
        Get the File object for a specific target_file.
        '''
        return self.data['targetFiles'].get_file(target_file)
        