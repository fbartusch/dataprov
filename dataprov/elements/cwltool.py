import os
import sys
import shutil
import subprocess
import cwltool
import cwltool.main
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.file import File
from dataprov.elements.cwl_command_line_tool import CWLCommandLineTool
from dataprov.elements.cwl_workflow import CWLWorkflow
from dataprov.definitions import XML_DIR

class CWLTool(GenericElement):
    '''
    This class describes an operation using CWLCommandLineTool or CWLWorkflow.
    '''
    
    element_name = "cwltool"
    schema_file = os.path.join(XML_DIR, 'cwl/cwltool_element.xsd')
    
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
            # Output directory
            outdir = args.outdir
            # Path to CWL file
            uri, tool_file_uri = cwltool.load_tool.resolve_tool_uri(args.workflow, resolver=cwltool.resolver.tool_resolver, fetcher_constructor=None)
            # Job order (e.g. input bindings)
            job_order_object, input_basedir, jobloader = cwltool.main.load_job_order(args, sys.stdin, None, None, tool_file_uri)
            # Parse CWL file and create a CWL tool
            cwl_tool = cwltool.load_tool.load_tool(args.workflow, cwltool.workflow.defaultMakeTool)
            self.data['cwlVersion'] = cwl_tool.metadata['cwlVersion']
            self.data['cwlFile'] = File(urlparse(tool_file_uri).path)
            self.data['cwlJobOrder'] = File(urlparse(job_order_object['id']).path)
            
            # Is the a CommandLineTool or a Workflow?
            cwl_tool_class = cwl_tool.tool['class']
            if cwl_tool_class == "CommandLineTool":
                self.data['cwlCommandLineTool'] = CWLCommandLineTool(cwl_tool, job_order_object, outdir)
                self.data['cwlWorkflow'] = None
            elif cwl_tool_class == "Workflow":
                self.data['cwlWorkflow'] = CWLWorkflow(cwl_tool, job_order_object, outdir)
                self.data['cwlCommandLineTool'] = None
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
        #target_ele = root.find('target')
        #target = File()
        #target.from_xml(target_ele, validate=False)
        self.data['wrappedCommand'] = root.find('wrappedCommand').text
        self.data['cwltoolPath'] = root.find('cwltoolPath').text
        self.data['cwltoolVersion'] = root.find('cwltoolVersion').text
        self.data['cwlVersion'] = root.find('cwlVersion').text
        # CWL file
        cwl_file_ele = root.find('cwlFile')
        cwl_file = File()
        cwl_file.from_xml(cwl_file_ele)
        self.data['cwlFile'] = cwl_file
        # CWL job order
        cwl_job_order_ele = root.find('cwlJobOrder')
        cwl_job_order = File()
        cwl_job_order.from_xml(cwl_job_order_ele)
        self.data['cwlJobOrder'] = cwl_job_order
        # CommandLineTool or Workflow?
        cwl_command_line_tool_ele = root.find('cwlCommandLineTool')
        cwl_workflow_ele = root.find('cwlWorkflow')
        if cwl_command_line_tool_ele is not None:
            self.data['cwlCommandLineTool'] = cwl_command_line_tool_ele.to_xml()
        elif cwl_workflow_ele is not None:
            self.data['cwlWorkflow'] = cwl_workflow_ele.to_xml()
    
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, "wrappedCommand").text = self.data["wrappedCommand"]
        etree.SubElement(root, "cwltoolPath").text = self.data["cwltoolPath"]
        etree.SubElement(root, "cwltoolVersion").text = self.data["cwltoolVersion"]
        etree.SubElement(root, "cwlVersion").text = self.data["cwlVersion"]
        cwl_file_ele = self.data["cwlFile"].to_xml("cwlFile")
        root.append(cwl_file_ele)
        cwl_job_order_ele = self.data["cwlJobOrder"].to_xml("cwlJobOrder")
        root.append(cwl_job_order_ele)
        if self.data['cwlCommandLineTool'] is not None:
            command_line_tool_ele = self.data['cwlCommandLineTool'].to_xml()
            root.append(command_line_tool_ele)
        elif self.data['cwlWorkflow'] is not None:
            workflow_ele = self.data['cwlWorkflow'].to_xml()
            root.append(workflow_ele)
        
        return root
        
            
    def get_input_files(self):
        '''
        Get input files specified by the wrapped command
        (e.g. from CWL input bindings)
        '''
        if self.data['cwlCommandLineTool'] is not None:
            return self.data['cwlCommandLineTool'].get_input_files()
        elif self.data['cwlWorkflow'] is not None:
            return self.data['cwlWorkflow'].get_input_files()


    def get_output_files(self):
        '''
        Get output files specified by the wrapped command
        (e.g. from outputs specified by CWL files)
        '''
        if self.data['cwlCommandLineTool'] is not None:
            return self.data['cwlCommandLineTool'].get_output_files()
        elif self.data['cwlWorkflow'] is not None:
            return self.data['cwlWorkflow'].get_output_files()
            
            
#CWL command line example
#argsl = ["data/cwl/20_software-requirements/custom-types.cwl", "data/cwl/20_software-requirements/custom-types.yml"]



# Has it's own module now
#argsl = ["data/cwl/user_guide/1st-tool.cwl", "data/cwl/user_guide/echo-job.yml"]
#arg_parser = cwltool.main.arg_parser()
#args = arg_parser.parse_args(argsl)

#uri, tool_file_uri = cwltool.load_tool.resolve_tool_uri(args.workflow, resolver=cwltool.resolver.tool_resolver, fetcher_constructor=None)


#job_order_object, input_basedir, jobloader = cwltool.main.load_job_order(args, sys.stdin, None, None, tool_file_uri)


#cwl_tool = cwltool.load_tool.load_tool(args.workflow, cwltool.workflow.defaultMakeTool)
#cwl_tool.tool
#cwl_tool.requirements
#cwl_tool.hints
#cwl_tool.inputs_record_schema # + job_order_dict to describe inputs
#cwl_tool.outputs_record_schem # to describe outputs
# Prints on which .cwl files the command depends:
#cwltool.main.main(["--print-deps", "data/cwl/user_guide/1st-tool.cwl", "data/cwl/user_guide/echo-job.yml"])
#{
#    "class": "File",
#    "location": "1st-tool.cwl"
#}

# cwlCommandLineTool:
#cwl_tool = cwltool.load_tool.load_tool("data/cwl/user_guide/1st-tool.cwl", cwltool.workflow.defaultMakeTool)
# tool (what to execute)
#cwl_tool.tool
# hints (docker, directories, ...)
#cwl_tool.hints
# inputs of the tool
#cwl_tool.inputs_record_schema
# outputs of the tool
#cwl_tool.outputs_record_schema


# cwlWorkflow
#cwl_tool = cwltool.load_tool.load_tool("data/cwl/user_guide/1st-workflow.cwl", cwltool.workflow.defaultMakeTool)

# Run workflow
#cwltool.main.main(["data/cwl/user_guide/1st-workflow.cwl", "data/cwl/user_guide/1st-workflow-job.yml"])

# Validate tool definition
#cwltool.main.main(["--validate", "data/cwl/user_guide/1st-workflow.cwl", "data/cwl/user_guide/1st-workflow-job.yml"])

# print rdf: 
# cwltool.main.main(["--print-rdf", "data/cwl/user_guide/1st-workflow.cwl", "data/cwl/user_guide/1st-workflow-job.yml"])