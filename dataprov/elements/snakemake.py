import os
from collections import defaultdict
from lxml import etree
import sys
import os
import shutil
import subprocess
import snakemake
from collections import defaultdict
from lxml import etree
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.command_line import CommandLine
from dataprov.elements.file import File
from dataprov.definitions import XML_DIR

class Snakemake(GenericElement):
    '''
    This class describes a snakemake element.
    '''
    
    element_name = "snakemake"
    schema_file = os.path.join(XML_DIR, 'snakemake_element.xsd')
    
    def __init__(self, remaining=None):
        # Empty data attribute
        self.data = defaultdict()
        
        self.input_files = []
        self.output_files = []
        
        if remaining is not None:
            # Command
            self.data['command'] = ' '.join(remaining)
            # Snakemake Path
            tool = 'snakemake'
            toolPath = shutil.which(tool)
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
                    print(rule_name)
                    if rule_name is not "all":
                        new_step = CommandLine()
                        rule_ended = False
                    else:
                        # 'all' ist last rule
                        break
                elif s.startswith('input: '):
                    input_list = s[7:].split(',')
                    input_list = [os.path.abspath(i.strip()) for i in input_list]
                    print("input_list: ", input_list)
                    new_step.input_files = input_list
                    self.input_files += input_list
                elif s.startswith('output: '):
                    output_list = s[8:].split(',')
                    output_list = [os.path.abspath(o.strip()) for o in output_list]
                    print("output_list: ", output_list)
                    new_step.output_files = output_list
                    self.output_files += output_list
                elif len(s) == 0 and not rule_ended:
                    command_next = True
                    rule_ended = True
                elif command_next:
                    command = s.strip()
                    if len(command) == 0:
                        print("command empty, do not track this step")
                    else:
                        print("command: ", command)
                        new_step.set_command(command)
                        print(new_step)
                        self.data['step'].append(new_step)
                    command_next = False
                    rule_ended = True
                print(self.data['step'])


    def from_xml(self, root, validate=True):
        '''
        Populate data attribute from the root of a xml ElementTree object.
        '''
        self.data = defaultdict()
        if validate and not self.validate_xml(root):
            print("XML document does not match XML-schema")
            return
        self.data['command'] = root.find('command').text
        self.data['snakemakePath'] = root.find('snakemakePath').text
        self.data['snakemakeVersion'] = root.find('snakemakeVersion').text
        # Snakefile
        snakefile = File()
        snakefile.from_xml(root.find('snakefile'))
        self.data['snakefile'] = snakefile
        # Configfile
        if root.find('configFile') is not none:
            config_file = File()
            config_file.from_xml(root.find('configFile'))
            self.data['configFile'] = config_file
        else:
            self.data['configFile'] = None
        # Steps
        self.data['step'] = []
        for step in root.findall('step'):
            command_line = CommandLine()
            command_line.from_xml(step)
            self.data['step'].append(step)


    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute.
        '''
        root = etree.Element(self.element_name)
        etree.SubElement(root, 'command').text = self.data['command']
        etree.SubElement(root, 'snakemakePath').text = self.data['snakemakePath']
        etree.SubElement(root, 'snakemakelVersion').text = self.data['snakemakeVersion']
        # Snakefile
        snakefile_ele = self.data['snakefile'].to_xml("snakefile")
        root.append(snakefile_ele)
        # Configfile
        if self.data['configFile'] is not None:
            config_file_ele = self.data['configFile'].to_xml("configFile")
            root.append(config_file_ele)
        # Steps
        for step in self.data['step']:
            step_ele = step.to_xml("step")
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
        for step in self.data['step']:
            step.post_processing()