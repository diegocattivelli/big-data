import csv
import os

os.makedirs("data/musicbrainz", exist_ok=True)

def convertir(input_path, output_path, columnas, indices, filtro=None):
    count = 0
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(columnas)
        for line in fin:
            cols = line.rstrip("\n").split("\t")
            if filtro and not filtro(cols):
                continue
            fila = [cols[i] if i < len(cols) else "" for i in indices]
            fila = ["" if v == "\\N" else v for v in fila]
            writer.writerow(fila)
            count += 1
    print(f"{output_path}: {count} filas")

# --- ARTIST ---
# Filtro: solo personas (type=1) y grupos (type=2) con begin_year definido
# Descarta orquestas, personajes ficticios, coros y registros incompletos
convertir(
    "mbdump/artist",
    "data/musicbrainz/mb_artist.csv",
    ["id","mbid","name","sort_name","begin_year","end_year","type","area"],
    [0, 1, 2, 3, 4, 7, 10, 11],
    filtro=lambda c: len(c) > 11 and c[10] in ("1","2") and c[4] != "\\N"
)

# --- EVENT ---
# Sin filtro: se incluyen los 117.931 eventos completos
convertir(
    "mbdump/event",
    "data/musicbrainz/mb_event.csv",
    ["id","mbid","name","begin_year","begin_month","begin_day",
     "end_year","end_month","end_day","type","cancelled"],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
)

# --- EVENT_ALIAS ---
# Sin filtro: nombres alternativos de eventos
convertir(
    "mbdump/event_alias",
    "data/musicbrainz/mb_event_alias.csv",
    ["id","event_id","name","locale","type","sort_name"],
    [0, 1, 2, 3, 4, 5]
)

# --- ARTIST_TYPE ---
# Tabla de referencia: 1=Person, 2=Group, 3=Orchestra, 4=Choir, 5=Character, 6=Other
convertir(
    "mbdump/artist_type",
    "data/musicbrainz/mb_artist_type.csv",
    ["id","name"],
    [0, 1]
)

# --- EVENT_TYPE ---
# Tabla de referencia: 1=Concert, 2=Festival, 3=Stage performance, etc.
convertir(
    "mbdump/event_type",
    "data/musicbrainz/mb_event_type.csv",
    ["id","name"],
    [0, 1]
)

# --- AREA ---
# Sin filtro: todas las áreas (países, ciudades, regiones)
convertir(
    "mbdump/area",
    "data/musicbrainz/mb_area.csv",
    ["id","mbid","name"],
    [0, 1, 2]
)

# --- COUNTRY_AREA ---
# Tabla de referencia: lista de area_id que son países
convertir(
    "mbdump/country_area",
    "data/musicbrainz/mb_country_area.csv",
    ["area_id"],
    [0]
)

# --- L_ARTIST_EVENT ---
# Tabla de relación: vincula artistas con eventos
convertir(
    "mbdump/l_artist_event",
    "data/musicbrainz/mb_l_artist_event.csv",
    ["id","artist_id","event_id"],
    [0, 1, 2]
)

print("Listo")