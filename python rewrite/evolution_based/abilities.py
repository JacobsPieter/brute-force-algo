"""
Contains data for each ability of each class (this must still be updated by hand, sorry)
"""
import numpy as np

class Ability:
    def __init__(self, total_convert, conversions, scaling) -> None:
        self.total_convert: int = total_convert/100
        self.conversions: np.ndarray = np.divide(conversions,100)
        self.scaling = scaling if scaling == 'melee' or scaling == 'spell' else print('this is not a valid scaling')


warrior_abilities = {
    'melee': Ability(100, [100, 0, 0, 0, 0, 0], 'melee'),
    'bash': Ability(200, [170, 30, 0, 0, 0, 0], 'spell')
}


