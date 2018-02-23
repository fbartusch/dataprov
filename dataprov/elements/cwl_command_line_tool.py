import os
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
import cwltool

from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR

class CWLCommandLineTool(GenericElement):
    '''
    This class describes a CWLCommandLineTool element.
    '''
    
    element_name = "cwlCommandLineTool"
    schema_file = os.path.join(XML_DIR, 'cwl/cwlCommandLineTool_element.xsd')
    
    def __init__(self, cwl_tool=None, job_order_object=None, outdir=None):
        # Empty data attribute
        self.data = defaultdict()
        self.input_files = []
        self.output_files = []
        if not cwl_tool is None and job_order_object is not None:
            # Additional input files
            for input in job_order_object:
                if input != 'id' and job_order_object[input]['class'] == 'File':
                    path = urlparse(job_order_object[input]['path']).path
                    self.input_files.append(path)
            # Additional output files
            for output in cwl_tool.tool['outputs']:
                if output != 'id' and output['type'] == 'File':
                    name = output['outputBinding']['glob']
                    path = os.path.join(outdir, name)
                    self.output_files.append(path)
            # Base command
            base_command = ' '.join(cwl_tool.tool['baseCommand'])
            # Arguments
            #TODO Implement
            self.data['baseCommand'] = base_command
            
#  <xs:complexType name="cwlCommandLineTool">
#    <xs:sequence>
#      <xs:element name="baseCommand" type="xs:string"/>
#      <xs:element name="inputs" type="fileList"/>
      #<xs:element name="outputs" type="fileList"/>#
    #</xs:sequence#>
  #</xs:complexType>

    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        for child in root:
            self.data[child.tag] = child.text    
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        Each subclass has to implement itself, because data (defaultdict) elements
        are not ordered.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, "baseCommand").text = self.data["baseCommand"]
        return root
        
            
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