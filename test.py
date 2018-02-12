# Test dataprov elements

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
h = Host()
h.data
root = h.to_xml()
h.validate_xml(root)