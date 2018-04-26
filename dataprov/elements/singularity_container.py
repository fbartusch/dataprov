from __future__ import absolute_import, division, print_function
import os
import subprocess
import json
from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.data_object import DataObject
from dataprov.definitions import XML_DIR, DATAPROV


class SingularityContainer(GenericElement):
    '''
    This class describes a Singularity container used by some operation types.
    '''

    element_name = DATAPROV + "singularityContainer"
    schema_file = os.path.join(XML_DIR, 'singularity/singularityContainer_element.xsd') 

    singularity_methods = ["singularityPull", "singularityLocal"]

    def __init__(self, method=None, source=None):
        super(SingularityContainer, self).__init__()

        if method is not None and source is not None:
            if method not in self.singularity_methods:
                print("Unknown singularity image source method: ", method)
                
            # ImageSource
            self.data['method'] = method
            self.data['source'] = source

            # ImageDetails
            #TODO Can you get metadata of container from SingularityHub/DockerHub?
            if method == "singularityLocal":
                source_abs = os.path.abspath(source)
                source_data_object = DataObject(source_abs)
                self.data['source'] = source_data_object
                
                self.data['imageDetails'] = defaultdict()
                image_dict = self.get_image_details(source)
                self.data['imageDetails']['labels'] = image_dict
                self.data['imageDetails']['singularityVersion'] = "unknown"

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
        image_source_ele = root.find('{Dataprov}imageSource')
        children = list(image_source_ele)
        self.data['method'] = children[0].tag
        if self.data['method'] == "singularityPull":
            self.data['source'] = image_source_ele.find('{Dataprov}singularityPull').text
        elif self.data['method'] == "singularityLocal":
            source_ele = image_source_ele.find('{Dataprov}singularityLocal')
            source = DataObject()
            source.from_xml(source_ele)
            self.data['source'] = source

        # Image Details
        if self.data['method'] == "singularityLocal":
            image_detail_ele = root.find('{Dataprov}imageDetails')
            self.data['imageDetails'] = defaultdict()
            self.data['imageDetails']['singularityVersion'] = image_detail_ele.find('{Dataprov}singularityVersion').text
            labels = defaultdict()
            for item in image_detail_ele.find('{Dataprov}labels').findall('{Dataprov}item'):
                attributes = item.attrib
                labels[attributes['key']] = attributes['value']
            self.data['imageDetails']['labels'] = labels

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)

        # ImageSource
        image_source_ele = etree.SubElement(root, DATAPROV + 'imageSource')

        if self.data['method'] == "singularityPull":
            etree.SubElement(image_source_ele, DATAPROV + self.data['method']).text = self.data['source']
        elif self.data['method'] == "singularityLocal":
            source_ele = self.data['source'].to_xml(DATAPROV + self.data['method'])
            image_source_ele.append(source_ele)
        else:
            print("Unknown method; ", self.data['method'])

        # Image details
        if self.data['method'] == "singularityLocal":
            image_detail_ele = etree.SubElement(root, DATAPROV + "imageDetails")
            etree.SubElement(image_detail_ele, DATAPROV + 'singularityVersion').text = self.data['imageDetails']['singularityVersion']
            labels = etree.SubElement(image_detail_ele, DATAPROV + 'labels')
            for key,value in self.data['imageDetails']['labels'].items():
                etree.SubElement(labels, DATAPROV + 'item', attrib={'key':key, 'value':value})
        return root

    def get_image_details(self, image):
        '''
        Get details of a singularity image.
        '''
        command = "singularity inspect " + image
        op_output = subprocess.check_output(command, shell=True)
        print("op_output: ", op_output)    
        image_dict = json.loads(op_output)
        return image_dict
