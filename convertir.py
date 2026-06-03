import csv
import os

os.makedirs("data", exist_ok=True)

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

# artist — filtrado: solo type 1 (Person) y 2 (Group) con area definida
convertir(
    "mbdump/artist",
    "data/mb_artist.csv",
    ["id","mbid","name","sort_name","begin_year","end_year","type","area"],
    [0, 1, 2, 3, 4, 7, 10, 11],
    filtro=lambda c: len(c) > 11 and c[10] in ("1","2") and c[11] != "\\N"
)

# event
convertir(
    "mbdump/event",
    "data/mb_event.csv",
    ["id","mbid","name","begin_year","begin_month","begin_day",
     "end_year","end_month","end_day","type","cancelled"],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
)

# event_alias
convertir(
    "mbdump/event_alias",
    "data/mb_event_alias.csv",
    ["id","event_id","name","locale","type","sort_name"],
    [0, 1, 2, 3, 4, 5]
)

# artist_type
convertir(
    "mbdump/artist_type",
    "data/mb_artist_type.csv",
    ["id","name"],
    [0, 1]
)

# event_type
convertir(
    "mbdump/event_type",
    "data/mb_event_type.csv",
    ["id","name"],
    [0, 1]
)

# area
convertir(
    "mbdump/area",
    "data/mb_area.csv",
    ["id","mbid","name"],
    [0, 1, 2]
)

# country_area
convertir(
    "mbdump/country_area",
    "data/mb_country_area.csv",
    ["area_id"],
    [0]
)

# l_artist_event
convertir(
    "mbdump/l_artist_event",
    "data/mb_l_artist_event.csv",
    ["id","artist_id","event_id"],
    [0, 1, 2]
)

print("Listo")