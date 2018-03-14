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
                                 
                                 
    # This subcommand will validate a xml-file                      
    validate = subparsers.add_parser("validate",
                                     help="Validate a xml-file")
    validate.add_argument('xml',
                          help="xml-file to validate")

    # This subcommand create DAG graph from an xml-file                  
    dag = subparsers.add_parser("dag",
                                     help="Create DAG from XML file")
    dag.add_argument('xml',
                     help="xml-file visualize")
    dag.add_argument('dag',
                     help="Resulting file in svg format.")
                        
    # Parse command line arguments
    args, remaining = parser.parse_known_args()
    debug = args.debug
    
    if args.command == "validate":
        abs_path = os.path.abspath(args.xml)
        # Read provenance data   
        if not os.path.exists(abs_path):
            print("Specified XML file does not exist: ", abs_path)
            exit(1)
        else:
            try:
                Dataprov(file=abs_path)
                print("XML is valid!")
                exit(0)
            except IOError:
                print("XML is not valid!")             
                exit(1)
    elif args.command == "dag":
        abs_path = os.path.abspath(args.xml)
        # Read provenance data   
        #TODO check if graphviz is in PATH
        if not os.path.exists(abs_path):
            print("Specified XML file does not exist: ", abs_path)
            exit(1)
        else:
            try:
                dataprov = Dataprov(file=abs_path)
                dag = dataprov.to_dag()
                #TODO Implement and save to output file
                dag.render(filename=args.dag)
            except Exception as inst:
                print(type(inst))    # the exception instance
                print(inst.args)     # arguments stored in .args
                print(inst)          # __str__ allows args to be printed directly,
                exit(1)
        exit(0)
    elif args.command == "run":
        executor_config_file = args.executor
        message = args.message
        if args.output is not None:
            command_output_files = args.output
        else:
            command_output_files = []
        if args.input is not None:
            command_input_files = args.input
        else:
            command_input_files = []
        
        if debug:
            print("Arguments: " + str(args))
            print("Remaining: " + str(remaining))
            print("Personal information: " + executor_config_file)
            print("Command outputs: " + str(command_output_files))
            print("Input metadata files: " + str(command_input_files))
            print("Message: ", message)
    
        # Check if executor information are available
        executor = Executor(executor_config_file)
    
        # Create the object describing this operation
        op_class = OpClass(remaining)  
    
    
        # Combine output files specified on commmand line and the files specified
        # in the wrapped command (e.g. from CWL file's output binding)
        output_files_tmp = command_output_files + op_class.get_output_files()
        output_files = []
        for output_file in output_files_tmp:
            abs_path = os.path.abspath(output_file)
            if abs_path not in output_files:
                output_files.append(abs_path)
        
        if debug:
            print("Output files: ", output_files)    
    
    
        # Combine input files specified on command line and the files specified in
        # the wrapped command (e.g. from CWL file's input binding)
        input_files_tmp = command_input_files + op_class.get_input_files()
        input_files = []
        for input_file in input_files_tmp:
            # Check if input file and the corresponding provenance metadata exists
            if not os.path.exists(input_file):
                print("Input file specified by -i does not exist: ", input_file)
                print("No provenance information will be considered for this file.")
                continue
            abs_path = os.path.abspath(input_file)
            if abs_path not in input_files:
                input_files.append(abs_path)
                
        if debug:
            print("Input files: ", input_files)
            
         # Read provenance data   
        input_provenance_data = defaultdict()
        for input_file in input_files:
            input_prov_file = input_file + '.prov'
            if not os.path.exists(input_prov_file):
                print("Metadata for input file specified by -i does not exist: ", input_file)
                input_provenance_data[input_file] = None
                continue
            print("Metadata for input file specified by -i does exist: ", input_file)
            #Parse XML and store in dictionary
            new_provenance_object = Dataprov(input_prov_file)
            input_provenance_data[input_file] = new_provenance_object
        
        if debug:
            print("Input Provenance Data: ", input_provenance_data)
                
        # Create a new provenance object
        new_operation = Operation()
          
        # Record Host
        new_operation.record_host()
    
        # Record executor
        new_operation.record_executor(executor)
      
        # Record more details about operation (commandLine, snakemake, ...)
        new_operation.record_op_class(op_class)
        
        # Record input files
        new_operation.record_input_files(input_provenance_data)
        
        # Record message
        new_operation.record_message(message)
        
        # Record start time
        new_operation.record_start_time()  
          
        # Execute the wrapped command
        op_class.run() 
        
        # Record end time
        new_operation.record_end_time()
    
        # Perform post processing
        # e.g. for workflows to annotate intermediate files that were generated during workflow execution
        new_operation.post_processing()
        
        # Record target files
        new_operation.record_target_files(output_files)
    
        # Create the final dataprov object for each output file
        #TODO Implement checks if output file exists and handle exception 
        result_dataprov_objects = []
        for output_file in output_files:
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
                print("Write resulting xml file to: ", output_xml_file)
                write_xml(dataprov_xml, output_xml_file)

if __name__ == '__main__':
    main()