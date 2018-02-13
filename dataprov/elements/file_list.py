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
            

    def from_xml(self, root):
        '''
        Cannot use the from_xml of the super class,
        because fileList is a complex type.
        '''
        self.data = defaultdict(list)
        if not self.validate_xml(root):
            print("XML document does not match XML-schema")
            exit(1)
        for file_ele in root.findall('file'):
            new_file = File()
            new_file.from_xml(file_ele)
            self.data['file'].append(new_file)

    
    def to_xml(self, root_name=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        if not root_name:
            root = etree.Element(self.element_name)
        else:
            root = etree.Element(root_name)
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
            
        