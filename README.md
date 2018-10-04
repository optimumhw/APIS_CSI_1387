# README
This project implements the APIs for querying history. See CSI_1387.


## Building
docker rm $(docker ps -a -q)
docker rmi $(docker images -q -a)

docker build -t tsapi .
dc up

## Deploy
docker exec -it 7ae06d5d98af /bin/bash
cloud config configurations list
gcloud app deploy --image-url = tsapi:latest


## Apis

### Supported Sites
WB3090
XI5016
XI2004
XR2099
XP2690
AZ2290

### Get Health
GET https://server/health

###  Get Access Token
POST https://server/oauth/token
{
username = "johndoe auth0user"
password = "...."
}


### Get Datapoints
GET https://server/datapoints?
site_name=[site_name]

### Get History
GET http://server/history?
site_name=[site_name]
&start_date=[yyyy-mm-dd]
&end_date=[yyyy-mm-dd]
&datapoints=[name1,name2,name3 ... ,nameN]