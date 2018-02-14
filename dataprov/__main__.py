import os
import argparse
import subprocess
from xml.etree.ElementTree import Element, SubElement
import hashlib
import datetime
from collections import defaultdict
from dataprov.elements.dataprov import Dataprov
from dataprov.elements.executor import Executor
from dataprov.elements.host import Host





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
    command_output_files = [os.path.join(cwd, "dataprov_output")]
    parser.add_argument('-o', '--output', nargs='+',
                        help="path to output files of the wrapped command. The provenance files with the same name + .prov suffix will be created beside the output files",
                        default=command_output_files)
                        
    # If the used command line tool used one or more input files, the user
    # Can specifiy the paths to the files.
    # If there are dataprov metadata files for the input files,
    # it will be incorporated into the resulting provenance metadata
    # If the user uses a workflow manager / workflow engine supported by this tool,
    # The output will be handled automatically     
    parser.add_argument('-i','--input', nargs='+',
                        help='path to input files used by the wrapped command',
                        default=None)    

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

    # Parse command line arguments
    args, remaining = parser.parse_known_args()
    debug = args.debug
    executor_config_file = args.executor
    message = args.message
    command_output_files = args.output
    command_input_files = args.input
    
    if debug:
        print("Arguments: " + str(args))
        print("Remaining: " + str(remaining))
        print("Personal information: " + executor_config_file)
        print("Command outputs: " + str(command_output_files))
        print("Input metadata files: " + str(command_input_files))
        print("Message: ", message)

    # Check if executor information are available
    executor = Executor(executor_config_file)
    if debug:
        print("Executor:" , executor)

    # Read input provenance metadata
    if command_input_files:
        input_provenance_data = defaultdict()
        for input_file in command_input_files:
            # Check if input file and the corresponding provenance metadata exists
            if not os.path.exists(input_file):
                print("Input file specified by -i does not exist: ", input_file)
                print("No provenance information will be considered for this file.")
                continue
            input_prov_file = input_file + '.prov'
            if not os.path.exists(input_prov_file):
                print("Metadate for input file specified by -i does not exist: ", input_prov_file)
                print("No provenance information will be considered for this file.")
                continue
        
            #Parse XML and store in dictionary
            new_provenance_object = Dataprov(input_prov_file)
            input_provenance_data[input_file] = new_provenance_object
            
    # Print input provenance data
    if debug:
        for key, value in input_provenance_data.items():
            print("Read provenance data for ", key, ":")
            print(str(value))
    exit(0)
    
    # Record start datetime
    # YYYY-MM-DDThh:mm:ss
    start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")
    
    # Execute the wrapped command
    command_string = ' '.join(remaining)
    commands = command_string.split('&&')
    for command in commands:
        command_list = command.split()
        return_code = subprocess.call(command_list)
        continue

    # Record end datetime
    # YYYY-MM-DDThh:mm:ss
    end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%m:%S")

    # Create an provenance object for each output file
    # Dictionary: File -> Provenance object (e.g. a dictionary)
    prov_dicts = defaultdict()
    for output_file in command_output_files:
        new_dict = defaultdict()
        
        # Because the metadata file is in the same directory as the file, we don't need the path
        new_file = os.path.basename(output_file)
        new_dict['file'] = new_file       
        
        # sha1 hashsum of file
        sha1 = hashlib.sha1()    
        # BUF_SIZE is totally arbitrary, change for your app!
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
        if os.path.isfile(output_file):
            with open(output_file, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
                sha1sum = sha1.hexdigest()
        else:
            sha1sum = "undefined"
        new_dict['sha1'] = sha1sum
        
        # Insert the operations taken from the input files metadata
        #TODO         
                 
        # History of the file. This is a list, because there can be several operations
        new_history = defaultdict(list)
        # The new operation
        new_op = defaultdict()
        new_op['startTime'] = start_time
        new_op['endTime'] = end_time
        # Executor
        new_executor = Executor(executor_config_file)
        new_op['executor'] = new_executor.data
        # hostname
        new_host = Host()
        new_op['host'] = new_host.data
        # Operation class
        new_op['opClass'] = 'CommandLine'
        # WrappedCommand
        new_op['wrappedCommand'] = ' '.join(remaining)
        # Message
        new_op['message'] = message
        # Append the new operation to the history
        new_history['op'].append(new_op)
        new_dict['history'] = new_history
        
        # Append the new dict to the other provenance dicts
        prov_dicts[output_file] = new_dict
        
    # Create XML-File from each provenance dictionary
    for file_name, prov_dict in prov_dicts.items():   
        # Create resulting provenance data
        xml_dataprov = Element('dataprov')
        # file element
        xml_file = SubElement(xml_dataprov, 'file')
        xml_file.text = file_name
        
        xml_sha1 = SubElement(xml_dataprov, 'sha1')
        xml_sha1.text = prov_dict['sha1']
        
        # The history
        xml_history = SubElement(xml_dataprov, 'history')
        
        # Iterate over the list of operations
        for op in prov_dict['history']['op']:
            # The NEW operation we just executed
            xml_new_op = SubElement(xml_history, 'op')
            # StartTime    
            xml_startTime = SubElement(xml_new_op, 'startTime')
            xml_startTime.text = op['startTime']
            # EndTime
            xml_endTime = SubElement(xml_new_op, 'endTime')
            xml_endTime.text = op['endTime']
            # Executor
            xml_executor = SubElement(xml_new_op, 'executor')
            xml_executor_honorific = SubElement(xml_executor, 'title')
            xml_executor_honorific.text = op['executor']['title']
            xml_executor_firstName = SubElement(xml_executor, 'firstName')
            xml_executor_firstName.text = op['executor']['firstName']
            xml_executor_middleName = SubElement(xml_executor, 'middleName')
            xml_executor_middleName.text = op['executor']['middleName']
            xml_executor_surname = SubElement(xml_executor, 'surname')
            xml_executor_surname.text = op['executor']['surname']
            xml_executor_suffix = SubElement(xml_executor, 'suffix')
            xml_executor_suffix.text = op['executor']['suffix']
            xml_executor_mail = SubElement(xml_executor, 'mail')
            xml_executor_mail.text = op['executor']['mail']
            xml_executor_affiliation = SubElement(xml_executor, 'affiliation')
            xml_executor_affiliation.text = op['executor']['affiliation']
            # Hostname
            xml_hostname = SubElement(xml_new_op, 'hostname')
            xml_hostname.text = op['hostname']
            # Operation class
            xml_opClass = SubElement(xml_new_op, 'opClass')
            xml_opClass.text = op['opClass']
            # WrappedCommand
            xml_wrappedCommand = SubElement(xml_new_op, 'wrappedCommand')
            xml_wrappedCommand.text = op['wrappedCommand']
            # Message
            xml_message = SubElement(xml_new_op, 'message')
            xml_message.text = op['message']
        
            # Save the provenance xml-files
            dataprov_file = file_name + ".prov"
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

if __name__ == '__main__':
    main()