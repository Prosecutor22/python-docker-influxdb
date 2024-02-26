import docker
import json
import time
import requests
client = docker.from_env()

url = "http://localhost:8086/api/v2/write?org=test&bucket=test"
token = "p0juZOFNve2hGnJEORETD5SRlbrVUd66bpRaJiw8zMrNwgSUWQEMxNOvJD1XUrWAHwvns96P3DSAlDd8O8L8iQ=="

def sendData(data):
    data_lines = [f'{point["measurement"]},{",".join([f"{k}={v}" for k, v in point["tags"].items()])} ' +
              f'{",".join([f"{k}={v}" for k, v in point["fields"].items()])} {point["time"]}' for point in data]
    payload = '\n'.join(data_lines)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 204:
        print("Data successfully pushed to InfluxDB")
    else:
        print(f"Failed to push data to InfluxDB. Status code: {response.status_code}")
        print(response.text)
timeNow = int(time.time())
containers = client.containers.list()
for container in containers:
    # Get container stats
    name = container.name
    if 'SizeRw' in container.attrs:
        size = container['SizeRw']
    else:
        size = None
    stats = container.stats(stream=False)
    cpu_percentage = stats['cpu_stats']['cpu_usage']['total_usage']
    total_cpu = stats['cpu_stats']['system_cpu_usage']
    percent_cpu = cpu_percentage/total_cpu*100
    memory_usage = stats['memory_stats']['usage']
    try:
        memory_limit = stats['memory_stats']['limit']
    except:
        memory_limit = None
    container_info = container.attrs
    ipv4 = container_info['NetworkSettings']['IPAddress']
    if ipv4 == "":
        ipv4 = None
    data_cpu = [
        {
            "measurement": "docker_monitor_cpu",
            "tags": {
                "name": name
            },
            "fields": {
                "value": percent_cpu
            },
            "time": timeNow
        }
    ]
    sendData(data_cpu)
    
    data_memory = [
        {
            "measurement": "docker_monitor_memory",
            "tags": {
                "name": name
            },
            "fields": {
                "usage": memory_usage,
            },
            "time": timeNow
        }
    ]
    if memory_limit is not None:
        data_memory[0]["fields"]["limit"] = memory_limit
    sendData(data_memory)
    
    data_disk = [
        {
            "measurement": "docker_monitor_disk",
            "tags": {
                "name": name
            },
            "fields": {
            },
            "time": timeNow
        }
    ]
    if size is not None:
        data_memory[0]["fields"]["value"] = size
        sendData(data_disk)
    
    data_ip = [
        {
            "measurement": "docker_monitor_ipv4",
            "tags": {
                "name": name
            },
            "fields": {
            },
            "time": timeNow
        }
    ]
    if ipv4 is not None:
        data_memory[0]["fields"]["value"] = ipv4
        sendData(data_ip)
    
