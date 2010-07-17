from pygraphviz import AGraph,  Edge,  Node
from netaddr import IPAddress,  IPNetwork

def drawmap(fs, rulename=None):
    """Draw a map of the firewalls and their connections based on their interfaces.
    If nulename is specified, draw also the sources and dests for a that rule.  #TODO: implement this
    """
    A = AGraph()
    A.graph_attr['bgcolor'] = 'transparent'
    for h in fs.hosts:
        A.add_node(h[0])
        if h[5] in (1, True, '1'): # network firewall
            f = Node(A, h[0])
            f.attr['color']  = 'red'
    for n in fs.networks:
        A.add_node(n[0])
        poly = Node(A, n[0])
        poly.attr['shape'] = 'polygon'
        poly.attr['sides'] = '8'
        for h in fs.hosts:
            if IPAddress(h[2]) in IPNetwork(n[1] + '/' + n[2]):
                A.add_edge(h[0], n[0])

    A.layout(prog='circo')
    image = A.draw(format='png')    # draw png
    return image

