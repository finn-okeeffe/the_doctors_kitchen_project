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
    cur.execute("SELECT recipe_id, name, quantity, unit, preparation FROM ingredient;")
    return pd.DataFrame(cur.fetchall(),
                        columns=['recipe_id','name','quantity','unit','preparation'])

def read_data_from_df(cur) -> Tuple[pd.DataFrame, pd.DataFrame]:
    load_equipment_dict()
    method_df = methods_from_db(cur)
    ingredient_df = ingredients_from_db(cur)
    return method_df, ingredient_df

def delete_old_equipment_data(cur):
    cur.execute("DELETE FROM recipe_equipment;")

def ingredient_strings_from_df(ingredients: pd.DataFrame) -> List[str]:
    return list(ingredients["quantity"].astype(str) + " " + ingredients["unit"].astype(str) + " " +\
                ingredients["name"].astype(str) + " " + ingredients["preparation"].astype(str))

def get_recipe_equipment(method: str, ingredients: pd.DataFrame) -> Set[str]:
    ingredient_strings = ingredient_strings_from_df(ingredients)
    return equipment_set([method], list(ingredient_strings))

def get_all_recipe_equipment(method_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> pd.DataFrame:
    recipe_equipment = pd.DataFrame(columns=['recipe_id', 'equipment_name'])
    for _, row in method_df.iterrows():
        recipe_id = row['recipe_id']
        method_text = row['method']
        ingredients = ingredient_df.loc[ingredient_df['recipe_id'] == recipe_id]
        equipment = get_recipe_equipment(method_text, ingredients)
        new_rows = pd.DataFrame(
            {'recipe_id': [recipe_id for e in equipment],
             'equipment_name': [name for name in equipment]}
        )
        recipe_equipment = pd.concat([recipe_equipment,new_rows])
    return recipe_equipment

def insert_recipe_equipment(recipe_equipment: pd.DataFrame, inserter: Inserter):
    pass

def refresh_equipment_synonyms(cur):
    method_df, ingredient_df = read_data_from_df(cur)

    delete_old_equipment_data(cur)

    recipe_equipment = get_all_recipe_equipment(method_df, ingredient_df)

    inserter = Inserter(cur)
    insert_recipe_equipment(recipe_equipment, inserter)
    
def comparison_test(cur):
    # compares locally parsed equipment to those stored in the db
    method_df, ingredient_df = read_data_from_df(cur)
    req_df = get_all_recipe_equipment(method_df, ingredient_df)
    cur.execute("SELECT recipe_id, equipment.name FROM recipe_equipment INNER JOIN equipment ON recipe_equipment.equipment_id = equipment.id")
    req_db_df = pd.DataFrame(cur.fetchall(), columns=['recipe_id', 'equipment_name'])
    merged_df = req_df.merge(req_db_df, on=['recipe_id','equipment_name'], how='outer', indicator=True)
    print(merged_df.loc[merged_df['_merge'] != 'both'])


def main():
    with pg2.connect(**secret.connection_kw_args) as conn:
        with conn.cursor() as cur:
            comparison_test(cur)


if __name__ == "__main__":
    main()