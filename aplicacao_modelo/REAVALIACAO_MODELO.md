# Reavaliação do Modelo de Churn — Vitaliza (Artefato 2)

Respostas às atividades das **Aula 06 (Métricas e validação)**, **Aula 07 (Deploy)** e
**Aula 09 (Explicabilidade com SHAP + LLM)**. Todos os números vêm de
`model_metrics.json`, gerado por `train_churn_model.py` (split estratificado 80/20,
`random_state=42`, 5-fold CV).

Base: **4.000 clientes**, churn de **26,5%**. Modelo servido: **Regressão Logística
tunada, sem features vazadoras (11 features)**.

---

## Parte A — Sobreajuste e desbalanceamento (Aula 06, slides 36–38)

### A.1 O dataset está desbalanceado? Isso impactou? Quais métricas validam?
Sim — **73,5% permanecem / 26,5% cancelam** (~2,8:1). Impacto: a **acurácia engana**.
Um modelo "burro" que prevê "ninguém cancela" teria ~73,5% de acurácia sem acertar
**nenhum** churn. Por isso avaliamos com métricas adequadas a classes desbalanceadas:

| Métrica | Por que olhamos |
|---|---|
| **Recall** (sensibilidade) | % de churners realmente capturados — o que importa para reter |
| **Precision** | % de acerto entre os sinalizados — custo de intervenção desnecessária |
| **F1** | equilíbrio precision × recall |
| **ROC-AUC** | separabilidade independente de threshold |
| **Matriz de confusão** | enxergar FP vs FN diretamente |

**Tratamento do desbalanceamento:** `class_weight='balanced'` na Regressão Logística
(penaliza mais o erro na classe minoritária). Resultado no modelo servido:
**recall 0,915** com acurácia 0,885 — ou seja, capturamos **194 dos 212 churners**
do teste (só 18 falsos negativos), exatamente o que a acurácia sozinha esconderia.

### A.2 O modelo ficou sobreajustado? Quais métricas validam?
**Não.** Medimos o **gap AUC treino − teste** e a **validação cruzada (5 folds)**:

| Modelo (sem vazamento) | AUC treino | AUC teste | **Gap** | CV AUC (5 folds) |
|---|---|---|---|---|
| **LogReg tunada (servido)** | 0,958 | **0,957** | **+0,001** | 0,956 ± 0,009 |
| Gradient Boosting tunado | 0,970 | 0,956 | +0,014 | 0,956 ± 0,009 |
| Random Forest | 0,983 | 0,950 | +0,033 | 0,954 ± 0,009 |

Regra prática da aula: **gap > 0,10 ⇒ overfit**. O modelo servido tem gap de **0,001**
e o AUC de validação cruzada (0,956) bate com o de teste — generaliza bem.

### A.3 O que foi feito para resolver o sobreajuste?
1. **Modelos de baixa complexidade / regularizados:** LogReg com regularização L2
   (fine tuning escolheu `C=0,5`), árvores rasas (GB `max_depth=2`, RF `max_depth=8`).
2. **Validação cruzada estratificada** (5 folds) além do holdout, para não confiar num
   único split.
3. **Seleção por generalização:** escolhemos o modelo por ROC-AUC de teste/CV, não por
   desempenho no treino. (O Random Forest, com gap 0,033, foi preterido.)

### A.4 O que foi feito para resolver o desbalanceamento?
`class_weight='balanced'` (reponderação da classe minoritária) + foco em
recall/F1/ROC-AUC + **seção interativa de Thresholds** no app, que permite mover o
ponto de corte e ver o trade-off precision×recall (e a matriz de confusão recalculada).
Resultado: recall de **0,915** já em `τ=0,50`.

---

## Parte B — Vazamento e variáveis futuras (Aula 06, slide 39)

Classificamos cada variável pelo esquema do slide 33 (tabela completa na aba
**Validação** do app e em `model_metrics.json → leakage_table`).

### B.1 Existe variável que vaza o target?
**Sim — 2 variáveis "proxy tardio" (co-temporais ao churn):**

| Variável | Corr. c/ churn | Classe | Conclusão |
|---|---|---|---|
| `Avg_class_frequency_current_month` | −0,41 | **Proxy tardio** | A frequência **do mês corrente**: quem está saindo já parou de ir. O sinal só se materializa **junto** com o churn — tarde demais para intervir. |
| `Month_to_end_contract` | −0,38 | **Proxy tardio** | Meses até o fim do contrato: mecanicamente ligado ao momento de **não renovar**. Co-temporal ao evento. |

Não há *vazamento direto* (nenhuma feature É o target), mas essas duas se comportam
como proxies que só existem no instante do desfecho.

**Prova quantitativa do vazamento** (o que justifica removê-las):

| Cenário | Melhor modelo | ROC-AUC | Recall | Gap |
|---|---|---|---|---|
| **COM** as 2 variáveis (13 features) | Gradient Boosting | 0,979 | 0,863 | +0,017 |
| **SEM** elas (11 features) — **servido** | LogReg tunada | 0,957 | 0,915 | +0,001 |

Remover as duas custou apenas **−0,022 de ROC-AUC**, mas entrega um modelo **honesto**,
que só usa informação disponível **antes** do churn — utilizável para intervir a tempo.
(O modelo com vazamento fica salvo em `churn_model_full.joblib` só para esta comparação.)

### B.2 Existe variável que exige informações futuras?
As **mesmas duas**. Para um cliente novo, `Avg_class_frequency_current_month` ainda não
é informativa e `Month_to_end_contract` antecipa o desfecho — por isso o formulário do
app **não as solicita**. As 11 features restantes (cadastro, contrato, tempo de casa,
frequência histórica, gasto extra) estão disponíveis cedo e são **aceitáveis**.

---

## Parte C — Deploy (Aula 07, slide 20)

| Critério | Resposta |
|---|---|
| **1. Foi feito fine tuning?** | Sim. `GridSearchCV` (5-fold, scoring ROC-AUC) sobre GB (`n_estimators`, `max_depth`, `learning_rate`) e LogReg (`C`, `penalty`). Servido: LogReg `C=0,5`, L2. |
| **2. Modelo serializado ou servido direto?** | **Serializado.** `train_churn_model.py` salva `churn_model.joblib`; `app.py` faz `joblib.load` e só infere. Treino e inferência são separados. |
| **3. Arquitetura?** | Pipeline de treinamento offline → artefato `.joblib` (Pipeline sklearn com `StandardScaler` embutido) → serviço web Streamlit de inferência (individual, em lote por CSV, e explicação). Deploy em Streamlit Community Cloud / container. |
| **4. Monitoramento / validação contínua (drift)?** | Ver `README_DEPLOY.md`: PSI/KS para data drift nas 11 features, recall/AUC em janelas, recall por segmento, recalibração de threshold, retreino a cada 4–8 semanas ou por gatilho; *shadow/canary* para promover novas versões. |

---

## Parte D — Explicabilidade (Aula 08/09)

- **Modelo apresentado e justificativa:** Regressão Logística — melhor ROC-AUC (0,957) e
  melhor recall (0,915) no cenário sem vazamento, gap de overfit ~0, e **interpretável**
  (baseline canônico para churn, Aula 05).
- **Métricas que sustentam a qualidade:** ROC-AUC 0,957 · recall 0,915 · precision 0,724
  · F1 0,808 · CV-AUC 0,956 ± 0,009.
- **Explicabilidade GLOBAL:** importância por |coeficiente| e por **SHAP médio** (aba
  Explicabilidade). Top fatores: `Lifetime`, `Contract_period`, `Age`,
  `Avg_class_frequency_total`.
- **Explicabilidade LOCAL (por cliente):** **SHAP `LinearExplainer`** — para cada cliente,
  o gráfico mostra quais variáveis **aumentaram** (vermelho) ou **reduziram** (verde) o
  risco. Reconstrução exata: `base + Σ(SHAP) = logit(probabilidade)`.
- **Explicação em linguagem natural:** gerada por template fiel aos SHAP + escala de
  threshold, para público de negócio (Customer Success), com ressalva explícita de
  **não-causalidade**. O *prompt* estruturado para o **OpenRouter** já está pronto na app
  (basta definir `OPENROUTER_API_KEY`) — Aula 09.
- **Limitações:** sem holdout **temporal** (split aleatório subestima drift); personas
  são tendências, não rótulos individuais; explicabilidade ≠ causalidade.

---

## Sobre o "item 3.5" — pode ser o SHAP?

**Não.** No relatório React (artefato), **o item 3.5 é "Correlação das features com o
churn"**, uma subseção da **Seção 3 (Análise Exploratória)**. SHAP é **explicabilidade do
modelo**, e seu lugar correto é a **Seção 6 (Modelos Preditivos)** ou uma seção própria de
Explicabilidade — **não** substituir o 3.5. Neste serviço (Streamlit), o SHAP está nas
abas **"Novo cliente"** (local) e **"Explicabilidade"** (global).
