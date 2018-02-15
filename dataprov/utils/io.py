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


def write_xml(root, output_file):
    '''
    Write an lxml Element to file.
    '''
    with open(output_file, 'w') as xml_file:
        s = etree.tostring(root, pretty_print=True).decode('ascii')
        xml_file.write(s)        