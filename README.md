# Artefato 2 — Predição de Churn Vitaliza (Inteli MBA · Módulo 2 · Semana 10)

Entrega final do Artefato 2: **modelo preditivo de churn validado**, **explicabilidade
(SHAP + linguagem natural)** e **interface web** que serve a inferência.

## Estrutura

```
Entrega_Artefato2_Semana10/
├── aplicacao_modelo/      ← APLICAÇÃO (serviço web de inferência) + pipeline de treino
│   ├── train_churn_model.py        pipeline de TREINAMENTO (gera os .joblib)
│   ├── eda_and_segmentation.py     EDA + KMeans → segmentation_artifact.joblib
│   ├── app.py                      pipeline de INFERÊNCIA (Streamlit) — o app
│   ├── churn_model.joblib          modelo servido (LogReg, SEM vazamento)
│   ├── churn_model_full.joblib     modelo COM vazamento (só comparação didática)
│   ├── segmentation_artifact.joblib
│   ├── model_metrics.json · gym_churn_us.csv · charts/
│   ├── requirements.txt · Dockerfile · run_app.bat · .streamlit/
│   ├── REAVALIACAO_MODELO.md        respostas das atividades (Aulas 06/07/09)
│   └── README_DEPLOY.md             arquitetura, deploy e monitoramento/drift
│
├── relatorio_web/         ← RELATÓRIO analítico (React) com a Seção 10 acessando o app
│   ├── frontend/          SPA (abrir relatorio_web/frontend/dist/index.html offline)
│   ├── python/            compute_data.py (gera os dados do relatório)
│   └── dados/             gym_churn_us.csv
│
├── requirements.txt       (cópia p/ o Streamlit Cloud achar as dependências)
└── README.md
```

## Como rodar

**Aplicação (Streamlit):**
```bash
cd aplicacao_modelo
pip install -r requirements.txt
streamlit run app.py            # http://localhost:8501
```
(ou `run_app.bat` no Windows — instala, treina se faltar e sobe a app)

**Relatório (React):** abra `relatorio_web/frontend/dist/index.html` no navegador
(funciona offline). Para desenvolver: `cd relatorio_web/frontend && npm install && npm run dev`.

## Mapa do checklist do Artefato 2

| Item | Onde |
|---|---|
| Pipeline de treino + inferência (serializado) | `train_churn_model.py` → `.joblib` → `app.py` |
| Modelo sem overfit / sem vazamento / métricas | aba **Validação** do app · `REAVALIACAO_MODELO.md` |
| Explicabilidade: SHAP (global + local) | abas **Explicabilidade** e **Novo cliente** |
| Explicabilidade: feature importances | aba **Explicabilidade** |
| Explicação em linguagem natural | aba **Novo cliente** (template fiel ao SHAP; plugue OpenRouter pronto) |
| Serviço web serve a inferência | `app.py` (Streamlit) |
| Aderente ao deploy | `requirements.txt` fixado · `Dockerfile` · `.streamlit/` · `README_DEPLOY.md` |
| Relatório com seção que acessa o app | `relatorio_web` — **Seção 10. Aplicação Interativa** |

## Modelo servido (resumo)

Regressão Logística tunada, **sem as 2 features co-temporais ao churn** —
ROC-AUC **0,957** · recall **0,915** · gap de overfit **~0** · validação cruzada 5-fold.
Explicabilidade local por **SHAP** (`LinearExplainer`). Detalhes e respostas das
atividades em `aplicacao_modelo/REAVALIACAO_MODELO.md`.

---
MBA em IA e Dados para Negócios · Inteli · Módulo 2 · Grupo 10 · 2026
