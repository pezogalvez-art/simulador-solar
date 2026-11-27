import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

# Catálogo nacional de estaciones oficiales SENAMHI por Departamento - Ciudad (Perú)
CATALOGO_PERU = {
    "Amazonas - Chachapoyas":      {"cod": "105012", "estacion": "Estación Chachapoyas", "altitud": "2,335 msnm", "radMax": 880, "iuv": 12, "cielo": "Parcialmente nublado"},
    "Áncash - Huaraz":             {"cod": "110025", "estacion": "Estación Santiago Antúnez de Mayolo", "altitud": "3,052 msnm", "radMax": 970, "iuv": 14, "cielo": "Despejado / Sierra"},
    "Apurímac - Abancay":          {"cod": "113045", "estacion": "Estación Abancay", "altitud": "2,378 msnm", "radMax": 950, "iuv": 13, "cielo": "Despejado / Valle interandino"},
    "Arequipa - Arequipa":         {"cod": "114002", "estacion": "Estación La Pampilla (Arequipa)", "altitud": "2,325 msnm", "radMax": 1020, "iuv": 15, "cielo": "Despejado permanente"},
    "Ayacucho - Huamanga":         {"cod": "113018", "estacion": "Estación Huamanga", "altitud": "2,761 msnm", "radMax": 960, "iuv": 14, "cielo": "Soleado / Sierra Central"},
    "Cajamarca - Cajamarca":       {"cod": "107015", "estacion": "Estación Augusto Weberbauer", "altitud": "2,750 msnm", "radMax": 920, "iuv": 13, "cielo": "Nubosidad parcial"},
    "Callao - Callao":             {"cod": "112194", "estacion": "Estación Jorge Chávez (Callao)", "altitud": "13 msnm", "radMax": 740, "iuv": 8, "cielo": "Nublado costero"},
    "Cusco - Cusco":               {"cod": "113030", "estacion": "Estación Granja Kayra (Cusco)", "altitud": "3,399 msnm", "radMax": 980, "iuv": 14, "cielo": "Despejado / Sierra Sur"},
    "Huancavelica - Huancavelica": {"cod": "112088", "estacion": "Estación Acobamba / Huancavelica", "altitud": "3,676 msnm", "radMax": 975, "iuv": 14, "cielo": "Frío seco / Alta radiación"},
    "Huánuco - Huánuco":           {"cod": "109014", "estacion": "Estación Huánuco", "altitud": "1,894 msnm", "radMax": 910, "iuv": 12, "cielo": "Templado soleado"},
    "Ica - Ica":                   {"cod": "112046", "estacion": "Estación San José (Ica)", "altitud": "406 msnm", "radMax": 940, "iuv": 12, "cielo": "Soleado / Desértico"},
    "Junín - Huancayo":            {"cod": "111032", "estacion": "Estación Huayao (Huancayo)", "altitud": "3,313 msnm", "radMax": 970, "iuv": 14, "cielo": "Soleado / Valle del Mantaro"},
    "La Libertad - Trujillo":      {"cod": "108011", "estacion": "Estación Trujillo", "altitud": "34 msnm", "radMax": 810, "iuv": 10, "cielo": "Despejado a parcial costero"},
    "Lambayeque - Chiclayo":       {"cod": "106008", "estacion": "Estación Lambayeque", "altitud": "29 msnm", "radMax": 840, "iuv": 11, "cielo": "Soleado / Costa Norte"},
    "Lima - Lima":                 {"cod": "112193", "estacion": "Estación Alexander Von Humboldt", "altitud": "240 msnm", "radMax": 750, "iuv": 8, "cielo": "Nublado parcial / Costero"},
    "Loreto - Iquitos":            {"cod": "104017", "estacion": "Estación Moronacocha (Iquitos)", "altitud": "106 msnm", "radMax": 820, "iuv": 10, "cielo": "Nubosidad variable tropical"},
    "Loreto - Yurimaguas":         {"cod": "104029", "estacion": "Estación Yurimaguas", "altitud": "184 msnm", "radMax": 835, "iuv": 11, "cielo": "Cálido húmedo amazónico"},
    "Madre de Dios - Puerto Maldonado": {"cod": "116005", "estacion": "Estación Puerto Maldonado", "altitud": "183 msnm", "radMax": 850, "iuv": 11, "cielo": "Cálido tropical"},
    "Moquegua - Moquegua":         {"cod": "114031", "estacion": "Estación Moquegua", "altitud": "1,410 msnm", "radMax": 1000, "iuv": 15, "cielo": "Despejado permanente"},
    "Pasco - Cerro de Pasco":      {"cod": "111009", "estacion": "Estación Cerro de Pasco", "altitud": "4,338 msnm", "radMax": 965, "iuv": 14, "cielo": "Frío extremo / Alta radiación"},
    "Piura - Piura":               {"cod": "103015", "estacion": "Estación Miraflores (Piura)", "altitud": "30 msnm", "radMax": 910, "iuv": 12, "cielo": "Soleado cálido"},
    "Puno - Puno":                 {"cod": "115004", "estacion": "Estación Bellavista (Puno)", "altitud": "3,812 msnm", "radMax": 990, "iuv": 14, "cielo": "Despejado / Altiplano"},
    "San Martín - Tarapoto":       {"cod": "106024", "estacion": "Estación San Martín (Tarapoto)", "altitud": "350 msnm", "radMax": 860, "iuv": 11, "cielo": "Parcialmente nublado"},
    "Tacna - Tacna":               {"cod": "114048", "estacion": "Estación Jorge Basadre (Tacna)", "altitud": "562 msnm", "radMax": 930, "iuv": 12, "cielo": "Soleado / Costa Sur"},
    "Tumbes - Tumbes":             {"cod": "101005", "estacion": "Estación Puerto Pizarro (Tumbes)", "altitud": "7 msnm", "radMax": 890, "iuv": 12, "cielo": "Cálido ecuatorial"},
    "Ucayali - Pucallpa":          {"cod": "109042", "estacion": "Estación Pucallpa", "altitud": "154 msnm", "radMax": 845, "iuv": 11, "cielo": "Cálido húmedo / Selva Baja"}
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def leer_estacion(codigo):
    url = f"https://www.senamhi.gob.pe/site/lvera/lluvia_historica_estacion.php?estacion={codigo}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    temps, hums, vientos = [], [], []

    for fila in soup.find_all("tr"):
        celdas = [c.get_text(strip=True) for c in fila.find_all(["td", "th"])]
        if len(celdas) >= 6 and re.match(r"^\d{2}:\d{2}", celdas[1]):
            try:
                t = float(celdas[2])
                if -15 < t < 45:
                    temps.append(t)
                h = float(celdas[4])
                if 5 <= h <= 100:
                    hums.append(h)
                if len(celdas) > 6:
                    v = float(celdas[6])
                    if 0 <= v < 120:
                        vientos.append(v)
            except (ValueError, IndexError):
                continue

    if not temps:
        return None

    return {
        "tempMin": round(min(temps), 1),
        "tempMax": round(max(temps), 1),
        "tempAmb": round(temps[-1], 1),
        "humedad": f"{round(hums[-1])}%" if hums else "65%",
        "vientoVel": round(vientos[-1], 1) if vientos else 12,
        "vientoTexto": f"{round(vientos[-1], 1)} km/h (SENAMHI)" if vientos else "12 km/h"
    }

def calcular_tiempo_45c(t_amb, rad_max):
    # Balance energético para 200 L de agua (m*Cp = 837,200 J/K) con Ac = 2.0 m² y eficiencia ~0.70
    delta_t = max(5.0, 45.0 - t_amb)
    energia_requerida_j = 200 * 4186 * delta_t
    potencia_util_w = max(400.0, rad_max * 2.0 * 0.70 * 0.85)
    horas = energia_requerida_j / (potencia_util_w * 3600)
    return round(max(1.5, min(5.5, horas)), 1)

def main():
    try:
        with open("datos_senamhi.json", "r", encoding="utf-8") as f:
            salida = json.load(f)
    except FileNotFoundError:
        salida = {"ciudades": {}}

    hora_peru = datetime.now(timezone(timedelta(hours=-5)))
    salida["actualizado"] = hora_peru.strftime("%d/%m/%Y %H:%M")
    ciudades = salida.setdefault("ciudades", {})

    for nombre_ciudad, meta in CATALOGO_PERU.items():
        base = ciudades.get(nombre_ciudad, {
            "estacion": meta["estacion"],
            "altitud": meta["altitud"],
            "cielo": meta["cielo"],
            "tempMin": 14.0,
            "tempMax": 25.0,
            "tempAmb": 20.0,
            "radMax": meta["radMax"],
            "iuv": meta["iuv"],
            "vientoVel": 12,
            "vientoTexto": "12 km/h",
            "humedad": "60%",
            "tMin": 2.9,
            "desc": f"Datos meteorológicos oficiales SENAMHI para {nombre_ciudad} ({meta['altitud']})."
        })

        try:
            lectura = leer_estacion(meta["cod"])
            if lectura:
                base.update(lectura)
                base["tMin"] = calcular_tiempo_45c(base["tempAmb"], base["radMax"])
                print(f"[OK] {nombre_ciudad}: {lectura['tempMin']}° / {lectura['tempMax']}°C")
        except Exception as e:
            print(f"[AVISO] {nombre_ciudad}: manteniendo base ({e})")

        ciudades[nombre_ciudad] = base

    with open("datos_senamhi.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print("Actualización de datos_senamhi.json finalizada con éxito.")

if __name__ == "__main__":
    main()
