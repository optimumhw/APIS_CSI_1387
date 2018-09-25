import jsonstruct

class SitesTableRecord( ):

    def __init__(self, args):

        #[(79, u'Universal', 269, u'UniStudOrl', 171, u'UniStudOLP', 172, u'UniStudLP1')]

        self.customerId = args[0]
        self.custShortName = args[1]
        self.siteId = args[2]
        self.siteShortName = args[3]
        self.installationId = args[4]
        self.instShortName = args[5]
        self.stationId = args[6]
        self.stationShortName = args[7]

        #def getJson(self):
