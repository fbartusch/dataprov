import os
import shutil
import subprocess
import docker
from docker.errors  import ImageNotFound
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from lxml import etree
from dataprov.definitions import XML_DIR

class Docker(GenericElement):
    '''
    This class describes a command that uses docker containers.
    '''
    
    element_name = "docker"
    schema_file = schema_file = os.path.join(XML_DIR, 'docker_element.xsd')
    
    def __init__(self, remaining=None):
        # Empty data attribute
        self.data = defaultdict()
        
        if remaining is not None:
            # Wrapped command
            self.data['wrappedCommand'] = ' '.join(remaining)
            # Tool Path
            tool = 'docker'
            toolPath = shutil.which(tool)
            self.data['dockerPath'] = toolPath
            
            # Tool Version
            try:
                toolVersion1 = subprocess.check_output([tool,  '--version'])
            except:
                toolVersion1 = None
            if toolVersion1 is not None:
                self.data['dockerVersion'] = toolVersion1
            else:
                self.data['dockerVersion'] = 'unknown'

            # Get the output of docker inspect on the container
            image_dict = self.get_container_image(remaining)
            print(image_dict)
            self.data['id'] = image_dict['Id']
            self.data['repoTag'] = image_dict['RepoTags'][0]
            self.data['repoDigest'] = image_dict['RepoDigests'][0]
            self.data['created'] = image_dict['Created']
            self.data['labels'] = image_dict['ContainerConfig']['Labels']
            print(self.data)

            
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['wrappedCommand'] = root.find('wrappedCommand').text
        self.data['dockerPath'] = root.find('dockerPath').text
        self.data['dockerVersion'] = root.find('dockerVersion').text
        self.data['id'] = root.find('id').text
        self.data['repoTag'] = root.find('repoTag').text
        self.data['repoDigest'] = root.find('repoDigest').text
        self.data['created'] = root.find('created').text
        labels = defaultdict()
        for item in root.find('labels').findall('item'):
            attributes = item.attrib
            labels[attributes['key']] = attributes['value']
        self.data['labels'] = labels 
            
            
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'wrappedCommand').text = self.data['wrappedCommand']
        etree.SubElement(root, 'dockerPath').text = self.data['dockerPath']
        etree.SubElement(root, 'dockerVersion').text = self.data['dockerVersion']
        etree.SubElement(root, 'id').text = self.data['id']
        etree.SubElement(root, 'repoTag').text = self.data['repoTag']
        etree.SubElement(root, 'repoDigest').text = self.data['repoDigest']
        etree.SubElement(root, 'created').text = self.data['created']
        labels = etree.SubElement(root, 'labels')
        for key,value in self.data['labels'].items():
            etree.SubElement(labels, 'item', attrib={'key':key, 'value':value})
        return root


    def get_container_image(self, remaining):
        '''
        Get the container image from the wrapped command.
        '''
        # Iterate over the arguments, ignore everything starting with '-'.
        # For the other strings, check if it's a docker image
        client = docker.APIClient(version='auto')
        if len(remaining) == 1:
            remaining_list = remaining[0].split()
        else:
            remaining_list = remaining
        for s in remaining_list:
            if s[0] == '-':
                continue
            else:
                # Check if this is the image to run
                try:
                    image_dict = client.inspect_image(s)
                    return image_dict                    
                except docker.errors.ImageNotFound:
                    continue