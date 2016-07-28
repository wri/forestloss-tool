from ConfigureGDB import ConfigureGDB
from TreeCoverLoss import TreeCoverLoss
from BiomassLoss import BiomassLoss

class Toolbox(object):
    '''
    Tree cover loss toolbox
    '''

    def __init__(self):
        self.label = "GFW-Analysis toolbox"
        self.alias = "gfw-analysis"

        # List of tool classes associated with this toolbox
        self.tools = [TreeCoverLoss, BiomassLoss, ConfigureGDB]

