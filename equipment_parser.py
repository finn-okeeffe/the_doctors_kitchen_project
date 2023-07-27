from typing import List, Tuple, Set

equipment_dict = {
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
    "measuring cup": {"cup", "cups", "ml"},
    "scale": {"g", "gram", "grams"},
    "bowl": {"bowl"},
    "baking paper": {"baking paper", "baking parchment"},
    "fridge": {"fridge", "refridgerator"},
    "freezer": {"freezer", "freeze"},
    "microwave": {"microwave"}
}

character_replacement_dict = {
    "-": " "
}

def equipment_set(method: List[str], ingredient_strings: List[str]) -> List[str]:
    words = method_words_list(method)

    equipment_set_object = set()
    for equipment, phrases in equipment_dict.items():

        for phrase in phrases:
            if phrase_in_str_list(phrase,words) or phrase_in_ingredients(phrase, ingredient_strings):
                equipment_set_object.add(equipment)
                break
    
    return equipment_set_object

def string_to_standard_string(string: str) -> str:
    string = [character_replacement_dict[c] if c in character_replacement_dict else c for c in string]
    string = ''.join([c.lower() for c in string if c.isalnum() or c.isspace()])
    return string

def method_alnum_string_from_list(method: List[str]) -> str:
    method_alnum = []
    for step in method:
        method_alnum.append(string_to_standard_string(step))

    method_alnum_string = ' '.join(method_alnum)
    return method_alnum_string

def method_words_list(method: List[str]) -> List[str]:
    method_string = method_alnum_string_from_list(method)
    return list(method_string.split())

def phrase_in_str_list(phrase: str, str_list: List[str]) -> bool:
    phrase_list = phrase.split()
    l = len(phrase_list)
    for i in range(len(str_list)-l+1):
        if str_list[i:i+l] == phrase_list:
            return True
    return False

def phrase_in_ingredients(phrase: str, ingredients_string_list: List[str]) -> bool:
    split_set: Set[str] = set()
    for s in ingredients_string_list:
        for word in s.split():
            split_set.add(word)

    return phrase in split_set



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

    print(equipment_set(method, ingredients))

if __name__ == "__main__":
    testing_procedure()