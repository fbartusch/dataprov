import os
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.directory import Directory
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR

class DataObject(GenericElement):
    '''
    Class describing the a data object element. A data object can describe
     - a file
     - a directory
     - an object in a S3 bucket (TODO)
    '''
    
    element_name = "dataObject"
    schema_file = os.path.join(XML_DIR, 'dataObject_element.xsd')
         
    
    def __init__(self, uri=None):
        '''
        Initialize this data object element.
        If an uri is given, populate the data object with information about the
        file or directory.
        '''
        super().__init__()
        if uri:
            # Compute absolute path
            if os.path.exists(uri):
                abs_uri = os.path.abspath(uri)
            else:
                raise IOError("File not found: ", uri)
            
            # Check if its a directory
            if os.path.isdir(uri):
                data_object = Directory(abs_uri)
            # Check if its a file
            elif os.path.isfile(uri):
                data_object = File(abs_uri)
            # Check if its an object in a S3 bucket (TODO)
            else:
                print("Uri is not a file nor a directory")
                exit(1)
            self.data['dataObject'] = data_object
    
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        This only works for simple elements like Host.
        Validity is not checked if not validate. This can be the case if validity
        is already checked by a superior element (e.g. dataprov vs. history)
        '''
        # The attribute 'type' of the root element
        # tells us the type of the data object
        object_type = root.get('type')
        if object_type == "file":
            self.data['dataObject'] = File().from_xml(root, validate)
        elif object_type == "directory":
            self.data['dataObject'] = Directory().from_xml(root, validate)
        else:
            print("Unknown data object type: ", object_type)
            exit(1)
        
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        return self.data['dataObject'].to_xml(root_tag)
        
    def get_uri(self):
        '''
        Return the URI of the data object.
        '''
        return self.data['dataObject'].data['uri']