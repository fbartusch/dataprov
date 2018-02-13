# Test dataprov elements


##
#TODO Check validation from xml file for each element
#TODO Reading a dataprov xml and writing to new xml should result in same file

## File



## Executor
from dataprov.elements.executor import Executor
executor_conf = '/home/fbartusch/.dataprov/executor.conf'
e = Executor()
e.data
e.from_config(executor_conf)
e.data
# Create xml tree
root = e.to_xml()
# Validate xml with xml-schema
e.validate_xml(root)

## Host
from dataprov.elements.host import Host
from lxml import etree
test_file = "/home/fbartusch/github/dataprov/dataprov/xml/host_example.xml"
# Test data derived from host system
h1 = Host()
h1.data
root = h1.to_xml()
h1.validate_xml(root)
# Test data derived from xml-example
h2 = Host()
with open(test_file, 'r') as xml_file:
    parser = etree.XMLParser()
    tree = etree.parse(xml_file, parser)
h2.from_xml(tree.getroot())


## Dataprov
from dataprov.elements.dataprov import Dataprov
from lxml import etree
test_file = "/home/fbartusch/github/dataprov/dataprov/xml/dataprov_example.xml"
with open(test_file, 'r') as xml_file:
    parser = etree.XMLParser()
    tree = etree.parse(xml_file, parser)
d = Dataprov()
d.from_xml(tree)
d.validate_xml(tree.getroot())
