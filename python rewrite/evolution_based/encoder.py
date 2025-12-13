import base64
import numpy as np
import json
import ctypes as ct

from classes import *



with open('data\\encoding_constants.json', 'r') as file:
    ENC = json.load(file)
    



def build_header():
    legacy = (12, 6) #Always first the value that should be added in the field, next the bitlength
    version = (23, 10)
    header = [legacy, version]
    return header

def build_equipment(build: Build):
    equipment = []
    for item in build.get_all_items():
        encoding_list = [(ENC['EQUIPMENT_KIND']['NORMAL'], ENC['EQUIPMENT_KIND']['BITLEN']), (item.id+1, ENC['ITEM_ID_BITLEN'])]
        if isinstance(item, Powderable):
            encoding_list.append((ENC['EQUIPMENT_POWDERS_FLAG']['NO_POWDERS'], ENC['EQUIPMENT_POWDERS_FLAG']['BITLEN']))
        equipment.append(encoding_list)
    return equipment


def build_tomes():
    tomes = [(ENC['TOMES_FLAG']['NO_TOMES'], ENC['TOMES_FLAG']['BITLEN'])]
    return tomes


def build_skillpoints():
    skillpoints = [(ENC['SP_FLAG']['AUTOMATIC'], ENC['SP_FLAG']['BITLEN'])]
    return skillpoints

def build_level():
    level = [(ENC['LEVEL_FLAG']['MAX'], ENC['LEVEL_FLAG']['BITLEN'])]
    return level

def build_aspects():
    aspects = [(ENC['ASPECTS_FLAG']['NO_ASPECTS'], ENC['ASPECTS_FLAG']['BITLEN'])]
    return aspects

def build_tree():
    tree = [(0,0)]
    return tree

def add_to_binary_string(string: str, field: tuple[int, int]):
    number, length = field
    number_binary = bin(number)
    string_of_raw_binary_number = str(number_binary)
    string_of_binary_number = string_of_raw_binary_number[2:][::-1]
    if len(string_of_binary_number) < length: #set length to zero for fields without a defined length.
        string_of_binary_number = string_of_binary_number + '0'*(length-len(string_of_binary_number))
    returnstring = f'{string}{string_of_binary_number}'
    return returnstring


def trim_bitstring(base64string: str, bitstring: str):
    base64_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '+', '-']
    if len(bitstring) >= 6:
        bitstring_slice = bitstring[:6]
        to_convert = f'0b{bitstring_slice[::-1]}'
        bitstring = bitstring[6:]
        #print(int(to_convert, base=2))
        base64string += base64_characters[int(to_convert, base=0)]
        #print(base64string)
        return trim_bitstring(base64string, bitstring)
    else:
        return base64string, bitstring






def encode_build(build):
    bitstring = ''
    base64string = ''
    header = build_header()
    equipment = build_equipment(build)
    tomes = build_tomes()
    skillpoints = build_skillpoints()
    level = build_level()
    aspects = build_aspects()
    tree = build_tree()
    for element in header:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    for item in equipment:
        for element in item:
            bitstring = add_to_binary_string(bitstring, element)
            base64string, bitstring = trim_bitstring(base64string, bitstring)
    for element in tomes:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    for element in skillpoints:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    for element in level:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    for element in aspects:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    for element in tree:
        bitstring = add_to_binary_string(bitstring, element)
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    if len(bitstring) > 0:
        bitstring += '0'*(6-len(bitstring))
        base64string, bitstring = trim_bitstring(base64string, bitstring)
        return base64string
    else:
        base64string, bitstring = trim_bitstring(base64string, bitstring)
        return base64string
    


""" if __name__ == "main":
    build = [('Brilliant Diamond Helmet', 0), ('Brilliant Diamond Chestplate', 0), ('Brilliant Diamond Leggings', 0), ('Brilliant Diamond Boots', 0), ('Bygg', 0), ('Bygg', 0), ('Depravity', 0), ('Grafted Eyestalk', 0), ('Cracked Oak Spear', 0)]
    print(encode_build(build)) """

