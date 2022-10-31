import sqlite3
import os
from urllib.request import urlopen

table_name = "tl_2021_us_state"
raw_file_name = f"{table_name}.zip"

if not os.path.isfile(raw_file_name):
    print("Downloading shapefile zip")
    with urlopen("https://www2.census.gov/geo/tiger/TIGER2021/STATE/tl_2021_us_state.zip") as reader:
        with open(raw_file_name, 'wb') as writer:
            writer.write(reader.read())

file_name = "us_states.db"
try:
    os.unlink(file_name)
except FileNotFoundError:
    pass

os.putenv("SPATIALITE_SECURITY", "relaxed")
conn = sqlite3.connect(file_name)
conn.enable_load_extension(True)
conn.execute("SELECT load_extension('mod_spatialite')")
conn.execute("select InitSpatialMetadataFull(1)")
conn.execute(
    "SELECT ImportZipSHP(?, ?, ?, 'utf-8');",
    (f"{table_name}.zip", table_name, table_name),
)
conn.execute("DROP TABLE IF EXISTS spatial_ref_sys")
conn.execute("DROP TABLE IF EXISTS spatial_ref_sys_aux")
conn.commit()

conn.execute("vacuum")
conn.commit()
conn.close()
