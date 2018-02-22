import os
import shutil
import subprocess
from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR

class CWLTool(GenericElement):
    '''
    This class describes an operation using CWLCommandLineTool or CWLWorkflow.
    '''
    
    element_name = "cwltool"
    schema_file = os.path.join(XML_DIR, 'cwltool_element.xsd')
    
    def __init__(self, remaining=None) :
        # Empty data attribute
        self.data = defaultdict()
        
        if remaining is not None:
            # Wrapped command
            self.data['wrappedCommand'] = ' '.join(remaining)
            # Tool Path
            tool = 'cwltool'
            toolPath = shutil.which(tool)
            self.data['cwltoolPath'] = toolPath
            
            # Tool Version
            try:
                toolVersion1 = subprocess.check_output([tool,  '--version'])
            except:
                toolVersion1 = None
            if toolVersion1 is not None:
                self.data['cwltoolVersion'] = toolVersion1
            else:
                self.data['cwltoolVersion'] = 'unknown'

             
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
        for child in root:
            self.data[child.tag] = child.text    
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        Each subclass has to implement itself, because data (defaultdict) elements
        are not ordered.
        '''
        return ""
        
            

