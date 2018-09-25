
import pytds

from datetime import datetime
from datetime import timedelta

class History:

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def private_getHistory(self, cache_time, from_time, to_time, prefix, point_names ):

        value_strings = []

        index = 1
        for point_name in point_names:
            value_string = "( %d, '%s.%s', 'Minute', 'Sum' )" % (index, prefix, point_name)
            value_strings.append(value_string)
            index += 1

        values_clause = " values " + ",".join(value_strings)

        queryString = '''
            USE oemvmdata; 
            declare @blah fact.DataPointsOfInterest, @FromTime datetime, @ToTime datetime, @CacheTime date
            declare @Results_Orig     fact.DataPointResults
            declare @Results          fact.DataPointResults
            insert into @blah (seqnbr, datapointxid, time_aggregatetype, rollup_aggregatetype) 
            
            %s
        
            set @CacheTime = '%s' 
            insert @Results 
            exec oemvmdata.fact.DataSeriesGet2 @DataPointsOfInterest=@blah, 
            @TimeRange=null, @TimeInterval='Minute', @FromTime_Local='%s', @ToTime_Local='%s', 
            @IncludeOutOfBounds=0, @IncludeUncommissioned=0, 
            @CalculatedFromTime = @FromTime, @CalculatedToTime=@ToTime 
            select * from @Results 
            ''' % (values_clause, cache_time, from_time, to_time)

        print(queryString)

        conn = pytds.connect(self.host, 'oemvmdata', user=self.user, password=self.password,
                             as_dict=True)
        cur = conn.cursor()
        cur.execute(queryString)

        #apparantly, the data returned is found in the 3rd set
        cur.nextset()
        cur.nextset()
        cur.nextset()
        data = cur.fetchall()

        conn.close()
        return data

    def private_transform_data(self, points, data):

        index_to_name = {}
        index = 1
        point_name_to_values = {}
        for point_name in points:
            index_to_name[index] = point_name
            point_name_to_values[point_name] = []
            index += 1

        timestamps = []

        for row in data:

            '''
            2018-09-20T14:50:09+00:00
            2018-09-20T14:50:09Z
            '''
            tempDate = row['time']
            tz = row['tz']
            tempDate = tempDate + timedelta(minutes=tz)
            ts = tempDate.replace(microsecond=0).isoformat() + 'Z'
            #ts = row['time'].strftime("%Y-%m-%d %H:%M")

            id = row['id']
            val = row['value']

            if ts not in timestamps:
                timestamps.append(ts)
            point_name = index_to_name[id]
            point_name_to_values[point_name].append(val)

        return timestamps, point_name_to_values


    def get_history(self, site_name, start_time, end_time, prefix, points ):
        data = self.private_getHistory( site_name, start_time, end_time, prefix, points )

        timestamps, timestamps_to_values = self.private_transform_data(points, data)

        returnData = {}
        returnData['timestamps'] = timestamps
        returnData['points'] = timestamps_to_values
        return returnData



