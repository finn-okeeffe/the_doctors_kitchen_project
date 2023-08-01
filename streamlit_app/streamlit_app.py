import streamlit as st
import pandas as pd
import altair as alt
import psycopg2 as pg2
import secret
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

@st.cache_data
def get_top_ingredients(tagsObject: SearchTags) -> pd.DataFrame:
    TOP_N = 8
    
    with pg2.connect(database=secret.database_name, user=secret.username, password=secret.password) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql_queries.top_ingredients_query(
                    tagsObject.include_unspecified_meals,
                    tagsObject.include_unspecified_diets
                ),
                (tagsObject.meals, tagsObject.diets, TOP_N)
            )
            data_tuples = cur.fetchall()
            df = pd.DataFrame()
            df['ingredient'] = [row[0] for row in data_tuples]
            df['num_recipes'] = [row[1] for row in data_tuples]
            return df


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

# Header
st.title('The Doctors Kitchen Dashboard')
st.subheader('An analysis of recipes from [The Doctor\'s Kitchen](https://thedoctorskitchen.com/)')

# Controls
tags = st.multiselect("Select Tags:",all_meal_labels+all_diet_labels, all_meal_labels+all_diet_labels)

# top ingredients chart
top_ingredients_df = get_top_ingredients(process_tags(tags))
chart = alt.Chart(top_ingredients_df,
                  title=alt.Title(
                      'What are the most used ingredients?'
                  ))\
    .mark_bar()\
    .encode(
        y=alt.Y('num_recipes', title='Appearance in recipes'),
        x=alt.X('ingredient', sort='-y', title=None),
        color='num_recipes'
    )
st.altair_chart(chart, use_container_width=True)

st.text('test')