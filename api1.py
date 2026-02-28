from fastapi import FastAPI
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re, uvicorn

app = FastAPI(title="API Cédula Venezolana")

def resolver_captcha(texto):
    match = re.search(r'(\d+)\s*\+\s*(\d+)', texto)
    if match:
        return str(int(match.group(1)) + int(match.group(2)))
    return None

@app.get("/cedula/{numero}")
async def consultar_cedula(numero: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = await browser.new_page()
        await page.goto('https://www.sistemaspnp.com/cedula/', timeout=30000)
        await page.wait_for_timeout(2000)

        texto = await page.evaluate('() => document.body.innerText')
        captcha = resolver_captcha(texto)

        await page.fill('input[placeholder*="cédula"]', numero)
        if captcha:
            await page.fill('input[placeholder*="resultado"]', captcha)
        await page.click('button:has-text("Buscar")')
        await page.wait_for_timeout(5000)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    texto = soup.get_text(separator='\n')

    if "Datos Personales" not in texto:
        return {"success": False, "message": "Cédula no encontrada"}

    datos = {}
    campos = {
        "Cédula:": "cedula", "RIF:": "rif",
        "Primer Apellido:": "primer_apellido",
        "Segundo Apellido:": "segundo_apellido",
        "Nombres:": "nombres", "Estado:": "estado",
        "Municipio:": "municipio", "Parroquia:": "parroquia",
        "Centro Electoral:": "centro_electoral"
    }
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        for clave, campo in campos.items():
            if clave in linea:
                valor = linea.replace(clave, '').strip()
                datos[campo] = valor if valor else (lineas[i+1].strip() if i+1 < len(lineas) else "")

    return {"success": True, "data": datos}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)