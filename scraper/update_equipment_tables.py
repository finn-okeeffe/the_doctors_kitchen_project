from equipment_parser import load_equipment_dict, equipment_set, equipment_dict
from db_functions import Inserter, DatabaseIdFields
import secret
import psycopg2 as pg2
import pandas as pd
from typing import Set, List, Tuple


new_equipment_synonyms = {
    "slow cooker": {"slow cooker", "crock pot"}
}

def equipment_in_db(ids: DatabaseIdFields, equipment_name: str) -> bool:
    return equipment_name in ids.equipment_ids


def methods_from_db(cur) -> pd.DataFrame:
    cur.execute("SELECT id, method FROM recipe;")
    return pd.DataFrame(cur.fetchall(), columns=['recipe_id', 'method'])

def ingredients_from_db(cur) -> pd.DataFrame:
    # cur.execute("SELECT quantity")
    pass

def read_data(cur) -> Tuple[pd.DataFrame, pd.DataFrame]:
    load_equipment_dict()
    method_df = methods_from_db(cur)
    ingredient_df = ingredients_from_db(cur)
    return method_df, ingredient_df

def delete_old_equipment_data(cur):
    cur.execute("DELETE FROM recipe_equipment;")

def get_recipe_equipment(method: str, ingredients: pd.DataFrame) -> Set[str]:
    ingredient_strings = ingredients["quantity"] + " " + ingredients["unit"] + \
                            ingredients["name"] + " " + ingredients["preparation"]
    return equipment_set([method], list[ingredient_strings])

def get_all_recipe_equipment(method_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> pd.DataFrame:
    recipe_equipment = pd.DataFrame(columns=['recipe_id', 'equipment_name'])
    for row in method_df.iterrows():
        recipe_id = row['recipe_id']
        method_text = row['method']
        ingredients = ingredient_df.loc[ingredient_df['recipe_id'] == recipe_id]
        equipment = get_recipe_equipment(method_text, ingredients)
        pd.concat([recipe_equipment,
                   {'recipe_id': [recipe_id for e in equipment],
                    'equipment_id': equipment}])
    return recipe_equipment


def refresh_equipment_synonyms(cur):
    inserter = Inserter(cur)
    method_df, ingredient_df = read_data(cur)
    delete_old_equipment_data(cur)
    get_all_recipe_equipment(method_df, ingredient_df)
    
def testing_procedure(cur):
    print(methods_from_db(cur))


def main():
    with pg2.connect(**secret.connection_kw_args) as conn:
        with conn.cursor() as cur:
            testing_procedure(cur)


if __name__ == "__main__":
    main()