# Streamlit Country Guessing Game

Using Streamlit + Sqlite + Spatialite to make Geography Guessing Games

- [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gerardrbentley-streamlit-state-guesser-streamlit-app-owl1sn.streamlit.app/) USA State Guessing 🇺🇸
- [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://country-guesser.streamlit.app/) International Country Guessing 🌏

## Local Setup

Assumes working python installation and some command line knowledge ([install python with conda guide](https://tech.gerardbentley.com/python/beginner/2022/01/29/install-python.html)).

Assumes working [brew](https://brew.sh/) installation if working on mac.

Haven't tried on Windows...

### Initialize codebase and dependencies

Only needs to happen once

```sh
# Download Codebase / Repository
git clone git@github.com:gerardrbentley/streamlit-location-guesser.git
cd streamlit-location-guesser
# Install python libraries or use your preferred virtualenv manager
python -m venv venv
. ./venv/bin/activate
python -m pip install -r requirements.txt

# Download Spatialite Mac
brew install spatialite-tools
# M1 Mac extra step to act like old homebrew
sudo ln -s /opt/homebrew/lib/mod_spatialite.dylib /usr/local/lib/mod_spatialite.dylib

# Download Spatialite Linux
apt-get install libsqlite3-mod-spatialite
```

### Run the applications

- `python make_states_db.py`: Will try to fetch 2021 US Census state boundaries shapefile zip and load it into a SQLite database file
- `python make_countries_db.py`: Will try to take directory of World Bank [World Boundaries GeoDatabase](https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries) shapefiles and load it into a SQLite database file
  - This source doesn't offer obvious direct download; download via browser and unzip via file browser or command line

## Data Sources

Countries of the World:

- World Bank: [World Boundaries GeoDatabase](https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries)

United States States:

- US Census: [States](https://www2.census.gov/geo/tiger/TIGER2021/STATE/)