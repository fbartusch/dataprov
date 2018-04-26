from __future__ import absolute_import, division, print_function
import sys
import os
import cwltool
import cwltool.flatten
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.elements.cwl_command_line_tool import CWLCommandLineTool
from dataprov.definitions import XML_DIR, DATAPROV

class CWLWorkflow(GenericElement):
    '''
    This class describes a CWLWorkflow element.
    '''
    
    element_name = DATAPROV + "cwlWorkflow"
    schema_file = os.path.join(XML_DIR, 'cwl/cwlWorkflow_element.xsd')
    
    def __init__(self, argsl=None):
        # Empty data attribute
        self.data = defaultdict()
        self.data['workflowSteps'] = []
        
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
            
            # cwlFile
            self.data['cwlFile'] = File(urlparse(tool_file_uri).path)
            # cwlVersion
            self.data['cwlVersion'] = cwl_tool.metadata['cwlVersion']                        
            
            # Additional input files
            #for input in job_order_object:
            #   if input != 'id' and job_order_object[input]['class'] == 'File':
            #        path = urlparse(job_order_object[input]['path']).path
            #        self.input_files.append(path)
                    
            # Additional output files
            #TODO same problem as for cwlCommandLineTools
            #for output in cwl_tool.tool['outputs']:
            #    if output != 'id' and output['type'] == 'File':
            #        name = output['outputBinding']['glob']
            #        path = os.path.join(outdir, name)
            #        self.output_files.append(path)
            
            
            #TODO Get workflow docker requirement and give them to workflow steps
            
            job_order_object = cwltool.main.init_job_order(job_order_object, args, cwl_tool, print_input_deps=args.print_input_deps, relative_deps=args.relative_deps, stdout=sys.stdout, make_fs_access=cwltool.stdfsaccess.StdFsAccess, loader=jobloader, input_basedir=input_basedir)
            del args.workflow
            del args.job_order
            jobiter = cwl_tool.job(job_order_object, self.do_nothing, **vars(args))
            
            # The job for the whole workflow
            workflow_job = jobiter.__next__()
            
            # Iterate over the workflow steps and collect data about them
            i = 0
            print(workflow_job.steps)
            #for workflow_step_job in jobiter:
            for workflow_step in workflow_job.steps:
                print(i)
                workflow_step_job = jobiter.__next__()
                i = i+1
                if not workflow_step_job:
                    break
                cur_step = CWLCommandLineTool()
                cur_step.from_job(workflow_job, workflow_step_job)
                self.data['workflowSteps'].append(cur_step)
                # Fake the run of this job ...
                # Set workflow_step_job.completed = True
                # Set workflow_job.made_progress = True
            
        
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
        '''
        root = etree.Element(self.element_name)
        # CWL file
        cwl_file_ele = self.data["cwlFile"].to_xml(DATAPROV + "cwlFile")
        root.append(cwl_file_ele)
        # CWL Version
        etree.SubElement(root, DATAPROV + "cwlVersion").text = self.data["cwlVersion"]
        # WorkflowSteps
        steps_ele = etree.SubElement(root, DATAPROV + "workflowSteps")
        print(self.data['workflowSteps'])
        for workflow_step in self.data['workflowSteps']:
            steps_ele.append(workflow_step.to_xml())
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
        
    def do_nothing():
        return