import os
import hashlib
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR
from lxml import etree


class Directory(GenericElement):
    '''
    Class describing the a directory element.
    '''
    
    element_name = "directory"
    schema_file = os.path.join(XML_DIR, 'directory_element.xsd')
             
    def __init__(self, uri=None):
        '''
        Initialize this directory element.
        If an uri is given, compute populate the data object.
        '''
        super().__init__()
        if uri:
            # Check if file exists
            if not os.path.exists(uri):
                raise IOError("Directory not found: ", uri)
            basename = os.path.basename(uri)
            self.data['name'] = basename
            self.data['uri'] = uri
            # Compute the shasum of each file in the directory.
            # Sort the resulting shasums according to the filename.
            filelist = []
            for root, directories, filenames in os.walk('/home/fbartusch/github/dataprov'):
                for filename in filenames: 
                    filelist.append(os.path.join(root, filename))
            file_hash_list = []
            for file in filelist:
                try:
                    hash = self.compute_hash(file)
                except:
                    hash = "undefined"
                file_hash_list.append((file, hash))
            file_hash_list.sort()
            # Write list to file (directory name with '.shalist' suffix)
            shalist_file = os.path.join(uri, ".shalist")
            with open(shalist_file, "w") as shafile:
                for file, hash in file_hash_list:
                    shafile.write(file + ", " + hash)
            self.data['shafile'] = File(shalist_file)
    
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


    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        This only works for simple elements like Host.
        Validity is not checked if not validate. This can be the case if validity
        is already checked by a superior element (e.g. dataprov vs. history)
        '''
        self.data['name'] = root.find('name').text
        self.data['uri'] = root.find('uri').text
        self.data['shafile'] = File(root.find('shafile').text)
        return
    
    def to_xml(self, root_tag=None):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        if root_tag is not None:
            root.tag = root_tag
        root.set("type", "directory")
        etree.SubElement(root, "name").text = self.data["name"]
        etree.SubElement(root, "uri").text = self.data["uri"]
        shafile_ele = self.data['shafile'].to_xml("sha1file")
        root.append(shafile_ele)
        return root    
    
    def get_uri(self):
        '''
        Get the URI of this file object.
        '''
        return self.data['uri']