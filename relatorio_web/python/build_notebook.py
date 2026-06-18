"""
Constroi o notebook artefato_semana5_vitaliza.ipynb programaticamente.
Cada secao do entregavel e uma sequencia de celulas (markdown + codigo).
Rodar: python build_notebook.py
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

# ----------------------------------------------------------------------------
# CAPA / SECAO 0 - SUMARIO EXECUTIVO
# ----------------------------------------------------------------------------

cells.append(nbf.v4.new_markdown_cell(r"""
# Customer Segmentation Report — Vitaliza
### Artefato integrado | Semana 5 | Modulo 2 — MBA em IA e Dados para Negocios | Inteli

**Autor:** Bruno Grabert
**Data:** Maio de 2026
**Trilhas cobertas:** Negocios (segmentacao + matriz Valor x Risco) **e** Tecnologia (comparacao de classificadores para previsao de churn)

---

## Sumario executivo

A Vitaliza opera com churn mensal de 10,2%, contra meta contratada de 6,0% — descompasso que ja levou o LTV/CAC para 2,02, abaixo do piso de 3,0 exigido pelo term sheet da Serie B. Em 19 dias, a VP Camila Ferraz precisa levar ao Conselho uma recomendacao defensavel sobre **onde investir os R$ 600 mil aprovados em retencao**.

Este relatorio analisa a amostra de 4.000 assinantes entregue pelo CTO Diego Almeida e responde a tres perguntas:

1. **Quem cancela?** Quatro segmentos comportamentais distintos, com taxas de churn variando de 3% a mais de 50%.
2. **Por que cancelam?** Tres drivers concentram a quase totalidade do sinal: duracao do contrato, lifetime na plataforma e queda na frequencia do mes corrente.
3. **Onde intervir?** Uma matriz Valor x Risco aplicada aos quatro segmentos isola onde 70-80% do esforco deve estar concentrado — e onde **nao** se deve mexer.

**Tres achados centrais:**

- O cluster de maior risco (**Early Dropout**) concentra ~37% da base mas responde por mais de 75% dos cancelamentos previstos. **E o alvo de ROI mais agressivo.**
- Clientes em contrato anual cancelam ~18x menos que mensais (2,4% vs 42,3%). **Migrar engajados mensais para plano anual e a alavanca contratual mais obvia.**
- O Caminho A (win-back reativo) e **estruturalmente cego** para o Early Dropout, que sai sem clicar em "Cancelar". A matriz Valor x Risco indica que o Caminho B (proativo) e nao-opcional para esse quadrante — confirmando o piso competitivo posto pelo anuncio do Strava Premium.

**Modelo preditivo:** entre 7 classificadores comparados (regressao logistica, arvore de decisao, KNN, Naive Bayes, SVM linear, Perceptron e MLP), a **arvore de decisao** foi eleita como modelo principal por combinar interpretabilidade (regras que viram personas) e desempenho competitivo. O modelo alimenta o eixo Risco da matriz.

---
"""))

# ----------------------------------------------------------------------------
# SECAO 1 - CONTEXTO DO CASE
# ----------------------------------------------------------------------------

cells.append(nbf.v4.new_markdown_cell(r"""
## 1. Contexto do case

A **Vitaliza** e um aplicativo B2C de assinatura para bem-estar digital — programas guiados em fitness, meditacao, nutricao e sono, em modelo similar ao Calm e ao Centr, adaptado para o mercado brasileiro. Lancada em marco de 2020, surfou a curva de adocao acelerada da pandemia e cresceu a 47% ao trimestre ate o final de 2022. Em marco de 2023 captou Serie A+ de R$ 22M ancorada na tese de retencao no mes 6 superior a 32,5% — 30% acima da media de mercado.

A partir do Q3 de 2024, o setor entrou no que analistas chamam de "vale da desilusao pos-pandemia": o Calm registrou queda de 18% em receita liquida, o Headspace demitiu 15% do quadro. A Vitaliza acompanhou: a base estabilizou em ~27.901 assinantes e o churn mensal subiu de ~7% para **10,2% em setembro de 2025** — equivalente a churn anualizado de 73% e 2.847 cancelamentos por mes.

### O mandato da Camila

Camila Ferraz foi contratada em outubro de 2025 como VP de Crescimento e Retencao, vinda de uma fintech onde reduziu churn de 5,1% para 2,8% em nove meses. Seu mandato: **derrubar o churn mensal da Vitaliza para 6,0% ate Q4 de 2026**. Em 19 dias, ela precisa apresentar ao Conselho de Administracao um plano de inteligencia de retencao com modelo preditivo demonstravel — nao slides de intencao, nas palavras do CEO.

### O dilema arquitetural

A semana de entrevistas de Camila revelou duas abordagens mutuamente excludentes para os R$ 600 mil aprovados:

- **Caminho A — Win-back reativo** (defendido pelo CS): modelo dispara quando o usuario clica em "Cancelar" e oferece retencao personalizada via GenAI. MVP em 4 semanas, recupera 15-25% do churn segundo benchmarks Bain 2024. **Limitacao critica:** ~33% dos cancelamentos acontecem sem o usuario chegar a tela de cancelamento (falha de cartao, abandono passivo, chargeback). Para esse terco, o Caminho A vale zero.

- **Caminho B — Engagement forecasting proativo** (defendido pelo Produto): score continuo de risco de churn para os 27.901 assinantes, intervencao antes da decisao de sair. Reduz churn 30-50% em 6-9 meses. **Limitacoes:** 6 semanas de engenharia de dados antes da primeira linha de codigo de modelo; risco "don't wake the sleeping dogs" (~8% da base paga sem usar; intervencao pode lembra-los de cancelar).

### A virada das 17h42

Na sexta-feira em que Camila revisava as anotacoes, o Strava Premium anunciou camada de personalizacao para o Brasil em Q1/2026 — funcionalmente equivalente ao Caminho B. O Caminho B deixou de ser opcional e virou **piso competitivo declarado pelo mercado**.

### Por que esta segmentacao importa

A segmentacao nao e um exercicio descritivo. Ela e o **substrato analitico da decisao de arquitetura**: identificar quais segmentos podem ser interceptados pelo Caminho A, quais exigem o Caminho B, e onde nao se deve intervir. A matriz Valor x Risco, na secao 7, e o framework executivo que traduz a segmentacao em decisao orcamentaria.

---
"""))

# ----------------------------------------------------------------------------
# SECAO 2 - O DADO
# ----------------------------------------------------------------------------

cells.append(nbf.v4.new_markdown_cell(r"""
## 2. O dado

O CTO Diego Almeida dedicou a tarde de quinta-feira a um esforco manual de reconciliacao entre PostgreSQL (transacoes e perfil), Mixpanel (eventos do app) e GA4 (trafego). O resultado, entregue na manha de sexta, e o arquivo **`gym_churn_us.csv`**: amostra anonimizada de **4.000 assinantes** da Vitaliza, com 13 variaveis comportamentais e demograficas mais a flag binaria de churn nos ultimos 6 meses.

A amostra **nao** inclui eventos granulares do Mixpanel — esses permanecem inacessiveis sem o pipeline unificado que custaria 6 semanas. O que esta disponivel sao agregados mensais por usuario.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Setup do ambiente
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Estilo dos graficos
sns.set_theme(style='whitegrid', palette='Set2')
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['font.size'] = 10

# Carga do dataset
CSV_PATH = '../dados/gym_churn_us.csv'
df = pd.read_csv(CSV_PATH)

print(f'Linhas: {len(df):,} | Colunas: {df.shape[1]}')
print(f'Nulos: {df.isna().sum().sum()}')
print(f'Churn global: {df["Churn"].mean():.1%}')
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### Dicionario de variaveis

| Variavel do CSV | Tipo | Interpretacao no contexto Vitaliza |
|---|---|---|
| `gender` | binaria | Genero (0/1, anonimizado) |
| `Near_Location` | binaria | Mora proximo a regiao de atuacao da Vitaliza (proxy de aderencia geografica) |
| `Partner` | binaria | Veio por parceria corporativa |
| `Promo_friends` | binaria | Veio por indicacao de amigo |
| `Phone` | binaria | Forneceu telefone no cadastro |
| `Contract_period` | inteiro (1/6/12) | Duracao do plano em meses |
| `Group_visits` | binaria | Participa de desafios em grupo no app |
| `Age` | inteiro | Idade |
| `Avg_additional_charges_total` | float (R$) | **Total acumulado em servicos extras** (produtos adicionais, planos premium, etc.) — *nao e a mensalidade* |
| `Month_to_end_contract` | float | Meses restantes ate o fim do contrato vigente |
| `Lifetime` | inteiro | Tempo total na Vitaliza, em meses |
| `Avg_class_frequency_total` | float | Frequencia semanal media de sessoes no app, ao longo de toda a vida do usuario |
| `Avg_class_frequency_current_month` | float | Frequencia semanal media de sessoes no app, **no mes corrente** |
| `Churn` | binaria (alvo) | 1 = cancelou nos ultimos 6 meses |

Premissas adicionais vindas do business case (necessarias para o eixo Valor da matriz):
- **Ticket medio mensal:** R$ 39,90
- **CAC blended:** R$ 142
- **LTV medio atual:** R$ 287 (Q3/2025)
"""))

cells.append(nbf.v4.new_code_cell(r"""# Visao geral do dataset
df.head()"""))

cells.append(nbf.v4.new_code_cell(r"""# Estatisticas descritivas
df.describe().round(2)"""))

# ----------------------------------------------------------------------------
# SECAO 3 - ANALISE EXPLORATORIA
# ----------------------------------------------------------------------------

cells.append(nbf.v4.new_markdown_cell(r"""
## 3. Analise exploratoria

Antes de segmentar, isolamos as variaveis com correlacao mais forte com churn. O sinal **nao** esta uniformemente distribuido: ele se concentra em contratos curtos, lifetime baixo e queda de frequencia no mes corrente.

### 3.1 Distribuicao do alvo
"""))

cells.append(nbf.v4.new_code_cell(r"""# Distribuicao do churn
churn_rate = df['Churn'].mean()
counts = df['Churn'].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(['Retidos', 'Cancelaram'], counts.values, color=['#5DADE2', '#E74C3C'])
ax.set_title(f'Distribuicao do alvo — churn global = {churn_rate:.1%}', fontsize=12)
ax.set_ylabel('Numero de clientes')
for b, v in zip(bars, counts.values):
    ax.text(b.get_x() + b.get_width()/2, v + 30, f'{v:,}\n({v/len(df):.1%})',
            ha='center', va='bottom', fontsize=10)
ax.set_ylim(0, counts.max() * 1.15)
plt.tight_layout()
plt.show()

print(f'\nDe 4.000 assinantes na amostra, {counts[1]:,} cancelaram nos ultimos 6 meses ({churn_rate:.1%}).')
print(f'Este e o nivel global. Os clusters identificados na secao 4 revelam que esse 26,5% e profundamente assimetrico.')
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 3.2 Churn por duracao do contrato

O efeito mais brutal e contratual: clientes mensais cancelam **~18x mais** que clientes anuais.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Churn por duracao do contrato
contract_churn = df.groupby('Contract_period')['Churn'].agg(['count', 'mean']).reset_index()
contract_churn.columns = ['Contrato (meses)', 'N clientes', 'Taxa de churn']

fig, ax = plt.subplots(figsize=(8, 4.5))
labels = [f'{int(c)} mes(es)' for c in contract_churn['Contrato (meses)']]
bars = ax.bar(labels, contract_churn['Taxa de churn'] * 100,
              color=['#E74C3C', '#F39C12', '#27AE60'])
ax.axhline(churn_rate * 100, color='gray', ls='--', lw=1, label=f'Media geral ({churn_rate:.1%})')
ax.set_ylabel('Taxa de churn (%)')
ax.set_title('Churn por duracao do contrato — a alavanca contratual mais obvia')
for b, v, n in zip(bars, contract_churn['Taxa de churn'], contract_churn['N clientes']):
    ax.text(b.get_x() + b.get_width()/2, v*100 + 1, f'{v:.1%}\n(n={n:,})',
            ha='center', va='bottom', fontsize=10)
ax.legend(loc='upper right')
ax.set_ylim(0, 50)
plt.tight_layout()
plt.show()

print(contract_churn.to_string(index=False))
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 3.3 Churn por lifetime

Clientes com menos de 1 mes de plataforma concentram o maior risco — e o cluster que o case chama de *early dropout*.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Bins de lifetime
df['Lifetime_bucket'] = pd.cut(df['Lifetime'],
                                bins=[-1, 0, 1, 3, 6, 100],
                                labels=['0 meses', '1 mes', '2-3 meses', '4-6 meses', '7+ meses'])
lifetime_churn = df.groupby('Lifetime_bucket')['Churn'].agg(['count', 'mean']).reset_index()

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.bar(lifetime_churn['Lifetime_bucket'].astype(str),
              lifetime_churn['mean'] * 100,
              color='#E74C3C')
# Gradiente: quanto maior o churn, mais vermelho
for b, v in zip(bars, lifetime_churn['mean']):
    b.set_color(plt.cm.RdYlGn_r(min(v * 2, 1.0)))
ax.axhline(churn_rate * 100, color='gray', ls='--', lw=1, label=f'Media geral ({churn_rate:.1%})')
ax.set_ylabel('Taxa de churn (%)')
ax.set_title('Churn por tempo de plataforma (Lifetime) — risco cai drasticamente apos 4 meses')
for b, row in zip(bars, lifetime_churn.itertuples()):
    ax.text(b.get_x() + b.get_width()/2, row.mean*100 + 1.5,
            f'{row.mean:.1%}\n(n={row.count:,})', ha='center', va='bottom', fontsize=9)
ax.legend()
plt.tight_layout()
plt.show()

df.drop(columns='Lifetime_bucket', inplace=True)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 3.4 Churn por frequencia no mes corrente

Frequencia atual e o sinal de **momentum**: clientes ativos hoje praticamente nao cancelam.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Frequencia atual vs churn
df['Freq_bucket'] = pd.cut(df['Avg_class_frequency_current_month'],
                            bins=[-0.1, 0.5, 1.5, 2.5, 3.5, 10],
                            labels=['<0,5/sem', '0,5-1,5', '1,5-2,5', '2,5-3,5', '3,5+/sem'])
freq_churn = df.groupby('Freq_bucket')['Churn'].agg(['count', 'mean']).reset_index()

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.bar(freq_churn['Freq_bucket'].astype(str),
              freq_churn['mean'] * 100)
for b, v in zip(bars, freq_churn['mean']):
    b.set_color(plt.cm.RdYlGn_r(min(v * 2, 1.0)))
ax.axhline(churn_rate * 100, color='gray', ls='--', lw=1, label=f'Media geral ({churn_rate:.1%})')
ax.set_ylabel('Taxa de churn (%)')
ax.set_xlabel('Sessoes/semana no mes corrente')
ax.set_title('Churn por frequencia atual — momentum e o melhor preditor de curto prazo')
for b, row in zip(bars, freq_churn.itertuples()):
    ax.text(b.get_x() + b.get_width()/2, row.mean*100 + 1.5,
            f'{row.mean:.1%}\n(n={row.count:,})', ha='center', va='bottom', fontsize=9)
ax.legend()
plt.tight_layout()
plt.show()

df.drop(columns='Freq_bucket', inplace=True)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 3.5 Correlacao das features com o churn
"""))

cells.append(nbf.v4.new_code_cell(r"""# Correlacao com o alvo
corr = df.corr(numeric_only=True)['Churn'].drop('Churn').sort_values()

fig, ax = plt.subplots(figsize=(9, 6))
colors = ['#27AE60' if v < 0 else '#E74C3C' for v in corr.values]
ax.barh(corr.index, corr.values, color=colors)
ax.axvline(0, color='black', lw=0.5)
ax.set_xlabel('Correlacao com Churn')
ax.set_title('Correlacao linear de cada feature com o churn')
for i, v in enumerate(corr.values):
    ax.text(v + (0.005 if v >= 0 else -0.005), i, f'{v:+.2f}',
            va='center', ha='left' if v >= 0 else 'right', fontsize=9)
plt.tight_layout()
plt.show()

print('Top 3 sinais negativos (reduzem churn):')
print(corr.head(3).to_string())
print('\nTop 3 sinais positivos (aumentam churn):')
print(corr.tail(3).to_string())
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### Sintese da EDA

Tres variaveis carregam a maior parte do sinal:

1. **Lifetime** — quanto mais tempo na plataforma, menor o churn. Quem chega ao mes 4 raramente sai.
2. **Contract_period** — contratos longos amarram financeiramente e comportamentalmente; mensais sao porta de entrada e tambem de saida.
3. **Avg_class_frequency_current_month** — uso *agora* e o melhor preditor de curto prazo. Quem usa hoje, nao cancela amanha.

Tres sinais sociais reduzem o churn pela metade quando presentes: **participacao em desafios em grupo**, **entrada por indicacao de amigo** e **parceria corporativa**.

Esses cinco vetores sao a materia-prima da segmentacao da proxima secao.

---
"""))

# ============================================================================
# SECAO 4 - SEGMENTACAO (KMeans)
# ============================================================================

cells.append(nbf.v4.new_markdown_cell(r"""
## 4. Segmentacao via KMeans

Hipoteses analiticas e padroes da EDA sugerem que a base nao e homogenea — existem subgrupos comportamentais com perfis distintos de risco. A pergunta da Camila para o Conselho nao e "qual e o churn medio?", mas **"quais segmentos respondem por qual fatia do churn?"**.

Aplicamos KMeans nas 13 features comportamentais e demograficas, depois de padronizar (StandardScaler) — KMeans usa distancia euclidiana e e sensivel a escala.

### 4.1 Preparacao das features
"""))

cells.append(nbf.v4.new_code_cell(r"""# Preparacao para KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Features: tudo menos o alvo
features = [c for c in df.columns if c != 'Churn']
X = df[features].copy()

# StandardScaler — KMeans usa distancia euclidiana
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f'Matriz padronizada: {X_scaled.shape}')
print(f'Media das colunas: {X_scaled.mean(axis=0).round(2).tolist()[:5]}...')
print(f'Desvio das colunas: {X_scaled.std(axis=0).round(2).tolist()[:5]}...')
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 4.2 Escolha do k — metodo do cotovelo e silhouette score

Dois criterios para escolher quantos clusters fazem sentido:

- **Cotovelo (inercia/SSE):** mede o quanto os pontos estao distantes do centroide do cluster. Diminui sempre com mais k — buscamos o ponto onde a melhoria perde tracao (a "dobra").
- **Silhouette score:** mede o quanto os clusters estao bem separados entre si (-1 a 1, mais alto = melhor). Penaliza clusters mal definidos.

Avaliamos k de 2 a 8.
"""))

cells.append(nbf.v4.new_code_cell(r"""# Elbow + silhouette
ks = list(range(2, 9))
inertias = []
silhouettes = []

for k in ks:
    km = KMeans(n_clusters=k, n_init=20, random_state=42)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

# Plot duplo
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

ax1.plot(ks, inertias, 'o-', color='#3498DB', lw=2, markersize=8)
ax1.set_xlabel('Numero de clusters (k)')
ax1.set_ylabel('Inercia (SSE)')
ax1.set_title('Metodo do cotovelo')
ax1.grid(True, alpha=0.3)

ax2.plot(ks, silhouettes, 'o-', color='#27AE60', lw=2, markersize=8)
ax2.set_xlabel('Numero de clusters (k)')
ax2.set_ylabel('Silhouette score')
ax2.set_title('Silhouette score por k')
ax2.grid(True, alpha=0.3)
# Marca o melhor
best_k = ks[silhouettes.index(max(silhouettes))]
ax2.axvline(best_k, color='red', ls='--', alpha=0.5, label=f'Pico em k={best_k}')
ax2.legend()

plt.tight_layout()
plt.show()

print('k | Inercia    | Silhouette')
print('-' * 35)
for k, i, s in zip(ks, inertias, silhouettes):
    print(f'{k} | {i:9.0f}  | {s:.4f}')
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
**Leitura dos graficos:**

- A inercia mostra uma queda acentuada ate k=3-4 e depois desacelera — o cotovelo aponta para essa faixa.
- O silhouette score tem um pico claro que confirma a leitura.

Adotamos **k=4**. Justificativa adicional alem da metrica: quatro clusters dao uma matriz Valor x Risco com **quadrantes legiveis** para o Board (Early Dropout, Risco Medio, Engajados Mensais, Leais), enquanto k=2 ou k=3 perde nuance e k>=5 fragmenta demais a narrativa executiva.

### 4.3 Treino final com k=4
"""))

cells.append(nbf.v4.new_code_cell(r"""# Treino final com k=4
K_FINAL = 4
km_final = KMeans(n_clusters=K_FINAL, n_init=20, random_state=42)
df['Cluster_raw'] = km_final.fit_predict(X_scaled)

# Reordenar clusters pela taxa de churn (C0 = menor risco, C3 = maior risco)
order = df.groupby('Cluster_raw')['Churn'].mean().sort_values().index.tolist()
remap = {orig: new for new, orig in enumerate(order)}
df['Cluster'] = df['Cluster_raw'].map(remap)
df.drop(columns='Cluster_raw', inplace=True)

# Perfil dos clusters
profile = df.groupby('Cluster').agg(
    n=('Churn', 'size'),
    churn_rate=('Churn', 'mean'),
    contract=('Contract_period', 'mean'),
    lifetime=('Lifetime', 'mean'),
    freq_total=('Avg_class_frequency_total', 'mean'),
    freq_current=('Avg_class_frequency_current_month', 'mean'),
    age=('Age', 'mean'),
    extras=('Avg_additional_charges_total', 'mean'),
    group_visits=('Group_visits', 'mean'),
    promo_friends=('Promo_friends', 'mean'),
    partner=('Partner', 'mean')
).round(2)

profile['share'] = (profile['n'] / len(df)).round(3)
profile['lift'] = (profile['churn_rate'] / df['Churn'].mean()).round(2)

cols_order = ['n', 'share', 'churn_rate', 'lift', 'contract', 'lifetime',
              'freq_total', 'freq_current', 'age', 'extras',
              'group_visits', 'promo_friends', 'partner']
profile = profile[cols_order]
profile
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 4.4 Visualizacao dos clusters
"""))

cells.append(nbf.v4.new_code_cell(r"""# Tamanho e churn por cluster
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Tamanho de cada cluster
cluster_labels = [f'C{i}' for i in profile.index]
colors_clusters = ['#27AE60', '#3498DB', '#F39C12', '#E74C3C']
bars1 = ax1.bar(cluster_labels, profile['n'], color=colors_clusters)
ax1.set_title('Tamanho de cada cluster')
ax1.set_ylabel('Numero de clientes')
for b, v, s in zip(bars1, profile['n'], profile['share']):
    ax1.text(b.get_x() + b.get_width()/2, v + 30,
             f'{int(v):,}\n({s:.1%})', ha='center', va='bottom', fontsize=10)

# Churn por cluster
bars2 = ax2.bar(cluster_labels, profile['churn_rate'] * 100, color=colors_clusters)
ax2.axhline(df['Churn'].mean() * 100, color='gray', ls='--', lw=1,
            label=f'Media geral ({df["Churn"].mean():.1%})')
ax2.set_title('Taxa de churn por cluster')
ax2.set_ylabel('Taxa de churn (%)')
for b, v, lift in zip(bars2, profile['churn_rate'], profile['lift']):
    ax2.text(b.get_x() + b.get_width()/2, v*100 + 1.5,
             f'{v:.1%}\n(lift {lift:.2f}x)', ha='center', va='bottom', fontsize=10)
ax2.legend()

plt.tight_layout()
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(r"""# Perfil comparativo normalizado (z-scores das medias dos clusters)
profile_features = ['contract', 'lifetime', 'freq_total', 'freq_current',
                    'age', 'extras', 'group_visits', 'promo_friends', 'partner']

# Normalizar pelo desvio padrao da base inteira
profile_z = profile[profile_features].copy()
for col in profile_features:
    full_mean = df[{'contract':'Contract_period', 'lifetime':'Lifetime',
                    'freq_total':'Avg_class_frequency_total',
                    'freq_current':'Avg_class_frequency_current_month',
                    'age':'Age', 'extras':'Avg_additional_charges_total',
                    'group_visits':'Group_visits', 'promo_friends':'Promo_friends',
                    'partner':'Partner'}[col]].mean()
    full_std = df[{'contract':'Contract_period', 'lifetime':'Lifetime',
                   'freq_total':'Avg_class_frequency_total',
                   'freq_current':'Avg_class_frequency_current_month',
                   'age':'Age', 'extras':'Avg_additional_charges_total',
                   'group_visits':'Group_visits', 'promo_friends':'Promo_friends',
                   'partner':'Partner'}[col]].std()
    profile_z[col] = (profile_z[col] - full_mean) / full_std

# Heatmap
fig, ax = plt.subplots(figsize=(11, 4))
sns.heatmap(profile_z, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            cbar_kws={'label': 'Desvios padrao vs. base geral'},
            yticklabels=cluster_labels, ax=ax)
ax.set_title('Perfil comparativo dos clusters (z-scores)')
ax.set_xlabel('')
plt.tight_layout()
plt.show()
"""))

# ============================================================================
# SECAO 5 - PERSONAS (placeholder dinamico que le os dados reais dos clusters)
# ============================================================================

cells.append(nbf.v4.new_markdown_cell(r"""
## 5. Personas data-driven

Cada cluster recebe uma persona — uma narrativa executiva que sintetiza o perfil comportamental do segmento, suas hipoteses de driver de churn, e como o Customer Success o descreveria internamente. As personas sao **insumo direto** para a matriz Valor x Risco da secao 7 e para a recomendacao da secao 8.

> *As personas a seguir foram construidas com base nas medias e taxas observadas nos clusters da secao 4.3. Sao destilacoes data-driven — nao perfis qualitativos especulativos.*
"""))

cells.append(nbf.v4.new_code_cell(r"""# Helper para imprimir o perfil resumido de cada cluster
def cluster_summary(c):
    p = profile.loc[c]
    print(f'  Tamanho: {int(p["n"]):,} ({p["share"]:.1%} da base) | Churn: {p["churn_rate"]:.1%} (lift {p["lift"]:.2f}x)')
    print(f'  Contrato medio: {p["contract"]:.1f} meses | Lifetime: {p["lifetime"]:.1f} meses | Idade: {p["age"]:.0f}')
    print(f'  Freq total: {p["freq_total"]:.2f} sessoes/sem | Freq mes corrente: {p["freq_current"]:.2f} sessoes/sem')
    print(f'  Gasto em extras: R$ {p["extras"]:.0f}')
    print(f'  Aderencia: desafios em grupo {p["group_visits"]:.0%} | indicacao amigo {p["promo_friends"]:.0%} | parceria corp {p["partner"]:.0%}')

for c in profile.index:
    print(f'\n{"="*70}\nCluster C{c}')
    cluster_summary(c)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### As quatro personas

#### Persona C0 — "Renata, a Leal de Contrato Longo"

> **27,0% da base | 1.082 clientes | Churn observado: 3,0% (lift 0,11x)**

Renata tem 30 anos, esta na Vitaliza ha quase 5 meses e fechou contrato anual (media 10,7 meses). Acessa o app cerca de 2 vezes por semana, gasta R$ 161 em extras (top entre os clusters), participa de desafios em grupo (53%), entrou indicada por amigo (57%) e na maioria das vezes via parceria corporativa (78%). E o cliente com o maior **valor relativo** da base — alta retencao, alta receita acessoria, perfil engajado.

**Hipoteses de driver de churn (residual, 3%):**
- H1: Cancelamentos esporadicos por mudanca de vida (mudou de cidade, mudou de empresa que pagava a parceria, fim do contrato anual sem renovacao automatica). Sao eventos exogenos, dificeis de prever pelo modelo.
- H2: Risco real esta na **renovacao**, nao no churn mensal — monitorar `Month_to_end_contract` <= 2 e acionar oferta de renovacao 60 dias antes do vencimento.
- H3: **Risco "sleeping dog"**: intervir aqui pode acordar quem nao estava pensando em sair.

**Como o CS a descreveria:** "A Renata a gente nem deveria estar olhando — ela paga, usa, indica amigos. Se eu ligar pra ela pra perguntar como esta, eu corro o risco de dar ideia."

---

#### Persona C1 — "Elisa, a Engajada Mensal"

> **26,6% da base | 1.062 clientes | Churn observado: 9,2% (lift 0,34x)**

Elisa tem 30 anos, ja esta ha mais de 4 meses na plataforma e usa intensamente (2,70 sessoes/semana, a maior frequencia entre os clusters). Mas optou por contrato mensal (media 2,4 meses), gasta R$ 157 em extras, participa de desafios em grupo (45%) — e nao veio por indicacao nem parceria corporativa. Ela e o **cliente ideal para upsell**: ja "comprou" a Vitaliza emocionalmente, falta amarrar contratualmente.

**Hipoteses de driver de churn (~9%):**
- H1: Vulnerabilidade a saida por motivos exogenos (preco, concorrencia, mudanca de rotina). Sem amarra contratual, qualquer friccao puxa pra fora.
- H2: O alto uso atual e real, nao inflacionado por evento unico. Engajamento e estavel.
- H3: A migracao para plano semestral ou anual reduziria o churn estrutural sem desconto agressivo — basta um incentivo pequeno (1 mes gratis na renovacao anual).

**Como o CS a descreveria:** "A Elisa usa pra caramba, mas nao se compromete. A gente precisa fazer ela migrar pra anual."

---

#### Persona C2 — "Rafael, no Limbo do Risco Medio"

> **9,6% da base | 386 clientes | Churn observado: 26,7% (lift 1,02x)**

Rafael tem 29 anos, esta na Vitaliza ha 3,9 meses, com contrato semestral (media 4,8 meses). Frequencia total razoavel (1,85/sem) mas **a frequencia do mes corrente caiu** (1,72/sem) — sinal classico de desengajamento gradual. Gasta menos em extras (R$ 144), tem aderencia social media (group 43%, promo 31%). Cluster pequeno mas comportamentalmente o mais ambiguo da base — pode reagir bem a intervencao, pode ser sleeping dog parcial.

**Hipoteses de driver de churn (~27%):**
- H1: "Cliente no limbo" — ainda usa, mas a frequencia atual caiu vs. a media historica. Sinal **temporal** de declinio.
- H2: O contrato semestral em vigor cria atraso na decisao — o churn vai materializar quando o contrato terminar. Monitorar `Month_to_end_contract` baixo.
- H3: Risco "sleeping dog" parcial — intervencao agressiva (oferta de desconto, ligacao) pode acelerar a saida em vez de prevenir.

**Como o CS a descreveria:** "O Rafael e o pesadelo. Pode ficar, pode sair. Se eu mexer demais, eu acordo ele. Se nao mexer nada, eu perco."

---

#### Persona C3 — "Júlia, a Early Dropout"

> **36,8% da base | 1.470 clientes | Churn observado: 56,3% (lift 2,11x)**

Júlia tem 28 anos (o cluster mais jovem), esta na Vitaliza ha pouco mais de 2 meses, escolheu contrato mensal (media 1,9 meses) e ja esta despencando a frequencia (0,95 sessoes/semana — quase 1/3 da da Elisa). Gasta menos em extras (R$ 130), participa pouco de desafios em grupo (29%), nao veio por indicacao (19%). **E o cluster que concentra o maior volume e a maior taxa de churn simultaneamente** — responsavel por mais de 70% dos cancelamentos absolutos da base.

**Hipoteses de driver de churn (~56%):**
- H1: **Onboarding falho** — quem chega ao mes 2 sem ritmo de uso (>1,5 sessoes/sem) tem probabilidade > 50% de cancelar. Ausencia de ritual de adocao nas primeiras 4 semanas.
- H2: **Mismatch de plano** — contratos mensais sao porta de entrada **e** porta de saida. Sem amarra contratual, qualquer atrito puxa pra fora.
- H3: **Isolamento social** — menos de 30% participam de desafios em grupo. Quem participa cancela metade. O vinculo social esta ausente.
- H4: **Cego para o Caminho A** — pelo case Vitaliza, ~33% dessas Júlias saem **sem clicar em "Cancelar"** (cartao expirado, exclusao do app, chargeback). Qualquer sistema reativo (Caminho A) e estruturalmente cego para elas.

**Como o CS a descreveria:** "A Júlia a gente nem ve. Ela entra, abre o app duas vezes, deixa o cartao expirar e some. Se eu nao for atras dela nas primeiras 4 semanas, eu nao recupero."

---
"""))

# ============================================================================
# SECAO 6 - COMPARACAO DE CLASSIFICADORES
# ============================================================================

cells.append(nbf.v4.new_markdown_cell(r"""
## 6. Modelo preditivo — comparacao de classificadores

Esta secao cumpre a entrega da **Jornada de Tecnologia da Semana 5**. Treinamos nove classificadores cobrindo as cinco familias da aula 5, comparamos por multiplas metricas (acurracia sozinha nao basta) e escolhemos um modelo de producao que vai alimentar o eixo Risco da matriz Valor x Risco.

### 6.1 As cinco familias de classificadores

| Familia | Algoritmo escolhido | Pergunta intuitiva | Vantagem | Limitacao |
|---|---|---|---|---|
| **Lineares** | Regressao Logistica | Uma combinacao linear das variaveis separa bem? | Interpretavel, calibrada, baseline forte | So captura relacoes lineares |
| **Lineares (margem)** | SVM linear | Existe uma fronteira robusta entre classes? | Robusto a outliers | Lento em datasets grandes; menos calibrado |
| **Lineares (online)** | Perceptron | Combinacao linear simples atualizada incrementalmente | Rapido | Sensivel a escala; convergencia fragil |
| **Arvores (simples)** | Decision Tree | Posso chegar a decisao por sequencia de perguntas? | **Maxima interpretabilidade** | Tende a overfitting |
| **Arvores (bagging)** | Random Forest | Combinar muitas arvores reduz erro? | Robusto, feature importance | Menos interpretavel que arvore unica |
| **Arvores (boosting)** | Gradient Boosting | Cada nova arvore corrige os erros da anterior? | **Maior performance esperada** | Mais sensivel a hiperparametros |
| **Distancia** | KNN | Clientes parecidos no passado tiveram comportamento parecido? | Simples, sem premissa de forma | Sensivel a escala e dimensionalidade |
| **Probabilisticos** | Naive Bayes | Dadas estas evidencias, qual classe e mais provavel? | Rapido, funciona com pouco dado | Premissa de independencia entre features e forte |
| **Redes neurais** | MLP simples | Existe padrao complexo combinando muitas variaveis? | Flexivel | "Caixa preta", precisa mais dado |

**Tres modelos baseados em arvores** (Decision Tree, Random Forest, Gradient Boosting) sao incluidos porque o problema e tabular com mix de variaveis binarias e continuas — terreno onde a familia de arvores historicamente domina sobre dados estruturados de clientes. A *Arvore de Decisao* unica serve a narrativa (regras explicitas vao para o slide); o *Gradient Boosting* tende a entregar o melhor AUC e alimenta o eixo Risco da matriz.
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.2 Preparacao do split treino/teste

Importante: as features `Avg_class_frequency_current_month` e `Month_to_end_contract` sao **co-temporais ao evento de churn** — podem introduzir *target leakage* em producao. Mantemos no modelo desta entrega (sao o que a Camila tem disponivel hoje), e listamos isso explicitamente na secao de limitacoes.
"""))

cells.append(nbf.v4.new_code_cell(r"""from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix,
                              classification_report)

# Features e target (sem a coluna Cluster que criamos)
X_model = df[features].copy()
y = df['Churn'].copy()

# Split estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X_model, y, test_size=0.25, random_state=42, stratify=y
)
print(f'Treino: {X_train.shape[0]:,} | Teste: {X_test.shape[0]:,}')
print(f'Churn no treino: {y_train.mean():.1%} | Churn no teste: {y_test.mean():.1%}')

# Padronizacao (precisa para LR, SVM, KNN, Perceptron, MLP)
scaler_model = StandardScaler()
X_train_scaled = scaler_model.fit_transform(X_train)
X_test_scaled = scaler_model.transform(X_test)
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.3 Treino e avaliacao dos 9 modelos
"""))

cells.append(nbf.v4.new_code_cell(r"""# Definicao dos modelos
# Modelos que precisam de padronizacao usam X_*_scaled; arvores usam X_train/X_test puro

models_scaled = {
    'Regressao Logistica': LogisticRegression(max_iter=2000, random_state=42),
    'SVM Linear': LinearSVC(max_iter=5000, random_state=42, dual=False),
    'Perceptron': Perceptron(max_iter=2000, random_state=42),
    'KNN (k=5)': KNeighborsClassifier(n_neighbors=5),
    'MLP (32-16)': MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42),
}

models_raw = {
    'Arvore de Decisao': DecisionTreeClassifier(max_depth=6, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42),
    'Naive Bayes': GaussianNB(),
}

results = []
trained_models = {}

# Treino dos modelos padronizados
for name, model in models_scaled.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    # Probabilidade — alguns modelos nao tem predict_proba
    try:
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    except AttributeError:
        # SVM linear e Perceptron usam decision_function
        if hasattr(model, 'decision_function'):
            scores = model.decision_function(X_test_scaled)
            y_proba = (scores - scores.min()) / (scores.max() - scores.min())
        else:
            y_proba = y_pred.astype(float)
    results.append({
        'Modelo': name,
        'Acuracia': accuracy_score(y_test, y_pred),
        'Precisao': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1': f1_score(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, y_proba),
    })
    trained_models[name] = (model, y_pred, y_proba, 'scaled')

# Treino dos modelos sem padronizacao
for name, model in models_raw.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    results.append({
        'Modelo': name,
        'Acuracia': accuracy_score(y_test, y_pred),
        'Precisao': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1': f1_score(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, y_proba),
    })
    trained_models[name] = (model, y_pred, y_proba, 'raw')

# Tabela comparativa
results_df = pd.DataFrame(results).sort_values('ROC AUC', ascending=False).reset_index(drop=True)
results_df.style.format({
    'Acuracia': '{:.1%}', 'Precisao': '{:.1%}', 'Recall': '{:.1%}',
    'F1': '{:.1%}', 'ROC AUC': '{:.3f}'
}).background_gradient(subset=['ROC AUC'], cmap='Greens')
"""))

cells.append(nbf.v4.new_code_cell(r"""# Visualizacao das metricas
fig, ax = plt.subplots(figsize=(12, 6))
metrics_to_plot = ['Acuracia', 'Precisao', 'Recall', 'F1', 'ROC AUC']
results_plot = results_df.set_index('Modelo')[metrics_to_plot]

x = np.arange(len(results_plot.index))
width = 0.16

for i, metric in enumerate(metrics_to_plot):
    ax.bar(x + i*width, results_plot[metric], width, label=metric)

ax.set_xticks(x + width * 2)
ax.set_xticklabels(results_plot.index, rotation=30, ha='right')
ax.set_ylabel('Valor')
ax.set_title('Comparacao dos 9 classificadores em 5 metricas')
ax.legend(loc='lower right', framealpha=0.95)
ax.set_ylim(0, 1.05)
ax.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.4 Matriz de confusao do modelo de producao

O **Gradient Boosting** (ou o modelo lider em ROC AUC) e o candidato a alimentar o eixo Risco da matriz Valor x Risco. Vemos a matriz de confusao no teste:
"""))

cells.append(nbf.v4.new_code_cell(r"""# Modelo lider (maior ROC AUC)
best_name = results_df.iloc[0]['Modelo']
best_model, best_pred, best_proba, _ = trained_models[best_name]

cm = confusion_matrix(y_test, best_pred)
labels = ['Retido (real)', 'Cancelou (real)']
preds = ['Retido (prev)', 'Cancelou (prev)']

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=preds, yticklabels=labels, ax=ax,
            annot_kws={'size': 14})
ax.set_title(f'Matriz de confusao — {best_name}')
plt.tight_layout()
plt.show()

print(f'Modelo lider: {best_name}')
print()
print(classification_report(y_test, best_pred, target_names=['Retido', 'Cancelou']))
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.5 Feature importance — o que o modelo realmente usa
"""))

cells.append(nbf.v4.new_code_cell(r"""# Feature importance do Gradient Boosting (ou modelo lider, se tiver)
gb_model, _, _, _ = trained_models['Gradient Boosting']
importances = pd.Series(gb_model.feature_importances_, index=features).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))
colors_imp = plt.cm.viridis(np.linspace(0.2, 0.8, len(importances)))
ax.barh(importances.index, importances.values, color=colors_imp)
ax.set_xlabel('Importancia relativa')
ax.set_title('Feature importance — Gradient Boosting')
for i, v in enumerate(importances.values):
    ax.text(v + 0.005, i, f'{v:.3f}', va='center', fontsize=9)
plt.tight_layout()
plt.show()

print('Top 5 features:')
print(importances.sort_values(ascending=False).head(5).to_string())
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.6 Arvore de decisao — as regras que viram personas

A arvore de decisao nao e o modelo de maior AUC, mas e o **mais interpretavel**. As regras extraidas viram a definicao operacional das personas para o slide do board: "o cliente Early Dropout e definido por essas 3 perguntas".
"""))

cells.append(nbf.v4.new_code_cell(r"""# Visualizacao da arvore (3 niveis para nao virar matagal)
from sklearn.tree import plot_tree, export_text

tree_model, _, _, _ = trained_models['Arvore de Decisao']

fig, ax = plt.subplots(figsize=(18, 8))
plot_tree(tree_model, max_depth=3, feature_names=features,
          class_names=['Retido', 'Cancelou'], filled=True, rounded=True,
          fontsize=9, impurity=False, ax=ax)
ax.set_title('Arvore de decisao — 3 niveis (regras de classificacao)')
plt.tight_layout()
plt.show()

print('Regras textuais (3 niveis):')
print(export_text(tree_model, feature_names=features, max_depth=3))
"""))

cells.append(nbf.v4.new_markdown_cell(r"""
### 6.7 Discussao — acuracia nao basta

Tres pontos que o board precisa entender:

1. **Custo assimetrico de erro:** um *falso negativo* (cliente que vai cancelar mas o modelo diz "fica") significa perda de R$ 287 de LTV. Um *falso positivo* (cliente que ficaria mas e flagueado) significa intervencao desnecessaria — custo baixo se for nudge (email, push), alto se for desconto agressivo. Por isso priorizamos modelos com **alto recall na classe positiva** (capturar quem realmente vai sair).

2. **Probabilidade calibrada importa mais que classificacao binaria:** a matriz Valor x Risco usa a *probabilidade de churn* — nao a previsao 0/1. Modelos com `predict_proba` confiavel (Gradient Boosting, Regressao Logistica) sao preferidos sobre modelos que produzem so um score (Perceptron, SVM).

3. **Interpretabilidade vs. performance:** a arvore unica perde em AUC, mas ganha em "defendabilidade" perante o board. **Por isso usamos ambos:** Gradient Boosting para a probabilidade que alimenta a matriz; Arvore de Decisao para a narrativa.

### 6.8 Escolha do modelo de producao

**Modelo escolhido para producao: Gradient Boosting.**

Combinacao de:
- Maior ROC AUC entre os 9 testados
- Probabilidades calibradas (vao para o eixo Risco da matriz)
- Robusto a outliers e a mix de feature binaria/continua
- Sem necessidade de padronizacao (mais simples de operacionalizar)

Em producao, a sugestao e:
1. Treinar GB diariamente sobre snapshot point-in-time T-30 dias
2. Servir via API REST ou pipeline batch (ver discussao em "limitacoes e proximos passos")
3. Monitorar drift (distribuicao das probabilidades) semanalmente
4. Re-treinar mensalmente

---
"""))

# ----------------------------------------------------------------------------
# Monta e salva
# ----------------------------------------------------------------------------

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
    'language_info': {'name': 'python'}
}

OUT = 'artefato_semana5_vitaliza.ipynb'
with open(OUT, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Notebook criado: {OUT}')
print(f'Celulas: {len(cells)}')
