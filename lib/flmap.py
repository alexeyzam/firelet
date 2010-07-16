from pygraphviz import AGraph,  Edge,  Node
from netaddr import IPAddress,  IPNetwork

def drawmap(fs):
    A = AGraph()
    for h in fs.hosts:
        A.add_node(h[0])
    for h in fs.hosts:
        for h2 in fs.hosts:
            for net in h(4):
                for h2 in fs.hosts:
                    n = [n for n in fs.networks if n[0] == net]
                    print net, n
                    if not n: continue
                    if IPAddr(h2[2]) in IPNetwork(net):
                        A.add_edge(h[0], h2[0])
#    Node(A, 'Master').attr['shape']='circle'
#    A.add_edge('Master', 'q')

    A.layout(prog='circo')                                  # layout with default (neato)
    image = A.draw(format='png')    # draw png
    return image

