"""
Build encoding module for generating Wynnbuilder URLs.

This module handles the conversion of Build objects into base64-encoded strings
that can be used in Wynnbuilder URLs. It implements the bit-level encoding format
used by Wynnbuilder, packing build information efficiently into a compact string.

The encoding process involves:
1. Building a bit string with various build components (header, equipment, tomes, etc.)
2. Converting the bit string to base64 for URL compatibility
3. Following the specific encoding constants and format expected by Wynnbuilder

Note: This encoder follows the Wynnbuilder format on time of writing and may need updates
if the Wynnbuilder encoding scheme changes.
Still up to date as of 2026-04-01.
"""

import json

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
    for item in build.get_all_gear():
        encoding_list = [(ENC['EQUIPMENT_KIND']['NORMAL'], ENC['EQUIPMENT_KIND']['BITLEN']), (item.id+1, ENC['ITEM_ID_BITLEN'])]
        if isinstance(item, Powderable):
            encoding_list.append((ENC['EQUIPMENT_POWDERS_FLAG']['NO_POWDERS'], ENC['EQUIPMENT_POWDERS_FLAG']['BITLEN']))
        equipment.append(encoding_list)
    return equipment


def build_tomes(build: Build):
    enc_tomes: list[list] = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i, tomes in enumerate(build.get_all_tomes()):
        for tome in tomes:
            match i:
                case 0: #armour
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[1].append(encoding_list)
                case 1: #weapon
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[0].append(encoding_list)
                case 2: #marathon
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[4].append(encoding_list)
                case 3: #expertise
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[6].append(encoding_list)
                case 4: #mysticism
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[5].append(encoding_list)
                case 5: #lootrunning
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[3].append(encoding_list)
                case 6: #guild
                    encoding_list = [(ENC['TOME_SLOT_FLAG']['USED'], ENC['TOME_SLOT_FLAG']['BITLEN']), (tome.id, ENC['TOME_ID_BITLEN'])]
                    enc_tomes[2].append(encoding_list)
    return (ENC['TOMES_FLAG']['HAS_TOMES'], ENC['TOMES_FLAG']['BITLEN']), itertools.chain.from_iterable(enc_tomes)


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


def create_base64string(bitstring: str):
    base64_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '+', '-']
    base64string = ''
    while len(bitstring) >= 6:
        bitstring_slice = bitstring[-6:]
        to_convert = f'0b{bitstring_slice[::-1]}'
        bitstring = bitstring[:-6]
        base64string += base64_characters[int(to_convert, base=0)]
    if len(bitstring) > 0:
        bitstring += '0'*(6-len(bitstring))
        base64string, bitstring = trim_bitstring(base64string, bitstring)
    return base64string


def encode_build(build):
    """
    Encode a Build object into a base64 string for Wynnbuilder URLs.

    Takes a complete build and converts it into the compact base64 format used
    by Wynnbuilder. This involves building a bit string with all build components
    (header, equipment, tomes, skill points, level, aspects, tree) and then
    converting to base64.

    The resulting string can be used directly in Wynnbuilder URLs like:
    https://wynnbuilder.github.io/builder/#{encoded_string}

    Args:
        build: The Build object to encode

    Returns:
        str: Base64-encoded string representing the build
    
    For now only will return changed items like armour, accessories, weapon and tomes,
    all other types from the build will default to the default specified by wynnbuilder.
    """
    bitstring = ''
    base64string = ''
    header = build_header()
    equipment = build_equipment(build)
    tome_flag, tomes = build_tomes(build)
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
    bitstring = add_to_binary_string(bitstring, tome_flag)
    for tome in tomes:
        for element in tome:
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
    #return create_base64string(bitstring)[::-1]
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
