import pytds
class Datapoints:

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def getDatapoints(self, siteID):

        queryString = '''
            SELECT [DataPointName]
            FROM [oemvm].[dim].[DataPoint_List]
            where SiteID = %d and isRollupPoint = 0
            ''' % (siteID)

        print(queryString)

        conn = pytds.connect(self.host, 'oemvm', user=self.user, password=self.password,
                             as_dict=False)
        cur = conn.cursor()
        cur.execute(queryString)
        data = cur.fetchall()

        conn.close()

        points = []
        for row in data:
            points.append( row[0])

        return points
