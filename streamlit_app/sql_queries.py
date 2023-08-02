from typing import List

def top_ingredients_query(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    WITH relevant_recipe AS (
        SELECT recipe.id FROM recipe
        LEFT JOIN meal ON meal.recipe_id = recipe.id
        LEFT JOIN diet ON diet.id = recipe.diet_id
        WHERE
            (meal.name IN %s {extra_meal_str}) AND
            (diet.name IN %s {extra_diet_str})
        GROUP BY recipe.id
    )

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
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    WITH relevant_recipe AS (
        SELECT recipe.id FROM recipe
        LEFT JOIN meal ON meal.recipe_id = recipe.id
        LEFT JOIN diet ON diet.id = recipe.diet_id
        WHERE
            (meal.name IN %s {extra_meal_str}) AND
            (diet.name IN %s {extra_diet_str})
        GROUP BY recipe.id
    )

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


def times(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    SELECT prep_time, cook_time FROM recipe
    LEFT JOIN meal ON meal.recipe_id = recipe.id
    LEFT JOIN diet ON diet.id = recipe.diet_id
    WHERE
        (meal.name IN %s {extra_meal_str}) AND
        (diet.name IN %s {extra_diet_str})
    GROUP BY recipe.id;
    """
    return query

def ingredient_search_query(num_terms: int) -> str:

    sub_query = "SELECT recipe_id FROM ingredient WHERE name LIKE %s"

    where_clause = f"WHERE id IN ({sub_query})" if num_terms > 0 else ""

    if num_terms > 1:
        for i in range(num_terms-1):
            where_clause = where_clause + f" AND id IN ({sub_query})"

    query = f"""
        SELECT title, url FROM recipe
        {where_clause}
    """
    return query