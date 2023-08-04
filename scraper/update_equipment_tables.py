from equipment_parser import load_equipment_dict, equipment_set, equipment_dict
from db_functions import Inserter, DatabaseIdFields
import secret
import psycopg2 as pg2
import pandas as pd
from typing import Set, List, Tuple
import log


new_equipment_synonyms = {
    "slow cooker": {"slow cooker", "crock pot"}
}


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

def delete_old_recipe_equipment_data(cur):
    cur.execute("DELETE FROM recipe_equipment RETURNING id;")

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
    for _,row in recipe_equipment.iterrows():
        inserter.insert_into_recipe_equipment(row['recipe_id'], row['equipment_name'])

def refresh_equipment(conn, cur):
    log.log('Re-parsing equipment in recipes')
    log.log('Reading method and ingredients...')
    method_df, ingredient_df = read_data_from_df(cur)
    log.log('parsing new equipment...')
    recipe_equipment = get_all_recipe_equipment(method_df, ingredient_df)
    log.log(f'{len(recipe_equipment)} recipe_equipment entries created')
    log.log('deleting old recipe_equipment rows...')
    delete_old_recipe_equipment_data(cur)
    num_rows_deleted = len(cur.fetchall())
    log.log(f'{num_rows_deleted} rows to be deleted from recipe_equipment')
    log.log('creating inserter object...')
    inserter = Inserter(cur)
    log.log('inserting new recipe_equipment rows...')
    insert_recipe_equipment(recipe_equipment, inserter)
    log.log('getting confirmation of changes:')

    print(f"Processing complete, changes will delete {num_rows_deleted} rows and insert {len(recipe_equipment)} rows in recipe_equipment")
    user_input = None
    while user_input not in ["y","n"]:
        user_input = input("Do you with to commit the changes [y/n]: ").lower()
    if user_input == "y":
        log.log('Changes committed')
        conn.commit()
    else:
        conn.rollback()
        log.log('Changes rolled back')
    log.log('done!')
    
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
            refresh_equipment(conn, cur)
            # comparison_test(cur)


if __name__ == "__main__":
    main()