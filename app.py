from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.sync_api import sync_playwright
import time

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial():
    html_content = """
    <html>
        <head>
            <title>Ticket Ninja 🥷</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px; text-align: center; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); display: inline-block; }
                input, button { padding: 10px; margin: 10px 0; font-size: 16px; width: 80%; border-radius: 5px; border: 1px solid #ccc; }
                button { background-color: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
                button:hover { background-color: #0056b3; }
                #resultados { margin-top: 20px; font-weight: bold; color: #28a745; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🥷 Ticket Ninja</h1>
                <p>Encontre tarifas ocultas usando Arbitragem Geográfica</p>
                <form id="formBusca">
                    <input type="text" id="origem" placeholder="Origem (ex: MAO)" required><br>
                    <input type="text" id="destino" placeholder="Destino (ex: GIG)" required><br>
                    <input type="date" id="data" required><br>
                    <button type="submit">Iniciar Varredura Ninja</button>
                </form>
                <div id="resultados"></div>
            </div>

            <script>
                document.getElementById('formBusca').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const divResultados = document.getElementById('resultados');
                    
                    divResultados.innerHTML = '⏳ <i>Iniciando navegador invisível no servidor... aguarde cerca de 15 segundos.</i>';
                    
                    const origem = document.getElementById('origem').value;
                    const destino = document.getElementById('destino').value;
                    const data = document.getElementById('data').value;

                    try {
                        const resposta = await fetch(`/buscar?origem=${origem}&destino=${destino}&data=${data}`);
                        const dados = await resposta.json();
                        
                        if (dados.status === "sucesso") {
                            divResultados.innerHTML = `✅ Varredura concluída para ${dados.origem} ➡️ ${dados.destino}! <br><br> <span style='font-size: 18px; color: #333;'>${dados.mensagem}</span>`;
                        } else {
                            divResultados.innerHTML = `❌ Erro: ${dados.mensagem}`;
                        }
                    } catch (error) {
                        divResultados.innerHTML = `❌ Erro ao conectar com o servidor Ninja.`;
                    }
                });
            </script>
        </body>
    </html>
    """
    return html_content

# IMPORTANTE: Tiramos o 'async' daqui. O FastAPI vai rodar isso em paralelo com segurança!
@app.get("/buscar")
def rodar_bot_real(origem: str, destino: str, data: str):
    print(f"🥷 Iniciando varredura no Kayak: {origem} para {destino} em {data}")
    
    url_alvo = f"https://www.kayak.com.br/flights/{origem}-{destino}/{data}?sort=price_a"
    
    try:
        # Usando a versão síncrona (sync_playwright)
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            pagina = contexto.new_page()
            
            print("🌍 Acessando o buscador de voos...")
            pagina.goto(url_alvo)
            
            print("⏳ Aguardando resultados carregarem (15s)...")
            time.sleep(15)
            
            nome_foto = f"resultado_{origem.upper()}_{destino.upper()}.png"
            pagina.screenshot(path=nome_foto)
            
            navegador.close()
            print(f"✅ Foto salva: {nome_foto}")

        return {
            "status": "sucesso",
            "origem": origem.upper(),
            "destino": destino.upper(),
            "mensagem": f"O robô buscou a rota e salvou a evidência visual no arquivo: {nome_foto}"
        }
    except Exception as e:
        print(f"❌ Erro no robô: {str(e)}")
        return {
            "status": "erro",
            "mensagem": str(e)
        }