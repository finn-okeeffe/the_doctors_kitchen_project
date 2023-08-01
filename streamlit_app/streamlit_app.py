import streamlit as st
import pandas as pd
import altair as alt
import psycopg2 as pg2
import secret
from typing import List

@st.cache_data
def get_top_ingredients(meals: List[str], diets: List[int]) -> pd.DataFrame:
    TOP_N = 8
    with pg2.connect(database=secret.database_name, user=secret.username, password=secret.password) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT ingredient.name, COUNT(recipe.id) FROM ingredient
                INNER JOIN recipe ON recipe.id = ingredient.recipe_id
                GROUP BY ingredient.name
                ORDER BY COUNT(recipe.id) DESC
                LIMIT %s""",
                (TOP_N,)
            )
            data_tuples = cur.fetchall()
            df = pd.DataFrame()
            df["ingredient"] = [row[0] for row in data_tuples]
            df["num_recipes"] = [row[1] for row in data_tuples]
            return df

st.title("The Doctors Kitchen Dashboard")
st.subheader("An analysis of recipes from [The Doctor's Kitchen](https://thedoctorskitchen.com/)")


top_ingredients_df = get_top_ingredients(None, None)

# st.write("## What are the most used ingredients?")
chart = alt.Chart(top_ingredients_df,
                  title=alt.Title(
                      "What are the most used ingredients?"
                  ))\
    .mark_bar()\
    .encode(
        y=alt.Y("num_recipes", title="Appearance in recipes"),
        x=alt.X("ingredient", sort="-y", title=None),
        color="num_recipes"
    )
st.altair_chart(chart, use_container_width=True)

