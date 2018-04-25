from __future__ import absolute_import, division, print_function
import os
import sys
import subprocess
import glob
import cwltool
import cwltool.main
import cwltool.stdfsaccess
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
from distutils.spawn import find_executable
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.file import File
from dataprov.elements.cwl_command_line_tool import CWLCommandLineTool
from dataprov.definitions import XML_DIR

class CWLTool(GenericOp):
    '''
    This class describes an operation using CWLCommandLineTool or CWLWorkflow.
    '''
    
    element_name = "cwltool"
    schema_file = os.path.join(XML_DIR, 'cwl/cwltool_element.xsd')
    
    def __init__(self, remaining=None):
        super(CWLTool, self).__init__()
        
        if remaining is not None:
            self.remaining = remaining[:]
            # Wrapped command
            self.data['wrappedCommand'] = ' '.join(remaining)
            # Tool Path
            tool = 'cwltool'
            toolPath = find_executable(tool)
            self.data['cwltoolPath'] = toolPath
            
            # Tool Version
            try:
                toolVersion = subprocess.check_output([tool,  '--version'])
            except:
                toolVersion = None
            if toolVersion is not None:
                self.data['cwltoolVersion'] = toolVersion
            else:
                self.data['cwltoolVersion'] = 'unknown'
       
            # Get information from the CWL file and the job order (e.g. input bindings)
            arg_parser = cwltool.main.arg_parser()
            args = arg_parser.parse_args(remaining[1:])
            # Path to CWL file
            uri, tool_file_uri = cwltool.load_tool.resolve_tool_uri(args.workflow, resolver=cwltool.resolver.tool_resolver, fetcher_constructor=None)
            # Job order (e.g. input bindings)
            job_order_object, input_basedir, jobloader = cwltool.main.load_job_order(args, sys.stdin, None, None, tool_file_uri)
            # Parse CWL file and create a CWL tool
            cwl_tool = cwltool.load_tool.load_tool(args.workflow, cwltool.workflow.defaultMakeTool)       
            self.data['cwlVersion'] = cwl_tool.metadata['cwlVersion']  # record it, but isn't part of schema
            self.data['cwlFile'] = File(urlparse(tool_file_uri).path)  # record it, but isn't part of schema
            self.data['cwlJobOrder'] = File(urlparse(job_order_object['id']).path)
            
            # Is the a CommandLineTool or a Workflow?
            cwl_tool_class = cwl_tool.tool['class']
            if cwl_tool_class == "CommandLineTool":
                self.data['cwlCommandLineTool'] = CWLCommandLineTool(remaining[1:])
                self.data['cwlWorkflow'] = None
            #elif cwl_tool_class == "Workflow":
            #    self.data['cwlWorkflow'] = CWLWorkflow(remaining[1:])
            #    self.data['cwlCommandLineTool'] = None
            else:
                print("Unknown cwl tool class: ", cwl_tool_class)
                exit(1)


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
        self.data['wrappedCommand'] = root.find('{Dataprov}wrappedCommand').text
        self.data['cwltoolPath'] = root.find('{Dataprov}cwltoolPath').text
        self.data['cwltoolVersion'] = root.find('{Dataprov}cwltoolVersion').text
        
        # CWL job order
        cwl_job_order_ele = root.find('{Dataprov}cwlJobOrder')
        cwl_job_order = File()
        cwl_job_order.from_xml(cwl_job_order_ele)
        self.data['cwlJobOrder'] = cwl_job_order
        # CommandLineTool or Workflow?
        cwl_command_line_tool_ele = root.find('{Dataprov}cwlCommandLineTool')
        cwl_workflow_ele = root.find('{Dataprov}cwlWorkflow')
        if cwl_command_line_tool_ele is not None:
            self.data['cwlCommandLineTool'] = cwl_command_line_tool_ele.from_xml()
        elif cwl_workflow_ele is not None:
            self.data['cwlWorkflow'] = cwl_workflow_ele.from_xml()
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, "wrappedCommand").text = self.data["wrappedCommand"]
        etree.SubElement(root, "cwltoolPath").text = self.data["cwltoolPath"]
        etree.SubElement(root, "cwltoolVersion").text = self.data["cwltoolVersion"]
        
        cwl_job_order_ele = self.data["cwlJobOrder"].to_xml("cwlJobOrder")
        root.append(cwl_job_order_ele)
        if self.data['cwlCommandLineTool'] is not None:
            command_line_tool_ele = self.data['cwlCommandLineTool'].to_xml()
            root.append(command_line_tool_ele)
        elif self.data['cwlWorkflow'] is not None:
            workflow_ele = self.data['cwlWorkflow'].to_xml()
            root.append(workflow_ele)
        
        return root
                 
    def get_input_data_objects(self):
        '''
        Get input data_objects specified by the wrapped command
        (e.g. from CWL input bindings)
        '''
        if self.data['cwlCommandLineTool'] is not None:
            return self.data['cwlCommandLineTool'].get_input_data_objects()
        elif self.data['cwlWorkflow'] is not None:
            return self.data['cwlWorkflow'].get_input_data_objects()


    def get_output_data_objects(self):
        '''
        Get output data objects specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        if self.data['cwlCommandLineTool'] is not None:
            return self.data['cwlCommandLineTool'].get_output_data_objects()
        elif self.data['cwlWorkflow'] is not None:
            return self.data['cwlWorkflow'].get_output_data_objects()
    
    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        # If the output files contain wildcards, use the output of the cwltool command
        # to replace the output with the correct path to the output file.
        
        # New list of output files
        output_files = []        
        
        # Get the known output files
        tmp_output_files = self.get_output_data_objects()
        # Get the known output files that containe a wildcard.
        # The other output files have no wildcards and won't be changed
        output_files_wildcards = []
        for output_file in tmp_output_files:
            if '*' in output_file:
                output_files_wildcards.append(output_file)
            else:
                output_files.append(output_file)
         
        # Iterate over the wildcards and use glob to list all matching files.
        # Check for each listed file, if it's contained in the output of the cwltool run.
        # If yes, add it to the list of output files
        cwltool_stdout_lines = self.output.decode('ascii').splitlines()
        for wildcard in output_files_wildcards:
            wildcard_matches = glob.glob(wildcard)
            for wildcard_match in wildcard_matches:
                if sum([True for l in cwltool_stdout_lines if wildcard_match in l]) > 0:
                    output_files.append(wildcard_match)
         
        # Set the new list of output files
        if self.data['cwlCommandLineTool'] is not None:
            self.data['cwlCommandLineTool'].output_data_objects = output_files
        elif self.data['cwlWorkflow'] is not None:
            self.data['cwlWorkflow'].output_data_objects = output_files
        return