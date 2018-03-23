from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.utils.io import prettify
from dataprov.definitions import XML_DIR

class GenericOp(GenericElement):
    '''
    This class describes a generic operation.
    This class provides basic functionalities to execute the operation via subprocess,
    post processing the output and returning information about output files.
    '''
    
    def __init__(self):
        # Empty data attribute
        self.data = defaultdict()
    
    
    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        return
    
    
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
            #parser = snakemake.get_argument_parser()
            #args = parser.parse_args(self.remaining[1:])
            try:
                snakemake.main(self.remaining[1:])
            except SystemExit as e:
                # snakemake main wants to exit ... but we want to write the xml files 
                return            
        else:
            output = subprocess.check_output(' '.join(self.remaining), shell=True)
            self.output = output
            print("Output: ", output)