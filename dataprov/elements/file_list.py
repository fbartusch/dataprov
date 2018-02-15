import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR
from lxml import etree


class FileList(GenericElement):
    '''
    Class describing the fileList element.
    '''
    
    element_name = "fileList"
    schema_file = os.path.join(XML_DIR, 'fileList_element.xsd')
         
    
    def __init__(self, files=None):
        '''
        Initialize this fileList element.
        If a list of files is given, populate the data object.
        The files have to be a list of URIs
        '''
        super().__init__()
        self.data = defaultdict(list)
        if files:
            for file in files:
                new_file = File(file)
                self.data['file'].append(new_file)
            

    def from_xml(self, root, validate=True):
        '''
        Cannot use the from_xml of the super class,
        because fileList is a complex type.
        '''
        self.data = defaultdict(list)
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            exit(1)
        for file_ele in root.findall('file'):
            new_file = File()
            new_file.from_xml(file_ele, validate)
            self.data['file'].append(new_file)

    
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        if not root_tag:
            root = etree.Element(self.element_name)
        else:
            root = etree.Element(root_tag)
        for file in self.data['file']:
            file_ele = file.to_xml()
            root.append(file_ele)
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
        file_ele = File()
        for child in root:
            isFile = file_ele.validate_xml(child)
            if not isFile:
                print("file in fileList is not a valid")
                exit(1)
    
    
    def add_file(self, new_file):
        '''
        Add a file to the file list.
        '''
        self.data['file'].append(new_file)
    
    
    def get_file(self, file):
        '''
        Return the file object of a specific file
        '''
        for file_object in self.data['file']:
            if os.path.realpath(file_object.data['uri']) == os.path.realpath(file):
                return file_object
            
        