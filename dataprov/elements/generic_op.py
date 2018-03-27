import subprocess
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement

class GenericOp(GenericElement):
    '''
    This class describes a generic operation and provides basic functions that
    should be implemented by the actual operations.
    '''
    
    def __init__(self):
        # Empty data attribute
        self.data = defaultdict()
        self.output = None
        self.executed = False
        # Input/Output files that aren't provided via dataprov command line options
        # and have to be infered from the actual operation
        self.input_files = []
        self.output_files = []
    
    def pre_processing(self):
        '''
        Perform necessary pre processing steps
        '''
        return

    def run(self):
        '''
        Run the wrapped command or workflow.
        '''
        # The generic operation can be run via a subprocess and saves the output
        op_output = subprocess.check_output(' '.join(self.remaining), shell=True)
        self.output = op_output
        self.executed = True
        print("op_output: ", op_output)    
    
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
        return self.input_files

    def get_output_files(self):
        '''
        Get output files specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        return self.output_files


