#! /usr/bin/python
import json
import pprint
import sys
import time
import os
import copy

def replaceStats(sample, table , text):  
  ret = copy.deepcopy(sample)
  newText = text.replace('-','_')
  ret['definition']['requests'][0]['q'] = ret['definition']['requests'][0]['q'].replace('<stats>', newText)
  ret['title'] = table+' '+newText  
  print ('Creating graph ...' + ret['title'])
  return ret

def generate_dash(data):
  try:
    with open('dash.json','r') as dfile:
      with open('newdash.json', 'w') as ofile:
        dash = json.load(dfile)
        sample =dash['graphs'][0]
        result_json = []
        for t in data['tables']:
          table= t['spl.redisTable']
          for v in t['variables']:
            if v['spl.varType'] != 'string' :
              result_json.append(replaceStats(sample, table, v['spl.redisKey'] ))
        dash['graphs'] = result_json
        json.dump(dash,ofile)
  except Exception as e:
    print(e)

if __name__ == '__main__':  
  if len(sys.argv) == 1:
    print ("usage:" + sys.argv[0] + " <spl json>")
    sys.exit(1)
  with open(sys.argv[1], 'r') as ifile:      
    generate_dash(json.load(ifile))
