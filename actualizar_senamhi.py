import json
import os
import time
from datetime import datetime, timezone, timedelta
import requests

# Coordenadas exactas de las estaciones meteorológicas de referencia por departamento
ESTACIONES_PERU = {
    "Amazonas - Chachapoyas":           {"estacion": "Ref. Chachapoyas", "lat": -6.229, "lon": -77.872, "altitud": "2,335 msnm"},
    "Áncash - Huaraz":                  {"estacion": "Ref. Huaraz", "lat": -9.528, "lon": -77.528, "altitud": "3,052 msnm"},
    "Apurímac - Abancay":               {"estacion": "Ref. Abancay", "lat": -13.634, "lon": -72.881, "altitud": "2,378 msnm"},
    "Arequipa - Arequipa":              {"estacion": "Ref. La Pampilla (Arequipa)", "lat": -16.404, "lon": -71.525, "altitud": "2,325 msnm"},
    "Ayacucho - Huamanga":              {"estacion": "Ref. Huamanga", "lat": -13.158, "lon": -74.223, "altitud": "2,761 msnm"},
    "Cajamarca - Cajamarca":            {"estacion": "Ref. Weberbauer (Cajamarca)", "lat": -7.164, "lon": -78.500, "altitud": "2,750 msnm"},
    "Callao - Callao":                  {"estacion": "Ref. Aeropuerto Callao", "lat": -12.022, "lon": -77.114, "altitud": "13 msnm"},
    "Cusco - Cusco":                    {"estacion": "Ref. Granja Kayra (Cusco)", "lat": -13.556, "lon": -71.875, "altitud": "3,399 msnm"},
    "Huancavelica - Huancavelica":      {"estacion": "Ref. Huancavelica", "lat": -12.786, "lon": -74.976, "altitud": "3,676 msnm"},
    "Huánuco - Huánuco":                {"estacion": "Ref. Huánuco", "lat": -9.930, "lon": -76.242, "altitud": "1,894 msnm"},
    "Ica - Ica":                        {"estacion": "Ref. San José (Ica)", "lat": -14.068, "lon": -75.729, "altitud": "406 msnm"},
    "Junín - Huancayo":                 {"estacion": "Ref. Huayao (Huancayo)", "lat": -12.040, "lon": -75.323, "altitud": "3,313 msnm"},
    "La Libertad - Trujillo":           {"estacion": "Ref. Trujillo", "lat": -8.112, "lon": -79.029, "altitud": "34 msnm"},
    "Lambayeque - Chiclayo":            {"estacion": "Ref. Chiclayo", "lat": -6.771, "lon": -79.841, "altitud": "29 msnm"},
    "Lima - Lima":                      {"estacion": "Ref. Von Humboldt (Lima)", "lat": -12.082, "lon": -76.943, "altitud": "240 msnm"},
    "Loreto - Iquitos":                 {"estacion": "Ref. Moronacocha (Iquitos)", "lat": -3.749, "lon": -73.254, "altitud": "106 msnm"},
    "Madre de Dios - Puerto Maldonado": {"estacion": "Ref. Puerto Maldonado", "lat": -12.593, "lon": -69.189, "altitud": "183 msnm"},
    "Moquegua - Moquegua":              {"estacion": "Ref. Moquegua", "lat": -17.193, "lon": -70.935, "altitud": "1,410 msnm"},
    "Pasco - Cerro de Pasco":           {"estacion": "Ref. Cerro de Pasco", "lat": -10.683, "lon": -76.256, "altitud": "4,338 msnm"},
    "Piura - Piura":                    {"estacion": "Ref. Miraflores (Piura)", "lat": -5.194, "lon": -80.632, "altitud": "30 msnm"},
    "Puno - Puno":                      {"estacion": "Ref. Bellavista (Puno)", "lat": -15.840, "lon": -70.021, "altitud": "3,812 msnm"},
    "San Martín - Tarapoto":            {"estacion": "Ref. Tarapoto", "lat": -6.482, "lon": -76.372, "altitud": "350 msnm"},
    "Tacna - Tacna":                    {"estacion": "Ref. Jorge Basadre (Tacna)", "lat": -18.014, "lon": -70.251, "altitud": "562 msnm"},
    "Tumbes - Tumbes":                  {"estacion": "Ref. Puerto Pizarro (Tumbes)", "lat": -3.566, "lon": -80.451, "altitud": "7 msnm"},
    "Ucayali - Pucallpa":               {"estacion": "Ref. Pucallpa", "lat": -8.379, "lon": -74.553, "altitud": "154 msnm"}
}

def calcular_tiempo_45c(t_amb, rad_max):
    t_agua_inicial = max(8.0, t_amb - 2.0)
    delta_t = max(2.0, 45.0 - t_agua_inicial)
    energia_requerida_j = 200 * 4186 * delta_t
    irradiancia_media = max(250.0, rad_max * 0.65)
    potencia_util_w = irradiancia_media * 2.0 * 0.62
    return round(energia_requerida_j / (potencia_util_w * 3600), 2)

def consultar_clima_real(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation,uv_index"
        "&daily=temperature_2m_min,temperature_2m_max&timezone=America%2FLima&forecast_days=1"
    )
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    hourly = data["hourly"]
    daily = data["daily"]

    # Hora actual en Perú (0 a 23)
    hora_peru = datetime.now(timezone(timedelta(hours=-5))).hour
    temp_min = round(daily["temperature_2m_min"][0], 1)
    temp_max = round(daily["temperature_2m_max"][0], 1)
    temp_amb = round(hourly["temperature_2m"][hora_peru], 1)
    humedad = round(hourly["relative_humidity_2m"][hora_peru])
    viento = round(hourly["wind_speed_10m"][hora_peru], 1)
    rad_max = round(max(hourly["shortwave_radiation"]))
    iuv_max = round(max(hourly["uv_index"]))

    cielo = "Despejado" if rad_max >= 850 else ("Parcialmente nublado" if rad_max >= 600 else "Nublado")

    return {
        "cielo": cielo,
        "tempMin": temp_min,
        "tempMax": temp_max,
        "tempAmb": temp_amb,
        "radMax": max(200, rad_max),
        "iuv": iuv_max,
        "vientoVel": viento,
        "vientoTexto": f"{viento} km/h",
        "humedad": f"{humedad}%"
    }

def main():
    hora_peru = datetime.now(timezone(timedelta(hours=-5)))
    salida = {
        "fuente": "Open-Meteo (Reanálisis / Pronóstico horario por coordenadas de estación)",
        "actualizado": hora_peru.strftime("%Y-%m-%d %H:%M PET"),
        "ciudades": {}
    }


    print("=== INICIANDO RECOLECCIÓN EN VIVO DE DATOS METEOROLÓGICOS (PERÚ) ===")
    for nombre, meta in ESTACIONES_PERU.items():
        clima = consultar_clima_real(meta["lat"], meta["lon"])
        clima["estacion"] = meta["estacion"]
        clima["altitud"] = meta["altitud"]
        clima["tMin"] = calcular_tiempo_45c(clima["tempAmb"], clima["radMax"])
        clima["desc"] = f"Lectura horaria real ({salida['actualizado']}) para {nombre} ({meta['altitud']})."
        salida["ciudades"][nombre] = clima
        print(f"[OK] {nombre}: {clima['tempMin']}° / {clima['tempMax']}°C | Rad: {clima['radMax']} W/m² | tMin: {clima['tMin']} h")
        time.sleep(0.1) # Respeto de tasa de peticiones

    # 1. Guardar archivo vivo para GitHub Pages y Vercel
    with open("datos_senamhi.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print("\n[OK] Guardado en datos_senamhi.json")

    # 2. Guardar copia histórica fechada para reproducibilidad de informes
    os.makedirs("historial", exist_ok=True)
    fecha_archivo = hora_peru.strftime("%Y-%m-%d_%H00")
    with open(f"historial/clima_{fecha_archivo}.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado registro histórico en historial/clima_{fecha_archivo}.json")

if __name__ == "__main__":
    main()

