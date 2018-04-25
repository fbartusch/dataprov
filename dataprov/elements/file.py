from __future__ import absolute_import, division, print_function
import os
import hashlib
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR
from lxml import etree


class File(GenericElement):
    '''
    Class describing the a file element.
    '''
    
    element_name = "file"
    schema_file = os.path.join(XML_DIR, 'file_element.xsd')
         
    
    def __init__(self, file=None):
        '''
        Initialize this file element.
        If a file is given, compute populate the data object.
        file has to be an URI.
        '''
        super(File, self).__init__()
        if file:
            # Check if file exists
            if not os.path.exists(file):
                raise IOError("File not found: ", file)
            basename = os.path.basename(file)
            uri = file
            sha1 = self.compute_hash(file)
            self.data['name'] = basename
            self.data['uri'] = uri
            self.data['sha1'] = sha1
        
    
    def compute_hash(self, file):
        '''
        Compute the sha1 hashsum of a file
        '''
        sha1 = hashlib.sha1()    
        # BUF_SIZE is totally arbitrary, change for your app!
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
                sha1sum = sha1.hexdigest()
        else:
            sha1sum = "undefined"
        return sha1sum

    
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        if root_tag is not None:
            root.tag = root_tag
        etree.SubElement(root, "name").text = self.data["name"]
        etree.SubElement(root, "uri").text = self.data["uri"]
        etree.SubElement(root, "sha1").text = self.data["sha1"]
        return root
    
    
    def get_uri(self):
        '''
        Get the URI of this file object.
        '''
        return self.data['uri']