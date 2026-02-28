from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI(title="API Cedula Venezolana")

def resolver_captcha(texto):
    match = re.search(r'(\d+)\s*\+\s*(\d+)', texto)
    if match:
        return str(int(match.group(1)) + int(match.group(2)))
    return None

def consultar_cedula(cedula):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.sistemaspnp.com/cedula/",
    }

    r = session.get("https://www.sistemaspnp.com/cedula/", headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    captcha = resolver_captcha(soup.get_text())

    data = {
        "cedula": cedula,
        "captcha": captcha or "0"
    }

    r2 = session.post("https://www.sistemaspnp.com/cedula/", data=data, headers=headers, timeout=15)
    soup2 = BeautifulSoup(r2.text, "html.parser")
    texto = soup2.get_text(separator="\n")

    if "Datos Personales" not in texto:
        return None

    datos = {}
    campos = {
        "Cédula:": "cedula",
        "RIF:": "rif",
        "Primer Apellido:": "primer_apellido",
        "Segundo Apellido:": "segundo_apellido",
        "Nombres:": "nombres",
        "Estado:": "estado",
        "Municipio:": "municipio",
        "Parroquia:": "parroquia",
        "Centro Electoral:": "centro_electoral"
    }

    lineas = texto.split("\n")
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        for clave, campo in campos.items():
            if clave in linea:
                valor = linea.replace(clave, "").strip()
                datos[campo] = valor if valor else (lineas[i+1].strip() if i+1 < len(lineas) else "")

    return datos

@app.get("/")
def inicio():
    return {"status": "online", "uso": "/cedula/{numero}"}

@app.get("/cedula/{numero}")
def cedula(numero: str):
    if not numero.isdigit():
        return JSONResponse(status_code=400, content={
            "success": False,
            "mensaje": "La cedula debe contener solo numeros"
        })

    datos = consultar_cedula(numero)

    if not datos or len(datos) < 3:
        return JSONResponse(status_code=404, content={
            "success": False,
            "mensaje": "No se encontraron datos para esa cedula"
        })

    return {
        "success": True,
        "data": datos
    }