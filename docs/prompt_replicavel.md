# Prompt Replicável e Escalável para Análise Jurimétrica de Processos

**Autor:** Manus AI  
**Data:** 29 de Dezembro de 2025  
**Versão:** 1.0

---

## 1. Objetivo

Este documento serve como um guia completo para utilizar, replicar e escalar o **Sistema de Análise Jurimétrica Automatizada**. O objetivo deste "prompt" (instrução) é capacitar qualquer usuário a executar análises jurimétricas em processos de recuperação judicial, começando com o Tribunal de Justiça de São Paulo (TJSP) e, posteriormente, expandindo para outras fontes de dados.

O sistema foi construído de forma modular e configurável, permitindo que seja facilmente adaptado para diferentes necessidades de pesquisa e análise.

## 2. Arquitetura do Sistema

O coração do sistema é o script `extrator_jurimetria_v2.py`. Ele foi projetado com os seguintes componentes principais:

- **Configuração (`Config`)**: Uma classe que centraliza todas as variáveis que podem ser alteradas, como URLs, timeouts, e diretórios. Isso evita a necessidade de modificar o código principal para simples ajustes.
- **Estrutura de Dados (`Processo`)**: Uma classe que define um modelo padrão para armazenar todas as informações coletadas de um processo. Isso garante consistência e facilita a análise posterior.
- **Analisador (`Analisador`)**: O cérebro do sistema. Contém os dicionários de palavras-chave e a lógica para analisar os textos extraídos e responder às 14 questões críticas do plano de estudo.
- **Extrator (`ExtratorTJSP`)**: O robô (bot) que utiliza o Playwright para navegar no portal do TJSP, inserir os dados do processo, extrair as informações da página e orquestrar a análise.
- **Execução (`main`)**: A função principal que define a lista de processos a serem analisados, inicializa o extrator e gera os relatórios finais.

## 3. Como Replicar a Análise (Passo a Passo)

Para executar a mesma análise em um novo conjunto de processos, siga os passos abaixo.

### **Passo 1: Configurar a Lista de Processos**

1.  Abra o arquivo `extrator_jurimetria_v2.py` em um editor de texto.
2.  Navegue até a função `main()` no final do arquivo.
3.  Localize a lista `PROCESSOS`.
4.  Adicione ou substitua os números dos processos que você deseja analisar. Mantenha o formato de string (entre aspas) e separe os números por vírgulas.

```python
# Exemplo de como adicionar mais processos
def main():
    PROCESSOS = [
        "1001535-69.2025.8.26.0260",  # Processo 1
        "1002086-35.2023.8.26.0100",  # Processo 2 (Ex: Americanas)
        "0038939-23.2020.8.26.0100",  # Processo 3 (Ex: Livraria Cultura)
        # Adicione quantos processos desejar aqui
    ]
    # ... resto do código ...
```

### **Passo 2: Executar o Extrator**

1.  Abra um terminal ou prompt de comando.
2.  Navegue até o diretório onde o projeto foi salvo (`/home/ubuntu/projeto_extracao/`).
3.  Execute o seguinte comando:

```bash
python3 extrator_jurimetria_v2.py
```

4.  O sistema iniciará a extração, exibindo o progresso de cada processo no terminal.

### **Passo 3: Analisar os Resultados**

Após a conclusão, o sistema gerará automaticamente os seguintes arquivos no diretório `resultados/`:

1.  **Relatório em Excel (`relatorio_jurimetria_AAAAMMDD_HHMMSS.xlsx`)**: Uma planilha detalhada contendo uma linha para cada processo e colunas com todos os dados extraídos e as respostas para as 14 questões. Ideal para análise manual e criação de gráficos.
2.  **Resumo em JSON (`resumo.json`)**: Um arquivo com estatísticas agregadas, como o número total de processos analisados com sucesso e a contagem para as principais questões (Q1, Q3, Q4, Q11).

## 4. Como Escalar o Sistema

O verdadeiro poder da jurimetria está na escala. Aqui estão as diretrizes para expandir e aprimorar o sistema.

### **Escala 1: Aprimorando a Análise (Inteligência)**

O componente mais fácil de escalar é o `Analisador`. Para melhorar a precisão das respostas:

- **Expanda os Dicionários:** Abra o `extrator_jurimetria_v2.py` e localize a classe `Analisador`. Adicione novos sinônimos, nomes de bancos, tipos de veículos ou termos jurídicos aos dicionários (`BANCOS`, `VEICULOS`, etc.). Quanto mais completo o dicionário, mais inteligente será a análise.

```python
class Analisador:
    BANCOS = [
        "banco", "bradesco", "itaú", "santander", # ...
        "banco do brasil", "daycoval", "banco pan" # Adicione novos bancos aqui
    ]
    # ... outros dicionários ...
```

### **Escala 2: Adaptando para Outros Tribunais**

Para extrair dados de outros tribunais (ex: TJRJ, TJMG), o processo é mais complexo, pois envolve adaptar o robô (`ExtratorTJSP`) para um novo layout de site.

1.  **Crie um Novo Extrator:** Crie uma nova classe, por exemplo, `ExtratorTJRJ`, seguindo a estrutura da `ExtratorTJSP`.
2.  **Mapeie os Seletores:** O principal trabalho é identificar os novos seletores (IDs e classes CSS) dos elementos da página do novo tribunal (campos de busca, botão de consulta, tabelas de dados). Ferramentas como o "Inspecionar Elemento" do navegador são essenciais aqui.
3.  **Ajuste a Lógica de Extração:** Modifique os métodos `_extrair_partes` e `_extrair_movimentacoes` para ler a estrutura HTML específica do novo site.
4.  **Integre no `main`:** Na função `main`, você pode adicionar uma lógica para escolher qual extrator usar com base no número do processo.

### **Escala 3: Análise de Documentos PDF**

Esta é a evolução mais estratégica do sistema.

1.  **Lógica de Download:** No `ExtratorTJSP`, adicione um método para identificar e clicar nos links que abrem os documentos PDF das decisões e petições.
2.  **Biblioteca de Leitura de PDF:** Utilize bibliotecas Python como `PyPDF2` ou `pdfplumber` para abrir os PDFs baixados e extrair seu texto.
3.  **Análise de Conteúdo:** Passe o texto extraído do PDF para o `Analisador`. Isso permitirá confirmar com 100% de certeza a existência de garantias, pedidos de essencialidade e os detalhes das teses, refinando drasticamente a qualidade das respostas.

## 5. Conclusão

Este prompt fornece um framework completo para a realização de estudos jurimétricos. Começando com a replicação da análise no TJSP, é possível escalar a solução em inteligência (aprimorando o `Analisador`) e em alcance (criando novos extratores e adicionando a leitura de PDFs). A metodologia modular garante que o sistema possa crescer e se adaptar a novas perguntas e fontes de dados, consolidando-se como uma poderosa ferramenta para a tomada de decisão baseada em dados no campo do Direito.
