import dataprov
import argparse
import subprocess


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

    # Parse command line arguments
    args, remaining = parser.parse_known_args()
    debug = args.debug

    if debug:
        print("Arguments: " + str(args))
        print("Remaining: " + str(remaining))

    remaining

    # CWL
    # Run cwltool or cwl-runner
    wf_engine = remaining[0]
    print(wf_engine)

    return_code = subprocess.call(["cwltool --basedir=. examples/cwl/bwa-index.cwl examples/cwl/bwa-index-job.yml"], shell=True)



    print(return_code)
