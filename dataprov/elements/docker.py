from __future__ import absolute_import, division, print_function
import os
import docker
import subprocess
from collections import defaultdict
from docker.errors import ImageNotFound
from distutils.spawn import find_executable
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.docker_container import DockerContainer
from lxml import etree
from dataprov.definitions import XML_DIR


class Docker(GenericOp):
    '''
    This class describes a command executed in a Docker container.
    '''

    element_name = "docker"
    schema_file = schema_file = os.path.join(XML_DIR, 'docker_element.xsd')

    def __init__(self, remaining=None):
        super(Docker, self).__init__()
        
        self.remaining = remaining

        if remaining is not None:
            # Command
            self.data['command'] = ' '.join(remaining)

            # Get the output of docker inspect on the container
            image_dict = self.get_container_image(remaining)

            # Create the docker container object
            docker_container = DockerContainer("dockerLocal", image_dict['RepoTags'][0])
            self.data['dockerContainer'] = docker_container
            
            # DockerPath
            tool = 'docker'
            toolPath = find_executable(tool)
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
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('{Dataprov}command').text
        self.data['dockerPath'] = root.find('{Dataprov}dockerPath').text
        self.data['dockerVersion'] = root.find('{Dataprov}dockerVersion').text
        # Docker Container
        docker_container_ele = root.find('{Dataprov}dockerContainer')
        docker_container = DockerContainer()
        docker_container.from_xml(docker_container_ele, validate)
        self.data['dockerContainer'] = docker_container

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'command').text = self.data['command']
        etree.SubElement(root, 'dockerPath').text = self.data['dockerPath']
        etree.SubElement(root, 'dockerVersion').text = self.data['dockerVersion']
        docker_container_ele = self.data['dockerContainer'].to_xml()
        root.append(docker_container_ele)
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
                except docker.errors.APIError:
                    continue