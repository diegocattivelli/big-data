import csv
import os

os.makedirs("data/musicbrainz", exist_ok=True)

MB = "mbdump"  # carpeta del dump de MusicBrainz ya descomprimido

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

# ============================================================
# ESQUEMA DE MUSICBRAINZ - leer antes de tocar los indices
# Las tablas de relacion l_<a>_<b> tienen el formato:
#     id, link, entity0, entity1, edits_pending, last_updated, ...
# => las entidades (los ids que sirven) estan en los indices 2 y 3, NO en 1 y 2.
# En l_artist_event:  entity0 = artist (idx 2),  entity1 = event (idx 3).
# Antes se usaba [0,1,2], que guardaba id, link y artist, y PERDIA el event_id real.
# Eso rompia la union artista<->evento. Corregido a [0,2,3] aca abajo.
# ============================================================

# --- ARTIST ---
# Filtro (se mantiene a proposito): solo personas (type=1) y grupos (type=2) con
# begin_year definido. Solo interesan cantantes y bandas; begin_year nulo descarta
# artistas sin registro formal y ademas mantiene el CSV bajo el limite de GitHub.
convertir(
    f"{MB}/artist",
    "data/musicbrainz/mb_artist.csv",
    ["id","mbid","name","sort_name","begin_year","end_year","type","area"],
    [0, 1, 2, 3, 4, 7, 10, 11],
    filtro=lambda c: len(c) > 11 and c[10] in ("1","2") and c[4] != "\\N"
)

# --- EVENT --- (ok, se salta idx 9 = time)
convertir(
    f"{MB}/event",
    "data/musicbrainz/mb_event.csv",
    ["id","mbid","name","begin_year","begin_month","begin_day",
     "end_year","end_month","end_day","type","cancelled"],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
)

# --- EVENT_ALIAS --- (CORREGIDO)
# esquema: id, event, name, locale, edits_pending, last_updated, type, sort_name, ...
# Antes [0,1,2,3,4,5] tomaba edits_pending como "type" y last_updated como "sort_name".
convertir(
    f"{MB}/event_alias",
    "data/musicbrainz/mb_event_alias.csv",
    ["id","event_id","name","locale","type","sort_name"],
    [0, 1, 2, 3, 6, 7]
)

# --- ARTIST_TYPE --- (ref: 1=Person, 2=Group, 3=Orchestra, 4=Choir, 5=Character, 6=Other)
convertir(
    f"{MB}/artist_type",
    "data/musicbrainz/mb_artist_type.csv",
    ["id","name"],
    [0, 1]
)

# --- EVENT_TYPE --- (ref: 1=Concert, 2=Festival, ...)
convertir(
    f"{MB}/event_type",
    "data/musicbrainz/mb_event_type.csv",
    ["id","name"],
    [0, 1]
)

# --- AREA --- (paises, ciudades, regiones)
convertir(
    f"{MB}/area",
    "data/musicbrainz/mb_area.csv",
    ["id","mbid","name"],
    [0, 1, 2]
)

# --- COUNTRY_AREA --- (lista de area_id que son paises)
convertir(
    f"{MB}/country_area",
    "data/musicbrainz/mb_country_area.csv",
    ["area_id"],
    [0]
)

# --- L_ARTIST_EVENT --- (CORREGIDO: [0,2,3] = id, artist(entity0), event(entity1))
convertir(
    f"{MB}/l_artist_event",
    "data/musicbrainz/mb_l_artist_event.csv",
    ["id","artist_id","event_id"],
    [0, 2, 3]
)

# ============================================================
# TABLAS NUEVAS (para ubicacion de eventos y fecha de festivales)
# ============================================================

# --- PLACE --- (lugares / venues)
# esquema: id, gid, name, type, address, area, coordinates, comment, ...
# coordinates viene como "(lat,lon)" cuando existe.
convertir(
    f"{MB}/place",
    "data/musicbrainz/mb_place.csv",
    ["id","mbid","name","type","area","coordinates"],
    [0, 1, 2, 3, 5, 6]
)

# --- L_EVENT_PLACE --- (evento -> lugar)  entity0=event, entity1=place
convertir(
    f"{MB}/l_event_place",
    "data/musicbrainz/mb_l_event_place.csv",
    ["id","event_id","place_id"],
    [0, 2, 3]
)

# --- L_AREA_AREA --- (jerarquia de areas)  entity0=area padre, entity1=area hijo
# sirve para subir de ciudad -> pais
convertir(
    f"{MB}/l_area_area",
    "data/musicbrainz/mb_l_area_area.csv",
    ["id","parent_area_id","child_area_id"],
    [0, 2, 3]
)

# --- SERIES --- (para enganchar el musicbrainz_series_id de Wikidata via mbid/gid)
# esquema tipico: id, gid, name, comment, type, ...
# OJO: el orden de columnas de series cambio entre versiones del dump.
# Verificar con:  head -2 mbdump/series   y ajustar el indice de "type" si hace falta.
convertir(
    f"{MB}/series",
    "data/musicbrainz/mb_series.csv",
    ["id","mbid","name","type"],
    [0, 1, 2, 4]
)

# --- L_EVENT_SERIES --- (evento -> serie)  entity0=event, entity1=series
convertir(
    f"{MB}/l_event_series",
    "data/musicbrainz/mb_l_event_series.csv",
    ["id","event_id","series_id"],
    [0, 2, 3]
)

print("Listo")
