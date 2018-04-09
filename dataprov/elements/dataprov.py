import os
import graphviz as gv
from collections import defaultdict
from dataprov.elements.generic_element import GenericElement
from dataprov.elements.data_object import DataObject
from dataprov.elements.data_object_list import DataObjectList
from dataprov.elements.history import History
from dataprov.definitions import XML_DIR
from lxml import etree


class Dataprov(GenericElement):
    '''
    Class describing the whole dataprov element.
    This class handles the parsing of input dataprov metadata files.
    
    A datprov model consists of:
    - a 'target': The file which provenance data gets provided
    - a 'history': A list of operations that lead to the target file
    '''
    
    element_name = "dataprov"
    schema_file = os.path.join(XML_DIR, 'dataprov_element.xsd')
    
    def __init__(self, file=None, validate=True):
        '''
        Initialize an empty object or read directly from file
        '''
        super().__init__()
        if file:
            with open(file, 'r') as xml_file:
                parser = etree.XMLParser()
                tree = etree.parse(xml_file, parser)
                try:
                    print("Dataprov __init__")
                    self.from_xml(tree.getroot(), validate=validate)
                except IOError as e:
                    print(e)
        
    def from_xml(self, root, validate=True): 
        print("Dataprov from_xml")
        self.data = defaultdict()
        # Validate XML against schema
        if validate and not self.validate_xml(root):
            raise IOError("XML document does not match XML-schema")
        
        # Get the target from the xml
        target_ele = root.find('target')
        target = DataObject()
        target.from_xml(target_ele, validate=False)
        self.data['target'] = target
        
        # Get the history from xml
        history_ele = root.find('history')
        history = History()
        history.from_xml(history_ele, validate=False)
        self.data['history'] = history

    def to_xml(self):
        '''
        Create a xml ElementTree object from the data attribute. 
        '''
        root = etree.Element(self.element_name)
        # Target
        target_ele = self.data['target'].to_xml("target")
        #target_ele.tag = "target"
        root.append(target_ele)
        # History
        root.append(self.data['history'].to_xml())
        return root
       
    def create_provenance(self, target_file, input_prov_data, applied_operation):
        '''
        Create the final provenance object from the path to an output data object,
        A dictionary of input provenance data and the object describing the
        applied operation
        '''
        self.data = defaultdict()
        # Target: Get this from the applied operation object
        self.data['target'] = applied_operation.get_target_data_object(target_file)
        # History: Combine the history of all input files with the applied operation
        new_history = History()
        new_history.combine_histories(input_prov_data, applied_operation)
        self.data['history'] = new_history
        
    def get_xml_file_path(self):
        '''
        Return the path to the corresponding xml file.
        '''
        return self.data['target'].get_uri() + '.prov'
    
    def to_dag(self):
        '''
        Create a graphical representation of the provenance metadata.
        Input and output/target files are nodes. These nodes are connected by the tracket operations/workflow steps.
        '''
        # Create the empty graph        
        dag = gv.Digraph(format='svg')
        
        # Dictionary of file objects with hash as key, name (not path!) as value
        # These will be file nodes
        file_dict = {}
        # Iterate over the operations and collect the stored information
        op_num = 0
        for operation in self.data['history'].data['operation']:
            op_num += 1
            # Input files
            if operation.data['inputFiles']:
                input_files = operation.data['inputFiles']
                for input_file in input_files.data['file']:
                    file_dict[input_file.data['sha1']] = input_file.data['name']
            # Output files
            output_files = operation.data['targetFiles']
            for output_file in output_files.data['file']:
                file_dict[output_file.data['sha1']] = output_file.data['name']

            print(file_dict)
            for key, value in file_dict.items():
                # Name of file node is <name>:<sha1>
                node_name = value + ":" + key
                #dag.node(node_name)
                
            # Edges
            # For commandLine, connect each input node with the corresponding output node
            # Label is the command?
            command = operation.data['opClass'].data['opClass'].data['command']
            if operation.data['inputFiles']:
                for input_file in input_files.data['file']:
                    for output_file in output_files.data['file']:
                        in_node = input_file.data['name'] + ":" + input_file.data['sha1']
                        out_node = output_file.data['name'] + ":" + output_file.data['sha1']
                        label = "Op " + str(op_num)
                        dag.edge(in_node, out_node, label=label)
        dag.render("test.svg")
        return
