from __future__ import absolute_import, division, print_function
import os
from collections import defaultdict
import subprocess
import snakemake
from lxml import etree
from distutils.spawn import find_executable
from dataprov.elements.generic_op import GenericOp
from dataprov.elements.command_line import CommandLine
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR, DATAPROV

class Snakemake(GenericOp):
    '''
    This class describes a snakemake element.
    '''
    
    element_name = DATAPROV + "snakemake"
    schema_file = os.path.join(XML_DIR, 'snakemake_element.xsd')
    
    def __init__(self, remaining=None):
        super(Snakemake, self).__init__()
        
        if remaining is not None:
            self.remaining = remaining[:]
            # Command
            self.data['command'] = ' '.join(remaining)
            # Snakemake Path
            tool = 'snakemake'
            toolPath = find_executable(tool)
            self.data['snakemakePath'] = toolPath
            # Snakemake Version
            try:
                toolVersion = subprocess.check_output([tool,  '--version'])
            except:
                toolVersion = None
            if toolVersion is not None:
                self.data['snakemakeVersion'] = toolVersion
            else:
                self.data['snakemakeVersion'] = 'unknown'
            
            argsl = remaining[1:]
            parser = snakemake.get_argument_parser()
            args = parser.parse_args(argsl)
            # Snakefile
            self.data['snakefile'] = File(os.path.abspath(args.snakefile))
            # Config file (optional)
            if args.configfile is not None:
                self.data['configFile'] = File(os.path.abspath(args.configfile))
            else:
                self.data['configFile'] = None
            # Workflow steps
            # Perform a dry run on that workflow using the configfile if provided
            dryrun_command = remaining
            dryrun_command.insert(1, "--dryrun")
            dryrun_command.insert(2, "--printshellcmds")

            dryrun = subprocess.check_output(dryrun_command).splitlines()
            
            # Iterate over the lines, create a command line element for each rule
            self.data['step'] = []
            rule_ended = True
            command_next = False
            for line in dryrun:
                s = line.decode('ascii').strip()
                if s.startswith('rule'):
                    rule_name = s.split()[1][:-1]
                    if rule_name is not "all":
                        new_step = CommandLine()
                        rule_ended = False
                    else:
                        # 'all' ist last rule
                        break
                elif s.startswith('input: '):
                    input_list = s[7:].split(',')
                    input_list = [os.path.abspath(i.strip()) for i in input_list]
                    new_step.input_data_objects = input_list
                    self.input_data_objects += input_list
                elif s.startswith('output: '):
                    output_list = s[8:].split(',')
                    output_list = [os.path.abspath(o.strip()) for o in output_list]
                    new_step.output_data_objects = output_list
                    self.output_data_objects += output_list
                elif len(s) == 0 and not rule_ended:
                    command_next = True
                    rule_ended = True
                elif command_next:
                    command = s.strip()
                    if len(command) == 0:
                        print("command empty, do not track this step")
                    else:
                        new_step.set_command(command)
                        self.data['step'].append(new_step)
                    command_next = False
                    rule_ended = True


    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('{Dataprov}command').text
        self.data['snakemakePath'] = root.find('{Dataprov}snakemakePath').text
        self.data['snakemakeVersion'] = root.find('{Dataprov}snakemakeVersion').text
        # Snakefile
        snakefile = File()
        snakefile.from_xml(root.find('{Dataprov}snakefile'), validate)
        self.data['snakefile'] = snakefile
        # Configfile
        if root.find('{Dataprov}configFile') is not None:
            config_file = File()
            config_file.from_xml(root.find('{Dataprov}configFile'), validate)
            self.data['configFile'] = config_file
        else:
            self.data['configFile'] = None
        # Steps
        self.data['step'] = []
        for step in root.findall('{Dataprov}step'):
            command_line = CommandLine()
            command_line.from_xml(step, validate)
            self.data['step'].append(step)


    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, DATAPROV + 'command').text = self.data['command']
        etree.SubElement(root, DATAPROV + 'snakemakePath').text = self.data['snakemakePath']
        etree.SubElement(root, DATAPROV + 'snakemakeVersion').text = self.data['snakemakeVersion']
        # Snakefile
        snakefile_ele = self.data['snakefile'].to_xml(DATAPROV + "snakefile")
        root.append(snakefile_ele)
        # Configfile
        if self.data['configFile'] is not None:
            config_file_ele = self.data['configFile'].to_xml(DATAPROV + "configFile")
            root.append(config_file_ele)
        # Steps
        for step in self.data['step']:
            step_ele = step.to_xml(DATAPROV + "step")
            root.append(step_ele)
        return root
        
        
    def validate_xml(self, root):
        '''
        Validate an lxml object against a the XSD schema of this dataprov element.
        '''
        # Read schema file
        with open(self.schema_file, 'r') as schema_file_handler:
            xml_schema_doc = etree.parse(schema_file_handler)
        # Create XML schema
        xml_schema = etree.XMLSchema(xml_schema_doc)
        # Validate
        return xml_schema.validate(root)
        
    def run(self):
        '''
        Run the wrapped command or workflow.
        '''
        # Overwrite the generic method, because we have to use the snakemake API
        try:
            snakemake.main(self.remaining[1:])
        except SystemExit:
            # snakemake main wants to exit ... but we want to write the xml files first
            return                
    
    def post_processing(self):
        '''
        Perform necessary post processing steps
        '''
        # Call post_processing for each step.
        for step in self.data['step']:
            step.post_processing()