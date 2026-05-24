from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from playwright.sync_api import sync_playwright
import time
import re
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def extrair_dados_voo(origem, destino, data, config_proxy=None, buscador="kayak"):
    """Motor universal de raspagem."""
    if buscador == "kayak":
        url_alvo = f"https://www.kayak.com.br/flights/{origem}-{destino}/{data}?sort=price_a"
    else:
        ano, mes, dia = data.split('-')
        data_sky = f"{ano[2:]}{mes}{dia}"
        url_alvo = f"https://www.skyscanner.com.br/transport/flights/{origem.lower()}/{destino.lower()}/{data_sky}/"

    textos_brutos = []
    try:
        with sync_playwright() as p:
            args = {"headless": True, "args": ["--disable-blink-features=AutomationControlled"]}
            if config_proxy: args["proxy"] = config_proxy
                
            navegador = p.chromium.launch(**args)
            contexto = navegador.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            pagina = contexto.new_page()
            pagina.goto(url_alvo)
            time.sleep(20) 
            
            textos_brutos = pagina.evaluate('''() => {
                return Array.from(document.querySelectorAll('div, span'))
                    .map(e => e.innerText)
                    .filter(t => t && t.length > 15 && t.length < 1000 && 
                           (t.includes("R$") || t.includes("$") || t.includes("£") || t.includes("€")));
            }''')
            navegador.close()
    except Exception as e:
        print(f"⚠️ Erro ao acessar {buscador.capitalize()}: {e}")

    melhor_voo = None
    menor_valor = float('inf')

    if textos_brutos:
        for texto in textos_brutos:
            texto_limpo = texto.replace('\\xa0', ' ').replace('\xa0', ' ')
            match_preco = re.search(r'((?:R\$|US\$|\$|£|€)\s*([\d\.]+)(?:,\d{2})?)', texto_limpo)
            if not match_preco: continue
            
            try:
                valor_matematico = float(match_preco.group(2).replace('.', ''))
                if 50 < valor_matematico < menor_valor:
                    menor_valor = valor_matematico
                    match_duracao = re.search(r'(\d{1,2}\s*h\s*\d{1,2}\s*m|\d{1,2}\s*h)', texto_limpo, re.IGNORECASE)
                    match_escala = re.search(r'(direto|\d+\s*escala[s]?)', texto_limpo, re.IGNORECASE)
                    
                    melhor_voo = {
                        "preco_texto": match_preco.group(1),
                        "valor_matematico": menor_valor,
                        "duracao": match_duracao.group(1).replace(' ', '') if match_duracao else "N/A",
                        "escalas": match_escala.group(1).capitalize() if match_escala else "N/A",
                        "fonte": buscador.capitalize()
                    }
            except: continue
    return melhor_voo

@app.get("/", response_class=HTMLResponse)
def tela_inicial(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/processar_busca", response_class=HTMLResponse)
def rodar_bot_real(request: Request, origem: str, destino: str, data: str):
    print(f"\n🥷 Iniciando varredura multi-motores: {origem} ➡️ {destino}")
    
    proxy_sorteado = random.choice([
        {"ip": "198.105.121.200", "porta": "6462", "pais": "Reino Unido"},
        {"ip": "38.154.203.95", "porta": "5863", "pais": "EUA"},
        {"ip": "64.137.96.74", "porta": "6641", "pais": "Espanha"}
    ])
    
    config_proxy = {"server": f"http://{proxy_sorteado['ip']}:{proxy_sorteado['porta']}", "username": "oluuxvlf", "password": "uoqcz77tr4g0"}
    
    voos = [extrair_dados_voo(origem, destino, data, config_proxy, b) for b in ["kayak", "skyscanner"]]
    voos_validos = [v for v in voos if v is not None]
    
    if voos_validos:
        voo_vencedor = min(voos_validos, key=lambda x: x["valor_matematico"])
    else:
        voo_vencedor = extrair_dados_voo(origem, destino, data, None, "kayak") or {
            "preco_texto": "Indisponível", "duracao": "-", "escalas": "-", "fonte": "-"
        }

    # Log seguro para evitar TypeError
    print(f"✅ Vencedor encontrado com sucesso.")

    return templates.TemplateResponse(
        request=request, 
        name="resultado.html", 
        context={"origem": origem.upper(), "destino": destino.upper(), "data": data, "dados_voo": voo_vencedor}
    )