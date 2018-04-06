import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.elements.directory import Directory
from dataprov.elements.data_object import DataObject
from dataprov.definitions import XML_DIR
from lxml import etree


class DataObjectList(GenericElement):
    '''
    Class describing a list of data objects.
    '''
    
    element_name = "dataObjectList"
    schema_file = os.path.join(XML_DIR, 'dataObjectList_element.xsd')
         
    def __init__(self, uris=None):
        '''
        Initialize this data object list element.
        If a list of URIs is given, create the list describing the data objects.
        '''
        super().__init__()
        self.data = defaultdict(list)
        if uris:
            for uri in uris:
                try:
                    new_object = DataObject(uri)
                    self.data['objects'].append(new_object)
                except IOError:
                    print("Data object does not exist: ", file)
            
    def from_xml(self, root, validate=True):
        self.data = defaultdict(list)
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            exit(1)
        for object_ele in root.findall('dataObject'):
            new_object = DataObject()
            new_object.from_xml(object_ele, validate)
            self.data['objects'].append(new_object)
   
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        if not root_tag:
            root = etree.Element(self.element_name)
        else:
            root = etree.Element(root_tag)
        for object in self.data['objects']:
            object_ele = object.to_xml()
            root.append(object_ele)
        return root       
    
    def validate_xml(self, root):
        '''
        Validate a xml ElementTree object.
        Check if the xml ElementTree object is a valid file list.
        This means, it consists of a list of file elements.
        We cannot use the fileList_element.xsd schema, because the root element
        of the fileList can have different names, depending on the purpose
        (e.g. 'inputFiles' vs. 'targetFiles').
        '''
        # Just check if the ElementTree consists of just files
        object_ele = DataObject()
        for child in root:
            isObject = object_ele.validate_xml(child)
            if not isObject:
                print("DataObject in DataObjectList is not a valid")
                exit(1)
    
    def add_object(self, new_object):
        '''
        Add a data object to the data object list.
        '''
        self.data['objects'].append(new_object)  
    
    def get_object(self, uri):
        '''
        Return the data  object of a specific URI.
        '''
        for data_object in self.data['objects']:
            print(data_object)
            if os.path.realpath(data_object.get_uri()) == os.path.realpath(uri):
                return data_object