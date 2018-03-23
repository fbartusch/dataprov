import sys
import os
import cwltool
import cwltool.flatten
from collections import defaultdict
from lxml import etree
from urllib.parse import urlparse
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.docker_container import DockerContainer
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR

class CWLCommandLineTool(GenericOp):
    '''
    This class describes a CWLCommandLineTool element.
    '''
    
    element_name = "cwlCommandLineTool"
    schema_file = os.path.join(XML_DIR, 'cwl/cwlCommandLineTool_element.xsd')
    
    def __init__(self, argsl=None, wf_requirements=None):
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
            
            # cwlFile
            self.data['cwlFile'] = File(urlparse(tool_file_uri).path)
            # cwlVersion
            self.data['cwlVersion'] = cwl_tool.metadata['cwlVersion']            
            
            # Additional input files
            for input in job_order_object:
                if input != 'id' and job_order_object[input]['class'] == 'File':
                    path = urlparse(job_order_object[input]['path']).path
                    self.input_files.append(path)
                    
            # Additional output files
            #TODO does not work if outputBinding uses '*'
            #TODO Try to determine output files after execution of tool?
            #This should be possible because the output file path is printed after execution of the command
            for output in cwl_tool.tool['outputs']:
                if output != 'id' and output['type'] == 'File':
                    name = output['outputBinding']['glob']
                    path = os.path.join(outdir, name)
                    self.output_files.append(path)
                    
            # Get job object
            job_order_object = cwltool.main.init_job_order(job_order_object, args, cwl_tool, print_input_deps=args.print_input_deps, relative_deps=args.relative_deps, stdout=sys.stdout, make_fs_access=cwltool.stdfsaccess.StdFsAccess, loader=jobloader, input_basedir=input_basedir)
            del args.workflow
            del args.job_order
            jobiter = cwl_tool.job(job_order_object, self.do_nothing, **vars(args))            
            job = jobiter.__next__()
            
            # CWL perfomrs computations in a temporary directory. The command string would countain these temporary directories.
            # Compute a map of path in cwltool temporary environment to real path
            file_mapping = dict()
            for binding in job.builder.bindings:
                value = binding.get("datum")
                if isinstance(value, dict) and value.get("class") in ("File", "Directory"):
                    real_path = urlparse(value['location']).path
                    file_mapping[value['path']] = real_path
            
            # Build command line
            command_line_list = cwltool.flatten.flatten(list(map(job.builder.generate_arg, job.builder.bindings)))
            
            # Iterate over command line and swap the temporary CWL paths with the real paths
            new_command_line_list = []      
            for value in command_line_list:
                if value in file_mapping:
                    new_command_line_list.append(file_mapping[value])
                else:
                    new_command_line_list.append(value)
                    
            # Command
            command = ' '.join(new_command_line_list)
            self.data['command'] = command
            
            # DockerRequirement
            job_hints = job.builder.hints
            job_requirements = job.builder.requirements
            
            self.record_docker_requirement(job_requirements, job_hints, wf_requirements)


    def record_docker_requirement(self, job_requirements, job_hints, wf_requirements=None):
        '''
        Get the Docker Requirement from the cwl information
        '''
        # Docker container are specified in the hints or requirements section
        # Requirements overrides hints! (http://www.commonwl.org/v1.0/CommandLineTool.html#Requirements_and_hints)
        # An enclosing workflow requirement also overrides hints of the command line tool
        # Search for Docker requirements
        # Docker requirement provided by workflow?
        docker_requirement = None
        print ("wf_requirements: ", wf_requirements)
        if wf_requirements is not None and len(wf_requirements) > 0 and wf_requirements['DockerRequirement'] is not None:
            docker_requirement = wf_requirements['DockerRequirement']
        if docker_requirement is None and job_requirements is not None:
            for requirement in job_requirements:
                if requirement['class'] == "DockerRequirement":
                    docker_requirement = requirement
                    break
        if docker_requirement is None and job_hints is not None:
            for hint in job_hints:
                if hint['class'] == "DockerRequirement":
                    docker_requirement = hint
                    break
            
        if docker_requirement is not None:
            cwl_docker_methods = ["dockerPull", "dockerLoad", "dockerFile", "dockerImport"] 
            docker_req_dict = dict(docker_requirement)
            for key, value in docker_req_dict.items():
                if key in cwl_docker_methods:
                    method = key
                    source = value
            docker_container_object = DockerContainer(method, source)
            self.data['dockerRequirement'] = docker_container_object
        else:
            self.data['dockerRequirement'] = None


    def from_job(self, workflow_job, step_job, wf_requirements=None):
        '''
        Record information from a cwltool.job.CommandLineJob object
        '''
        # Get step name
        step_name = step_job.name
        cwl_path = ""
        # Get the corresponding cwl file from the workflow
        for step in workflow_job.tool['steps']:
            if step['id'].split('#')[1] == step_name:
                cwl_path = urlparse(step['run']).path
                cwl_file = File(cwl_path)
                self.data['cwlFile'] = cwl_file
                break
        # cwlVersion
        cwl_tool = cwltool.load_tool.load_tool(cwl_path, cwltool.workflow.defaultMakeTool)
        self.data['cwlVersion'] = cwl_tool.tool['cwlVersion']

        # CWL perfomrs computations in a temporary directory. The command string would countain these temporary directories.
        # Compute a map of path in cwltool temporary environment to real path
        file_mapping = dict()
        for binding in step_job.builder.bindings:
            value = binding.get("datum")
            if isinstance(value, dict) and value.get("class") in ("File", "Directory"):
                real_path = urlparse(value['location']).path
                file_mapping[value['path']] = real_path

        # Command
        # Build command line
        command_line_list = cwltool.flatten.flatten(list(map(step_job.builder.generate_arg, step_job.builder.bindings)))
        
        # Iterate over command line and swap the temporary CWL paths with the real paths
        new_command_line_list = []      
        for value in command_line_list:
            if value in file_mapping:
                new_command_line_list.append(file_mapping[value])
            else:
                new_command_line_list.append(value)
                
        # Command
        command = ' '.join(new_command_line_list)
        self.data['command'] = command
        # Docker Requirement
        job_hints = step_job.builder.hints
        job_requirements = step_job.builder.requirements
        self.record_docker_requirement(job_requirements, job_hints, wf_requirements)

       
    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        # CWL File
        cwl_file = File()
        cwl_file.from_xml(root.find('cwlFile'))
        self.data['cwlFile'] = cwl_file
        # CWL Version
        self.data['cwlVersion'] = root.find('cwlVersion').text
        # Command
        self.data['command'] = root.find('command').text        
        # Docker Requirement
        docker_req_ele = root.find('dockerRequirement')
        if docker_req_ele is not None:
            docker_req = DockerContainer()
            docker_req.from_xml(root.find('dockerRequirement'))
            self.data['dockerRequirement'].append(docker_req)
            
    
    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        Each subclass has to implement itself, because data (defaultdict) elements
        are not ordered.
        '''
        root = etree.Element(self.element_name)
        # CWL file
        cwl_file_ele = self.data['cwlFile'].to_xml("cwlFile")
        root.append(cwl_file_ele)
        # CWL Version
        etree.SubElement(root, "cwlVersion").text = self.data["cwlVersion"]
        # Command
        etree.SubElement(root, "command").text = self.data['command']
        # Docker Requirement
        if self.data['dockerRequirement'] is not None:
            docker_req_ele = self.data['dockerRequirement'].to_xml()
            docker_req_ele.tag = "dockerRequirement"
            root.append(docker_req_ele)
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

    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        # Parse output files from the captured output
        # This is especially important if wildcards were used in the cwl-file
        # Replace the wildcards with the actual filenames
        # so we now for which file a prov-file should be written
        print(self.output)
        return
    
    def do_nothing():
        return