import os
import subprocess
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.command_line import CommandLine
from dataprov.definitions import XML_DIR
# Conditional imports. If the docker, cwltool or snakemake is not installed throw no error
try:
    from dataprov.elements.docker import Docker
except ImportError as e:
    print(str(e))
try:
    from dataprov.elements.cwltool import CWLTool
except ImportError as e:
    print(str(e))
try:
    import snakemake
    from dataprov.elements.snakemake import Snakemake
except ImportError as e:
    print(str(e))



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
        self.remaining = list(remaining)
        self.input_files = []
        self.output_files = []
        if remaining is not None:
            # Try to determine the correct opClass
            # (e.g. docker, singularity, commandLine, ...)
            self.executable = remaining[0].split()[0]
            if self.executable == "docker":
                self.data['opClass'] = Docker(remaining)
            #elif executable == "singularity"
                #TODO implement
                #self.data['opClass'] = Singularity(remaining)
            elif self.executable == 'cwltool':
                self.data['opClass'] = CWLTool(remaining)
            elif self.executable == 'snakemake':
                self.data['opClass'] = Snakemake(remaining)
            else:
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
        # Discriminate from child tag which class to use
        child_tag = root[0].tag
        print(child_tag)
        if child_tag == 'docker':
            #TODO implement
            op_class = Docker()
            docker_ele = root.find('docker')
            op_class.from_xml(docker_ele, validate)
        #elif root_tag =='singularity':
            #TODO implement
        else:
            op_class = CommandLine()
            command_line_ele = root.find('commandLine')
            op_class.from_xml(command_line_ele, validate)
        self.data['opClass'] = op_class
        
        
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = self.data['opClass'].to_xml()
        return root


    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        self.data['opClass'].post_processing()
    
    
    def get_input_files(self):
        '''
        Get input files specified by the wrapped command
        (e.g. from CWL input bindings)
        '''
        return self.data['opClass'].get_input_files()


    def get_output_files(self):
        '''
        Get output files specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        return self.data['opClass'].get_output_files()


    def run(self):
        '''
        Run the wrapped command or workflow.
        '''
        # Snakemake starts a child process for the workflow and therefore
        # subprocess would return immediately. So use the snakemake Python API.
        if self.executable == "snakemake":
            print("Before Snakemake main")
            #parser = snakemake.get_argument_parser()
            #args = parser.parse_args(self.remaining[1:])
            try:
                snakemake.main(self.remaining[1:])
            except SystemExit as e:
                # snakemake main wants to exit ... but we want to write the xml files 
                print("After Snakemake main")
                return            
        else:
            subprocess.run(' '.join(self.remaining), shell=True) 