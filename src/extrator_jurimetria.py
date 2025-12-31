#!/usr/bin/env python3
"""
================================================================================
EXTRATOR JURIMÉTRICO CONSOLIDADO - VERSÃO 2.0 (ESCALÁVEL)
================================================================================
Autor: Sistema de Jurimetria
Versão: 2.0 (Testada e Funcional)
Objetivo: Extrair dados completos de processos de Recuperação Judicial do TJSP,
          responder às 14 questões críticas do plano de estudo.

QUESTÕES DO PLANO DE ESTUDO:
1. Quantas RJs têm bancos no polo e discutem veículos pesados?
2. Quais são os pedidos mais comuns?
3. Envolvem garantias extraconcursais?
4. Envolvem pedido de essencialidade?
5. Quais são as teses discutidas?
6. Como é o entendimento dos tribunais?
7. Qual escritório ajuizou a ação?
8. O crédito extraconcursal foi reconhecido?
9. Há recursos pendentes?
10. Bens essenciais vs busca e apreensão?
11. O stay period está vigente?
12. É possível executar as garantias?
13. O plano de RJ foi votado/homologado?
14. Há AGC ou mediação marcada?
================================================================================
"""

import re
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page
import pandas as pd


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

@dataclass
class Config:
    """Configurações do extrator"""
    URL_TJSP_1GRAU: str = "https://esaj.tjsp.jus.br/cpopg/open.do"
    URL_TJSP_2GRAU: str = "https://esaj.tjsp.jus.br/cposg/open.do"
    TIMEOUT_PAGINA: int = 30000
    TIMEOUT_ELEMENTO: int = 15000
    DELAY_ENTRE_PROCESSOS: float = 3.0
    DELAY_DIGITACAO: int = 50
    HEADLESS: bool = True
    DIR_SAIDA: str = "/home/ubuntu/projeto_extracao/resultados"
    DIR_PDFS: str = "/home/ubuntu/projeto_extracao/resultados/pdfs"


# =============================================================================
# ESTRUTURA DE DADOS
# =============================================================================

@dataclass
class Processo:
    """Dados completos de um processo"""
    numero: str = ""
    classe: str = ""
    assunto: str = ""
    foro: str = ""
    vara: str = ""
    juiz: str = ""
    data_distribuicao: str = ""
    
    # Partes
    requerente: str = ""
    advogados_requerente: List[str] = field(default_factory=list)
    interessados: List[str] = field(default_factory=list)
    credores: List[str] = field(default_factory=list)
    perito: str = ""
    
    # Movimentações
    movimentacoes: List[Dict] = field(default_factory=list)
    texto_completo: str = ""
    
    # Status
    status: str = "Pendente"
    erro: str = ""
    
    # 14 Questões
    q01_bancos_veiculos: str = ""
    q02_pedidos: str = ""
    q03_garantias_extraconcursais: str = ""
    q04_essencialidade: str = ""
    q05_teses: str = ""
    q06_entendimento: str = ""
    q07_escritorio: str = ""
    q08_credito_extraconcursal: str = ""
    q09_recursos: str = ""
    q10_bens_busca: str = ""
    q11_stay_period: str = ""
    q12_executar_garantias: str = ""
    q13_plano_rj: str = ""
    q14_agc_mediacao: str = ""


# =============================================================================
# ANALISADOR JURIMÉTRICO
# =============================================================================

class Analisador:
    """Analisa texto e responde às 14 questões"""
    
    BANCOS = [
        "banco", "bradesco", "itaú", "santander", "caixa", "bb", "safra",
        "btg", "votorantim", "fidc", "fundo", "financ", "credor fiduciário"
    ]
    
    VEICULOS = [
        "caminhão", "ônibus", "frota", "carreta", "veículo", "scania",
        "volvo", "mercedes", "mills pesados", "locação", "equipamento"
    ]
    
    ESSENCIALIDADE = [
        "essencial", "indispensável", "continuidade", "art. 49", "§ 3"
    ]
    
    GARANTIAS = [
        "alienação fiduciária", "trava bancária", "garantia real",
        "cessão fiduciária", "fiduciário"
    ]
    
    STAY = [
        "stay period", "suspensão", "180 dias", "art. 6", "blindagem"
    ]
    
    def analisar(self, proc: Processo) -> Processo:
        """Analisa o processo e preenche as 14 questões"""
        texto = proc.texto_completo.lower()
        movs = " ".join([m.get("descricao", "") for m in proc.movimentacoes]).lower()
        partes = f"{proc.requerente} {' '.join(proc.interessados)} {' '.join(proc.credores)}".lower()
        
        # Q1: Bancos + Veículos
        tem_banco = any(b in partes or b in texto for b in self.BANCOS)
        tem_veiculo = any(v in partes or v in texto for v in self.VEICULOS)
        
        if tem_banco and tem_veiculo:
            proc.q01_bancos_veiculos = "SIM - Bancos E Veículos"
        elif tem_banco:
            proc.q01_bancos_veiculos = "Apenas Bancos"
        elif tem_veiculo:
            proc.q01_bancos_veiculos = "Apenas Veículos/Equipamentos"
        else:
            proc.q01_bancos_veiculos = "Não identificado"
        
        # Q2: Pedidos
        pedidos = []
        if "tutela" in proc.classe.lower():
            pedidos.append("Tutela Cautelar")
        if "recuperação" in proc.assunto.lower():
            pedidos.append("Recuperação Judicial")
        if "suspensão" in texto:
            pedidos.append("Suspensão de execuções")
        if "essencial" in texto:
            pedidos.append("Essencialidade de bens")
        proc.q02_pedidos = ", ".join(pedidos) if pedidos else "Verificar petição inicial"
        
        # Q3: Garantias extraconcursais
        proc.q03_garantias_extraconcursais = "SIM" if any(g in texto for g in self.GARANTIAS) else "Não identificado"
        
        # Q4: Essencialidade
        proc.q04_essencialidade = "SIM" if any(e in texto for e in self.ESSENCIALIDADE) else "Não identificado"
        
        # Q5: Teses
        teses = []
        if any(e in texto for e in self.ESSENCIALIDADE):
            teses.append("Essencialidade de bens")
        if any(g in texto for g in self.GARANTIAS):
            teses.append("Crédito extraconcursal")
        if any(s in texto for s in self.STAY):
            teses.append("Stay period")
        proc.q05_teses = ", ".join(teses) if teses else "Verificar decisões"
        
        # Q6: Entendimento tribunal
        if "deferido" in movs or "deferida" in movs:
            if "essencial" in movs:
                proc.q06_entendimento = "Favorável à empresa"
            else:
                proc.q06_entendimento = "Decisão deferida - verificar teor"
        elif "indeferido" in movs or "indeferida" in movs:
            proc.q06_entendimento = "Desfavorável à empresa"
        else:
            proc.q06_entendimento = "Aguardando decisão"
        
        # Q7: Escritório
        if proc.advogados_requerente:
            proc.q07_escritorio = proc.advogados_requerente[0]
        else:
            proc.q07_escritorio = "Não identificado"
        
        # Q8: Crédito extraconcursal reconhecido
        if "extraconcursal" in texto and "reconhec" in texto:
            proc.q08_credito_extraconcursal = "SIM"
        elif "extraconcursal" in texto:
            proc.q08_credito_extraconcursal = "Em discussão"
        else:
            proc.q08_credito_extraconcursal = "Não identificado"
        
        # Q9: Recursos
        if "agravo" in movs or "apelação" in movs or "recurso" in movs:
            proc.q09_recursos = "SIM - Verificar tipo"
        else:
            proc.q09_recursos = "Não identificado"
        
        # Q10: Bens essenciais vs busca/apreensão
        if "busca e apreensão" in texto and any(e in texto for e in self.ESSENCIALIDADE):
            proc.q10_bens_busca = "Conflito identificado"
        elif "busca e apreensão" in texto:
            proc.q10_bens_busca = "Há pedido de busca/apreensão"
        else:
            proc.q10_bens_busca = "Não identificado"
        
        # Q11: Stay period
        if "prorrogação" in movs and "prazo" in movs:
            proc.q11_stay_period = "Prorrogado"
        elif "processamento" in movs and "deferido" in movs:
            proc.q11_stay_period = "Ativo"
        elif "encerr" in movs or "falência" in movs:
            proc.q11_stay_period = "Encerrado"
        else:
            proc.q11_stay_period = "Verificar manualmente"
        
        # Q12: Executar garantias
        if proc.q11_stay_period in ["Ativo", "Prorrogado"]:
            proc.q12_executar_garantias = "NÃO (Stay Period vigente)"
        else:
            proc.q12_executar_garantias = "Possivelmente SIM"
        
        # Q13: Plano RJ
        if "homologação" in movs and "plano" in movs:
            proc.q13_plano_rj = "Homologado"
        elif "aprovação" in movs and "plano" in movs:
            proc.q13_plano_rj = "Aprovado"
        elif "apresentação" in movs and "plano" in movs:
            proc.q13_plano_rj = "Apresentado"
        else:
            proc.q13_plano_rj = "Aguardando/Em elaboração"
        
        # Q14: AGC/Mediação
        if "assembleia" in movs:
            proc.q14_agc_mediacao = "AGC realizada/marcada"
        elif "mediação" in movs:
            proc.q14_agc_mediacao = "Mediação em andamento"
        else:
            proc.q14_agc_mediacao = "Não identificado"
        
        return proc


# =============================================================================
# EXTRATOR PRINCIPAL
# =============================================================================

class ExtratorTJSP:
    """Extrator de dados do TJSP"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.analisador = Analisador()
        os.makedirs(self.config.DIR_SAIDA, exist_ok=True)
        os.makedirs(self.config.DIR_PDFS, exist_ok=True)
    
    def _extrair_partes(self, page: Page, proc: Processo) -> Processo:
        """Extrai informações das partes do processo"""
        try:
            # Clica em "Mais" para expandir partes se disponível
            try:
                mais_btn = page.locator("text=Mais").first
                if mais_btn.is_visible():
                    mais_btn.click()
                    time.sleep(0.5)
            except:
                pass
            
            tabela = page.locator("#tablePartesPrincipais")
            if tabela.is_visible():
                linhas = tabela.locator("tr").all()
                
                tipo_atual = ""
                for linha in linhas:
                    texto = linha.inner_text().strip()
                    
                    if "Reqte" in texto or "Requerente" in texto:
                        tipo_atual = "requerente"
                        # Extrai nome após ":"
                        partes = texto.split("\n")
                        for p in partes:
                            if ":" in p and "Advogado" not in p:
                                nome = p.split(":")[-1].strip()
                                if nome and len(nome) > 2:
                                    proc.requerente = nome
                                    break
                    
                    elif "Interessado" in texto or "Interessd" in texto:
                        tipo_atual = "interessado"
                        partes = texto.split("\n")
                        for p in partes:
                            if ":" in p and "Advogado" not in p:
                                nome = p.split(":")[-1].strip()
                                if nome and len(nome) > 2:
                                    proc.interessados.append(nome)
                                    break
                    
                    elif "Credor" in texto:
                        tipo_atual = "credor"
                        partes = texto.split("\n")
                        for p in partes:
                            if ":" in p and "Advogado" not in p:
                                nome = p.split(":")[-1].strip()
                                if nome and len(nome) > 2:
                                    proc.credores.append(nome)
                                    break
                    
                    elif "Perito" in texto:
                        partes = texto.split("\n")
                        for p in partes:
                            if ":" in p and "Advogado" not in p:
                                nome = p.split(":")[-1].strip()
                                if nome and len(nome) > 2:
                                    proc.perito = nome
                                    break
                    
                    # Extrai advogados
                    if "Advogado:" in texto or "Advogada:" in texto:
                        for p in texto.split("\n"):
                            if "Advogado:" in p or "Advogada:" in p:
                                nome = p.replace("Advogado:", "").replace("Advogada:", "").strip()
                                if nome and len(nome) > 3:
                                    if tipo_atual == "requerente":
                                        proc.advogados_requerente.append(nome)
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair partes: {e}")
        
        return proc
    
    def _extrair_movimentacoes(self, page: Page, proc: Processo) -> Processo:
        """Extrai movimentações do processo"""
        try:
            # Tenta expandir todas as movimentações
            try:
                link_todas = page.locator("#linkTodasMovimentacoes")
                if link_todas.is_visible():
                    link_todas.click()
                    time.sleep(1)
            except:
                pass
            
            # Busca tabela de movimentações
            tabela = page.locator("#tabelaTodasMovimentacoes, #tabelaUltimasMovimentacoes").first
            if tabela.is_visible():
                linhas = tabela.locator("tr").all()
                
                for linha in linhas:
                    try:
                        texto = linha.inner_text().strip()
                        if texto and len(texto) > 5:
                            # Tenta extrair data e descrição
                            partes = texto.split("\n")
                            if len(partes) >= 2:
                                proc.movimentacoes.append({
                                    "data": partes[0].strip()[:10],
                                    "descricao": " ".join(partes[1:]).strip()
                                })
                            else:
                                proc.movimentacoes.append({
                                    "data": "",
                                    "descricao": texto
                                })
                    except:
                        pass
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair movimentações: {e}")
        
        return proc
    
    def extrair_processo(self, numero: str) -> Processo:
        """Extrai dados completos de um processo"""
        proc = Processo(numero=numero)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.config.HEADLESS,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                print(f"\n🔍 Processando: {numero}")
                
                # Acessa portal
                page.goto(self.config.URL_TJSP_1GRAU, timeout=self.config.TIMEOUT_PAGINA)
                
                # Seleciona busca por número
                page.locator("#radioNumeroUnificado").click()
                time.sleep(0.5)
                
                # Prepara número
                num_limpo = re.sub(r'\D', '', numero)
                parte1 = num_limpo[:-4]
                parte2 = num_limpo[-4:]
                
                # Preenche campos
                page.locator("#numeroDigitoAnoUnificado").clear()
                page.locator("#numeroDigitoAnoUnificado").press_sequentially(parte1, delay=self.config.DELAY_DIGITACAO)
                time.sleep(0.3)
                page.locator("#foroNumeroUnificado").clear()
                page.locator("#foroNumeroUnificado").press_sequentially(parte2, delay=self.config.DELAY_DIGITACAO)
                time.sleep(0.5)
                
                # Consulta
                page.locator("#botaoConsultarProcessos").click()
                
                # Aguarda resultado
                try:
                    page.wait_for_selector("#classeProcesso, #mensagemRetorno", timeout=self.config.TIMEOUT_ELEMENTO)
                except:
                    pass
                
                # Verifica sucesso
                if page.locator("#classeProcesso").is_visible():
                    print("   ✅ Processo encontrado!")
                    proc.status = "Sucesso"
                    
                    # Dados básicos
                    proc.classe = page.locator("#classeProcesso").inner_text().strip()
                    
                    try:
                        proc.assunto = page.locator("#assuntoProcesso").inner_text().strip()
                    except:
                        pass
                    
                    try:
                        proc.juiz = page.locator("#juizProcesso").inner_text().strip()
                    except:
                        pass
                    
                    try:
                        # Foro
                        foro_elem = page.locator("span:has-text('Foro')").locator("..").locator("span").last
                        if foro_elem.is_visible():
                            proc.foro = foro_elem.inner_text().strip()
                    except:
                        pass
                    
                    try:
                        # Vara
                        vara_elem = page.locator("span:has-text('Vara')").locator("..").locator("span").last
                        if vara_elem.is_visible():
                            proc.vara = vara_elem.inner_text().strip()
                    except:
                        pass
                    
                    try:
                        proc.data_distribuicao = page.locator("#dataHoraDistribuicaoProcesso").inner_text().strip()
                    except:
                        pass
                    
                    # Extrai partes
                    proc = self._extrair_partes(page, proc)
                    
                    # Extrai movimentações
                    proc = self._extrair_movimentacoes(page, proc)
                    
                    # Texto completo para análise
                    proc.texto_completo = page.locator("body").inner_text()
                    
                    # Análise jurimétrica
                    proc = self.analisador.analisar(proc)
                    print("   🧠 Análise jurimétrica concluída")
                    
                else:
                    if page.locator("#mensagemRetorno").is_visible():
                        proc.erro = page.locator("#mensagemRetorno").inner_text().strip()
                    proc.status = "Não encontrado"
                    print(f"   ❌ {proc.erro}")
                
            except Exception as e:
                proc.status = "Erro"
                proc.erro = str(e)
                print(f"   ❌ Erro: {e}")
            
            finally:
                browser.close()
        
        return proc
    
    def extrair_lote(self, processos: List[str]) -> List[Processo]:
        """Extrai múltiplos processos"""
        resultados = []
        total = len(processos)
        
        print(f"\n{'='*60}")
        print(f"🚀 EXTRAÇÃO EM LOTE - {total} processos")
        print(f"{'='*60}")
        
        for i, num in enumerate(processos, 1):
            print(f"\n[{i}/{total}]", end="")
            proc = self.extrair_processo(num)
            resultados.append(proc)
            
            if i < total:
                print(f"   ⏳ Aguardando {self.config.DELAY_ENTRE_PROCESSOS}s...")
                time.sleep(self.config.DELAY_ENTRE_PROCESSOS)
        
        return resultados
    
    def gerar_relatorio(self, processos: List[Processo], nome: str = None) -> str:
        """Gera relatório Excel"""
        if not nome:
            nome = f"relatorio_jurimetria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        caminho = os.path.join(self.config.DIR_SAIDA, nome)
        
        dados = []
        for p in processos:
            dados.append({
                "Processo": p.numero,
                "Status": p.status,
                "Classe": p.classe,
                "Assunto": p.assunto,
                "Foro": p.foro,
                "Vara": p.vara,
                "Juiz": p.juiz,
                "Requerente": p.requerente,
                "Advogados": ", ".join(p.advogados_requerente[:2]),
                "Interessados": ", ".join(p.interessados[:2]),
                "Credores": ", ".join(p.credores[:2]),
                "Perito/Administrador": p.perito,
                "Q1 - Bancos/Veículos": p.q01_bancos_veiculos,
                "Q2 - Pedidos": p.q02_pedidos,
                "Q3 - Garantias Extraconcursais": p.q03_garantias_extraconcursais,
                "Q4 - Essencialidade": p.q04_essencialidade,
                "Q5 - Teses": p.q05_teses,
                "Q6 - Entendimento Tribunal": p.q06_entendimento,
                "Q7 - Escritório": p.q07_escritorio,
                "Q8 - Crédito Extraconcursal": p.q08_credito_extraconcursal,
                "Q9 - Recursos": p.q09_recursos,
                "Q10 - Bens vs Busca/Apreensão": p.q10_bens_busca,
                "Q11 - Stay Period": p.q11_stay_period,
                "Q12 - Executar Garantias": p.q12_executar_garantias,
                "Q13 - Plano RJ": p.q13_plano_rj,
                "Q14 - AGC/Mediação": p.q14_agc_mediacao,
                "Erro": p.erro
            })
        
        df = pd.DataFrame(dados)
        df.to_excel(caminho, index=False)
        print(f"\n💾 Relatório salvo: {caminho}")
        
        return caminho
    
    def gerar_resumo(self, processos: List[Processo]) -> Dict:
        """Gera resumo estatístico das 14 questões"""
        sucesso = [p for p in processos if p.status == "Sucesso"]
        total = len(sucesso)
        
        if total == 0:
            return {"total": 0, "sucesso": 0}
        
        resumo = {
            "total_processos": len(processos),
            "extraidos_sucesso": total,
            "questoes": {
                "Q1_bancos_veiculos": {
                    "sim": len([p for p in sucesso if "SIM" in p.q01_bancos_veiculos]),
                    "percentual": f"{len([p for p in sucesso if 'SIM' in p.q01_bancos_veiculos])/total*100:.1f}%"
                },
                "Q3_garantias": {
                    "sim": len([p for p in sucesso if p.q03_garantias_extraconcursais == "SIM"]),
                    "percentual": f"{len([p for p in sucesso if p.q03_garantias_extraconcursais == 'SIM'])/total*100:.1f}%"
                },
                "Q4_essencialidade": {
                    "sim": len([p for p in sucesso if p.q04_essencialidade == "SIM"]),
                    "percentual": f"{len([p for p in sucesso if p.q04_essencialidade == 'SIM'])/total*100:.1f}%"
                },
                "Q11_stay_period": {
                    "ativo": len([p for p in sucesso if p.q11_stay_period in ["Ativo", "Prorrogado"]]),
                    "percentual": f"{len([p for p in sucesso if p.q11_stay_period in ['Ativo', 'Prorrogado']])/total*100:.1f}%"
                }
            }
        }
        
        return resumo


# =============================================================================
# EXECUÇÃO
# =============================================================================

def main():
    """Execução principal"""
    
    # Lista de processos para extração
    PROCESSOS = [
        "1001535-69.2025.8.26.0260",  # Metalcore - Mills Pesados
    ]
    
    # Configuração
    config = Config(HEADLESS=True)
    
    # Extrator
    extrator = ExtratorTJSP(config)
    
    print("\n" + "="*60)
    print("   EXTRATOR JURIMÉTRICO v2.0 - RECUPERAÇÃO JUDICIAL")
    print("   Respondendo às 14 Questões do Plano de Estudo")
    print("="*60)
    
    # Extração
    resultados = extrator.extrair_lote(PROCESSOS)
    
    # Relatório
    arquivo = extrator.gerar_relatorio(resultados)
    
    # Resumo
    resumo = extrator.gerar_resumo(resultados)
    
    print("\n" + "="*60)
    print("   📊 RESUMO")
    print("="*60)
    print(f"Total: {resumo.get('total_processos', 0)}")
    print(f"Sucesso: {resumo.get('extraidos_sucesso', 0)}")
    
    # Exibe dados do primeiro processo como exemplo
    if resultados and resultados[0].status == "Sucesso":
        p = resultados[0]
        print(f"\n📋 EXEMPLO - Processo {p.numero}:")
        print(f"   Classe: {p.classe}")
        print(f"   Assunto: {p.assunto}")
        print(f"   Requerente: {p.requerente}")
        print(f"   Q1 (Bancos/Veículos): {p.q01_bancos_veiculos}")
        print(f"   Q2 (Pedidos): {p.q02_pedidos}")
        print(f"   Q7 (Escritório): {p.q07_escritorio}")
    
    # Salva resumo JSON
    json_path = os.path.join(config.DIR_SAIDA, "resumo.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resumo JSON: {json_path}")
    print("\n✅ EXTRAÇÃO CONCLUÍDA")


if __name__ == "__main__":
    main()
