#cópia do R2A_AverageTroughput, para entendimento do algoritmo e futura adaptação para SARA.

from r2a.ir2a import IR2A
from player.parser import *
import time
import math
from statistics import harmonic_mean
from base.whiteboard import *


class R2A_Sara(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.wb = Whiteboard()
        self.throughputs = []
        self.request_time = 0
        self.qi = []
        self.weights = []
        self.seg_size = [][]
        self.h_mean = 0
        self.b_max = self.wb.get_max_buffer_size()
        self.b_min = 2
        self.b_alpha = math.floor(self.b_max*0.4)
        self.b_beta = math.floor(self.b_max*0.8)
        self.b_curr = 0
        self.curr_seg = 0
        self.curr_qi = 0
        

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        print(self.throughputs)
        
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        
        self.request_time = time.perf_counter()

        selected_qi = self.qi[0]
        self.h_mean = harmonic_mean(self.throughputs, self.weights)
        self.b_curr = wb.get_buffer()
        
        if self.b_curr < self.b_min:
            selected_qi = self.qi[0]
        elif size[curr_qi][curr_seg+1]/self.h_mean > self.b_curr - self.b_min:
            while size[curr_qi][curr_seg+1]/self.h_mean > self.b_curr - self.b_min:
                curr_qi = curr_qi - 1
            selected_qi = curr_qi
        #elif #falta terminar
        
        
        
        
        for i in self.qi:
            if self.h_mean > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.weights.append(msg.get_segment_size())

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
    
    
