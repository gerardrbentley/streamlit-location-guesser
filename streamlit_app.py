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
        database="file:us_states.db?immutable=1",
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
    query = "SELECT name, stusps, AsGeoJSON(geometry) as 'geo', AsGeoJSON(Envelope(geometry)) as 'envelope', AsGeoJSON(PointOnSurface(geometry)) as 'random_point' FROM tl_2021_us_state WHERE division != 0 ORDER BY RANDOM() LIMIT 1;"
    cursor = conn.execute(query)
    result = cursor.fetchone()
    return result


def on_reset():
    st.session_state.pop(RANDOM_LOCATION)


RANDOM_LOCATION = "random_location"


def main():
    st.set_page_config(page_title="Spatial-lit", page_icon="🌎")
    st.title("Guess the State!")

    if RANDOM_LOCATION not in st.session_state:
        random_location = get_random_location()
        st.session_state[RANDOM_LOCATION] = random_location
    else:
        random_location = st.session_state.get(RANDOM_LOCATION)

    with st.expander("Hints", expanded=False):
        show_envelope = st.checkbox("Show Bounding Box of State (Envelope)", False)
        show_geo = st.checkbox("Show State Outline", False)

    random_point = json.loads(random_location["random_point"])
    lon, lat = random_point["coordinates"]
    m = folium.Map(
        location=[39.960, -95.537],
        zoom_start=4,
        tiles="Stamen Watercolor",
        attr="Stamen",
    )
    folium.Marker(
        [lat, lon], popup="Guess the State", tooltip="Guess the State"
    ).add_to(m)
    if show_geo:
        folium.GeoJson(random_location["geo"]).add_to(m)
    if show_envelope:
        folium.GeoJson(random_location["envelope"]).add_to(m)
    folium_static(m, width=725)
    with st.form("guess", True):
        guess = st.text_input("Guess the state (Full name or 2 Letter Abbrev)")
        has_guessed = st.form_submit_button("Submit Guess!")
    st.button("Get new Random Location", on_click=on_reset)
    if not has_guessed or len(guess) < 2:
        st.warning("Submit Guess with at least 2 characters to continue!")
        st.stop()

    clean_guess = guess.lower().strip()
    clean_abbrev = random_location["stusps"].lower()
    clean_name = random_location["name"].lower()
    st.header(clean_name.title())
    st.subheader(clean_abbrev.upper())
    if clean_guess == clean_abbrev or clean_guess == clean_name:
        st.balloons()
        st.success("You Guessed Correctly! 🥳")
    else:
        st.error("You Guessed Incorrectly. 😔")

    with st.expander("Random Location Details!", expanded=True):
        st.json(
            {
                k: v
                for k, v in zip(random_location.keys(), random_location)
                if k != "geometry" and k != "geo"
            }
        )


if __name__ == "__main__":
    main()
