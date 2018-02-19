import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.command_line import CommandLine
from dataprov.definitions import XML_DIR
from lxml import etree


class OpClass(GenericElement):
    '''
    Class describing the a the opClass element.
    '''
    
    element_name = "opClass"
    schema_file = os.path.join(XML_DIR, 'opClass_element.xsd')
         
    
    def __init__(self, remaining=None):
        '''
        Initialize this file element.
        '''
        super().__init__()
        if remaining is not None:
            # Try to determine the correct opClass
            # (e.g. docker, singularity, commandLine, ...)
            executable = remaining[0]
            #if executable == "docker":
                #TODO implement
                #self.data['opClass'] = Docker(remaining)
            #elif executable == "singularity"
                #TODO implement
                #self.data['opClass'] = Singularity(remaining)
            #else:
                #Generic command line tool
            self.data['opClass'] = CommandLine(remaining)


    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        # Discriminate from root tag which class to use
        root_tag = root.tag
        #if root_tag == 'docker':
            #TODO implement
        #elif root_tag =='singularity':
            #TODO implement
        #else:
        op_class = CommandLine()
        command_line_ele = root.find('commandLine')
        op_class.from_xml(command_line_ele)
        self.data['opClass'] = op_class
        
        
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = self.data['opClass'].to_xml()
        return root