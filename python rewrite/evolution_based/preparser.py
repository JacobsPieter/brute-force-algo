import json


def main():
    all_needed_keys: set = {''}
    with open("data\\items.json", 'r') as file:
        data: dict = json.load(file)
    for item_names, item_values in data.items():
        for item_value_keys, item_values_values in item_values.items():
            if not item_value_keys in all_needed_keys:
                if item_value_keys == 'requirements':
                    for req, _ in item_values_values.items():
                        all_needed_keys.add(req)
                elif item_value_keys == 'identifications':
                    for id, _ in item_values_values.items():
                        all_needed_keys.add(id)
                elif item_value_keys == 'base':
                    for base, _ in item_values_values.items():
                        all_needed_keys.add(base)
                else:
                    all_needed_keys.add(item_value_keys)
    all_needed_keys.remove('')
    for i, key in enumerate(all_needed_keys):
        print(f'{i+1}) {key}')




if __name__ == "__main__":
    main()