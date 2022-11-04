import sqlite3
import os
import zipfile

filename = "WB_countries_Admin0_10m/WB_countries_Admin0_10m"
basename = "WB_countries_Admin0_10m"
table = "country"
charset = "utf-8"
database_filename = "countries.db"

try:
    os.unlink(database_filename)
except FileNotFoundError:
    pass

os.putenv("SPATIALITE_SECURITY", "relaxed")
conn = sqlite3.connect(database_filename)
conn.enable_load_extension(True)
conn.execute("SELECT load_extension('mod_spatialite')")
conn.execute("select InitSpatialMetadataFull(1)")
conn.execute(
    "SELECT ImportSHP(?, ?, ?, -1, 'geometry', 'fid');",
    (filename, table, charset),
)
conn.execute("DROP TABLE IF EXISTS spatial_ref_sys")
conn.execute("DROP TABLE IF EXISTS spatial_ref_sys_aux")
conn.commit()

conn.execute("vacuum")
conn.commit()
conn.close()
