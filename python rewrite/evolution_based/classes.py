import human_readable_stat_names_and_indices as stat_indices

import itertools


class Item:
    def __init__(self, item: dict) -> None:
        self.name = item['name']
        self.id = item['id']
        self.type = item['type']
        self.__stats = self.__get_item_stats_from_dict(item)
        self.__skillpoints_requirements = tuple(self.get_stats_list(['strength_requirement', 'dexterity_requirement', 'intelligence_requirement', 'defense_requirement', 'agility_requirement']))
        self.__skillpoints = tuple(self.get_stats_list(['strength', 'dexterity', 'intelligence', 'defense', 'agility']))
    
    def __str__(self):
        return f'{self.name}, {self.__stats}'
    
    def __get_item_stats_from_dict(self, item: dict) -> np.ndarray:
        ordered_stats = sorted(stat_indices.STAT_NAMES.values())
        stats = np.array([item.get(stat_key, 0) for stat_key in ordered_stats])
        return stats

    
    def get_skillpoints_requirements(self) -> tuple:
        return self.__skillpoints_requirements

    def get_skillpoints(self) -> tuple:
        return self.__skillpoints
    
    def get_all_stats(self):
        return self.__stats

    def get_stat(self, stat: str):
        value = self.__stats[stat_indices.get_stat_pos(stat)]
        return value
    
    def get_stats_list(self, stats: list[str]):
        values = [self.__stats[stat_indices.get_stats_pos_list(stats)[i]] for i in range(len(stats))]
        return values


class Gear(Item):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.category = item['category']
        self.majorid = item.get('majorid', '')

    def get_majorid(self):
        return self.majorid


class Powderable(Gear):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.powderslots = self.get_stat('powder_slots')


class Armour(Powderable):
    def __init__(self, item: dict) -> None:
        super().__init__(item)


class Accessory(Gear):
    def __init__(self, item: dict) -> None:
        super().__init__(item)


class Weapon(Powderable):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        match self.type:
            case 'bow':
                self.character_class = 'Archer'
            case 'spear':
                self.character_class = 'Warrior'
            case 'wand':
                self.character_class = 'Mage'
            case 'dagger':
                self.character_class = 'Assassin'
            case 'relik':
                self.character_class = 'Shaman'
            case _:
                raise ValueError
        self.powderslots = self.get_stat('powder_slots')



class Tome(Item):
    def __init__(self, item: dict) -> None:
        super().__init__(item)



class Build:
    def __init__(self, armour: list[Armour], accessories: list[Accessory], weapon: Weapon, tomes: list[list[Tome]]):
        self.armour = armour
        self.helmet, self.chestplate, self.leggings, self.boots = tuple(self.armour)
        self.accessories = accessories
        self.ring1, self.ring2, self.bracelet, self.necklace = tuple(self.accessories)
        self.weapon = weapon

        self.tomes = tomes
        self.armour_tomes: list[Tome] = self.tomes[0]
        self.weapon_tomes: list[Tome] = self.tomes[1]
        self.marathon_tomes: list[Tome] = self.tomes[2]
        self.expertise_tomes: list[Tome] = self.tomes[3]
        self.mysticism_tomes: list[Tome] = self.tomes[4]
        self.lootrunning_tome: Tome = self.tomes[5][0]
        self.guild_tome: Tome = self.tomes[6][0]

        self.skill_points = [0, 0, 0, 0, 0]
        self.skill_points_applied = [0, 0, 0, 0, 0]

        self.validated = False
        self.__fitness = 0
        self.__calculated_build_stats = False
        self.__calculated_skill_point_requirements = False
    
    def set_item(self, item: Armour | Accessory | Weapon | Tome, position=0):
        match item.type:
            case 'weapon':
                if isinstance(item, Weapon):
                    self.weapon = item
                if isinstance(item, Tome):
                    self.weapon_tomes[position] = item
            case 'helmet':
                if isinstance(item, Armour):
                    self.helmet = item
            case 'chestplate':
                if isinstance(item, Armour):
                    self.chestplate = item
            case 'leggings':
                if isinstance(item, Armour):
                    self.leggings = item
            case 'boots':
                if isinstance(item, Armour):
                    self.boots = item
            case 'ring':
                if isinstance(item, Accessory):
                    if position == 0:
                        self.ring1 = item
                    else:
                        self.ring2 = item
            case 'bracelet':
                if isinstance(item, Accessory):
                    self.bracelet = item
            case 'necklace':
                if isinstance(item, Accessory):
                    self.necklace = item
            case 'armour':
                if isinstance(item, Tome):
                    self.armour_tomes[position] = item
            case 'marathon':
                if isinstance(item, Tome):
                    self.marathon_tomes[position] = item
            case 'expertise':
                if isinstance(item, Tome):
                    self.expertise_tomes[position] = item
            case 'mysticism':
                if isinstance(item, Tome):
                    self.mysticism_tomes[position] = item
            case _:
                pass
        self.armour = [self.helmet, self.chestplate, self.leggings, self.boots]
        self.accessories = [self.ring1, self.ring2, self.bracelet, self.necklace]
        self.tomes = [self.armour_tomes, self.weapon_tomes, self.marathon_tomes, self.expertise_tomes, self.mysticism_tomes, [self.lootrunning_tome], [self.guild_tome]]
        

    def __str__(self):
        return f'{self.get_all_items()}'
    
    def get_name(self):
        return f'{self.get_all_items()}'
    
    def get_all_gear(self):
        return list(itertools.chain(self.armour, self.accessories, [self.weapon]))
    
    def get_all_tomes(self):
        return list(itertools.chain(self.tomes))
    
    def get_all_tomes_flattened(self):
        return list(itertools.chain.from_iterable(self.tomes))

    def get_all_items(self):
        return list(itertools.chain(self.armour, self.accessories, [self.weapon], self.get_all_tomes_flattened()))
    
    def get_combined_build_stats(self) -> np.ndarray:
        if self.__calculated_build_stats:
            return self.__combined_build_stats
        
        self.__calculated_build_stats = True
        self.__combined_build_stats = self.__combine_build_stats()
        return self.__combined_build_stats
    
    def get_stat_from_combined_stats(self, stat: str):
        value = self.get_combined_build_stats()[stat_indices.get_stat_pos(stat)]
        return value
    
    def get_stats_from_combined_stats(self, stats: list[str]):
        values = [self.get_combined_build_stats()[stat_indices.get_stats_pos_list(stats)[i]] for i in range(len(stats))]
        return values
    
    def __combine_build_stats(self) -> np.ndarray:
        combined_stats = np.zeros_like(self.helmet.get_all_stats())
        for item in list(itertools.chain(self.armour, self.accessories, [self.weapon], itertools.chain.from_iterable(self.tomes))):
            combined_stats = np.add(combined_stats, item.get_all_stats())
        return combined_stats
    
    def get_fitness(self):
        return self.__fitness

    def set_fitness(self, new_fitness):
        self.__fitness = new_fitness
    
    def get_combined_skill_point_requirements(self):
        if self.__calculated_skill_point_requirements:
            return self.__combined_skill_point_requirements
        self.__combined_skill_point_requirements = self.__combine_skill_point_requirements()
        return self.__combined_skill_point_requirements
        
    def __combine_skill_point_requirements(self) -> tuple:
        str_req, dex_req, int_req, def_req, agi_req = 0, 0, 0, 0, 0
        for item in self.get_all_gear():
            str_req = max([item.get_skillpoints_requirements()[0], str_req])
            dex_req = max([item.get_skillpoints_requirements()[1], dex_req])
            int_req = max([item.get_skillpoints_requirements()[2], int_req])
            def_req = max([item.get_skillpoints_requirements()[3], def_req])
            agi_req = max([item.get_skillpoints_requirements()[4], agi_req])
        self.__calculated_skill_point_requirements = True
        return (str_req, dex_req, int_req, def_req, agi_req)

    def set_build_validated(self, value: bool):
        self.validated = value



