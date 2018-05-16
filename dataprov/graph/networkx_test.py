import networkx as nx

G = nx.DiGraph()

# Four nodes
G.add_node(1, label="genome.fa", checksum="asdf1")
G.add_node(2, label="genome.fa.bwt", checksum="asdf2")
G.add_node(3, label="A.fastq", checksum="asdf3")
G.add_node(4, label="A.bam", checksum="asdf4")

# Edges
G.add_edge(1, 2, label="Op1", executor="Felix")
G.add_edge(2, 4, label="Op2", executor="Felix")
G.add_edge(3, 4, label="Op1", executor="Felix")

nx.readwrite.json_graph.jit_data(G)