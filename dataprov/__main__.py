import os
import argparse
import subprocess
from collections import defaultdict
from dataprov.elements.dataprov import Dataprov
from dataprov.elements.executor import Executor
from dataprov.elements.operation import Operation
from dataprov.elements.op_class import OpClass
from dataprov.utils.io import write_xml


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
    #command_output_files = [os.path.join(cwd, "dataprov_output")]
    command_output_files = []
    parser.add_argument('-o', '--output', action='append',
                        help="path to output files of the wrapped command. The provenance files with the same name + .prov suffix will be created beside the output files",
                        default=command_output_files)
                        
    # If the used command line tool used one or more input files, the user
    # Can specifiy the paths to the files.
    # If there are dataprov metadata files for the input files,
    # it will be incorporated into the resulting provenance metadata
    # If the user uses a workflow manager / workflow engine supported by this tool,
    # The output will be handled automatically     
    parser.add_argument('-i','--input', action='append',
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
    # This subcommand will run arbitrary command line commands                      
    run = subparsers.add_parser("run",
                                 help="Run a command line command and create provenance metadata")

    # Singularity
    # This subcommand will wrap Singularity commmands. The Metadata will
    # contain a special element describing the container.
    #singularity = subparsers.add_parser("singularity",
    #                                    help="Run a Singularity command and create provenance metadata")
    # Docker
    # This subcommand will wrap Docker commmands. The Metadata will
    # contain a special element describing the container.
    #docker = subparsers.add_parser("docker",
    #                               help="Run a Docker command and create provenance metadata")

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

    # Read input provenance metadata
    input_provenance_data = defaultdict()
    if command_input_files:
        for input_file in command_input_files:
            # Check if input file and the corresponding provenance metadata exists
            if not os.path.exists(input_file):
                print("Input file specified by -i does not exist: ", input_file)
                print("No provenance information will be considered for this file.")
                continue
            abs_path = os.path.abspath(input_file)
            input_prov_file = input_file + '.prov'
            if not os.path.exists(input_prov_file):
                print("Metadata for input file specified by -i does not exist: ", input_file)
                input_provenance_data[abs_path] = None
                continue
        
            #Parse XML and store in dictionary
            new_provenance_object = Dataprov(input_prov_file)
            input_provenance_data[abs_path] = new_provenance_object
            
    # Create a new provenance object
    new_operation = Operation()
    # Record input files
    new_operation.record_input_files(input_provenance_data)
    # Record start time
    new_operation.record_start_time()        
    # Record Host
    new_operation.record_host()
    #TODO Introduce an environment element: PATH, LIBRARY_PATH, glibc, ... Check for loaded modules / conda environments and update schema/code
    # Record executor
    new_operation.record_executor(executor)
    # Record operation class
    new_operation.record_op_class(remaining)

    #TODO Implement the opClasses
    #TODO discriminate based on following executable names; docker, singularity, cwltool, cwl-runner
    #TODO Change the to/from_xml methods of operation
    op_class = OpClass(remaining)    
    new_operation.record_op_class(op_class)
    
    
    # Record message
    new_operation.record_message(message)
            
    # Execute the wrapped command
    return_code = subprocess.call(' '.join(remaining), shell=True)  
    #command_string = ' '.join(remaining)
    #commands = command_string.split('&&')
    #for command in commands:
    #    command_list = command.split()
    #    return_code = subprocess.call(command_list)
    #    continue
    
    # Record end time
    new_operation.record_end_time()
    
    # Record target files
    new_operation.record_target_files(command_output_files)

    # Create the final dataprov object for each output file
    result_dataprov_objects = []
    for output_file in command_output_files:
        new_dataprov = Dataprov()
        new_dataprov.create_provenance(output_file, input_provenance_data, new_operation)
        result_dataprov_objects.append(new_dataprov)

    # Check if the create xml is valid, then write to file
    for dataprov_object in result_dataprov_objects:
        dataprov_xml = dataprov_object.to_xml()
        write_xml(dataprov_xml, "test.prov")
        if not dataprov_object.validate_xml(dataprov_xml):
            # TODO do this with an Error type
            print("Resulting dataprov object is not valid!")
        else:
            output_xml_file = dataprov_object.get_xml_file_path()
            write_xml(dataprov_xml, output_xml_file)

    exit(0)
    
    print(return_code)

if __name__ == '__main__':
    main()