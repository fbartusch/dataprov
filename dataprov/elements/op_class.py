import os
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.command_line import CommandLine
from dataprov.elements.docker import Docker
from dataprov.elements.cwltool import CWLTool
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
            executable = remaining[0].split()[0]
            if executable == "docker":
                self.data['opClass'] = Docker(remaining)
            #elif executable == "singularity"
                #TODO implement
                #self.data['opClass'] = Singularity(remaining)
            elif executable == 'cwltool':
                self.data['opClass'] = CWLTool(remaining)
            else:
                #Generic command line tool
                self.data['opClass'] = CommandLine(remaining)




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