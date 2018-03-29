import sys
import os
import shutil
import subprocess
import docker
from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR


class SingularityContainer(GenericElement):
    '''
    This class describes a Singularity container used by some operation types.
    '''

    element_name = "singularityContainer"
    schema_file = os.path.join(XML_DIR, 'singularity/singularityContainer_element.xsd') 

    def __init__(self, containerPath=None):
        # Empty data attribute
        self.data = defaultdict()
        if container is not None:

            # ImageSource
            self.data['containerPath'] = File(containerPath)

            # ImageDetails
            self.data['imageDetails'] = defaultdict()
            image_dict = self.get_image_details(containerPath)
            self.data['imageDetails']['singularityVersion'] = image_dict['DockerVersion']
            self.data['imageDetails']['labels'] = image_dict['ContainerConfig']['Labels']

    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        This only works for simple elements like Host.
        Validity is not checked if not validate. This can be the case if validity
        is already checked by a superior element (e.g. dataprov vs. history)
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return

        # ImageSource
        image_source_ele = root.find('dockerImageSource')
        children = list(image_source_ele)
        self.data['method'] = children[0].tag
        if self.data['method'] == "dockerPull":
            self.data['source'] = image_source_ele.find('dockerPull').text
        elif self.data['method'] == "dockerLoad":
            self.data['source'] = image_source_ele.find('dockerLoad').find('uri').text
        elif self.data['method'] == "dockerFile":
            self.data['source'] = image_source_ele.find('dockerFile').find('uri').text
        elif self.data['method'] == "dockerImport":
            self.data['source'] = image_source_ele.find('dockerImport').text
        elif self.data['method'] == "dockerLocal":
            self.data['source'] = image_source_ele.find('dockerLocal').text

        # Image Details
        if self.data['method'] == "dockerLocal":
            image_detail_ele = root.find('imageDetails')
            self.data['imageDetails'] = defaultdict()
            self.data['imageDetails']['imageID'] = image_detail_ele.find('imageID').text
            self.data['imageDetails']['repoTag'] = image_detail_ele.find('repoTag').text
            self.data['imageDetails']['repoDigest'] = image_detail_ele.find('repoDigest').text
            self.data['imageDetails']['created'] = image_detail_ele.find('created').text
            self.data['imageDetails']['dockerVersion'] = image_detail_ele.find('dockerVersion').text
            labels = defaultdict()
            for item in image_detail_ele.find('labels').findall('item'):
                attributes = item.attrib
                labels[attributes['key']] = attributes['value']
            self.data['imageDetails']['labels'] = labels


    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)

        # ImageSource
        image_source_ele = etree.SubElement(root, 'dockerImageSource')

        if self.data['method'] == "dockerPull":
            etree.SubElement(image_source_ele, self.data['method']).text = self.data['source']
        elif self.data['method'] == "dockerLoad":
            docker_file_ele = File(self.data['source']).to_xml("dockerLoad")
            image_source_ele.append(docker_file_ele)
        elif self.data['method'] == "dockerFile":
            docker_file_ele = File(self.data['source']).to_xml("dockerFile")
            image_source_ele.append(docker_file_ele)
        elif self.data['method'] == "dockerImport":
            etree.SubElement(image_source_ele, self.data['method']).text = self.data['source']
        elif self.data['method'] == "dockerLocal":
            etree.SubElement(image_source_ele, self.data['method']).text = self.data['source']
        else:
            print("Unknown method; ", self.data['method'])

        # Image details
        if self.data['method'] == "dockerLocal":
            image_detail_ele = etree.SubElement(root, "imageDetails")
            etree.SubElement(image_detail_ele, 'imageID').text = self.data['imageDetails']['imageID']
            etree.SubElement(image_detail_ele, 'repoTag').text = self.data['imageDetails']['repoTag']
            etree.SubElement(image_detail_ele, 'repoDigest').text = self.data['imageDetails']['repoDigest']
            etree.SubElement(image_detail_ele, 'created').text = self.data['imageDetails']['created']
            etree.SubElement(image_detail_ele, 'dockerVersion').text = self.data['imageDetails']['dockerVersion']
            labels = etree.SubElement(image_detail_ele, 'labels')
            for key,value in self.data['imageDetails']['labels'].items():
                etree.SubElement(labels, 'item', attrib={'key':key, 'value':value})
        return root

    def get_image_details(self, image):
        '''
        Get details of a singularity image.
        '''
        client = docker.APIClient(version='auto')
        try:
            image_dict = client.inspect_image(image)
            return image_dict
        except docker.errors.ImageNotFound:
            print("Docker image not found: ", image)
