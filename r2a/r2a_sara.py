#cópia do R2A_AverageTroughput, para entendimento do algoritmo e futura adaptação para SARA.

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean


class R2A_Sara(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = []
        self.request_time = 0
        self.qi = []
        self.weights = []
        self.bit_rates = []
        self.h_mean = 0

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter()
        avg = mean(self.throughputs) / 2

        selected_qi = self.qi[0]
        for i in self.qi:
            if avg > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def wheigted_h_mean(self, weights, bit_rates):
        
        if weights:
            den = []
            for i, j in weights, bit_rates:
                den.append(i/j)

            self.h_mean = sum(weights)/sum(den)



    def initialize(self):
        pass

    def finalization(self):
        pass
    
    
