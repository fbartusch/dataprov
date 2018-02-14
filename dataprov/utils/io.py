import os
import errno
from lxml import etree
from xml.etree import ElementTree
from xml.dom import minidom

def mkdir_p(path):
    '''
    Create directory with any parent directories
    '''
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def prettify(elem):
    '''
    Return a pretty-printed XML string for the Element.
    '''
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def print_xml(self, path):
    print('Element name: ', self.element_name)
    print('Schema: ', self.schema_file)
    with open(path, 'r') as xml_file:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file, parser)
        s = etree.tostring(tree, pretty_print=True)
        with open('./test.xml', 'wb') as f:
            f.write(s)