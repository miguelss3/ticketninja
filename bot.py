from playwright.sync_api import sync_playwright
import time

def iniciar_teste_bot():
    print("🤖 Iniciando o Ticket Ninja...")
    
    with sync_playwright() as p:
        # headless=False faz o navegador abrir de verdade na sua tela
        navegador = p.chromium.launch(headless=False)
        
        contexto = navegador.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        pagina = contexto.new_page()
        
        print("🌍 Acessando site de verificação de IP...")
        pagina.goto("https://ident.me/")
        
        ip_detectado = pagina.locator("body").inner_text()
        print(f"🕵️ IP detectado pelo servidor agora: {ip_detectado}")
        
        print("⏳ Pausando por 5 segundos para você ver a tela...")
        time.sleep(5)
        
        navegador.close()
        print("✅ Teste finalizado.")

if __name__ == "__main__":
    iniciar_teste_bot()