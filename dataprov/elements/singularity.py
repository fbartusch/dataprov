import os
import shutil
import subprocess
from collections import defaultdict
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.singularity_container import SingularityContainer
from lxml import etree
from dataprov.definitions import XML_DIR


class Singularity(GenericOp):
    '''
    This class describes a command executed in a Singularity container.
    '''

    element_name = "singularity"
    schema_file = schema_file = os.path.join(XML_DIR, 'singularity_element.xsd')

    def __init__(self, remaining=None):
        super().__init__()
        
        self.remaining = remaining

        if remaining is not None:
            # Command
            self.data['command'] = ' '.join(remaining)

            # Get the output of singularity inspect on the container
            image = self.get_container_image(remaining)

            # Create the singularity container object
            singularity_container = SingularityContainer("singularityLocal", image)
            self.data['singularityContainer'] = singularity_container
            
            # SingularityPath
            tool = 'singularity'
            toolPath = shutil.which(tool)
            self.data['singularityPath'] = toolPath

            # SingularityVersion
            try:
                singularityVersion = subprocess.check_output([tool,  '--version'])
            except:
                singularityVersion = None
            if singularityVersion is not None:
                self.data['singularityVersion'] = singularityVersion
            else:
                self.data['singularityVersion'] = 'unknown'

    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('command').text
        self.data['singularityPath'] = root.find('singularityPath').text
        self.data['singularityVersion'] = root.find('singularityVersion').text
        # Singularity Container
        singularity_container_ele = root.find('singularityContainer')
        singularity_container = SingularityContainer()
        singularity_container.from_xml(singularity_container_ele, validate)
        self.data['singularityContainer'] = singularity_container

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'command').text = self.data['command']
        etree.SubElement(root, 'singularityPath').text = self.data['singularityPath']
        etree.SubElement(root, 'singularityVersion').text = self.data['singularityVersion']
        singularity_container_ele = self.data['singularityContainer'].to_xml()
        root.append(singularity_container_ele)
        return root

    def get_container_image(self, remaining):
        '''
        Get the container image from the wrapped command.
        '''
        # Iterate over the arguments, ignore everything starting with '-'.
        # For the other strings, check if it's a singularity image
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
                    command = "singularity inspect " + s
                    out = subprocess.check_output(command, shell=True)
                    print("s: ", s, " out: ", out)
                    return s
                except:
                    continue