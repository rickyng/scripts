#! /usr/bin/python

import redis
import json
import pprint
import sys
import time
import os

def connect(redis_host):
  try:
    redis_port = 6379
    redis_password = ""
    # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
    # using the default encoding utf-8.  This is client specific.
    r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    return r
  except Exception as e:
    print (e)

def dumpJson(r):
  try:
    instances = r.smembers("InstanceTable")
    for ins in instances :
      jsonStr =  r.hget("InstanceTable:"+ins, "jsonFile")
      data = json.loads(jsonStr)
      with open(ins+"_spl.json", "w") as ofile:
        json.dump(data,ofile)
  except Exception as e:
    print (e)



def check_alive(r):
  try:
    instances = r.smembers("InstanceTable")
    for i in range(10):
      for ins in instances :
        if ins != 'JsonLog':
          status  = r.hget("InstanceTable:"+ins, "applicationStatus")
          alive = r.hget("InstanceTable:"+ins, "alive")
          print (ins + " "+ status + " " + alive)
      time.sleep(10)
  except Exception as e:
    print(e)

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print ("usage:" + sys.argv[0] + " <redis_ip>")
    sys.exit(1)
  redis = connect(sys.argv[1])
  dumpJson(redis)
  check_alive(redis)
