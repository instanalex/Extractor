import json
import requests
import time
import csv
from pyexcel.cookbook import merge_all_to_a_book
import glob
from datetime import datetime

def extractPodAndNS(a):
    separator = a.find('/')
    end = a.find('(')
    return {'pod': a[separator+1:end-1:], 'namespace': a[0:separator:]}


#connection
print('Please enter your Instana url (https://server-name) ')
baseURL = input('')
print('Please enter your API Key')
key = input('')
authHEADER = 'apiToken '+key
conn={'baseURL': baseURL, 'auth': authHEADER}

print('enter your K8s cluster name')
clustername=input()
clusterDFQ='entity.kubernetes.cluster.label:'+clustername
############

#Retreive SnapshotsID for all nodes. 
url = conn['baseURL'] + "/api/infrastructure-monitoring/snapshots"
paramsClusterNodes = {'query' :clusterDFQ, 'to' :'', 'windowSize' :'3600000' ,'plugin' :'kubernetesNode', 'offline' :'false', 'size' :''}
paramsClusterPods = {'query' :clusterDFQ, 'to' :'', 'windowSize' :'3600000' ,'plugin' :'kubernetesPod', 'offline' :'false', 'size' :''}

headers = {
    'authorization': conn['auth']
}
snapshotListOfAllK8sNodes = requests.get(url, headers=headers, params=paramsClusterNodes,verify= False).json()
snapshotListOfAllK8sPods = requests.get(url, headers=headers, params=paramsClusterPods,verify= False).json()


line = ['Time','hostName','cluster','cpu.usage','memory.usage','link to host dash']
with open('nodes.csv', 'w', newline='') as f:
    thewriter = csv.writer(f)
    #thewriter.writerow(['clusterName', 'nodeName', 'nodeSnapshotId', 'hostSanpshotId', 'cpu.total', 'memory.total', 'TS', 'cpu', 'mem'])
    thewriter.writerow(line)
    toTS = int(round(time.time() * 1000))
    #Last 14days
    #fromTS=toTS-1209600000
    fromTS=toTS-259200000

    #retreive hosts metrics for a given cluster
    for items in snapshotListOfAllK8sNodes['items']:
        #This block retreives SnapshotID of related host (different from the one on Node)
        url = conn['baseURL'] + "/api/infrastructure-monitoring/graph/related-hosts/"
        url = url+items['snapshotId']
        params = {}
        headers = {
            'authorization': conn['auth']
        }
        relatedHostSnapId = requests.get(url, headers=headers, params=params,verify= False).json()[0]

        url = conn['baseURL'] + "/api/metrics"
        paramsCPU = {"metric": 'cpu.used', "from": fromTS, "to": toTS, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": relatedHostSnapId}
        paramsMem = {"metric": 'memory.used', "from": fromTS, "to": toTS, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": relatedHostSnapId}
        headers = {
            'authorization': conn['auth'],
        }
        
        cpuUsage = requests.request("GET", url, headers=headers, params = paramsCPU,verify= False).json()
        memUsage = requests.request("GET", url, headers=headers, params = paramsMem,verify= False).json()

        line[1]=items['label']
        line[2]=clustername
        line[5]=conn['baseURL']+"#/physical/dashbaord/dashboard?snapshotId="+relatedHostSnapId
        

        for x in range(len(cpuUsage['values'])):
            line[0]=datetime.fromtimestamp(cpuUsage['values'][x]['timestamp']/1000)
            line[3]=cpuUsage['values'][x]['value']
            line[4]=memUsage['values'][x]['value']
            thewriter.writerow(line)

line = ['Time','PodName','cluster','Namespace','CPU requests','Memory Requests','link to Pod dash']
with open('pods.csv', 'w', newline='') as f:
    thewriter = csv.writer(f)
    thewriter.writerow(line)
    toTS = int(round(time.time() * 1000))
    #Last 14days
    #fromTS=toTS-1209600000
    fromTS=toTS-259200000
    for items in snapshotListOfAllK8sPods['items']:
        line[1]=extractPodAndNS(items['label'])['pod']
        line[2]=clustername
        line[3]=extractPodAndNS(items['label'])['namespace']
        line[6]=conn['baseURL']+"#/physical/dashbaord/dashboard?snapshotId="+items['snapshotId']

        paramsCPU = {"metric": 'cpuRequests', "from": fromTS, "to": toTS, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        paramsMem = {"metric": 'memoryRequests', "from": fromTS, "to": toTS, "rollup": 3600000, "fillTimeSeries": "true", "snapshotId": items['snapshotId']}
        headers = {
            'authorization': conn['auth'],
        }
        
        cpuUsage = requests.request("GET", url, headers=headers, params = paramsCPU,verify= False).json()
        memUsage = requests.request("GET", url, headers=headers, params = paramsMem,verify= False).json()
        
        for x in range(len(cpuUsage['values'])):
            line[0]=datetime.fromtimestamp(cpuUsage['values'][x]['timestamp']/1000)
            line[4]=cpuUsage['values'][x]['value']
            line[5]=memUsage['values'][x]['value']
            thewriter.writerow(line)



# import pyexcel.ext.xlsx # no longer required if you use pyexcel >= 0.2.2 
import glob


merge_all_to_a_book(["nodes.csv","pods.csv"], "output.xlsx")
