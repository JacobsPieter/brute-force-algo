"""
Tries to make the ability tree file from the wynnapi better readable
"""





import re
import json







def parse_tree():
    with open('data\\at_data\\wynn_warrior_ability_tree.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    filter = re.compile('<.*?>')
    for abils in data['pages'].values():
        for abil in abils.values():
            for data_key, data_value in abil.items():
                if data_key == 'name':
                    print(f'{data_key}: {re.sub(filter, "", data_value)}\n')
                if data_key == 'description':
                    print(f'{data_key}: ')
                    description_elements = ['', '', '', '']
                    index = 0
                    for _, element in enumerate(data_value):
                        if element == '</br>' and index < 3:
                            index += 1
                            continue
                        description_elements[index] = f'{description_elements[index]} {re.sub(filter, "", element)}\n'
                    for element in description_elements:
                        print(element)
                        #print(f'{re.sub(filter, "", element)}')
                    print('')
                if data_key == 'requirements':
                    print(f'{data_key}: {data_value}\n')



def main():
    print(parse_tree())


if __name__ == '__main__':
    main()
