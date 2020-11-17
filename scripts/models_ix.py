from config import Config
import sys
import traceback
import collections
import random
import math as m

"""
Configs
"""

# elements for a given config
class IxConfig(Config):
    # five important things we need for a switch box element
    # 1. the width of the connections
    # 2. the available nodes
    # 3. the mapping from node to node (indexed by config bit location)
    # 4. the directioness of the switches
    def __init__(self, instance_name, data_width, nodes, switches, bidirectional):
        super().__init__(instance_name)
        self.data_width = data_width
        self.nodes = nodes 
        self.switches = switches
        self.bidirectional = bidirectional 


# method that generates a type of ix config based on the parameter passed in
def generate_config(type_name):
    name = str(type_name)
    if name == "switch_box_element_one_config":
        return IxConfig(
            'switch_box_element_one_config',
            1,
            {"n0":1, "s0":2, "e0":3, "w0":4},
            [(1,3), (2,3), (2,4), (1,4), (1,2), (3,4)],
            True
        )
    elif name == "switch_box_element_two_config":
        return IxConfig(
            'switch_box_element_two_config',
            1,
            {"n0":1, "n1":2, "s0":3, "s1":4, "e0":5, "e1":6, "w0":7, "w1":8},
            [(1,5), (3,6), (4,8), (2,7), (2,6), (4,5), (3,7), (1,8), (1,3), (6,8), (2,4), (5,7)],
            True
        )
    else:
        # default config is used
        return IxConfig(
            "default_config",
            1,
            {1:"north", 2:"south"},
            [(1,2)],
            True
        )


"""
Models
"""

# model of an instantiated switch box
class InstantiatedSwitchBox():
    # model the switch box based on existing model (model) and user input (active_mapping)
    def __init__(self, model, active_mapping):
        self.model = model
        self.nodes = self.model.nodes
        self.active_mapping = self.match_mapping_to_internal(active_mapping)
        self.switches = self.model.connections
        self.bitstream = [None] * len(self.switches)

    # user passes in text format, this method converts it to internal format
    # for example, use passes: [("n0","w1"), ("n0","e0")]
    # the method convert to:   [(1,3), (1,4)]
    def match_mapping_to_internal(self, mapping):
        converted = list()
        for start_label, end_label in mapping:
            converted.append((self.nodes[start_label], self.nodes[end_label]))
        return converted


    # map the active config to the given config
    def map_input_to_config(self):
        for index, edge in enumerate(self.switches):
            # assume the user follows the naming convention
            if edge in self.active_mapping:
                self.bitstream[index] = 1    
            else:
                self.bitstream[index] = 0

    # generate the bistream for this configured element
    def output_bitstream(self):
        result = ""
        for bit in self.bitstream:
            result += str(bit)
        return result    


# model for generic switch box
class SwitchBoxModel():
    def __init__(self):
        pass

    def report_index(self, start, end):
        try:
            return self.connections.index((self.nodes[start], self.nodes[end]))
        except ValueError as e:
            print(traceback.format_exception(None, e, e.__traceback__), file=sys.stderr, flush=True)
            return "Note the above error"


# model for switch_box_element_one
class SwitchBoxElementOne(SwitchBoxModel):
    def __init__(self):
        self.config = generate_config("switch_box_element_one_config")
        self.name = "switch_box_element_one"
        # North -> south -> east -> west
        self.nodes = {"n0":1, "s0":2, "e0":3, "w0":4}
        self.connections = self.config.switches


# model for switch_box_element_one
class SwitchBoxElementTwo(SwitchBoxModel):
    def __init__(self):
        self.config = generate_config("switch_box_element_two_config")
        self.name = "switch_box_element_two"
        # North -> south -> east -> west
        self.nodes = {"n0":1, "n1":2, "s0":3, "s1":4, "e0":5, "e1":6, "w0":7, "w1":8}
        self.connections = self.config.switches


class UniversalSwitchBox(SwitchBoxModel):
    def __init__(self, W):
        self.name = "universal_switch_box"
        self.W = W
        self.nodes, self.connections = self.configure()
        

    def configure(self):
        nodes = dict()
        connections = list()

        count = 0
        for i in range (0, self.W-1, 2):
            # configure the nodes
            count += 1
            nodes["n"+str(i)] = count
            count += 1
            nodes["n"+str(i+1)] = count
            count += 1
            nodes["s"+str(i)] = count                
            count += 1
            nodes["s"+str(i+1)] = count   
            count += 1
            nodes["e"+str(i)] = count                
            count += 1
            nodes["e"+str(i+1)] = count 
            count += 1
            nodes["w"+str(i)] = count                
            count += 1
            nodes["w"+str(i+1)] = count 

            # configure the connections
            connections.append((nodes["n"+str(i)], nodes["e"+str(i)]))
            connections.append((nodes["s"+str(i)], nodes["e"+str(i+1)]))
            connections.append((nodes["s"+str(i+1)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i+1)], nodes["w"+str(i)]))
            connections.append((nodes["n"+str(i+1)], nodes["e"+str(i+1)]))
            connections.append((nodes["s"+str(i+1)], nodes["e"+str(i)]))
            connections.append((nodes["s"+str(i)], nodes["w"+str(i)]))
            connections.append((nodes["n"+str(i)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i)], nodes["s"+str(i)]))
            connections.append((nodes["e"+str(i+1)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i+1)], nodes["e"+str(i+1)]))
            connections.append((nodes["e"+str(i)], nodes["w"+str(i)]))

        if self.W % 2 != 0:
            # generate one more sb_element_one
            count += 1
            nodes["n"+str(self.W-1)] = count
            count += 1
            nodes["s"+str(self.W-1)] = count
            count += 1
            nodes["e"+str(self.W-1)] = count
            count += 1
            nodes["w"+str(self.W-1)] = count

            # configure the connections
            connections.append((nodes["n"+str(self.W-1)], nodes["e"+str(self.W-1)]))
            connections.append((nodes["s"+str(self.W-1)], nodes["e"+str(self.W-1)]))
            connections.append((nodes["s"+str(self.W-1)], nodes["w"+str(self.W-1)]))
            connections.append((nodes["n"+str(self.W-1)], nodes["w"+str(self.W-1)]))
            connections.append((nodes["n"+str(self.W-1)], nodes["s"+str(self.W-1)]))

        return nodes, connections


class CLBSwitchBox(SwitchBoxModel):
    def __init__(self, WS, WD):
        self.name = "clb_switch_box"
        self.WS = WS
        self.WD = WD  # WD must be multiple of 2
        self.nodes, self.connections = self.configure()    

    # note that the double line direct connections do not need to be configured
    def configure(self):
        nodes = dict()
        connections = list()

        # configure the single line Universal Switch Box
        count = 0
        for i in range (0, self.WS-1, 2):
            # configure the nodes
            count += 1
            nodes["n"+str(i)] = count
            count += 1
            nodes["n"+str(i+1)] = count
            count += 1
            nodes["s"+str(i)] = count                
            count += 1
            nodes["s"+str(i+1)] = count   
            count += 1
            nodes["e"+str(i)] = count                
            count += 1
            nodes["e"+str(i+1)] = count 
            count += 1
            nodes["w"+str(i)] = count                
            count += 1
            nodes["w"+str(i+1)] = count 

            # configure the connections
            connections.append((nodes["n"+str(i)], nodes["e"+str(i)]))
            connections.append((nodes["s"+str(i)], nodes["e"+str(i+1)]))
            connections.append((nodes["s"+str(i+1)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i+1)], nodes["w"+str(i)]))
            connections.append((nodes["n"+str(i+1)], nodes["e"+str(i+1)]))
            connections.append((nodes["s"+str(i+1)], nodes["e"+str(i)]))
            connections.append((nodes["s"+str(i)], nodes["w"+str(i)]))
            connections.append((nodes["n"+str(i)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i)], nodes["s"+str(i)]))
            connections.append((nodes["e"+str(i+1)], nodes["w"+str(i+1)]))
            connections.append((nodes["n"+str(i+1)], nodes["e"+str(i+1)]))
            connections.append((nodes["e"+str(i)], nodes["w"+str(i)]))

        if self.WS % 2 != 0:
            # generate one more sb_element_one
            count += 1
            nodes["n"+str(self.WS-1)] = count
            count += 1
            nodes["s"+str(self.WS-1)] = count
            count += 1
            nodes["e"+str(self.WS-1)] = count
            count += 1
            nodes["w"+str(self.WS-1)] = count

            # configure the connections
            connections.append((nodes["n"+str(self.WS-1)], nodes["e"+str(self.WS-1)]))
            connections.append((nodes["s"+str(self.WS-1)], nodes["e"+str(self.WS-1)]))
            connections.append((nodes["s"+str(self.WS-1)], nodes["w"+str(self.WS-1)]))
            connections.append((nodes["n"+str(self.WS-1)], nodes["w"+str(self.WS-1)]))
            connections.append((nodes["n"+str(self.WS-1)], nodes["s"+str(self.WS-1)]))

        # configure the double line Universal Switch Box
        for i in range (0, self.WD//2, 2):
            # configure the nodes
            count += 1
            nodes["dn"+str(i)] = count
            count += 1
            nodes["dn"+str(i+1)] = count
            count += 1
            nodes["ds"+str(i)] = count                
            count += 1
            nodes["ds"+str(i+1)] = count   
            count += 1
            nodes["de"+str(i)] = count                
            count += 1
            nodes["de"+str(i+1)] = count 
            count += 1
            nodes["dw"+str(i)] = count                
            count += 1
            nodes["dw"+str(i+1)] = count 

            # configure the connections
            connections.append((nodes["dn"+str(i)], nodes["de"+str(i)]))
            connections.append((nodes["ds"+str(i)], nodes["de"+str(i+1)]))
            connections.append((nodes["ds"+str(i+1)], nodes["dw"+str(i+1)]))
            connections.append((nodes["dn"+str(i+1)], nodes["dw"+str(i)]))
            connections.append((nodes["dn"+str(i+1)], nodes["de"+str(i+1)]))
            connections.append((nodes["ds"+str(i+1)], nodes["de"+str(i)]))
            connections.append((nodes["ds"+str(i)], nodes["dw"+str(i)]))
            connections.append((nodes["dn"+str(i)], nodes["dw"+str(i+1)]))
            connections.append((nodes["dn"+str(i)], nodes["ds"+str(i)]))
            connections.append((nodes["de"+str(i+1)], nodes["dw"+str(i+1)]))
            connections.append((nodes["dn"+str(i+1)], nodes["de"+str(i+1)]))
            connections.append((nodes["de"+str(i)], nodes["dw"+str(i)]))

        return nodes, connections


# model for the overall fabric
class Fabric():
    def __init__(self):
        self.elements = list()    # hold elements
        self.type_count = dict()  # keep track of types
    
    def add_element(self, instantiated_model, priority):
        self.elements.append((instantiated_model, priority))
        if instantiated_model.model.name not in self.type_count.keys():
            self.type_count[instantiated_model.model.name] = 1
        else:
            self.type_count[instantiated_model.model.name] += 1
    
    def change_priority(self, instantiated_model, old_piority, new_priority):
        try:
            res = self.elements.index((instantiated_model, old_piority))
            self.elements.remove((instantiated_model, old_piority))
            self.elements.append((instantiated_model, new_priority))
        except ValueError as e:
            print(traceback.format_exception(None, e, e.__traceback__), file=sys.stderr, flush=True)
            return "update not successful, the pair cannot be found"

    # output the bitstream of all elements within this fabric in terms of the priority
    def output_bitstream(self):
        self.elements.sort(key=lambda x: x[1], reverse=True)
        # for i in self.elements:
        #     print(i)

        # output the bitsteam from high priority to the lowest
        res = ""
        for index, item in enumerate(self.elements):
            if index == len(self.elements) - 1:
                res += item[0].output_bitstream()
            else:
                res += item[0].output_bitstream() + "_"
        return res

"""
LUTs
"""

# model for generic logic block
class LogicBlock():
    def __init__(self):
        pass

    def output_bitstream(self):
        return self.config_bits

    # randomly generate a sequence
    def configure(self):
        bitstream = ""
        for i in range(0, self.config_width):
            k = random.randint(0, 1)
            bitstream += str(k)
        return bitstream

# 
class ConfiguredLUT(LogicBlock):
    # INPUT_WIDTH is the width of the input
    # config_bits are the input config bits stored at each location (ascending index)
    def __init__(self, INPUT_WIDTH, generate, config_bits="0000111100001111"):
        self.name = str(INPUT_WIDTH) + "_LUT"
        self.config_width = int(pow(2, INPUT_WIDTH))
        self.config_bits = self.configure() if generate else config_bits


class ConfiguredS44(LogicBlock):
    def __init__(self, INPUT_WIDTH, generate, split="1", lut_left_config="0000111100001111", lut_right_config="0000111100001111"):
        self.mem_size = int(pow(2, INPUT_WIDTH))
        self.config_width = 2 * self.mem_size + 1
        self.name = str(INPUT_WIDTH) + "_S44"
        # the top config bits determine the split signal
        self.config_bits = self.configure() if generate else split + lut_left_config + lut_right_config
        # create two Configured LUTs (with the config bits distributed)
        self.lut_left = ConfiguredLUT(INPUT_WIDTH, False, self.config_bits[2*self.mem_size-1:self.mem_size])
        self.lut_right = ConfiguredLUT(INPUT_WIDTH, False, lut_right_config[self.mem_size-1:0])


class ConfiguredMuxFSlice(LogicBlock):
    def __init__(self, INPUT_WIDTH, generate, mux_f_slice_config="10"):
        self.name = str(INPUT_WIDTH) + "_mux_f_slice"
        self.config_width = int(m.log2(INPUT_WIDTH))
        self.config_bits = self.configure() if generate else mux_f_slice_config


class ConfiguredRegisters(LogicBlock):
    def __init__(self, INPUT_WIDTH, generate, regs_config="11001100"):
        self.name = str(INPUT_WIDTH) + "_regs"
        self.config_width = 2 * INPUT_WIDTH
        self.config_bits = self.configure() if generate else regs_config


# the configuration bits are carried out as (LEFT IS THE MSB):
# [mux_f_slice (2bits)] [config_use_cc (1bit)] [regs (8bits)] [S44_3 (33bits)] [S44_2 (33bits)] [S44_1 (33bits)] [S44_0 (33bits)]
class ConfiguredSliceL(LogicBlock):
    def __init__ (self, params, generate, slicel_config="1" * 143):
        # parameters
        self.s_xx_base = params["s_xx_base"]
        self.num_luts = params["num_luts"]
        self.name = str(self.num_luts) + "_SliceL"
        self.cfg_size = 2 * int(pow(2, self.s_xx_base)) + 1
        self.mux_lvls = int(m.log2(self.num_luts))

        # models
        self.luts = list()

        # config size and bits
        self.config_width = (self.num_luts * self.cfg_size) + self.mux_lvls + 1 + (2 * self.num_luts)
        self.config_bits = self.configure() if generate else slicel_config

        # instantiated models
        # fslice, config_use_cc, regs, luts
        for i in range(0, self.num_luts):
            self.luts.append(ConfiguredS44(self.s_xx_base, False, self.config_bits[(i+1)*self.cfg_size-1:i*self.cfg_size]))    
        self.regs = ConfiguredRegisters(self.num_luts, False, self.config_bits[(self.num_luts * self.cfg_size + 2 * self.num_luts - 1):self.num_luts * self.cfg_size])
        self.config_use_cc = self.config_bits[(self.num_luts * self.cfg_size + 2 * self.num_luts + 1):self.num_luts * self.cfg_size + 2 * self.num_luts]
        self.fslice = ConfiguredMuxFSlice(self.num_luts, False, self.config_bits[self.config_width-1:self.config_width-1-int(m.log2(self.num_luts))])


