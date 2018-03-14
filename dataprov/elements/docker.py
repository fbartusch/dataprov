import os
import docker
from collections import defaultdict
from docker.errors import ImageNotFound
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.docker_container import DockerContainer
from lxml import etree
from dataprov.definitions import XML_DIR


class Docker(GenericElement):
    '''
    This class describes a command executed in a Docker container.
    '''

    element_name = "docker"
    schema_file = schema_file = os.path.join(XML_DIR, 'docker_element.xsd')

    def __init__(self, remaining=None):
        # Empty data attribute
        self.data = defaultdict()

        self.input_files = []
        self.output_files = []

        if remaining is not None:
            # Command
            self.data['command'] = ' '.join(remaining)

            # Get the output of docker inspect on the container
            image_dict = self.get_container_image(remaining)

            print(image_dict)

            # Create the docker container object
            docker_container = DockerContainer("dockerLocal", image_dict['RepoTags'][0])
            self.data['dockerContainer'] = docker_container

    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('command').text
        # Docker Container
        docker_container_ele = root.find('dockerContainer')
        docker_container = DockerContainer()
        docker_container.from_xml(docker_container_ele, validate)
        self.data['dockerContainer'] = docker_container

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'command').text = self.data['command']
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
                    print("Current s: ", s)
                    image_dict = client.inspect_image(s)
                    return image_dict
                except docker.errors.ImageNotFound:
                    continue
                except docker.errors.APIError:
                    continue

    def get_input_files(self):
        '''
        Get input files specified by the wrapped command
        (e.g. from CWL input bindings)
        '''
        return self.input_files

    def get_output_files(self):
        '''
        Get output files specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        return self.output_files

    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        return
