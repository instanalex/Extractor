import json
import requests
import time
import csv
from pyexcel.cookbook import merge_all_to_a_book
import glob
from datetime import datetime
from statistics import mean 
import statistics
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def getAggregatedStats(data):
    #print(data)
    Array =[]
    for x in range(len(data['values'])):
        #print("DEBUG:"+str(data['values'][x]['value']))
        if str(data['values'][x]['value'])!='None':
            Array.append(float(data['values'][x]['value']))

    #the if condition prevent empty array to be processed
    if len(Array)!=0: 
        avgVal = mean(Array)
        maxVal = max(Array)
        minVal = min(Array)
        stdDev = statistics.stdev(Array)
        a = np.array(Array)
        per90=np.percentile(a,90)
        per95=np.percentile(a,95)
        per99=np.percentile(a,99)
        
        stats = {'min' : minVal, 'max': maxVal, 'avg': avgVal, 'stdDev': statistics.stdev(Array), 'count': len(Array), 'p90' : per90, 'p95': per95, 'p99': per99}

    else:
        stats = {'min' : 0, 'max': 0, 'avg': 0, 'stdDev': 0, 'count': '0', 'p90' : 0, 'p95': 0, 'p99': 0}

    return stats
    


print('Please enter your Instana tenant?')
tenant = input('')
print('Please enter your Instana unit?')
unit = input('')
print('Please enter your API Key')
key = input('')

baseURL = 'https://'+ unit + '-' + tenant +'.instana.io'
authHEADER = 'apiToken '+key
restdata={'baseURL': baseURL, 'auth': authHEADER}


#apiKey='wgb4-kyEq9VdZ-BZ'
#conn={'baseURL': 'https://demoeu-instana.instana.io', 'auth': 'apiToken wgb4-kyEq9VdZ-BZ'}

#OuiSNCF
#conn={'baseURL': 'https://ouisncf-ouisncf.instana.io', 'auth': 'apiToken mgGM5xlIdbSdOfgS'}
#Apple Conn
conn={'baseURL': 'https://nurv.apple.com', 'auth': 'apiToken G3lamdCqKElwiKWN'}
DFQ = 'entity.zone:\"Mobile Apps\" AND entity.type:host'
plugin='host'
url = conn['baseURL'] + "/api/infrastructure-monitoring/snapshots"
params = {'query' :DFQ, 'to' :'', 'windowSize' :'2678400000' ,'plugin' :plugin, 'offline' :'false', 'size':''}
headers = {'authorization': conn['auth']}

hostList=requests.get(url, headers=headers, params=params,verify= False).json()



#Got my host list
#Need to get CPU count, available memory
toTS = int(round(time.time() * 1000))
fromTS=toTS-3600000
urlMetrics = conn['baseURL'] + "/api/metrics"
urlDetails = conn['baseURL'] + "/api/infrastructure-monitoring/snapshots/"
line = ['snapshotId',
        'hostName',
        'CPU Underused',
        'Mem underused',
        'cpu.count',
        'cpu.min',
        'cpu.max',
        'cpu.avg',
        'cpu.stddev',
        'cpu.metriccount',
        'cpu.p90',
        'cpu.p95',
        'cpu.p99',
        'cpuLoad.min',
        'cpuLoad.max', 
        'cpuLoad.avg', 
        'cpuLoad.stddev', 
        'cpuLoad.metriccount',
        'cpuLoad.p90',
        'cpuLoad.p95',
        'cpuLoad.p99', 
        'mem.min',
        'mem.max',
        'mem.avg',
        'mem.stddev',
        'mem.metriccount',
        'mem.p90',
        'mem.p95',
        'mem.p99',
        'swapFree.min',
        'swapFree.max',
        'swapFree.avg',
        'swapFree.stddev',
        'swapFree.metriccount',
        'swapFree.p90',
        'swapFree.p95',
        'swapFree.p99',
        'swapTotal',
        'tag1',#request OuiSNCF
        'tag2'#request OuiSNCF
        ]
with open('output.csv', 'w', newline='') as f:
    thewriter = csv.writer(f)
    #thewriter.writerow(['clusterName', 'nodeName', 'nodeSnapshotId', 'hostSanpshotId', 'cpu.total', 'memory.total', 'TS', 'cpu', 'mem'])
    thewriter.writerow(line)
    for items in hostList['items']:
        print("DEBUG: snapshotId = "+items['snapshotId']+" | hostname = "+items['label'])
        paramsCPU = {"metric": 'cpu.used', "from": 1585014613000, "to": 1587603013000, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        paramsCPULoad = {"metric": 'load.1min', "from": 1585014613000, "to": 1587603013000, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        paramsMem = {"metric": 'memory.used', "from": 1585014613000, "to": 1587603013000, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        paramsSwapFree = {"metric": 'memory.swapFree', "from": 1585014613000, "to": 1587603013000, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        paramsSwapTotal = {"metric": 'memory.swapTotal', "from": 1585014613000, "to": 1587603013000, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        
        #paramsMem = {"metric": 'memory.used', "from": fromTS, "to": toTS, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        CPUStats = getAggregatedStats(requests.get(urlMetrics, headers=headers, params=paramsCPU,verify= False).json())
        CPULoadStats = getAggregatedStats(requests.get(urlMetrics, headers=headers, params=paramsCPULoad,verify= False).json())
        MEMStats = getAggregatedStats(requests.get(urlMetrics, headers=headers, params=paramsMem,verify= False).json())
        swapFreeStats = getAggregatedStats(requests.get(urlMetrics, headers=headers, params=paramsSwapFree,verify= False).json())
        swapTotalStats = getAggregatedStats(requests.get(urlMetrics, headers=headers, params=paramsSwapTotal,verify= False).json())
        machineDetails = requests.get(urlDetails+items['snapshotId'], headers=headers, params={},verify= False).json()
        
        CPUCount = machineDetails['data']['cpu.count']
        tags = machineDetails['tags']
        dTag = {} #dict of tags
        for i in range(len(tags)):
            dTag.update({tags[i].split('=')[0]:tags[i].split('=')[1]})
        
        
        #if avg CPU is < 50% and max CPULoad < 2 x cpu.count and perc99 < 80 -> CPU underused
        if (CPUStats.get('avg')<=0.5 and CPUStats.get('p99')<=0.8 and CPULoadStats.get('max')<CPUCount):
            CPUUnder = 'true'
        else:
            CPUUnder = 'false'
        
        if swapTotalStats.get('avg')!=0:

            if (MEMStats.get('avg')<=0.5 and MEMStats.get('p99')<=0.8 and swapFreeStats.get('avg')/swapTotalStats.get('avg')>0.9):
                MemUnder = 'true'
            else:
                MemUnder = 'false'
            
        else:
            MemUnder = CPUUnder = 'undefined (metric incomplete)'
            
        line = [
                items['snapshotId'],
                items['label'],
                CPUUnder,
                MemUnder,
                str(CPUCount),
                str(CPUStats['min']),
                str(CPUStats['max']),
                str(CPUStats['avg']),
                str(CPUStats['stdDev']),
                str(CPUStats['count']),
                str(CPUStats['p90']),
                str(CPUStats['p95']),
                str(CPUStats['p99']),
                str(CPULoadStats['min']),
                str(CPULoadStats['max']),
                str(CPULoadStats['avg']),
                str(CPULoadStats['stdDev']),
                str(CPULoadStats['count']),
                str(CPULoadStats['p90']),
                str(CPULoadStats['p95']),
                str(CPULoadStats['p99']),
                str(MEMStats['min']),
                str(MEMStats['max']),
                str(MEMStats['avg']),
                str(MEMStats['stdDev']),
                str(MEMStats['count']),
                str(MEMStats['p90']),
                str(MEMStats['p95']),
                str(MEMStats['p99']),
                str(swapFreeStats['min']),
                str(swapFreeStats['max']),
                str(swapFreeStats['avg']),
                str(swapFreeStats['stdDev']),
                str(swapFreeStats['count']),
                str(swapFreeStats['p90']),
                str(swapFreeStats['p95']),
                str(swapFreeStats['p99']),
                str(swapTotalStats['avg']),
                dTag['datacenter'],
                dTag['application']
            ]
        
        
        thewriter.writerow(line)
        #print(getStats(CPU))
        #print(getStats(MEM))


merge_all_to_a_book(["output.csv"], "output.xlsx")
