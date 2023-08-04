import streamlit as st
import pandas as pd
import altair as alt
import psycopg2 as pg2
from typing import Tuple, List
import sql_queries
from dataclasses import dataclass

all_diets = ('Vegan', 'Vegetarian', 'Pescatarian', 'None')
all_meals = ('Dinner', 'Lunch', 'Breakfast', 'Snack')

all_meal_labels = ('Dinner', 'Lunch', 'Breakfast', 'Snack', 'Unspecified Meals')
all_diet_labels = ('Vegan', 'Vegetarian', 'Pescatarian', 'No diet')

@dataclass
class SearchTags:
    diets: Tuple[str] = tuple()
    include_unspecified_diets: bool = False
    meals: Tuple[str] = tuple()
    include_unspecified_meals: bool = False

def process_tags(tags: List[str]) -> SearchTags:
    tagsObject = SearchTags()
    for tag in tags:
        if tag in all_diets:
            tagsObject.diets += (tag,)
        elif tag in all_meals:
            tagsObject.meals += (tag,)
        elif tag == 'Unspecified Meals':
            tagsObject.include_unspecified_meals = True
        elif tag == 'No diet':
            tagsObject.diets += (tag,)
            tagsObject.include_unspecified_diets = True
    return tagsObject

allTags = process_tags(all_meal_labels+all_diet_labels)


def run_query(query_function,
              field_names: List[str],
              query_function_args: List = None,
              query_arguments: List = None
              ) -> pd.DataFrame:
    
    with pg2.connect(**st.secrets["postgres"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                query_function(*query_function_args),
                query_arguments
            )
            data_tuples = cur.fetchall()
            df = pd.DataFrame()
            for i,field in enumerate(field_names):
                df[field] = [row[i] for row in data_tuples]
            return df

def run_filtered_query(query_function, tagsObject: SearchTags, field_names: List[str], lim_results = True) -> pd.DataFrame:
    TOP_N = 8
    query_arguments = (tagsObject.meals, tagsObject.diets, TOP_N) if lim_results else (tagsObject.meals, tagsObject.diets) 
    return run_query(query_function, field_names,
                     query_function_args=[tagsObject.include_unspecified_meals, tagsObject.include_unspecified_diets],
                     query_arguments=query_arguments)

@st.cache_data
def get_top_ingredients(tagsObject: SearchTags) -> pd.DataFrame:
    df = run_filtered_query(sql_queries.top_ingredients_query, tagsObject, ["ingredient","num_recipes"])
    return df

@st.cache_data
def get_top_equipment(tagsObject: SearchTags) -> pd.DataFrame:
    df = run_filtered_query(sql_queries.top_equipment_query, tagsObject, ["equipment","num_recipes"])
    return df

@st.cache_data
def get_times(tagsObject: SearchTags) -> pd.DataFrame:
    df = run_filtered_query(sql_queries.times, tagsObject, ["prep_time","cook_time"], lim_results=False)
    return df

@st.cache_data
def num_recipes_selected(tagsObject: SearchTags) -> int:
    df = run_filtered_query(sql_queries.num_recipes_selected, tagsObject, ["num"], lim_results=False)
    return df.loc[0,"num"]

# Header
st.title('The Doctors Kitchen Dashboard')
st.subheader('An analysis of recipes from [The Doctor\'s Kitchen](https://thedoctorskitchen.com/)')

# Controls
tags = st.multiselect("Select Tags:",all_meal_labels+all_diet_labels, all_meal_labels+all_diet_labels)
searchTags = process_tags(tags)
st.write(num_recipes_selected(searchTags), "recipes selected")

# top ingredients chart
top_ingredients_df = get_top_ingredients(searchTags)
ingredients_chart = alt.Chart(top_ingredients_df,
                  title=alt.Title(
                      'What are the most used ingredients?'
                  ))\
    .mark_bar()\
    .encode(
        y=alt.Y('num_recipes', title='Number in recipes'),
        x=alt.X('ingredient', sort='-y', title=None),
        color=alt.Color('num_recipes', legend=None)
    )

# top equipment chart
top_equipment_df = get_top_equipment(searchTags)
equipment_chart = alt.Chart(top_equipment_df,
                  title=alt.Title(
                      'What are the most used equipment?'
                  ))\
    .mark_bar()\
    .encode(
        y=alt.Y('num_recipes', title='Number of recipes'),
        x=alt.X('equipment', sort='-y', title=None),
        color=alt.Color('num_recipes', legend=None)
    )

# time spent
times_df = get_times(searchTags)
prep_time_chart = alt.Chart(times_df).mark_bar().encode(
    x=alt.X("prep_time", bin=True),
    y='count()'
)
cook_time_chart = alt.Chart(times_df).mark_bar().encode(
    x=alt.X('cook_time', bin=True),
    y='count()'
)


# Charts
ingredients_tab, equipment_tab, time_tab = st.tabs(
    ["Ingredients", "Equipment", "Preparation and Cooking Time"]
)
ingredients_tab.altair_chart(ingredients_chart, use_container_width=True)
equipment_tab.altair_chart(equipment_chart, use_container_width=True)
col1, col2 = time_tab.columns(2)
col1.altair_chart(prep_time_chart, use_container_width=True)
col2.altair_chart(cook_time_chart, use_container_width=True)


# search for ingredients
def search_terms(search_string: str) -> List[str]:
    terms = search_string.strip().split(",")
    terms = [f"%{term.strip()}%" for term in terms]
    return terms


def get_search_results(ingredient_search_string: str) -> pd.DataFrame:
    terms = search_terms(ingredient_search_string)
    results = run_query(sql_queries.ingredient_search_query,
                        ["title", "url"],
                        [len(terms)],
                        terms)
    return results

st.subheader('Search for recipes by ingredients:')
ingredient_search = st.text_input('Enter ingredients separated by a commas',
             placeholder="e.g. olive oil, coriander, bean")
st.write(search_terms(ingredient_search))

results = get_search_results(ingredient_search)
st.write(len(results), "results found.")
st.dataframe(results, hide_index=True, use_container_width=True)