"""
            GRUPO 2
            
@authors:   Brando Wilhan Galdino da Silva      -   17/0161579
            Sabrina Carvalho Neves              -   17/0113973
            Thiago Cardoso Pinheiro Dias Pais   -   16/0146372

@description: Algoritmo de adaptação dinâmica para streaming de vídeo por HTTP baseado no 
"SARA - Segment Aware Rate Adaptation Algorithm"
"""

from r2a.ir2a import IR2A
from player.parser import *
import time
import math
from statistics import mean
from base.whiteboard import Whiteboard


class R2A_Sara(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.wb = Whiteboard.get_instance()
        self.throughputs = []
        self.request_time = 0
        self.qi = []
        self.seg_size = []
        self.seg_size_per_throughput = []
        self.seg_size_per_qi = []
        self.h_mean = 0
        self.b_max = 0
        self.b_min = 0
        self.b_alpha = 0
        self.b_beta = 0
        self.b_curr = 0
        self.curr_seg = 0
        self.curr_qi = 0
        self.delay = 0
    
    def estimated_size_for_next_seg(self, qi):
        if self.seg_size_per_qi[qi] == []:
            return mean(self.seg_size_per_qi[0]) * (self.qi[qi]/self.qi[0])
        else:
            return mean(self.seg_size_per_qi[qi])
    
    
    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        print(self.throughputs)
        
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()
        for i in range(len(self.qi)):
            self.seg_size_per_qi.append([])
            
        self.b_max = self.wb.get_max_buffer_size()
        self.b_min = math.floor(self.b_max*0.2)
        self.b_alpha = math.floor(self.b_max*0.4)
        self.b_beta = math.floor(self.b_max*0.8)
        
        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        if sum(self.seg_size_per_throughput) != 0:
            self.h_mean = sum(self.seg_size)/sum(self.seg_size_per_throughput)
        else:
            self.h_mean = 1
            
        self.b_curr = self.wb.get_amount_video_to_play()
        
        if self.seg_size_per_qi[self.curr_qi] != []:
            estimated_time = mean(self.seg_size_per_qi[self.curr_qi])/self.h_mean
        else:
            estimated_time = 0
        
        if self.b_curr < self.b_min:
            self.curr_qi = 0

        elif estimated_time > (self.b_curr - self.b_min):
            while (self.estimated_size_for_next_seg(self.curr_qi)/self.h_mean > (self.b_curr - self.b_min)) and self.curr_qi > 0:
                self.curr_qi = self.curr_qi - 1
                
        elif self.b_curr <= self.b_alpha:
            if estimated_time < (self.b_curr - self.b_min):
                if self.curr_qi < len(self.qi)-1:
                    self.curr_qi = self.curr_qi + 1
            else:
                self.curr_qi = self.curr_qi
                
        elif self.b_curr <= self.b_beta:
            while (self.curr_qi < len(self.qi)) and (self.estimated_size_for_next_seg(self.curr_qi)/self.h_mean <= self.b_curr - self.b_min):
                self.curr_qi = self.curr_qi + 1
            
            self.curr_qi = self.curr_qi - 1
        
        elif self.b_curr > self.b_beta:
            while (self.estimated_size_for_next_seg(self.curr_qi)/self.h_mean <= self.b_curr - self.b_alpha) and (self.curr_qi < len(self.qi)):
                self.curr_qi = self.curr_qi + 1
                
            self.curr_qi = self.curr_qi - 1
            self.delay = self.b_curr - self.b_beta
            
        
        if self.delay > 0:
            time.sleep(self.delay)
            self.delay = 0

        msg.add_quality_id(self.qi[self.curr_qi])
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.seg_size.append(msg.get_segment_size())
        if msg.get_bit_length() != 0 and t != 0:
            self.seg_size_per_throughput.append(msg.get_segment_size()/(msg.get_bit_length() / t))
        else:
            self.seg_size_per_throughput.append(0)
        
        self.seg_size.append(msg.get_bit_length())
        self.seg_size_per_qi[self.curr_qi].append(msg.get_bit_length())

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
    
    
