from __future__ import absolute_import, division, print_function
import os
import datetime
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.data_object import DataObject
from dataprov.elements.data_object_list import DataObjectList
from dataprov.elements.executor import Executor
from dataprov.elements.host import Host
from dataprov.elements.op_class import OpClass
from dataprov.definitions import XML_DIR, DATAPROV
from lxml import etree


class Operation(GenericElement):
    '''
    This class describes an operation element of a dataprov object.
    '''

    element_name = DATAPROV + "operation"
    schema_file = os.path.join(XML_DIR, 'operation_element.xsd')
    
    def __init__(self):
        super(Operation, self).__init__()      
        
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.__init__()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        # Input Files (minOccurs=0)
        input_data_objects_ele = root.find('{Dataprov}inputDataObjects')
        if input_data_objects_ele is not None:
            input_data_objects = DataObjectList()
            input_data_objects.from_xml(input_data_objects_ele, validate)
            self.data['inputDataObjects'] = input_data_objects
        else:
            self.data['inputDataObjects'] = None
        # Target Files
        target_data_objects_ele = root.find('{Dataprov}targetDataObjects')
        target_data_objects = DataObjectList()
        target_data_objects.from_xml(target_data_objects_ele, validate)
        self.data['targetDataObjects'] = target_data_objects
        # Start time
        start_time_ele = root.find('{Dataprov}startTime')
        self.data['startTime'] = start_time_ele.text
        # End time
        end_time_ele = root.find('{Dataprov}endTime')
        self.data['endTime'] = end_time_ele.text
        # Executor
        executor_ele = root.find('{Dataprov}executor')
        executor = Executor()
        executor.from_xml(executor_ele, validate)
        self.data['executor'] = executor
        # Host
        host_ele = root.find('{Dataprov}host')
        host = Host()
        host.from_xml(host_ele, validate)
        self.data['host'] = host
        # Operation class (opClass)
        op_class_ele = root.find('{Dataprov}opClass')
        op_class= OpClass()
        op_class.from_xml(op_class_ele, validate)
        self.data['opClass'] = op_class
        # Message
        message_ele = root.find('{Dataprov}message')
        self.data['message'] = message_ele.text

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        # Input Data Objects
        if self.data['inputDataObjects']:
            tag = DATAPROV + 'inputDataObjects'
            input_data_objects_ele = self.data['inputDataObjects'].to_xml(root_tag=tag)
            root.append(input_data_objects_ele)
        # Target Files
        tag = DATAPROV + 'targetDataObjects'
        root.append(self.data['targetDataObjects'].to_xml(root_tag=tag))
        # Start Time
        start_time_ele = etree.SubElement(root, DATAPROV + 'startTime')
        start_time_ele.text = self.data['startTime']
        # End Time
        end_time_ele = etree.SubElement(root, DATAPROV + 'endTime')
        end_time_ele.text = self.data['endTime']
        # Executor
        root.append(self.data['executor'].to_xml())
        # Host
        root.append(self.data['host'].to_xml())
        # Operation class (opClass)
        op_class_ele = etree.SubElement(root, DATAPROV + 'opClass')
        op_class_ele.append(self.data['opClass'].to_xml())
        # Message
        message_ele = etree.SubElement(root, DATAPROV + 'message')
        message_ele.text = self.data['message']
        return root
        
    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        self.data['opClass'].post_processing()
       
    def record_input_data_objects(self, input_provenance_data):
        '''
        Record the input data objects.
        '''
        input_data_objects = DataObjectList()
        if input_provenance_data is not None:
            for input_data_object, provenance_object in input_provenance_data.items():
                # Check if there is provenance data available
                if provenance_object is not None:
                    input_data_objects.add_object(provenance_object.data['target'])
                else:
                    new_object = DataObject(input_data_object)
                    input_data_objects.add_object(new_object)
            self.data['inputDataObjects'] = input_data_objects
        else:
            self.data['inputDataObjects'] = None
            
    def record_target_data_objects(self, uris):
        '''
        Record target data objects
        '''
        # Check which of the specified target files are present
        target_data_objects = DataObjectList()
        for uri in uris:
            try:
                new_object = DataObject(os.path.abspath(uri))
                target_data_objects.add_object(new_object)
            except IOError:
                print("Target data object not found: ", file)
                continue
        self.data['targetDataObjects'] = target_data_objects
               
    def record_start_time(self):
        '''
        Record start time in the format:
        YYYY-MM-DDThh:mm:ss
        '''
        start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.data['startTime'] = start_time
        
    def record_end_time(self):
        '''
        Record end time in the format:
        YYYY-MM-DDThh:mm:ss
        '''
        end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
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
        
    def get_target_data_object(self, target_data_object):
        '''
        Get the File object for a specific target_file.
        '''
        return self.data['targetDataObjects'].get_object(target_data_object)
        