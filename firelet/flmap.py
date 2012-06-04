try:
    from pygraphviz import AGraph,  Edge,  Node
    graphviz_available = True
except ImportError:
    graphviz_available = False

def _drawmap(fs, rulename=None):
    """Draw a map of the firewalls and their connections based on their interfaces.
    If nulename is specified, draw also the sources and dests for a that rule.  #TODO: implement this
    """
    A = AGraph()
    A.graph_attr['bgcolor'] = 'transparent'
#    A.graph_attr['size'] = '8,5'
    # Draw hosts
    for h in fs.hosts:
        A.add_node(h.hostname)
        if h.network_fw in (1, True, '1'): # network firewall
            f = Node(A, h.hostname)
            f.attr['color']  = 'red'

    # Draw nets
    for net in fs.networks:
        A.add_node(net.name)
        poly = Node(A, net.name)
        poly.attr['shape'] = 'polygon'
        poly.attr['sides'] = '8'

    # Connect hosts to nets
    for host in fs.hosts:
        on_Internet = True
        for net in fs.networks:
            if host in net:
                on_Internet = False
                A.add_edge(host.hostname, net.name)
                e = Edge(A, host.hostname, net.name)
                e.attr['label'] = host.iface
                e.attr['fontsize'] = '6'
        # If a host is not in any configured net, it's on the Internet
        if on_Internet:
            A.add_edge(host.hostname, 'Internet')
            e = Edge(A, host.hostname, 'Internet')
            e.attr['label'] = host.iface
            e.attr['fontsize'] = '6'

    A.layout(prog='circo')
    return A


def draw_png_map(fs, rulename=None):
    if not graphviz_available:
        return None
    A = _drawmap(fs, rulename)
    return A.draw(format='png')

def draw_svg_map(fs, rulename=None):
    if not graphviz_available:
        return None
    A = _drawmap(fs, rulename)
    return A.draw(format='svg')


