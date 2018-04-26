import os

# Root of the package
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory with xml-schema files
XML_DIR = os.path.join(ROOT_DIR, 'xml')

# For the Dataprov XML Namexpace
DATAPROV_NAMESPACE = "Dataprov"
DATAPROV = "{%s}" % DATAPROV_NAMESPACE
NSMAP = {None : DATAPROV_NAMESPACE} # the default namespace (no prefix)

