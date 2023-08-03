from equipment_parser import load_equipment_dict, equipment_set, equipment_dict
from db_functions import Inserter, DatabaseIdFields
import secret
import psycopg2 as pg2


new_equipment_synonyms = {
    "slow cooker": {"slow cooker", "crock pot"}
}

def equipment_in_db(ids: DatabaseIdFields, equipment_name: str) -> bool:
    return equipment_name in ids.equipment_ids

def synonym_in_db(equipment_name: str, equipment_synonym: str) -> bool:
    return equipment_synonym in equipment_dict[equipment_name]

def get_new_equipment(new_equipment_synonyms):
    pass


def main():
    with pg2.connect(**secret.connection_kw_args) as conn:
        with conn.cursor() as cur:
            inserter = Inserter(cur)
            get_new_equipment(new_equipment_synonyms)


if __name__ == "__main__":
    main()