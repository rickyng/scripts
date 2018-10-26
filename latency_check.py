#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np 
import sys
import csv
import collections

class LatFileParser:
    def __init__(self, filename=None):        
        self.total_count = 0
        self.frequency = 0
        self.report=collections.OrderedDict([("FTE","all_messages_.internal_delta_"), 
                ("Input","all_messages_.input_delta_"), 
                ("Dispatch Queue", "all_messages_.dispatch_delta_"), 
                ("Dispatch to Process", "all_messages_.dispatch_to_process_delta_"), 
                ("Processing Queue","all_messages_.process_queue_delta_"),
                ("Processing", "all_messages_.processing_delta_"), 
                ("FrameEncoding", "all_messages_.frame_encoding_delta_"), 
                ("Sending", "all_messages_.sending_delta_")])
                
        self.sum_counter_name = ['all_messages_.count_', 
                'all_messages_.internal_delta_.sum_', 
                'all_messages_.feed_handler_delta_.sum_',
                'all_messages_.dispatch_delta_.sum_', 
                'all_messages_.dispatch_to_process_delta_.sum_', 
                'all_messages_.frame_encoding_delta_.sum_',
                'all_messages_.input_delta_.sum_', 
                'all_messages_.process_queue_delta_.sum_', 
                'all_messages_.processing_delta_.sum_', 
                'all_messages_.sending_delta_.sum_', 
                'all_messages_.internal_over_threshold_count_', 
                'all_messages_.transform_container_delta_.sum_' ]
        
        self.max_counter_name = ['all_messages_.dispatch_delta_.max_', 
                'all_messages_.dispatch_to_process_delta_.max_',
                'all_messages_.frame_encoding_delta_.max_', 
                'all_messages_.input_delta_.max_', 
                'all_messages_.internal_delta_.max_',
                'all_messages_.feed_handler_delta_.max_',
                'all_messages_.process_queue_delta_.max_', 
                'all_messages_.processing_delta_.max_', 
                'all_messages_.sending_delta_.max_', 
                'all_messages_.process_queue_depth_.max_', 
                'all_messages_.send_queue_depth_.max_']

        self.sum_counter_value = dict.fromkeys(self.sum_counter_name, 0)
        self.max_counter_value = dict.fromkeys(self.max_counter_name, 0)
        self.perSec_sum_value = dict.fromkeys(self.sum_counter_name,0)
        self.perSec_max_value = dict.fromkeys(self.max_counter_name,0)
        self.max_dist_value = {}
        self.timeline =[]
        self.msgCount =[]
        for item in self.max_counter_name:
          self.max_dist_value.setdefault(item, [])
        self.last_ts =""
        with open(filename, 'r') as csvfile:
            lat_reader = csv.DictReader(csvfile, delimiter=',')
            #row = lat_reader.next() #skip the header
            for row in lat_reader:                 
                self.check(row)        
            
    def check(self, row):
        self.frequency = int(row['Frequency'] or 0) / 1000000        
        ts = row['SampleTime']
        count = int (row['all_messages_.count_'])
                
        if self.last_ts != ts:
            if self.last_ts != "":
                localMax = self.perSec_max_value["all_messages_.internal_delta_.max_"]/(self.frequency)  
                if localMax > 50000:
                    print ("PerSec %s: %.3f"%(self.last_ts,localMax))
            self.last_ts = ts
                        
            self.timeline.append(ts)
            self.msgCount.append(self.perSec_sum_value['all_messages_.count_'])
                
            for val in self.sum_counter_value:
                self.perSec_sum_value[val] = int(row[val])
            for val in self.max_counter_value:
              if '_depth_' not in val:
                self.max_dist_value[val].append(self.perSec_max_value[val]/self.frequency)                
              else:  
                self.max_dist_value[val].append(self.perSec_max_value[val])
              self.perSec_max_value[val] = int(row[val])
            
            #print (self.perSec_max_value["all_messages_.internal_delta_.max_"])
        if count != 0:
            for sv in self.sum_counter_value:
                local_sum = int(row[sv])
                self.sum_counter_value[sv]+= local_sum 
                self.perSec_sum_value[sv] += local_sum
            for mv in self.max_counter_value:
                local_max  = int(row[mv])
                if local_max  > self.perSec_max_value[mv]:
                    self.perSec_max_value[mv] = local_max
                if local_max > self.max_counter_value[mv]:
                    self.max_counter_value[mv] = local_max
                
                    
    def print_result(self, latency_file):
        sum_ =  self.sum_counter_value['all_messages_.count_']
        print ("Sum %d Frequency %d"%( sum_, self.frequency))
        for val in self.report:            
            print("%s: %.3f" %(val, float(self.sum_counter_value[self.report[val]+".sum_"])/float(sum_)/float(self.frequency) ))
        print ("Max")    
        for val in self.report:
            print("%s max: %.3f" %(val, self.max_counter_value[self.report[val]+".max_"]/self.frequency))
        plt.figure(1)
        for index, key in enumerate(self.report):
          sp = plt.subplot(3,4,index+1)
          sp.plot(self.max_dist_value[self.report[key]+".max_"], label=key+ " max") 
          sp.set_title(key+ " max")
          sp.set_ylim([0, 10000])
          #plt.legend(loc='upper right')             
        
        sp = plt.subplot(3,4,10)  
        sp.plot(self.max_dist_value['all_messages_.process_queue_depth_.max_']) 
        sp.set_title('all_messages_.process_queue_depth_.max_')
        sp.set_ylim([0, 50])
        
        sp = plt.subplot(3,4,11)  
        sp.plot(self.max_dist_value['all_messages_.send_queue_depth_.max_']) 
        sp.set_title('all_messages_.send_queue_depth_.max_')
        sp.set_ylim([0, 50])
        
        sp = plt.subplot(3,4,12)  
        sp.plot(self.msgCount, label='MsgCount') 
        sp.set_title('MsgCount')
        #plt.legend(loc='upper right')          
        plt.show()        
        
latency_file = sys.argv[1]
print (latency_file)
parser = LatFileParser(latency_file)
parser.print_result(latency_file)

