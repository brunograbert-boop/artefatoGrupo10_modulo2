# Preditor de Churn Vitaliza — Serviço Web e Deploy

Serviço de inferência de churn do case Vitaliza (Inteli MBA — Módulo 2, Artefato 2).
Arquitetura **pipeline de treinamento → artefato serializado → pipeline de inferência**.

## Arquitetura (Aula 07)

```
 gym_churn_us.csv
        │
        ▼
 train_churn_model.py            eda_and_segmentation.py
 (PIPELINE DE TREINAMENTO)       (PIPELINE DE SEGMENTAÇÃO)
        │                                  │
        ▼                                  ▼
 churn_model.joblib              segmentation_artifact.joblib
 churn_model_full.joblib         (KMeans + scaler + personas)
 model_metrics.json
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
                    app.py  ← PIPELINE DE INFERÊNCIA (Streamlit)
            joblib.load → predict_proba → SHAP → explicação
```

- **Treino e inferência são separados.** `app.py` nunca treina: só carrega os `.joblib`
  com `joblib.load` (cacheado por `@st.cache_resource`).
- **Pré-processamento embutido:** o `StandardScaler` vive dentro do `Pipeline`
  serializado, então treino e inferência usam exatamente a mesma transformação.
- **Modelo servido:** Regressão Logística tunada, **sem features vazadoras** (11 features).
- **Explicabilidade:** SHAP `LinearExplainer` (local, por cliente) + importância global.

## Rodar localmente

```bash
cd aplicacao_modelo
pip install -r requirements.txt
python train_churn_model.py        # gera os .joblib (1ª vez)
python eda_and_segmentation.py     # gera o artefato de segmentação
streamlit run app.py               # http://localhost:8501
```

Ou simplesmente: `run_app.bat` (Windows) — instala deps, treina se faltar e sobe a app.

## Colocar no ar — Streamlit Community Cloud (recomendado, grátis)

A pasta de entrega (`Entrega_Artefato2_Semana10/`) é a raiz do repositório.

1. Suba o repositório para o GitHub, **incluindo os `.joblib`** (são pequenos: ~330 KB + ~20 KB).
2. Em [share.streamlit.io](https://share.streamlit.io), conecte o repo e aponte o
   *Main file path* para **`aplicacao_modelo/app.py`**.
3. O `requirements.txt` da **raiz do repositório** é o que o Streamlit Cloud instala
   (cópia idêntica ao de `aplicacao_modelo/`).
4. Em *Advanced settings*, selecione **Python 3.12+**.
5. As versões estão **fixadas** — importante: o `.joblib` é um pickle do scikit-learn;
   manter `scikit-learn==1.8.0` evita erro de versão ao carregar o modelo.
6. Depois de no ar, cole a URL na constante `APP_URL` em
   `relatorio_web/frontend/src/sections/Aplicacao.tsx` e rode `npm run build` para o
   relatório embutir o app (botão + iframe na Seção 10).

> Para habilitar a explicação via LLM (Aula 09), defina `OPENROUTER_API_KEY` em
> *App settings → Secrets*. Sem a chave, a app usa a explicação por template (fiel ao SHAP).

## Deploy containerizado (alternativa — Render / Railway / Cloud Run)

`Dockerfile` incluído. A plataforma injeta `$PORT`:

```bash
docker build -t churn-vitaliza .
docker run -p 8501:8501 churn-vitaliza
```

## Monitoramento e validação contínua (Aula 07, critério 4 — evitar drift)

Em produção, operacionalizar:

| O que monitorar | Como | Gatilho de ação |
|---|---|---|
| **Data drift** | PSI / teste KS das 11 features vs. distribuição de treino | PSI > 0,2 → investigar/retreinar |
| **Performance** | Recall e ROC-AUC em janelas mensais (quando o churn real chega) | Queda de recall > 10% → retreinar |
| **Underperforming segments** | Recall por cluster/persona | Segmento abaixo da média → revisar |
| **Label drift** | Taxa de churn real vs. taxa prevista | Divergência sustentada → recalibrar threshold |

- **Cadência de retreino:** a cada 4–8 semanas ou disparada por gatilho.
- **Deploy seguro de novas versões:** *shadow deployment* (modelo novo recebe o tráfego
  em paralelo só para validação) antes de promover; ou *canary*.

## Arquivos

| Arquivo | Papel |
|---|---|
| `train_churn_model.py` | Pipeline de treinamento (gera os modelos + métricas) |
| `eda_and_segmentation.py` | EDA + KMeans → artefato de segmentação |
| `app.py` | Pipeline de inferência + interface web (Streamlit) |
| `churn_model.joblib` | Modelo servido (LogReg, **sem vazamento**) |
| `churn_model_full.joblib` | Modelo **com vazamento** (só comparação didática) |
| `segmentation_artifact.joblib` | KMeans + scaler + personas |
| `model_metrics.json` | Comparação completa de métricas |
| `REAVALIACAO_MODELO.md` | Respostas das atividades das Aulas 06/07/09 |
