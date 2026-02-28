from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests

app = FastAPI(title="API Cedula Costa Rica")

@app.get("/")
def inicio():
    return {"status": "online", "uso": "/cedula/109380752"}

@app.get("/cedula/{numero}")
def cedula(numero: str):
    try:
        r = requests.get(
            f"https://apis.gometa.org/cedulas/{numero}",
            timeout=15
        )

        data = r.json()

        if r.status_code in [200, 201] and data.get("results") and len(data["results"]) > 0:
            res = data["results"][0]
            return {
                "success": True,
                "data": {
                    "nombre_completo":       res.get("fullname", "N/A"),
                    "apellidos":             res.get("lastname", "N/A"),
                    "primer_apellido":       res.get("lastname1", "N/A"),
                    "segundo_apellido":      res.get("lastname2", "N/A"),
                    "nombres":               res.get("firstname", "N/A"),
                    "primer_nombre":         res.get("firstname1", "N/A"),
                    "segundo_nombre":        res.get("firstname2", "N/A"),
                    "genero":                "Femenino" if res.get("type") == "F" else "Masculino",
                    "cedula":                data.get("cedula", "N/A"),
                    "cedula_raw":            res.get("rawcedula", "N/A"),
                    "tipo_persona":          res.get("guess_type", "N/A"),
                    "numero_identificacion": res.get("guess_type_num", "N/A"),
                    "tipo_identificacion":   data.get("tipoIdentificacion", "N/A"),
                    "clase":                 res.get("class", "N/A"),
                    "admin":                 "Si" if res.get("admin") != "00" else "No",
                    "fecha_base_datos":      data.get("database_date", "N/A"),
                }
            }
        else:
            return JSONResponse(status_code=404, content={
                "success": False,
                "mensaje": "Cedula no encontrada"
            })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "mensaje": str(e)
        })

@app.get("/nombre/{nombre}")
def por_nombre(nombre: str):
    try:
        r = requests.get(
            f"https://apis.gometa.org/cedulas/{nombre}",
            timeout=15
        )

        data = r.json()

        if r.status_code in [200, 201] and data.get("results"):
            results = data["results"]
            return {
                "success": True,
                "total": len(results),
                "data": [
                    {
                        "nombre_completo":       res.get("fullname", "N/A"),
                        "apellidos":             res.get("lastname", "N/A"),
                        "primer_apellido":       res.get("lastname1", "N/A"),
                        "segundo_apellido":      res.get("lastname2", "N/A"),
                        "nombres":               res.get("firstname", "N/A"),
                        "primer_nombre":         res.get("firstname1", "N/A"),
                        "segundo_nombre":        res.get("firstname2", "N/A"),
                        "cedula_raw":            res.get("rawcedula", "N/A"),
                        "tipo_persona":          res.get("guess_type", "N/A"),
                        "numero_identificacion": res.get("guess_type_num", "N/A"),
                        "genero":                "Femenino" if res.get("type") == "F" else "Masculino",
                        "clase":                 res.get("class", "N/A"),
                        "admin":                 "Si" if res.get("admin") != "00" else "No",
                    }
                    for res in results
                ]
            }
        else:
            return JSONResponse(status_code=404, content={
                "success": False,
                "mensaje": "No se encontraron resultados"
            })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "mensaje": str(e)
        })