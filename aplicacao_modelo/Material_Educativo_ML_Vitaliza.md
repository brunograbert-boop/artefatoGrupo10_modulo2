# Case Vitaliza: Aprendizado em Machine Learning

## Objetivos Educacionais

Este documento transforma o case Vitaliza em uma jornada de aprendizado prático sobre conceitos fundamentais de Machine Learning, explorando:

1. **Tipos de Problemas de ML** (Classificação vs. Previsão)
2. **Preparação de Dados** (Data Engineering, Feature Engineering, Qualidade de Dados)
3. **Modelagem Preditiva** (Algoritmos, Treinamento, Validação)
4. **Arquitetura de Sistemas de ML** (Infraestrutura, Pipelines, Produção)
5. **Armadilhas e Riscos** (Overfitting, Bias, Drift, Interpretabilidade)
6. **Impacto Estratégico** (Quando usar ML, quando não usar)

---

## Módulo 1: Identificando o Tipo de Problema de Machine Learning

### Contexto do Case

A Vitaliza enfrenta um problema de **churn (cancelamento) de clientes** com taxa de 10,2% ao mês. O desafio não é apenas identificar quem cancelou, mas **por que** cancelaram e, mais importante, **quem vai cancelar**.

### 1.1 Classificação do Problema

**Tipo Formal**: **Classificação Binária com Desequilíbrio de Classes**

```
Pergunta: Para cada usuário, qual é a probabilidade de cancelar nos próximos 30 dias?
Saída: Binária
  - Classe 0: Usuário permanece (maioria)
  - Classe 1: Usuário cancela (minoria ~10%)
Contexto: Altamente desbalanceado (90/10)
```

### 1.2 Por que não é um Problema Simples de Regressão?

❌ **Não é previsão de quantidade contínua:**
- Não estamos prevendo "quanto" o usuário vai gastar
- Estamos prevendo um evento binário (sim/não)

✅ **É classificação porque:**
- Output discreto (cancelará ou não)
- Métrica de sucesso é diferente (precisão, recall, F1, AUC-ROC)
- Threshold é crítico (em que score de risco 0-100 acionamos intervenção?)

### 1.3 Desafio do Desequilíbrio de Classes

A Vitaliza tem ~27.901 usuários ativos, dos quais apenas 2.847 cancelaram em setembro (~10%).

```
Estrutura dos Dados:
┌─────────────────────────────┐
│ Classe 0 (Permanece): 24.000 │
│ Classe 1 (Cancela):    2.847 │
│ Proporção: 89,5% / 10,5%     │
└─────────────────────────────┘

Problema: Um modelo "ingênuo" que sempre prevê 
"não vai cancelar" teria 89,5% de acurácia, 
mas seria inútil!
```

**Lição ML**: Acurácia não é a métrica certa para dados desbalanceados. Use:
- **Precision**: De todas as previsões de "vai cancelar", quantas estavam certas?
- **Recall**: De todos os usuários que realmente cancelaram, quantos nós identificamos?
- **F1-Score**: Média harmônica entre Precision e Recall
- **AUC-ROC**: Área sob a curva ROC (mede performance em todos os thresholds)

---

## Módulo 2: Preparação de Dados - A Raiz do Problema

### Contexto do Case

O CTO Diego revelou que a Vitaliza tinha dados "em três lugares que não se conversam":
1. **Mixpanel**: ~120 tipos de eventos do app
2. **PostgreSQL**: Transações, perfil, billing
3. **Google Analytics 4**: Tráfego web

### 2.1 O Ciclo de Vida dos Dados em ML

```
Raw Data (Bruto)
    ↓
Data Cleaning (Limpeza)
    ↓
Data Integration (Integração)
    ↓
Feature Engineering (Engenharia de Features)
    ↓
Feature Selection (Seleção de Features)
    ↓
Data Splitting (Divisão Treino/Teste)
    ↓
Model Training (Treinamento)
```

A Vitaliza estava PRESA no passo "Data Integration" — por isso precisava de 6 semanas de engenharia de dados!

### 2.2 Problema 1: Fragmentação de Dados (Data Silos)

**Situação Atual da Vitaliza:**

```
Sistema 1: Mixpanel
├─ user_id: abc123
├─ event_type: "session_start"
├─ timestamp: 2025-09-15T10:30:00Z
├─ duration: 45
└─ content_id: "meditation_001"

Sistema 2: PostgreSQL
├─ user_id: abc123
├─ subscription_type: "annual"
├─ signup_date: 2024-03-15
├─ ltv_estimate: R$ 287
└─ churn: 1 (cancelou em setembro)

Sistema 3: GA4
├─ user_id: abc123
├─ source: "organic"
├─ campaign: "tiktok_creator"
└─ landing_page: "homepage"

Desafio: Como saber se foram o MESMO usuário?
Timestamps são consistentes? IDs são únicos?
```

**Solução: Data Warehouse Unificado**

```
Data Warehouse (BigQuery/Snowflake)
│
├─ Dimensão Usuário
│  ├─ user_id (PK)
│  ├─ signup_date
│  ├─ subscription_type
│  ├─ ltv
│  └─ churn_label
│
├─ Dimensão Comportamento
│  ├─ user_id (FK)
│  ├─ total_sessions_lifetime
│  ├─ avg_session_duration
│  ├─ sessions_last_7days
│  └─ engagement_score
│
└─ Dimensão Aquisição
   ├─ user_id (FK)
   ├─ acquisition_source
   ├─ acquisition_campaign
   └─ days_since_signup
```

**Lição ML**: 70% do trabalho em ML é preparação de dados. Um dataset limpo vale mais que um algoritmo sofisticado.

### 2.3 Problema 2: Granularidade Temporal

O dataset preliminar que Diego entregou tinha apenas **snapshots mensais**:

```
Dataset Preliminar (Agregado):
user_id | sessions_lifetime | sessions_current_month | churn
--------|------------------|----------------------|------
  abc   |      120         |          2           |  1
  def   |       45         |          1           |  0
  ghi   |       200        |          25          |  0

Problema: Não conseguimos capturar PADRÕES TEMPORAIS
- Usuário abc teve 120 sessões lifetime mas só 2 no mês
  → Está em declínio? Mudou de interesse? Ficou ocupado?
```

**O que falta: Série Temporal (Time Series)**

```
Dataset Melhorado (Granular):
user_id | week | sessions | avg_duration | programs_completed | churn
--------|------|----------|--------------|-------------------|------
  abc   |  1   |    35    |    12min     |         3          |  0
  abc   |  2   |    28    |    11min     |         2          |  0
  abc   |  3   |    18    |     9min     |         1          |  0    ← Declínio
  abc   |  4   |     8    |     6min     |         0          |  0    ← Continua
  abc   |  5   |     2    |     4min     |         0          |  1    ← Cancela!
```

**Lição ML**: A hipótese de Marcelo ("declínio de frequência é sinal forte") requer **dados de série temporal granular**. Sem isso, o modelo fica "cego" para padrões que são óbvios visualmente.

### 2.4 Problema 3: Early Churn Invisível

O dataset revelou que **32,9% dos cancelamentos ocorrem por mecanismos não-registrados**:

```
Cancelamento Tipo 1: Via UI (/account/cancel)
→ Visível nos dados: SIM
→ Pode ser capturado para win-back reativo: SIM
→ Frequência: 71% (2.000 de 2.847)

Cancelamento Tipo 2: Falha de Pagamento
→ Visível nos dados: SIM (mas passivamente)
→ Pode ser capturado para win-back reativo: NÃO (não sabe motivo)
→ Frequência: 22% (623 de 2.847)

Cancelamento Tipo 3: Invisível (early churn)
├─ Exclusão do app (sem clique em cancelar)
├─ Cancelamento do cartão no app do banco
├─ Chargeback junto à operadora
→ Visível nos dados: NÃO
→ Pode ser capturado: SÓ COM MODELO PREDITIVO
→ Frequência: 7% (aproximadamente 200 de 2.847)
```

**Lição ML**: O modelo NUNCA vai ser melhor que os dados que você tem. Se 33% do fenômeno que você quer prever é invisível no seu dataset, o modelo máximo que você consegue é ~67% de recall.

### 2.5 Problema 4: Target Leakage (Vazamento de Informação)

Um erro clássico em ML: incluir informação do FUTURO no treino.

```
ERRADO (Com Leakage):
Variáveis de Treino:
├─ user_id
├─ signup_date
├─ subscription_type
├─ sessions_count
├─ last_login_date ← PROBLEMA!
└─ churn (Alvo)

Por que? Se o usuário cancelou, é óbvio que 
last_login_date foi ANTES do cancelamento. 
Você está literalmente dando a resposta ao modelo!

CORRETO (Sem Leakage):
Variáveis de Treino (Snapshot em 2025-08-31):
├─ user_id
├─ signup_date
├─ subscription_type
├─ sessions_count (ATÉ 2025-08-31)
├─ avg_session_duration (ATÉ 2025-08-31)
└─ Alvo: churn em SETEMBRO (futuro relativo ao snapshot)
```

**Lição ML**: Temporal awareness é crítico em ML preditivo. Sempre defina um "point in time" para features e certifique-se de que nenhuma feature contém informação do futuro.

---

## Módulo 3: Feature Engineering - Transformando Dados Brutos em Sinais

### Contexto

O dataset preliminar tinha 14 variáveis simples. Mas um modelo realmente eficaz precisa de **features que capturam padrões comportamentais**.

### 3.1 Tipos de Features

**Features Brutas (do dataset inicial):**
```python
- user_id
- age
- gender
- contract_duration (1, 6, ou 12 meses)
- time_on_platform (meses)
- participated_in_challenges (sim/não)
- referred_by_friend (sim/não)
- avg_sessions_per_week
- current_month_sessions
```

**Features Transformadas (Feature Engineering):**

```python
# Feature 1: Engagement Decline (A Hipótese de Marcelo!)
engagement_decline = (avg_sessions_last_4_weeks - avg_sessions_previous_4_weeks) / avg_sessions_previous_4_weeks
# Se = -0.5, usuário perdeu 50% de uso em 2 semanas → Alto risco!

# Feature 2: Recency (Quanto tempo desde último uso?)
recency_days = (today - last_session_date).days
# recency > 21 dias = comportamento de "dorminhoco"

# Feature 3: Frequency (Frequência de uso normalizada)
frequency_percentile = percentile_rank(current_month_sessions, all_users)
# Usuário está no top 10%? Fundo 25%?

# Feature 4: Tenure Effect (Efeito do tempo na plataforma)
tenure_months = (today - signup_date).days / 30
tenure_quartile = quartile(tenure_months)  # Q1, Q2, Q3, Q4
# Usuários novos têm padrão diferente de churn que veteranos

# Feature 5: Program Diversity (Quantos programas diferentes usa?)
unique_programs = count(distinct content_type)
program_diversity_score = unique_programs / 4  # 4 verticais: fitness, meditação, nutrição, sono
# Diversidade = mais engajamento = menos churn

# Feature 6: Challenge Participation Effect
challenge_participation_rate = challenges_completed / challenges_available
# Usuário que participa tem churn 50% menor (insight do dataset!)

# Feature 7: Billing Friction (Proxy para satisfação)
failed_payment_attempts = count(payment_failures_last_90_days)
# Múltiplas falhas de pagamento = indicador de frustração?

# Feature 8: Seasonal Pattern
signup_season = extract_season(signup_date)
is_seasonal_user = (signup_season == "summer")  # Muitos se inscrevem no verão
# Usuários sazonais têm churn diferente
```

### 3.2 Feature Importance - Quais Features Realmente Importam?

Após treinar um modelo, você pode medir qual feature tem maior impacto:

```
Feature Importance Simulado (Vitaliza):
╔═════════════════════════════════════════╗
║ Feature                     Importância  ║
╠═════════════════════════════════════════╣
║ engagement_decline              34%     ║  ← Hipótese de Marcelo validada!
║ recency_days                    18%     ║
║ contract_duration               15%     ║
║ challenge_participation_rate    12%     ║
║ tenure_months                    9%     ║
║ program_diversity_score          7%     ║
║ failed_payment_attempts          3%     ║
║ age                              2%     ║
╚═════════════════════════════════════════╝

Insight: Declínio de engajamento (34%) é 
MUITO mais preditivo que idade (2%).
```

### 3.3 Problema: Multicolinearidade

```python
# Problema: Duas features correlacionadas
feature_1 = current_month_sessions
feature_2 = engagement_score  # Que é function(current_month_sessions)

Correlação: 0.95 (muito alta!)

Problema: Modelo não consegue separar qual é mais importante.
O modelo fica confuso.

Solução: Usar apenas uma. Ou usar técnicas de regularização 
(L1/L2 Regularization) que penalizam multicolinearidade.
```

**Lição ML**: Feature Engineering é uma arte. Requer conhecimento do domínio (Business Intelligence) combinado com compreensão de ML. O melhor engenheiro de features é alguém que entende AMBOS.

---

## Módulo 4: Escolha de Algoritmos

### Contexto

Ambos os caminhos da Vitaliza usam "modelos", mas qual algoritmo é apropriado?

### 4.1 Caminho A: Classificação Simples

```
Algoritmos Possíveis para Win-back Reativo:

1. Logistic Regression (Regressão Logística)
   - Output: Probabilidade de "preço-sensível"
   - Vantagens: Interpretável, rápido, simples
   - Desvantagens: Assume relação linear
   - Tempo treino: <1 minuto
   
2. Decision Tree (Árvore de Decisão)
   - Estrutura: IF engagement > 5 AND tenure < 3 THEN "preço-sensível"
   - Vantagens: Interpretável, captura não-linearidades
   - Desvantagens: Pode overfitar
   - Tempo treino: <1 minuto

3. Random Forest (Floresta Aleatória)
   - 100+ árvores votando juntas
   - Vantagens: Robusto, menos overfitting
   - Desvantagens: Menos interpretável ("black box")
   - Tempo treino: 2-5 minutos em 4.000 usuários

4. Gradient Boosting (XGBoost, LightGBM)
   - Árvores construídas iterativamente
   - Vantagens: Performance superior
   - Desvantagens: Complexo, risco de overfitting
   - Tempo treino: 5-10 minutos
```

**Para Caminho A: Logistic Regression ou Decision Tree**
- Precisa ser rápido (decisão em <2 segundos)
- Precisa ser interpretável (por quê o modelo sugeriu desconto de 50%?)
- Dataset pequeno (apenas usuários que chegam à tela de cancelamento)

### 4.2 Caminho B: Classificação com Série Temporal

```
Algoritmos Possíveis para Engagement Forecasting:

1. LSTM (Long Short-Term Memory)
   - Rede neural especializada em sequências
   - Vantagens: Captura dependências temporais
   - Desvantagens: Precisa muitos dados, complexo
   - Tempo treino: 30+ minutos em GPU
   - Interpretabilidade: Muito baixa (caixa preta total)

2. Prophet (Facebook)
   - Modelo de série temporal
   - Vantagens: Fácil usar, captura sazonalidade
   - Desvantagens: Não usa features externas bem
   - Tempo treino: <5 minutos

3. Gradient Boosting com Features Temporais
   - XGBoost com features engineeradas da série temporal
   - Vantagens: Bom balanço entre performance e interpretabilidade
   - Desvantagens: Requer feature engineering cuidadoso
   - Tempo treino: 10-15 minutos

4. Hidden Markov Models (HMM)
   - Modela estados latentes (engajado, desengajado, etc)
   - Vantagens: Captura transições de estado
   - Desvantagens: Complexo implementar em produção
   - Tempo treino: 5-10 minutos
```

**Para Caminho B: Gradient Boosting com Features Temporais**
- Precisa de série temporal (dados tem isso após pipeline)
- Precisa de performance alta (reduzir churn 30-50%)
- Precisa de alguma interpretabilidade (qual feature acionou alerta?)
- Dataset grande (27.901 usuários × 365 dias em teoria)

### 4.3 Trade-offs Clássicos: Performance vs. Interpretabilidade

```
                    Performance
                        ↑
                        │
                   ┌────┴────┐
                   │ XGBoost  │ ← Melhor performance
                   │ LSTM     │
                   │ (Caixa   │
                   │  Preta)  │
                   │          │
Random Forest ─────┼─────────────  Bom balanço
                   │          │
                   │  Linear  │
                   │  Model   │ ← Mais interpretável
                   │  (Caixa  │
                   │  Branca) │
                   └────┬────┘
                        │
                        ↓
                 Interpretabilidade
```

**Lição ML**: Não existe algoritmo "melhor" universalmente. Depende de:
- Quantidade de dados
- Requisitos de interpretabilidade
- Latência aceitável
- Recursos computacionais

---

## Módulo 5: Validação de Modelos - Não Caia nas Armadilhas

### Contexto

Um modelo que funciona bem nos dados de treino pode fracassar em produção. Existem várias armadilhas clássicas.

### 5.1 Overfitting vs. Underfitting

```
Cenário: Treinar modelo de churn em 80% dos dados (4.000 usuários)
Testar em 20% dos dados (1.000 usuários) NÃO vistos durante treino

Performance do Modelo:
┌──────────────┬─────────────┐
│ Treino (80%) │ Teste (20%) │
├──────────────┼─────────────┤
│   AUC: 0.95  │  AUC: 0.70  │  ← OVERFITTING!
│   F1: 0.92   │  F1: 0.62   │     Modelo memorizou dados
└──────────────┴─────────────┘     de treino em vez de aprender
                                    padrões gerais

Problema: Em produção, vai funcionar como 0.70, não 0.95!

Como Diagnosticar:
- Se gap treino/teste > 0.1 (10%), provavelmente overfitting
- Plotar learning curves
- Testar em dados de períodos diferentes (treino em setembro,
  teste em outubro - dados realmente novos!)
```

### 5.2 Data Leakage - Vazamento de Informação

```
Cenário da Vitaliza:

CORRETO - Treino em Setembro, Teste em Outubro:
├─ Features: Tudo até 30-09-2025
├─ Alvo: Churn em Outubro 2025
└─ Resultado: Modelo prevê futuro (válido!)

ERRADO - Vítima de Leakage:
├─ Features: Incluindo "days_since_last_cancellation_attempt"
├─ Alvo: Churn em Setembro
└─ Problema: Se o usuário cancelou, é óbvio que
           "days_since_last_cancellation_attempt" = 0!
           Você está dando a resposta ao modelo!

Resultado: Performance aparentemente 95% em teste,
           mas 30% em produção (porque feature não existe)
```

### 5.3 Class Imbalance - O Desafio da Minoria

```
Problema da Vitaliza: 90% usuários não cancelam, 10% cancelam

Dataset Balanceado (Imaginário):
┌────────────┬──────────┐
│ Classe 0   │ 50 dados │
│ Classe 1   │ 50 dados │  ← Balanceado
│ Total      │ 100      │
└────────────┴──────────┘

Métrica apropriada: Acurácia (50% cada classe)

Dataset Desbalanceado (Vitaliza Real):
┌────────────┬──────────┐
│ Classe 0   │ 4.000 dados (89%)
│ Classe 1   │  500 dados (11%)  ← Minoritária
│ Total      │ 4.500
└────────────┴──────────┘

Métrica ERRADA: Acurácia
- Um modelo ingênuo que sempre prevê "não cancela"
  teria 89% de acurácia (inútil!)

Métricas CORRETAS:
- Precision: De quem eu disse "vai cancelar", quantos realmente cancelaram?
- Recall: De quem realmente cancelou, quantos eu peguei?
- F1-Score: Balanço entre precision e recall
- AUC-ROC: Curva que avalia em TODOS os thresholds

Técnicas para Lidar:
1. Resampling (Oversampling da minoria, Undersampling da maioria)
2. Class Weights (Penalizar erros na classe minoritária)
3. Threshold Tuning (Ao invés de 0.5, usar 0.3 como cutoff)
4. SMOTE (Synthetic Minority Oversampling)
```

**Lição ML**: Com dados desbalanceados, acurácia é uma métrica enganosa. Use sempre Precision-Recall ou AUC-ROC.

### 5.4 Validação Cruzada (Cross-Validation)

```
Objetivo: Evitar "sorte" na divisão treino/teste

Método Naive (NÃO FAÇA):
┌────────────────────────────────────┐
│ Dados Inteiros (4.000 usuários)     │
├────────────────┬────────────────────┤
│ Treino (80%)   │ Teste (20%)        │
│ 3.200 usuários │ 800 usuários       │
└────────────────┴────────────────────┘
Problema: E se os 800 de teste forem "sorte"?
         (usuários mais fiéis, menos propensos a churn)

Método Correto (K-Fold Cross-Validation):
Dividir dados em K partes (ex: K=5)

┌─────────────────────────────────────────────────┐
│ Fold 1: Treino em 4 partes, Teste em 1         │
│ Fold 2: Treino em 4 partes (diferentes), Teste  │
│ Fold 3: Treino em 4 partes (diferentes), Teste  │
│ Fold 4: Treino em 4 partes (diferentes), Teste  │
│ Fold 5: Treino em 4 partes (diferentes), Teste  │
└─────────────────────────────────────────────────┘

Resultado Final: Média das 5 iterações
Vantagem: Estimativa mais robusta de performance real
```

### 5.5 Temporal Validation (Crítico para Séries Temporais!)

```
Cenário da Vitaliza (Caminho B):

ERRADO (Forward Leakage):
├─ Treino: Dados de Setembro + Outubro + Novembro
├─ Teste: Dados de Agosto
└─ Problema: Modelo treinou com o "futuro"
            que ele precisa prever!

CORRETO (Temporal Order):
├─ Treino: Dados até Setembro
├─ Validação: Dados de Outubro
├─ Teste: Dados de Novembro
└─ Respeitando: O modelo nunca vê o futuro

Lição: Em problemas de série temporal, 
       SEMPRE validar em ordem cronológica!
```

---

## Módulo 6: Risco 1 do Caminho A - Cegueira Estrutural

### Análise Técnica de ML

```
Problema Identificado:
32,9% dos cancelamentos (349 de 1.060 usuários) ocorrem 
por mecanismos que NÃO ativam o evento "cancelar" no app.

Implicação de ML:
"Um modelo treinado apenas em dados de usuários que 
clicaram em 'Cancelar' NUNCA consegue aprender a prever 
cancelamentos que não deixam esse rastro."

Visualização:
┌─────────────────────────────────────────────┐
│ Universo de Usuários que Cancelam (100%)    │
├────────────────────┬────────────────────────┤
│ Visível no app     │ Invisível no app       │
│ (71% dos dados)    │ (29% dos dados)        │
│                    │                        │
│ Via clique         │ Exclusão app           │
│ "Cancelar"         │ + falha passiva        │
│                    │                        │
│ ← Pode treinar     │ Cancelamento cartão    │
│   modelo aqui      │ no app do banco        │
│                    │                        │
│                    │ Chargeback             │
│                    │                        │
│                    │ ← Invisível ao modelo  │
└────────────────────┴────────────────────────┘

Máximo Teórico de Recall (True Positive Rate):
Se nosso modelo é PERFEITO em identificar os 71%, 
mas 29% são estruturalmente invisíveis:
Máximo Recall = 71%

Em outras palavras:
- Modelo A (melhor caso): Identifica 71% dos cancelamentos
- Modelo B (Caminho B): Potencialmente identifica 100% 
  (porque previne antes, não espera cancelamento)
```

### Trade-off Crítico de ML: Precisão vs. Recall

```
Para Caminho A, o custo de Recall baixo é alto:

┌──────────────┬────────────┬─────────┐
│              │ Recall 71% │ Recall 100% (possível?)
├──────────────┼────────────┼─────────┤
│ Positivos ID │    500     │   705   │ (de ~705 em mês)
│ Falsos Neg.  │    205     │     0   │ (deixados passar)
│ Custo MRR    │  R$8.180   │   R$0   │ (não recuperados)
└──────────────┴────────────┴─────────┘

Pergunta de Negócio:
Essa perda de R$ 8.180/mês é aceitável?
Resposta: SÓ se o Caminho A custar muito menos que o B
```

---

## Módulo 7: Risco 2 do Caminho B - Sleeping Dogs

### Análise Técnica de ML

```
Situação: ~320 usuários (8% da base) com:
- Contrato > 6 meses
- Frequência semanal < 0.5 (quase nunca usam)
- Ainda estão pagando (inércia, esquecimento, "doação simbólica")

Valor em ARR: ~R$ 153.000 (receita praticamente pura)

Problema de ML:
┌─────────────────────────────────────────────────┐
│ Modelo Preditivo vê esses dados como:           │
│ usage_freq: 0.2 (muito baixa!)                  │
│ engagement_score: 2/100 (quase nada!)           │
│ tenure_months: 18 (longo tempo)                 │
│ contract_status: "paid" (ativo)                 │
│                                                 │
│ Conclusão do Modelo: "RISCO ALTÍSSIMO!"        │
│ Predição: 95% probabilidade de churn            │
│                                                 │
│ Ação Acionada:                                  │
│ - Push notification                             │
│ - Email "Voltamos a nos ver!"                   │
│ - Oferta de desconto                            │
│                                                 │
│ O Que Acontece:                                 │
│ Usuário vê mensagem e pensa:                    │
│ "Ah, é verdade, estou pagando naquele app      │
│  que não uso mais. Melhor cancelar agora."     │
│                                                 │
│ Resultado: Ação que pretendia PREVENIR         │
│ churn CAUSA o churn!                           │
└─────────────────────────────────────────────────┘
```

### Paradoxo de Retenção em ML

```
Modelo Tradicional:
Risco Alto → Intervir → Resultado: Churn

Sleeping Dogs:
Risco Alto (segundo modelo) 
  ↓
Intervir (enviar mensagem)
  ↓
Usuário despertado (awareness do pagamento)
  ↓
Decisão consciente de cancelar (ao invés de inércia)
  ↓
Churn REAL (ao invés de dorminhoco)

Resultado Paradoxal: Ação de "retenção" aumenta churn!
```

### Como Detectar Sleeping Dogs com ML

```python
# Feature para identificar sleeping dogs:
is_sleeping_dog = (
    (tenure_months > 6) AND
    (current_month_sessions < 0.5) AND  # Quase nunca usa
    (payment_active == True) AND
    (NOT last_session_initiated_by_reminder)  # Não usa depois de email
)

# Estratégia: Deixar quietos (não intervir!)
if is_sleeping_dog:
    skip_intervention()  # Não fazer nada!
else:
    apply_retention_campaign()
```

**Lição ML**: Um modelo pode ter performance estatística excelente (95% AUC-ROC), mas introduzir **viés causal** na produção. Sempre teste:
1. Performance estatística (AUC, F1, etc.)
2. **Impacto causal** (ação que modelo recomenda piora o resultado?)

---

## Módulo 8: Drift de Dados - O Inimigo Silencioso

### Contexto

Um modelo treinado em setembro de 2025 pode não funcionar em outubro se o comportamento dos usuários mudou.

### 8.1 Tipos de Drift

```
CONCEPT DRIFT (Mudança de Conceito):
┌────────────────────────────────────────────────┐
│ Setembro 2025: Padrão de Churn                 │
│ Usuário que não usa = alta probabilidade churn │
│ Correlação: engagement ↔ retenção               │
│                                                 │
│ Outubro 2025: Strava Premium lança no Brasil   │
│ Novo padrão: Até usuários engajados cancelam   │
│ Mudança: Competição externa redefiniu problema │
│                                                 │
│ Resultado: Modelo setembro NÃO funciona bem    │
│ em outubro!                                    │
└────────────────────────────────────────────────┘

DATA DRIFT (Mudança nos Dados):
┌────────────────────────────────────────────────┐
│ Setembro 2025: Distribuição de Features        │
│ avg_sessions: média 15.3, std 8.2              │
│ age: média 32, std 9.1                         │
│                                                 │
│ Outubro 2025: Mudança demográfica              │
│ avg_sessions: média 12.1, std 6.5  ← Mudou!   │
│ age: média 29, std 10.3  ← Mudou!              │
│                                                 │
│ Problema: Features estão fora de distribuição  │
│ Modelo não foi treinado com esses valores      │
│ Predições tornam-se menos confiáveis          │
└────────────────────────────────────────────────┘

LABEL DRIFT (Mudança no Alvo):
┌────────────────────────────────────────────────┐
│ Setembro 2025: 10.2% churn mensal (baseline)   │
│                                                 │
│ Outubro 2025: 15% churn mensal                 │
│                                                 │
│ Mudança: Proporção de positivos mudou          │
│ Desbalanceamento que era 90/10 virou 85/15     │
│                                                 │
│ Implicação: Modelo treino em 90/10 pode        │
│ ter performance diferente em 85/15             │
└────────────────────────────────────────────────┘
```

### 8.2 Monitoramento de Drift em Produção

```
Sistema de Alerta de Drift:

┌────────────────────────────────────────┐
│ Modelo em Produção (Outubro 2025)      │
│                                        │
│ Performance esperada (do treino):      │
│ ├─ AUC-ROC: 0.78                      │
│ ├─ Precision: 0.72                    │
│ └─ Recall: 0.65                       │
│                                        │
│ Performance observada (em produção):   │
│ ├─ AUC-ROC: 0.61  ← ALERTA! (-0.17)   │
│ ├─ Precision: 0.58  ← ALERTA! (-0.14) │
│ └─ Recall: 0.42  ← ALERTA! (-0.23)    │
│                                        │
│ Ação: Retreinar modelo                │
└────────────────────────────────────────┘
```

**Lição ML**: Um modelo não é um ativo estático. Requer monitoramento contínuo. Recomendação: retreinar a cada 4-8 semanas ou quando drift é detectado.

---

## Módulo 9: Interpretabilidade e Explicabilidade

### Por que Importa?

```
Cenário: Usuário X recebe score de churn 95%
e seu plano é cancelado automaticamente.

Usuário pergunta ao suporte: "Por quê?"

Se o modelo for uma "caixa preta" (Neural Network),
a resposta é: "Algoritmo complexo decidiu"
→ Insatisfação, reclamação, perda de confiança

Se o modelo for interpretável (Árvore de Decisão),
a resposta é: "Você teve 2 sessões em 4 semanas, 
depois 0 em 2 semanas. Padrão típico de churn."
→ Usuário entende, até concorda
```

### 9.1 SHAP Values - A Melhor Ferramenta

```
Feature Importance Global:
"Qual feature é mais importante em geral?"
feature_A: 34%
feature_B: 25%
feature_C: 18%

SHAP Values (Local):
"Para este USUÁRIO ESPECÍFICO, qual feature impactou a predição?"

Usuário X:
├─ engagement_decline: -25 pontos (piora predição, aumenta risco)
├─ challenge_participation: +8 pontos (melhora predição)
├─ recency: -15 pontos (piora, pois é recente inatividade)
├─ contract_duration: +3 pontos (melhora, contrato anual é estável)
└─ Predição Final: 72% probabilidade de churn

Narrativa Interpretável:
"Seu score de risco é 72% principalmente porque:
1. Sua frequência de uso caiu significativamente (-25)
2. Você não usa há 3 semanas (-15)
COMPENSADO POR:
3. Você tem contrato anual (+3)
4. Já participou de desafios (+8)"
```

### 9.2 Quando Sacrificar Interpretabilidade

```
Trade-off: Interpretabilidade vs. Performance

Caso A: Recomendação de Desconto no Cancelamento
├─ Impacto: Direto, conversacional
├─ Requisito: MUITO interpretável
├─ Usuário pode contestar: SIM
├─ Algoritmo apropriado: Árvore de Decisão, Logistic Regression
└─ Sacrificar Interpretabilidade? NÃO (ganho de performance vale <1%)

Caso B: Predição de Risco Contínuo (Background)
├─ Impacto: Indireto (alimenta UI, não é visível direto)
├─ Requisito: Interpretabilidade média
├─ Usuário contesta: RARAMENTE (é background)
├─ Algoritmo apropriado: Gradient Boosting, Neural Networks
└─ Sacrificar Interpretabilidade? SIM (ganho de performance vale 3-5%)
```

**Lição ML**: Interpretabilidade é um requisito não-funcional que depende do contexto. Não há resposta universal "sempre maximize performance" ou "sempre maximize interpretabilidade".

---

## Módulo 10: O Ciclo de Vida Completo de um Projeto de ML

### Estrutura do Projeto Vitaliza

```
Week 1-2: Problem Definition & Data Exploration
├─ Entender o problema (churn de 10.2%)
├─ Explorar dados disponíveis (3 silos)
├─ Definir métrica de sucesso (reduzir churn para 6%)
└─ Identificar gargalos (fragmentação de dados)

Week 3-8: Data Engineering & Feature Engineering
├─ Construir pipeline unificado (data warehouse)
├─ Sincronizar IDs entre Mixpanel/PostgreSQL/GA4
├─ Criar features (engagement_decline, recency, etc)
├─ Validar qualidade de dados (outliers, missing values)
└─ Explorar hipóteses (declínio de frequência importa?)

Week 9-10: Modelagem & Validação
├─ Treinar múltiplos modelos (Logistic Reg, XGBoost, LSTM)
├─ Validação cruzada (K-fold)
├─ Validação temporal (treino set, test set respeitando ordem)
├─ Detectar overfitting/underfitting
├─ Medir performance em dados não vistos
└─ Técnicas de lidar com class imbalance

Week 11+: Implantação & Monitoramento
├─ Build API de inferência (chamadas em <2s)
├─ Integrar com sistema existente
├─ Monitoramento de drift (AUC, Precision, Recall)
├─ Feedback loop (coletar resultados reais das predições)
├─ Retreinar periodicamente (a cada 4-8 semanas)
└─ Iteração contínua

Ongoing: Experimentation & Improvement
├─ Test: Novo modelo vs. baseline
├─ Measure: Impacto em churn real (A/B test)
├─ Learn: O que funcionou, o que não funcionou
└─ Repeat
```

### A Importância do Feedback Loop

```
Loop de Melhoria Contínua:

┌─────────────────────────────────────────┐
│ 1. Treinar Modelo (Performance: 0.78)   │
├─────────────────────────────────────────┤
│ 2. Deploy em Produção                   │
├─────────────────────────────────────────┤
│ 3. Coletar Predições + Outcomes Reais   │
│    (Quem efetivamente cancelou?)        │
├─────────────────────────────────────────┤
│ 4. Calcular Performance Real             │
│    (Performance real: 0.65 - caiu!)      │
├─────────────────────────────────────────┤
│ 5. Análise de Gap                       │
│    Por que testado deu 0.78 mas          │
│    produção deu 0.65? Drift? Leakage?   │
├─────────────────────────────────────────┤
│ 6. Coletar Feedback dos Usuários        │
│    "Por quê meu score era 80%?"          │
│    "Cancelei por X, não por Y"          │
├─────────────────────────────────────────┤
│ 7. Retreinar com Dados Novos + Feedback │
└─────────────────────────────────────────┘
          (Volta ao Passo 1)
```

---

## Módulo 11: Armadilha Final - Quando NÃO Usar ML

### Contexto

Nem todo problema é um problema de ML. Às vezes, a resposta é mais simples.

### 11.1 Quando Não Use ML

```
Problema: Retenção de usuários com >R$ 1 milhão LTV

Abordagem ML:
├─ Treinar modelo de churn complexo
├─ Investir R$ 600k em infraestrutura
├─ 10 semanas de desenvolvimento
└─ Predição: Este usuário tem 45% risco de churn

Abordagem Simples (Business):
├─ Listar 30 usuários de maior LTV
├─ Atribuir dedicated account manager
├─ Check-in mensal
└─ Retenção: 95%+ (muito superior!)

Lição: Para 30 usuários, NÃO use ML!
       Use inteligência humana (mais eficaz, mais barato).

ML é para ESCALA:
- Quando temos milhares/milhões de "decisões" individuais
- Quando padrão é complexo demais para regras manuais
- Quando retorno financeiro justifica investimento
```

### 11.2 A Pergunta Crítica

Antes de iniciar qualquer projeto de ML, responda:

```
1. Problema é bem definido? (SIM)
   Reduzir churn de 10.2% para 6.0% é claro

2. Temos dados suficientes? (SIM)
   4.000 históricos de usuários + cancelamentos

3. Padrão é capturável em dados? (TALVEZ)
   Alguns cancelamentos são invisíveis (33%)

4. Valor econômico justifica investimento? (SIM)
   R$ 113k/mês em MRR, investimento é R$ 600k (5-6 meses ROI)

5. Solução ML é melhor que alternativa? (DEPENDE)
   - Alternativa: Caminho A (mais rápido, menos investimento)
   - Proposição ML: Caminho B (mais abrangente, longo prazo)

6. Conseguimos operacionalizar? (CRÍTICO!)
   - Treinar modelo é fácil
   - Colocar em produção é 80% do trabalho
   - Manter em produção é contínuo
```

---

## Conclusão: Jornada de Aprendizado

### O que Aprendemos

| Conceito | Vitaliza | ML Geral |
|----------|----------|----------|
| **Tipo de Problema** | Classificação binária desbalanceada | Entender problema é 50% da batalha |
| **Preparação de Dados** | 6 semanas em pipeline unificado | 70% do tempo de ML |
| **Features** | Engagement_decline é 34% importante | Engenharia de features é arte + ciência |
| **Algoritmos** | Logistic Reg vs. XGBoost vs. LSTM | Não há melhor universal |
| **Validação** | Temporal validation é crítico | Cross-validation robusta |
| **Armadilhas** | 33% churn invisível, sleeping dogs | Sempre validar causalidade |
| **Drift** | Strava muda o jogo em 1 dia | Monitorar produção continuamente |
| **Interpretabilidade** | Usuários precisam entender risco | Trade-off com performance |
| **Produção** | Feedback loop é essencial | Modelo é 20%, infraestrutura é 80% |
| **Decisão** | Não é puramente técnica | Entender negócio é mandatório |

### Lições-Chave

1. **ML é 20% modelagem, 80% infraestrutura**
   - Semanas em engenharia de dados
   - Monitoramento contínuo
   - Feedback loops

2. **Dados dominam modelos**
   - Um dataset limpo + modelo simples > Dataset sujo + modelo complexo
   - Garbage in, garbage out

3. **Interpretabilidade importa**
   - Stakeholders precisam entender predições
   - Regulação (LGPD) exige transparência

4. **Validação temporal é crítico**
   - Em problemas preditivos, SEMPRE respeitar ordem cronológica
   - Forward leakage é erro comum letal

5. **Nem sempre a resposta é ML**
   - Às vezes, regra de negócio é mais eficaz
   - Sempre questionar: "Vale o investimento?"

6. **Produção é diferente de Protótipo**
   - Modelo que funciona em notebook pode quebrar em produção
   - Drift, outliers, edge cases surgem
   - Monitoramento contínuo é necessário

7. **O negócio comes the model**
   - A melhor decisão estatística pode ser pior decisão de negócio
   - Entender contexto (Strava) é tão importante quanto performance

---

## Recursos para Aprofundamento

### Cursos Online
- Fast.ai: Practical Deep Learning for Coders
- Andrew Ng: Machine Learning Specialization (Coursera)
- Kaggle: Learn Machine Learning

### Livros
- "Hands-On Machine Learning" - Aurélien Géron
- "The Hundred-Page ML Book" - Andriy Burkov
- "Feature Engineering for Machine Learning" - Alice Zheng

### Ferramentas Práticas
- Scikit-learn: ML clássico
- XGBoost / LightGBM: Gradient Boosting
- TensorFlow / PyTorch: Deep Learning
- MLflow: Experiment Tracking
- Weights & Biases: Model Monitoring

### Datasets para Treinar
- Kaggle Datasets
- UCI Machine Learning Repository
- Vitaliza Case Dataset (educacional)

---

## Próximos Passos

### Para Iniciantes
1. Entender o pipeline completo com dataset pequeno
2. Implementar validação cruzada corretamente
3. Praticar feature engineering
4. Estudar interpretabilidade (SHAP, LIME)

### Para Intermediários
1. Entender trade-offs (interpretabilidade vs. performance)
2. Lidar com dados desbalanceados
3. Detecção e tratamento de drift
4. Implementar feedback loops

### Para Avançados
1. Causal Inference (quando correlação não implica predição)
2. Reinforcement Learning (não apenas predição, mas ação)
3. MLOps em escala (produção, monitoramento, retraining)
4. Fairness & Bias (viés em modelos, equidade)

---

**Fim da Jornada de Aprendizado no Case Vitaliza**

Esperamos que este material tenha transformado o case de uma "história de negócio" em uma **lição estruturada de Machine Learning**. O melhor aprendizado vem de problemas reais — e Vitaliza oferece um excelente estudo de caso de decisões técnicas, operacionais e estratégicas em torno de ML.
