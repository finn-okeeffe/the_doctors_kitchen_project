from typing import List, Tuple
from dataclasses import dataclass



def relevant_recipes(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    relevant_recipes_query = f"""
    WITH relevant_recipe AS (
        SELECT DISTINCT(recipe.id) FROM recipe
        LEFT JOIN meal ON meal.recipe_id = recipe.id
        LEFT JOIN diet ON diet.id = recipe.diet_id
        WHERE
            (meal.name IN %s {extra_meal_str}) AND
            (diet.name IN %s {extra_diet_str})
    )"""
    return relevant_recipes_query


def top_ingredients_query(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    relevant_recipes_definition = relevant_recipes(include_unspecified_meal, include_unspecified_diet)
    query = f"""
    {relevant_recipes_definition}
    SELECT
        ingredient.name,
        COUNT(relevant_recipe.id)
    FROM relevant_recipe
    INNER JOIN ingredient ON relevant_recipe.id = ingredient.recipe_id
    GROUP BY ingredient.name
    ORDER BY COUNT(relevant_recipe.id) DESC
    LIMIT %s;
    """
    return query

def top_equipment_query(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    relevant_recipes_definition = relevant_recipes(include_unspecified_meal, include_unspecified_diet)
    query = f"""
    {relevant_recipes_definition}

    SELECT
        equipment.name,
        COUNT(relevant_recipe.id)
    FROM relevant_recipe
    INNER JOIN recipe_equipment ON relevant_recipe.id = recipe_equipment.recipe_id
    INNER JOIN equipment ON recipe_equipment.equipment_id = equipment.id
    GROUP BY equipment.name
    ORDER BY COUNT(relevant_recipe.id) DESC
    LIMIT %s;
    """
    return query

def num_recipes_selected(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    relevant_recipes_definition = relevant_recipes(include_unspecified_meal, include_unspecified_diet)
    query = f"""
    {relevant_recipes_definition}

    SELECT COUNT(*) FROM relevant_recipe;
    """
    return query


def times(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    relevant_recipes_definition = relevant_recipes(include_unspecified_meal, include_unspecified_diet)
    query = f"""
    {relevant_recipes_definition}

    SELECT prep_time, cook_time FROM recipe
    INNER JOIN relevant_recipe ON recipe.id = relevant_recipe.id;
    """
    return query

def ingredient_search_query(num_terms: int) -> str:
    sub_query = "SELECT ingredient.recipe_id FROM ingredient WHERE ingredient.name LIKE %s"
    where_clause = f"WHERE recipe.id IN ({sub_query})" if num_terms > 0 else ""
    if num_terms > 1:
        for i in range(num_terms-1):
            where_clause = where_clause + f" AND recipe.id IN ({sub_query})"
    query = f"""
        SELECT recipe.title, recipe.url, diet.name FROM recipe
        INNER JOIN diet ON diet.id = recipe.diet_id
        {where_clause}
    """
    return query