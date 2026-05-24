from playwright.sync_api import sync_playwright
import time

def caçar_passagem(origem, destino, data_ida):
    print(f"🥷 Ticket Ninja ativado: Buscando {origem} ➡️ {destino} para o dia {data_ida}...")
    
    # Construímos a URL direta do Kayak já ordenada pelo menor preço
    url_alvo = f"https://www.kayak.com.br/flights/{origem}-{destino}/{data_ida}?sort=price_a"
    
    with sync_playwright() as p:
        # Iniciamos o navegador visível para testes
        navegador = p.chromium.launch(headless=False)
        
        contexto = navegador.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        pagina = contexto.new_page()
        
        print(f"🌍 Acessando a rota secreta...")
        pagina.goto(url_alvo)
        
        # Sites de passagem demoram para carregar porque estão buscando em várias companhias.
        # Precisamos mandar o robô ter paciência e esperar a barra de progresso do site terminar.
        print("⏳ Aguardando os motores de busca do site terminarem (esperando 15 segundos)...")
        time.sleep(15)
        
        # Como o HTML muda muito, a melhor forma de provar que o bot chegou no resultado 
        # antes de extrair o texto é tirar uma "foto" da tela.
        caminho_foto = "resultado_busca.png"
        pagina.screenshot(path=caminho_foto)
        print(f"📸 Foto da tela salva com sucesso: {caminho_foto}")
        
        navegador.close()
        print("✅ Caçada finalizada com sucesso.")

if __name__ == "__main__":
    # Testando um voo de Manaus para Guarulhos para daqui a algumas semanas
    caçar_passagem("MAO", "GRU", "2026-07-15")