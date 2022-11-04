import json
import streamlit as st
import logging
import sqlite3
from streamlit_folium import folium_static
import folium
import pandas as pd
from pathlib import Path
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

log = logging.getLogger("streamlit")
log.setLevel(logging.DEBUG)


@st.experimental_singleton
def get_connection(filename: str) -> sqlite3.Connection:
    conn = sqlite3.connect(
        database=f"file:{filename}?immutable=1",
        timeout=5,
        detect_types=0,
        isolation_level="DEFERRED",
        check_same_thread=False,
        factory=sqlite3.Connection,
        cached_statements=128,
        uri=True,
    )
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    conn.load_extension("mod_spatialite")
    return conn


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    SRC: https://github.com/tylerjrichards/st-filter-dataframe

    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

@st.experimental_singleton
def get_all_locations(filename: str, table: str):
    conn = get_connection(filename)
    query = f"SELECT *, AsGeoJSON(geometry) as 'json_geom' FROM {table};"
    cursor = conn.execute(query)
    result = cursor.fetchall()
    return result


def main():
    st.set_page_config(page_title="Spatial-lit", page_icon="🌎")
    st.title("Spatialite Viewer!")
    db_files =[str(x) for x in Path('.').glob('*.db')]
    filename = st.selectbox("DB File", db_files)
    table = 'country' if 'countr' in filename else 'tl_2021_us_state'
    all_locations = get_all_locations(filename, table)
    all_geoms = [json.loads(row["json_geom"]) for row in all_locations]
    m = folium.Map(
        location=[0, 0],
        zoom_start=1,
        tiles="Stamen Watercolor",
        attr="Stamen",
    )
    for geom in all_geoms:
        folium.GeoJson(geom).add_to(m)
    folium_static(m, width=725)

    st.dataframe(filter_dataframe(pd.DataFrame(all_locations, columns=all_locations[0].keys())))


if __name__ == "__main__":
    main()
