import numpy as np
from numba import njit



def bubbleSort(str_arr: list[str], value_arr: list) -> tuple[list[str], list]:
    n = len(str_arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if value_arr[j] > value_arr[j+1]:
                value_arr[j], value_arr[j+1] = value_arr[j+1], value_arr[j]
                str_arr[j], str_arr[j+1] = str_arr[j+1], str_arr[j]
                swapped = True
        """ if swapped == False:
            break """
    return str_arr, value_arr

def sort_by_value(keys: list[str], data: list[list], sort_by: str) -> tuple[list[str], list[int]]:
    filtered_data: list = []
    for item in data:
        filtered_data.append(item[1][item[0].index(sort_by)])
    return bubbleSort(keys, filtered_data)
    


def sort_dict_by_value(unsorted_dict: dict[str, dict[str, int]], sort_by) -> tuple[list[str], list[dict[str, int]]]:
    keys = list(unsorted_dict.keys())
    value_groups = list(unsorted_dict.values())
    n = len(keys)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if value_groups[j][sort_by] > value_groups[j+1][sort_by]:
                value_groups[j], value_groups[j+1] = value_groups[j+1], value_groups[j]
                keys[j], keys[j+1] = keys[j+1], keys[j]
                swapped = True
        if swapped == False:
            break
    return keys, value_groups

def sort_dict(unsorted_dict: dict[str, int]) -> tuple[list[str], list[int]]:
    keys_list = list(unsorted_dict.keys())
    values_list = list(unsorted_dict.values())
    sorted_keys, sorted_values = bubbleSort(keys_list, values_list)
    return (sorted_keys, sorted_values)







""" 
dictionary = {'a': 5, 'b': 3, 'c': 8, 'd': 1}
sorted_keys, sorted_values = sort_dict(dictionary)
print("Sorted Keys:", sorted_keys)
print("Sorted Values:", sorted_values) """

