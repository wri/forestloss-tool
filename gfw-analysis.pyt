from ConfigureGDB import ConfigureGDB
from TreeCoverLoss import TreeCoverLossMean

class Toolbox(object):
    '''
    Tree cover loss toolbox
    '''

    def __init__(self):
        self.label = "GFW-Analysis toolbox (mean)"
        self.alias = "gfw-analysis (mean)"

        # List of tool classes associated with this toolbox
        self.tools = [TreeCoverLossMean, ConfigureGDB]

