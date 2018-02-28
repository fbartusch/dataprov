import sys
import os
import cwltool
import cwltool.flatten
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
from dataprov.elements.generic_element import GenericElement
from dataprov.definitions import XML_DIR

class CWLWorkflow(GenericElement):
    '''
    This class describes a CWLWorkflow element.
    '''
    
    element_name = "cwlWorkflow"
    schema_file = os.path.join(XML_DIR, 'cwl/cwlWorkflow_element.xsd')
    
    def __init__(self, argsl=None):
        # Empty data attribute
        self.data = defaultdict()
        
        self.input_files = []
        self.output_files = []
        
        if argsl is not None:
            
            # Get information from the CWL file and the job order (e.g. input bindings)
            arg_parser = cwltool.main.arg_parser()
            args = arg_parser.parse_args(argsl)
            # Output directory
            outdir = args.outdir
            # Path to CWL file
            uri, tool_file_uri = cwltool.load_tool.resolve_tool_uri(args.workflow, resolver=cwltool.resolver.tool_resolver, fetcher_constructor=None)
            # Job order (e.g. input bindings)
            job_order_object, input_basedir, jobloader = cwltool.main.load_job_order(args, sys.stdin, None, None, tool_file_uri)
            # Parse CWL file and create a CWL tool
            cwl_tool = cwltool.load_tool.load_tool(args.workflow, cwltool.workflow.defaultMakeTool)          
            
            # Additional input files
            #for input in job_order_object:
            #    if input != 'id' and job_order_object[input]['class'] == 'File':
            #        path = urlparse(job_order_object[input]['path']).path
            #        self.input_files.append(path)
                    
            # Additional output files
            #for output in cwl_tool.tool['outputs']:
            #    if output != 'id' and output['type'] == 'File':
            #        name = output['outputBinding']['glob']
            #        path = os.path.join(outdir, name)
            #        self.output_files.append(path)
            
            
            job_order_object = cwltool.main.init_job_order(job_order_object, args, cwl_tool, print_input_deps=args.print_input_deps, relative_deps=args.relative_deps, stdout=sys.stdout, make_fs_access=cwltool.stdfsaccess.StdFsAccess, loader=jobloader, input_basedir=input_basedir)
            del args.workflow
            del args.job_order
            jobiter = cwl_tool.job(job_order_object, self.do_nothing, **vars(args))
            
            # The job for the whole workflow
            workflow_job = jobiter.__next__()
            
            # Iterate over the workflow steps and collect data about them
            for workflow_step in jobiter:
                # Get type of the step
                step_type = type(workflow_step1)
            
                # Based on the type, create the corresponding objects
            
        
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
        #etree.SubElement(root, "name").text = self.data["name"]
        return root
        
            

