import os
import dataprov
import argparse
import subprocess
import configparser
import errno
from xml.etree.ElementTree import Element, SubElement
import hashlib
import datetime
import socket
from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def create_empty_executor_config(path):
    '''
    Create an empty executor information file
    '''
    # A simple, empty configuration
    config = configparser.ConfigParser()
    config['executor'] = {'honorific': '',
                          'firstName': '',
                          'middleName': '',
                          'surname': '',
                          'suffix': '',
                          'mail': '',
                          'affiliation': ''}
                          
    # Create base directory if needed
    base_dir = os.path.dirname(path)
    mkdir_p(base_dir)
    with open(path, 'w') as configfile:
        config.write(configfile)


def read_executor_config(path):
    '''
    Read an executor information file
    '''
    config = configparser.ConfigParser()
    config.read(path)
    return config

def main():

    parser = argparse.ArgumentParser(description='Automatic provenance metadata creator.')

    parser.add_argument('-d', '--debug',
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument('-q', '--quiet',
                        help="suppress print output", 
                        default=False, action='store_true')

    parser.add_argument('-v', '--version',
                        help="print version information",
                        default=False, action='store_true')
                        
    # Default place for personal information
    home_dir = os.path.expanduser("~")
    executor_default_config_file = os.path.join(home_dir, ".dataprov/executor.conf")
    parser.add_argument('-e', '--executor',
                        help="personal information about executor added to recorded metadata.",
                        default=executor_default_config_file)

    # Path to output file
    # This is the path to the output file of the wrapped command
    # If the user uses a workflow manager / workflow engine supported by this tool,
    # The output will be detected automatically
    cwd = os.getcwd()
    command_output_file = os.path.join(cwd, "dataprov_output")
    parser.add_argument('-o', '--output',
                        help="path to the output file of the wrapped command. The provenance file with the same name + .prov suffix will be created beside the output file",
                        default=command_output_file)
                        
    # If the used command line tool used one or more input files, the user
    # Can specifiy the paths to the files.
    # If there are dataprov metadata files for the input files,
    # it will be incorporated into the resulting provenance metadata
    # If the user uses a workflow manager / workflow engine supported by this tool,
    # The output will be handled automatically     
    parser.add_argument('-i','--input', nargs='+',
                        help='path to input files used by the wrapped command')    

    # Message incorporated into metadata
    parser.add_argument('-m', '--message',
                        help="message for operation metadata",
                        default="")

    subparsers = parser.add_subparsers(help='dataprov actions',
                                       title='actions',
                                       dest="command")
                
    # Run
    # This subcommand will run arbitrary command line arguments
    # No further arguments. All input following 'run' will be given to subprocess.call directly                       
    run = subparsers.add_parser("run",
                                 help="Run a command line command and create provenance metadata")

    # CWL
    #cwltool = subparsers.add_parser("cwltool",
    #                             help="")

                        
    # Parse command line arguments
    args, remaining = parser.parse_known_args()
    debug = args.debug
    executor_config_file = args.executor
    message = args.message
    command_output_file = args.output
    input_metadata_files = args.input
    
    if debug:
        print("Arguments: " + str(args))
        print("Remaining: " + str(remaining))
        print("Personal information: " + executor_config_file)
        print("Command output: " + str(command_output_file))
        print("Input metadata files: " + str(input_metadata_files))
        print("Message: ", message)

    # Check if executor information are available
    if not os.path.exists(executor_config_file):
        print("No personal information found at ", executor_config_file)
        print("An empy personal information file will be created at ", executor_config_file)
        print("Please provide your personal information at ", executor_config_file, " or provide a configuration file with the --p/--person option")
        create_empty_executor_config(executor_config_file)
        exit(1)
    
    # Read executor information
    executor_config = read_executor_config(executor_config_file)
    if debug:
        print("Executor configuration: ", executor_config_file)
        print("\tHonorific: " + executor_config.get('executor', 'honorific'))
        print("\tFirst Name: " + executor_config.get('executor', 'firstName'))
        print("\tMiddle Name: " + executor_config.get('executor', 'middleName'))
        print("\tSurname: " + executor_config.get('executor', 'surname'))
        print("\tSuffix: " + executor_config.get('executor', 'suffix'))
        print("\tMail: " + executor_config.get('executor', 'mail'))
        print("\tAffiliation: " + executor_config.get('executor', 'affiliation'))

    #TODO
    # Read input provenance metadata

    # Record start datetime
    # YYYY-MM-DDThh:mm:ss
    start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")
    
    # Execute the wrapped command
    return_code = subprocess.call(remaining)

    # Record end datetime
    # YYYY-MM-DDThh:mm:ss
    end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")

    # Create resulting provenance data
    xml_dataprov = Element('dataprov')
    # file element
    xml_file = SubElement(xml_dataprov, 'file')
    xml_file.text = command_output_file
    
    # sha1 hashsum of file
    sha1 = hashlib.sha1()    
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    if os.path.isfile(command_output_file):
        with open(command_output_file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        sha1sum = sha1.hexdigest()
    else:
        sha1sum = "undefined"
    xml_sha1 = SubElement(xml_dataprov, 'sha1')
    xml_sha1.text = sha1sum
    
    # The history
    xml_history = SubElement(xml_dataprov, 'history')
    
    # Insert the operations taken from the input files metadata
    #TODO 
    
    # The NEW operation we just executed
    xml_new_op = SubElement(xml_history, 'op')
    # StartTime    
    xml_startTime = SubElement(xml_new_op, 'startTime')
    xml_startTime.text = str(start_time)
    # EndTime
    xml_endTime = SubElement(xml_new_op, 'endTime')
    xml_endTime.text = str(end_time)
    # Executor
    xml_executor = SubElement(xml_new_op, 'executor')
    xml_executor_honorific = SubElement(xml_executor, 'honorific')
    xml_executor_honorific.text = executor_config.get('executor', 'honorific')
    xml_executor_firstName = SubElement(xml_executor, 'firstName')
    xml_executor_firstName.text = executor_config.get('executor', 'firstName')
    xml_executor_middleName = SubElement(xml_executor, 'middleName')
    xml_executor_middleName.text = executor_config.get('executor', 'middleName')
    xml_executor_surname = SubElement(xml_executor, 'surname')
    xml_executor_surname.text = executor_config.get('executor', 'surname')
    xml_executor_suffix = SubElement(xml_executor, 'suffix')
    xml_executor_suffix.text = executor_config.get('executor', 'suffix')
    xml_executor_mail = SubElement(xml_executor, 'mail')
    xml_executor_mail.text = executor_config.get('executor', 'mail')
    xml_executor_affiliation = SubElement(xml_executor, 'affiliation')
    xml_executor_affiliation.text = executor_config.get('executor', 'affiliation')
    # Hostname
    hostname = socket.gethostname()
    xml_hostname = SubElement(xml_new_op, 'hostname')
    xml_hostname.text = hostname
    # Operation class
    xml_opClass = SubElement(xml_new_op, 'opClass')
    xml_opClass.text = 'CommandLine'
    # WrappedCommand
    xml_wrappedCommand = SubElement(xml_new_op, 'wrappedCommand')
    xml_wrappedCommand.text = ' '.join(remaining)
    # Message
    xml_message = SubElement(xml_new_op, 'message')
    xml_message.text = message
    
    # Save the provenance xml-file
    dataprov_file = command_output_file + ".prov"
    pretty_xml = prettify(xml_dataprov)
    with open(dataprov_file, "w") as dataprov_file_handler:
        dataprov_file_handler.write(pretty_xml)
        
    exit(0)
    # CWL
    # Run cwltool or cwl-runner
    #wf_engine = remaining[0]
    #print(wf_engine)

    #return_code = subprocess.call(["cwltool --basedir=. examples/cwl/bwa-index.cwl examples/cwl/bwa-index-job.yml"], shell=True)



    print(return_code)
