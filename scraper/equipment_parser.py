from typing import List, Set
import psycopg2 as pg2
import secret
import log
from db_functions import equipment_dict_from_db, equipment_dict


backup_dict = {
    "pan": {"pan", "frypan"},
    "pot": {"pot", "boil", "saucepan"},
    "blender": {"blend"},
    "air fryer": {"air frier", "air fryer"},
    "toaster": {"toaster", "toast"},
    "oven": {"oven", "bake", "roast"},
    "cast-iron pan": {"cast iron pan"},
    "knife": {"slice", "sliced", "chop", "chopped", "dice", "diced", "cube", "cubed"},
    "chopping board": {"slice", "sliced", "chop", "chopped", "dice", "diced", "cube", "cubed", "board"},
    "measuring spoons": {"tbsp", "tsp"},
    "measuring cup": {"cup", "ml"},
    "scale": {"g", "gram", "grams"},
    "bowl": {"bowl"},
    "baking paper": {"baking paper", "baking parchment"},
    "fridge": {"fridge", "refridgerator"},
    "freezer": {"freezer"}
}



def load_equipment_dict():
    equipment_dict_from_db()
    

character_replacement_dict = {
    "-": " "
}

def equipment_set(method: List[str], ingredient_strings: List[str]) -> Set[int]:
    words = words_list(method) + words_list(ingredient_strings)

    equipment_set = set()
    for equipment_name, phrases in equipment_dict.items():

        for phrase in phrases:
            if phrase_in_str_list(phrase,words):
                equipment_set.add(equipment_name)
                log.log(f'Found equipment {equipment_name}')
                break
    
    return equipment_set

def string_to_standard_string(string: str) -> str:
    string = [character_replacement_dict[c] if c in character_replacement_dict else c for c in string]
    string = ''.join([c.lower() for c in string if c.isalnum() or c.isspace()])
    return string

def alnum_string_from_list(method: List[str]) -> str:
    alnum = []
    for step in method:
        alnum.append(string_to_standard_string(step))

    alnum_string = ' '.join(alnum)
    return alnum_string

def words_list(method: List[str]) -> List[str]:
    alnum_string = alnum_string_from_list(method)
    return list(alnum_string.split())

def phrase_in_str_list(phrase: str, str_list: List[str]) -> bool:
    phrase_list = phrase.split()
    l = len(phrase_list)
    for i in range(len(str_list)-l+1):
        if str_list[i:i+l] == phrase_list:
            return True
    return False



def testing_procedure():
    ingredients = [
        "onion 500 g diced",
        "olive oil",
        "milk 1 cup"
    ]

    method = [
        "Air fry the onion.",
        "Boil the milk in a saucepan."
    ]
    print(equipment_dict)
    print(equipment_set(method, ingredients))

if __name__ == "__main__":
    log.logging = True
    load_equipment_dict()
    testing_procedure()