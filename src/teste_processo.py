#!/usr/bin/env python3
"""
Teste simplificado para o processo 1001535-69.2025.8.26.0260
"""

import re
import time
from playwright.sync_api import sync_playwright

PROCESSO = "1001535-69.2025.8.26.0260"

def testar_processo():
    with sync_playwright() as p:
        print(f"🚀 Testando processo: {PROCESSO}")
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            # Acessa o portal
            print("📡 Acessando TJSP...")
            page.goto("https://esaj.tjsp.jus.br/cpopg/open.do", timeout=30000)
            print("✅ Portal carregado")
            
            # Seleciona busca por número
            page.locator("#radioNumeroUnificado").click()
            time.sleep(1)
            
            # Prepara o número
            numero_limpo = re.sub(r'\D', '', PROCESSO)
            parte_1 = numero_limpo[:-4]  # 100153569202582600
            parte_2 = numero_limpo[-4:]   # 0260
            
            print(f"📝 Digitando: {parte_1} | {parte_2}")
            
            # Preenche os campos
            page.locator("#numeroDigitoAnoUnificado").clear()
            page.locator("#numeroDigitoAnoUnificado").press_sequentially(parte_1, delay=50)
            time.sleep(0.5)
            
            page.locator("#foroNumeroUnificado").clear()
            page.locator("#foroNumeroUnificado").press_sequentially(parte_2, delay=50)
            time.sleep(1)
            
            # Consulta
            print("🔍 Consultando...")
            page.locator("#botaoConsultarProcessos").click()
            
            # Aguarda resultado
            try:
                page.wait_for_selector("#classeProcesso, #mensagemRetorno", timeout=15000)
            except:
                pass
            
            # Verifica resultado
            if page.locator("#classeProcesso").is_visible():
                classe = page.locator("#classeProcesso").inner_text().strip()
                print(f"✅ SUCESSO! Classe: {classe}")
                
                # Extrai mais dados
                try:
                    juiz = page.locator("#juizProcesso").inner_text().strip()
                    print(f"   Juiz: {juiz}")
                except:
                    pass
                
                try:
                    assunto = page.locator("#assuntoProcesso").inner_text().strip()
                    print(f"   Assunto: {assunto}")
                except:
                    pass
                
                # Salva screenshot
                page.screenshot(path="/home/ubuntu/projeto_extracao/resultado_teste.png")
                print("📸 Screenshot salvo: resultado_teste.png")
                
            elif page.locator("#mensagemRetorno").is_visible():
                msg = page.locator("#mensagemRetorno").inner_text().strip()
                print(f"⚠️ Mensagem do sistema: {msg}")
                page.screenshot(path="/home/ubuntu/projeto_extracao/erro_teste.png")
            else:
                print("❌ Resultado desconhecido")
                page.screenshot(path="/home/ubuntu/projeto_extracao/desconhecido_teste.png")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            try:
                page.screenshot(path="/home/ubuntu/projeto_extracao/erro_exception.png")
            except:
                pass
        
        finally:
            browser.close()
            print("🏁 Teste finalizado")

if __name__ == "__main__":
    testar_processo()
