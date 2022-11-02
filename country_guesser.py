import json
import streamlit as st
import logging
import sqlite3
from streamlit_folium import folium_static
import folium


log = logging.getLogger("streamlit")
log.setLevel(logging.DEBUG)


@st.experimental_singleton
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        database="file:countries.db?immutable=1",
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


def get_random_location() -> sqlite3.Row:
    conn = get_connection()
    query = "SELECT *, AsGeoJSON(geometry) as 'geo', AsGeoJSON(Envelope(geometry)) as 'envelope', AsGeoJSON(PointOnSurface(geometry)) as 'random_point' FROM country WHERE type != 'Dependency' and type != 'Lease' ORDER BY RANDOM() LIMIT 1;"
    cursor = conn.execute(query)
    result = cursor.fetchone()
    return result

def on_reset():
    st.session_state.pop(RANDOM_LOCATION)


RANDOM_LOCATION = "random_location"

def main():
    st.set_page_config(page_title="Spatial-lit", page_icon="🌎")
    st.title("Guess the Country! 🌍")

    if RANDOM_LOCATION not in st.session_state:
        random_location = get_random_location()
        st.session_state[RANDOM_LOCATION] = random_location
    else:
        random_location = st.session_state.get(RANDOM_LOCATION)

    with st.expander("Hints", expanded=False):
        show_envelope = st.checkbox("Show Bounding Box of Country (Envelope)", False)
        show_geo = st.checkbox("Show Country Outline", False)

    random_point = json.loads(random_location["random_point"])
    lon, lat = random_point["coordinates"]
    m = folium.Map(
        location=[0, 0],
        zoom_start=1,
        tiles="Stamen Watercolor",
        attr="Stamen",
    )
    folium.Marker(
        [lat, lon], popup="Guess the Country", tooltip="Guess the Country"
    ).add_to(m)
    if show_geo:
        folium.GeoJson(random_location["geo"]).add_to(m)
    if show_envelope:
        folium.GeoJson(random_location["envelope"]).add_to(m)
    folium_static(m, width=725)
    with st.form("guess", True):
        guess = st.text_input("Guess the country (Full Name, Translated Name, 2 or 3 Letter ISO/FIPS Abbrev)")
        has_guessed = st.form_submit_button("Submit Guess!")
    st.button("Get new Random Location", on_click=on_reset)
    if not has_guessed or len(guess) < 2:
        st.warning("Submit Guess with at least 2 characters to continue!")
        st.stop()

    clean_guess = guess.lower().strip()
    st.header(random_location["name_en"])
    st.subheader(random_location["fips_10_"])

    did_win = False
    for column in NAME_COLUMNS:
        clean_value = random_location[column].lower().strip()
        if clean_value == clean_guess:
            st.balloons()
            st.success("You Guessed Correctly! 🥳")
            did_win = True
            break
    if not did_win:
        st.error("You Guessed Incorrectly. 😔")

    with st.expander("Random Location Details!", expanded=True):
        st.json(
            {
                k: v
                for k, v in zip(random_location.keys(), random_location)
                if k != "geometry" and k != "geo"
            }
        )

NAME_COLUMNS = (
    "formal_en",
    "formal_fr",
    "fips_10_",
    "iso_a2",
    "iso_a3",
    "iso_a3_eh",
    "wb_a2",
    "wb_a3",
    "name_ar",
    "name_bn",
    "name_de",
    "name_en",
    "name_es",
    "name_fr",
    "name_el",
    "name_hi",
    "name_hu",
    "name_id",
    "name_it",
    "name_ja",
    "name_ko",
    "name_nl",
    "name_pl",
    "name_pt",
    "name_ru",
    "name_sv",
    "name_tr",
    "name_vi",
    "name_zh",
    "wb_name",
)


if __name__ == "__main__":
    main()
