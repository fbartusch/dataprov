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


class DockerContainer(GenericElement):
    '''
    This class describes a Docker container used by some operation types.
    '''

    element_name = "dockerContainer"
    schema_file = os.path.join(XML_DIR, 'docker/dockerContainer_element.xsd')

    docker_methods = ["dockerPull", "dockerLoad", "dockerFile", "dockerImport", "dockerLocal"]    

    def __init__(self, method=None, source=None):
        # Empty data attribute
        self.data = defaultdict()
        if method is not None and source is not None:
            if method not in self.docker_methods:
                print("Unknown docker image source method: ", method)

            # ImageSource
            self.data['method'] = method
            self.data['source'] = source

            # ImageDetails
            # Only possible for images that are already pulled
            if method == "dockerLocal":
                self.data['imageDetails'] = defaultdict()
                image_dict = self.get_image_details(source)
                self.data['imageDetails']['imageID'] = image_dict['Id']
                self.data['imageDetails']['repoTag'] = image_dict['RepoTags'][0]
                self.data['imageDetails']['repoDigest'] = image_dict['RepoDigests'][0]
                self.data['imageDetails']['created'] = image_dict['Created']
                self.data['imageDetails']['labels'] = image_dict['ContainerConfig']['Labels']

            # DockerPath
            tool = 'docker'
            toolPath = shutil.which(tool)
            self.data['dockerPath'] = toolPath

            # DockerVersion
            try:
                dockerVersion = subprocess.check_output([tool,  '--version'])
            except:
                dockerVersion = None
            if dockerVersion is not None:
                self.data['dockerVersion'] = dockerVersion
            else:
                self.data['dockerVersion'] = 'unknown'

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
        image_source_ele = root.find('imageSource')
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
            labels = defaultdict()
            for item in image_detail_ele.find('labels').findall('item'):
                attributes = item.attrib
                labels[attributes['key']] = attributes['value']
            self.data['imageDetails']['labels'] = labels

        self.data['dockerPath'] = root.find('dockerPath').text
        self.data['dockerVersion'] = root.find('dockerVersion').text

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)

        # ImageSource
        image_source_ele = etree.SubElement(root, 'imageSource')

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
            labels = etree.SubElement(image_detail_ele, 'labels')
            for key,value in self.data['imageDetails']['labels'].items():
                etree.SubElement(labels, 'item', attrib={'key':key, 'value':value})

        # DockerPath and DockerVersion
        etree.SubElement(root, 'dockerPath').text = self.data['dockerPath']
        etree.SubElement(root, 'dockerVersion').text = self.data['dockerVersion']
        return root

    def get_image_details(self, image):
        '''
        Get details of a docker image.
        '''
        client = docker.APIClient(version='auto')
        try:
            image_dict = client.inspect_image(image)
            return image_dict
        except docker.errors.ImageNotFound:
            print("Docker image not found: ", image)
