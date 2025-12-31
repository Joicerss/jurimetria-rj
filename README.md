# 📊 Jurimetria RJ - Extrator de Processos de Recuperação Judicial

Sistema automatizado de extração e análise jurimétrica de processos de Recuperação Judicial do Tribunal de Justiça de São Paulo (TJSP).

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Objetivo

Este projeto foi desenvolvido para responder às **14 questões críticas** sobre processos de Recuperação Judicial, utilizando técnicas de jurimetria e automação de coleta de dados:

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

## 🚀 Funcionalidades

- ✅ Extração automatizada de dados do portal e-SAJ/TJSP
- ✅ Análise semântica para responder às 14 questões
- ✅ Geração de relatórios em Excel
- ✅ Exportação de resumos em JSON
- ✅ Arquitetura modular e escalável
- ✅ Configuração flexível (headless/visual)

## 📁 Estrutura do Projeto

```
jurimetria-rj/
├── README.md                 # Este arquivo
├── requirements.txt          # Dependências do projeto
├── src/
│   ├── extrator_jurimetria.py    # Script principal
│   └── teste_processo.py         # Script de teste
├── docs/
│   ├── respostas_plano_de_estudo.md  # Análise das 14 questões
│   ├── prompt_replicavel.md          # Guia de replicação
│   └── resultado_teste.png           # Screenshot de exemplo
└── resultados/
    ├── relatorio_jurimetria_*.xlsx   # Relatórios gerados
    └── resumo.json                   # Estatísticas agregadas
```

## ⚙️ Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/jurimetria-rj.git
cd jurimetria-rj
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o navegador Chromium para o Playwright:
```bash
python -m playwright install chromium
```

## 🔧 Uso

### Executar o Extrator

1. Edite a lista de processos no arquivo `src/extrator_jurimetria.py`:
```python
PROCESSOS = [
    "1001535-69.2025.8.26.0260",  # Adicione seus processos aqui
    "1002086-35.2023.8.26.0100",
]
```

2. Execute o script:
```bash
cd src
python extrator_jurimetria.py
```

3. Os resultados serão salvos na pasta `resultados/`.

### Teste Rápido

Para testar com um único processo:
```bash
cd src
python teste_processo.py
```

## 📊 Exemplo de Saída

```
============================================================
   EXTRATOR JURIMÉTRICO v2.0 - RECUPERAÇÃO JUDICIAL
============================================================

🔍 Processando: 1001535-69.2025.8.26.0260
   ✅ Processo encontrado!
   🧠 Análise jurimétrica concluída

📋 EXEMPLO - Processo 1001535-69.2025.8.26.0260:
   Classe: Tutela Cautelar Antecedente
   Assunto: Recuperação judicial e Falência
   Q1 (Bancos/Veículos): SIM - Bancos E Veículos
   Q2 (Pedidos): Tutela Cautelar, Recuperação Judicial
   Q7 (Escritório): Gustavo Bismarchi Motta

✅ EXTRAÇÃO CONCLUÍDA
```

## 📈 Roadmap

- [ ] Adicionar suporte para download de PDFs
- [ ] Implementar análise de conteúdo de documentos
- [ ] Expandir para outros tribunais (TJRJ, TJMG)
- [ ] Criar dashboard interativo com Streamlit
- [ ] Integrar com API DataJud do CNJ

## 📚 Documentação

- [Respostas ao Plano de Estudo](docs/respostas_plano_de_estudo.md)
- [Guia de Replicação e Escalabilidade](docs/prompt_replicavel.md)

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👩‍💻 Autora

Desenvolvido como parte do **Plano de Estudo Consolidado para Jurimetria**.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!
