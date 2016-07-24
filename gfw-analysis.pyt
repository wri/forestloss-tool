from configuregdb import ConfigureGDB
from treecover_loss import TreeCoverLoss
from biomass_loss import BioMassLoss

class Toolbox(object):
    '''
    Tree cover loss toolbox
    '''

    def __init__(self):
        self.label = "GFW-Analysis toolbox"
        self.alias = "gfw-analysis"

        # List of tool classes associated with this toolbox
        self.tools = [TreeCoverLoss, BioMassLoss, ConfigureGDB]

