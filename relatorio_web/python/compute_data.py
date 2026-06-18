"""
Roda todas as analises (EDA, KMeans, classificadores) e exporta um arquivo JSON
que e consumido pelo frontend React em src/data/analysis_data.json.

Uso:
    python compute_data.py

Saida:
    ../frontend/src/data/analysis_data.json
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (silhouette_score, accuracy_score, precision_score,
                              recall_score, f1_score, roc_auc_score, confusion_matrix)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
HERE = Path(__file__).parent
CSV_PATH = HERE.parent / 'dados' / 'gym_churn_us.csv'
OUT_PATH = HERE.parent / 'frontend' / 'src' / 'data' / 'analysis_data.json'
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Premissas financeiras do business case Vitaliza
TICKET_MEDIO = 39.90
CAC = 142.00

# ---------------------------------------------------------------------------
# 1. Carrega
# ---------------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)
features = [c for c in df.columns if c != 'Churn']

# ---------------------------------------------------------------------------
# 2. EDA
# ---------------------------------------------------------------------------
churn_global = float(df['Churn'].mean())

# Churn por contract_period
contract_breakdown = []
for cp, grp in df.groupby('Contract_period'):
    contract_breakdown.append({
        'contract': int(cp),
        'n': int(len(grp)),
        'churn_rate': float(grp['Churn'].mean()),
    })

# Churn por bucket de lifetime
df['_lifetime_bucket'] = pd.cut(df['Lifetime'],
                                 bins=[-1, 0, 1, 3, 6, 100],
                                 labels=['0 meses', '1 mes', '2-3 meses', '4-6 meses', '7+ meses'])
lifetime_breakdown = []
for bucket, grp in df.groupby('_lifetime_bucket', observed=True):
    lifetime_breakdown.append({
        'bucket': str(bucket),
        'n': int(len(grp)),
        'churn_rate': float(grp['Churn'].mean()),
    })

# Churn por frequencia atual
df['_freq_bucket'] = pd.cut(df['Avg_class_frequency_current_month'],
                             bins=[-0.1, 0.5, 1.5, 2.5, 3.5, 10],
                             labels=['<0,5/sem', '0,5-1,5', '1,5-2,5', '2,5-3,5', '3,5+/sem'])
freq_breakdown = []
for bucket, grp in df.groupby('_freq_bucket', observed=True):
    freq_breakdown.append({
        'bucket': str(bucket),
        'n': int(len(grp)),
        'churn_rate': float(grp['Churn'].mean()),
    })

# Correlacoes
corr = df[features + ['Churn']].corr(numeric_only=True)['Churn'].drop('Churn')
correlations = [
    {'feature': feat, 'corr': float(val)}
    for feat, val in corr.sort_values().items()
]

df.drop(columns=['_lifetime_bucket', '_freq_bucket'], inplace=True)

# ---------------------------------------------------------------------------
# 3. KMeans
# ---------------------------------------------------------------------------
X = df[features].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Elbow + silhouette
elbow_data = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=20, random_state=42)
    labels = km.fit_predict(X_scaled)
    elbow_data.append({
        'k': k,
        'inertia': float(km.inertia_),
        'silhouette': float(silhouette_score(X_scaled, labels)),
    })

# Treino final com k=4
K_FINAL = 4
km_final = KMeans(n_clusters=K_FINAL, n_init=20, random_state=42)
df['Cluster_raw'] = km_final.fit_predict(X_scaled)

# Reordenar pela taxa de churn (C0 = menor risco, C3 = maior risco)
order = df.groupby('Cluster_raw')['Churn'].mean().sort_values().index.tolist()
remap = {orig: new for new, orig in enumerate(order)}
df['Cluster'] = df['Cluster_raw'].map(remap)
df.drop(columns='Cluster_raw', inplace=True)

# Personas - metadata (nomes definidos pela narrativa de negocio)
PERSONA_META = {
    0: {
        'name': 'Renata',
        'archetype': 'Leal de Contrato Longo',
        'color': '#27AE60',
        'quadrant': 'True Friends',
        'action': 'Manter engajamento. Foco em upsell, NAO em desconto.',
        'channel': 'Email/notificacao soft de renovacao 60 dias antes do vencimento',
    },
    1: {
        'name': 'Elisa',
        'archetype': 'Engajada Mensal',
        'color': '#3498DB',
        'quadrant': 'Butterflies',
        'action': 'Upsell para plano semestral/anual. Pequeno incentivo (1 mes gratis).',
        'channel': 'Push + email com oferta de upgrade contextual',
    },
    2: {
        'name': 'Rafael',
        'archetype': 'No Limbo do Risco Medio',
        'color': '#F39C12',
        'quadrant': 'Barnacles (parcial)',
        'action': 'Monitoramento ativo + nudges leves. NAO ofertar desconto.',
        'channel': 'Email com programa novo / desafio em grupo',
    },
    3: {
        'name': 'Julia',
        'archetype': 'Early Dropout',
        'color': '#E74C3C',
        'quadrant': 'Strangers',
        'action': 'Caminho B (proativo) nas primeiras 4 semanas. Caminho A nao funciona aqui.',
        'channel': 'Onboarding gamificado, desafio em grupo nas primeiras 2 semanas',
    },
}

# Perfil de cada cluster
clusters = []
for c in sorted(df['Cluster'].unique()):
    grp = df[df['Cluster'] == c]
    n = len(grp)
    churn = float(grp['Churn'].mean())
    lifetime_meses_esperado = 1.0 / churn if churn > 0 else 100.0
    ltv = TICKET_MEDIO * lifetime_meses_esperado + float(grp['Avg_additional_charges_total'].mean())
    valor_agregado = ltv * n

    clusters.append({
        'id': int(c),
        'name': PERSONA_META[c]['name'],
        'archetype': PERSONA_META[c]['archetype'],
        'color': PERSONA_META[c]['color'],
        'quadrant': PERSONA_META[c]['quadrant'],
        'action': PERSONA_META[c]['action'],
        'channel': PERSONA_META[c]['channel'],
        'n': n,
        'share': n / len(df),
        'churn_rate': churn,
        'lift': churn / churn_global,
        'contract': float(grp['Contract_period'].mean()),
        'lifetime': float(grp['Lifetime'].mean()),
        'freq_total': float(grp['Avg_class_frequency_total'].mean()),
        'freq_current': float(grp['Avg_class_frequency_current_month'].mean()),
        'age': float(grp['Age'].mean()),
        'extras': float(grp['Avg_additional_charges_total'].mean()),
        'group_visits': float(grp['Group_visits'].mean()),
        'promo_friends': float(grp['Promo_friends'].mean()),
        'partner': float(grp['Partner'].mean()),
        'ltv_estimado': float(ltv),
        'valor_agregado': float(valor_agregado),
    })

# ---------------------------------------------------------------------------
# 4. Classificadores
# ---------------------------------------------------------------------------
y = df['Churn']
X_model = df[features].copy()
X_train, X_test, y_train, y_test = train_test_split(
    X_model, y, test_size=0.25, random_state=42, stratify=y
)

scaler_model = StandardScaler()
X_train_scaled = scaler_model.fit_transform(X_train)
X_test_scaled = scaler_model.transform(X_test)

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

model_results = []
trained = {}

for name, model in models_scaled.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    try:
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    except AttributeError:
        scores = model.decision_function(X_test_scaled)
        y_proba = (scores - scores.min()) / (scores.max() - scores.min())
    model_results.append({
        'modelo': name,
        'familia': {
            'Regressao Logistica': 'Lineares',
            'SVM Linear': 'Lineares',
            'Perceptron': 'Lineares',
            'KNN (k=5)': 'Distancia',
            'MLP (32-16)': 'Redes Neurais',
        }[name],
        'acuracia': float(accuracy_score(y_test, y_pred)),
        'precisao': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'f1': float(f1_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_proba)),
    })
    trained[name] = (model, y_pred, y_proba)

for name, model in models_raw.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    model_results.append({
        'modelo': name,
        'familia': {
            'Arvore de Decisao': 'Arvores',
            'Random Forest': 'Arvores (Bagging)',
            'Gradient Boosting': 'Arvores (Boosting)',
            'Naive Bayes': 'Probabilisticos',
        }[name],
        'acuracia': float(accuracy_score(y_test, y_pred)),
        'precisao': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'f1': float(f1_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_proba)),
    })
    trained[name] = (model, y_pred, y_proba)

# Ordenar por AUC
model_results.sort(key=lambda r: r['roc_auc'], reverse=True)
best_model_name = model_results[0]['modelo']

# Feature importance do Gradient Boosting (modelo de producao)
gb_model, _, _ = trained['Gradient Boosting']
feature_importance = [
    {'feature': f, 'importance': float(imp)}
    for f, imp in sorted(zip(features, gb_model.feature_importances_),
                         key=lambda x: x[1], reverse=True)
]

# Matriz de confusao do modelo lider
best_pred = trained[best_model_name][1]
cm = confusion_matrix(y_test, best_pred).tolist()

# Probabilidade media de churn por cluster (do modelo Gradient Boosting)
# Usamos a base completa - serve para a matriz Valor x Risco
gb_proba_full = gb_model.predict_proba(X_model)[:, 1]
df['ProbaChurn'] = gb_proba_full

cluster_proba = {}
for c, grp in df.groupby('Cluster'):
    cluster_proba[int(c)] = float(grp['ProbaChurn'].mean())

# Atualiza cada cluster com a prob. media
for cluster in clusters:
    cluster['prob_churn_modelo'] = cluster_proba[cluster['id']]

# Regras textuais da arvore (3 niveis)
tree_model, _, _ = trained['Arvore de Decisao']
tree_rules = export_text(tree_model, feature_names=features, max_depth=3)

# Imagem PNG da arvore para o frontend (top 3 niveis para nao virar matagal)
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

PUBLIC_DIR = HERE.parent / 'frontend' / 'public'
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
TREE_IMG = PUBLIC_DIR / 'arvore_decisao.png'

fig, ax = plt.subplots(figsize=(20, 10), dpi=120)
plot_tree(
    tree_model,
    max_depth=3,
    feature_names=features,
    class_names=['Retido', 'Cancelou'],
    filled=True,
    rounded=True,
    fontsize=10,
    impurity=False,
    proportion=True,
    ax=ax,
)
ax.set_title('Arvore de Decisao (3 primeiros niveis) - regras de classificacao de churn',
             fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(TREE_IMG, dpi=120, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Arvore PNG salva: {TREE_IMG} ({TREE_IMG.stat().st_size / 1024:.1f} KB)')

# ---------------------------------------------------------------------------
# 5. Matriz Valor x Risco - dados consolidados
# ---------------------------------------------------------------------------
matrix_data = [
    {
        'id': c['id'],
        'persona': c['name'],
        'archetype': c['archetype'],
        'color': c['color'],
        'quadrant': c['quadrant'],
        'x_risco': c['prob_churn_modelo'],
        'y_valor_agregado': c['valor_agregado'],
        'n': c['n'],
        'share': c['share'],
        'churn_rate': c['churn_rate'],
        'ltv': c['ltv_estimado'],
    }
    for c in clusters
]

# ---------------------------------------------------------------------------
# 5b. Pipeline anti-leakage + split estratificado por persona (Aula 6)
# ---------------------------------------------------------------------------
# Plano:
#   1. Remover variaveis vazadoras (Avg_class_frequency_current_month, Month_to_end_contract)
#   2. Holdout 20% (800 clientes) estratificado por Churn, separado antes de tudo
#   3. Re-clusterizar 3200 do pool de treino em 4 personas SEM as variaveis vazadoras
#   4. Resultado: 5 particoes (Renata/Elisa/Rafael/Julia treino + Teste holdout)
#   5. Treinar GB padrao + GB com sample_weight balanceado
#   6. Atribuir personas ao teste e avaliar global + por persona

from sklearn.utils.class_weight import compute_sample_weight

LEAKY = ['Avg_class_frequency_current_month', 'Month_to_end_contract']
features_clean = [f for f in features if f not in LEAKY]
print(f'\n=== Pipeline anti-leakage ===')
print(f'Features apos remocao de leakage: {len(features_clean)} (removidas: {LEAKY})')

X_full_clean = df[features_clean].copy()
y_full = df['Churn'].copy()
cluster_full_orig = df['Cluster'].copy()  # para comparar com novo clustering

# Holdout 20% estratificado, COM os indices originais para conseguir comparar clusters
idx = np.arange(len(df))
idx_train_pool, idx_test, y_train_pool_v, y_test_v = train_test_split(
    idx, y_full, test_size=0.2, random_state=42, stratify=y_full
)
X_train_pool = X_full_clean.iloc[idx_train_pool].reset_index(drop=True)
X_test_clean = X_full_clean.iloc[idx_test].reset_index(drop=True)
y_train_pool_v = y_train_pool_v.reset_index(drop=True)
y_test_v = y_test_v.reset_index(drop=True)
cluster_orig_train = cluster_full_orig.iloc[idx_train_pool].reset_index(drop=True)
cluster_orig_test = cluster_full_orig.iloc[idx_test].reset_index(drop=True)

# Re-clusterizar pool de treino com 11 features limpas
scaler_v = StandardScaler()
X_train_scaled_v = scaler_v.fit_transform(X_train_pool)
km_v = KMeans(n_clusters=4, n_init=20, random_state=42)
cluster_train_raw = km_v.fit_predict(X_train_scaled_v)

# Reordenar pela taxa de churn (manter convencao C0=menor risco, C3=maior)
order_v = pd.DataFrame({'c': cluster_train_raw, 'y': y_train_pool_v}).groupby('c')['y'].mean().sort_values().index.tolist()
remap_v = {orig: new for new, orig in enumerate(order_v)}
cluster_train_new = np.array([remap_v[c] for c in cluster_train_raw])

# Atribuir personas ao teste usando o cluster model treinado no pool
X_test_scaled_v = scaler_v.transform(X_test_clean)
cluster_test_raw = km_v.predict(X_test_scaled_v)
cluster_test_new = np.array([remap_v[c] for c in cluster_test_raw])

# Comparar clusters novos (sem leakage) com originais (com leakage) - confusion matrix
# para o pool de treino
from sklearn.metrics import confusion_matrix as cm_func
cluster_compare_train = cm_func(cluster_orig_train, cluster_train_new, labels=[0,1,2,3]).tolist()
# Diagonal alta = personas similares; off-diagonal = mudanca
diag_sum = sum(cluster_compare_train[i][i] for i in range(4))
total_train = sum(sum(row) for row in cluster_compare_train)
overlap_pct = diag_sum / total_train

print(f'Overlap personas originais vs novas (pool treino): {overlap_pct:.1%}')
print(f'Matriz de confusao personas (linhas=original, colunas=nova):')
for i, row in enumerate(cluster_compare_train):
    print(f'  C{i}: {row}')

# Particoes de treino por persona
parts_train = {}
for c in range(4):
    mask = cluster_train_new == c
    parts_train[c] = {
        'n': int(mask.sum()),
        'churn_rate': float(y_train_pool_v[mask].mean()) if mask.sum() > 0 else 0.0,
    }
print(f'\nParticoes de treino:')
for c, p in parts_train.items():
    print(f'  C{c}: {p["n"]} clientes, churn {p["churn_rate"]:.1%}')
print(f'  TESTE (holdout): {len(idx_test)} clientes, churn {y_test_v.mean():.1%}')

# === Treinar 2 modelos GB ===
# Modelo 1: GB padrao (sem class_weight)
gb_v1 = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
gb_v1.fit(X_train_pool, y_train_pool_v)
y_pred_v1 = gb_v1.predict(X_test_clean)
y_proba_v1 = gb_v1.predict_proba(X_test_clean)[:, 1]

# Modelo 2: GB com sample_weight balanceado
gb_v2 = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
sw = compute_sample_weight('balanced', y_train_pool_v)
gb_v2.fit(X_train_pool, y_train_pool_v, sample_weight=sw)
y_pred_v2 = gb_v2.predict(X_test_clean)
y_proba_v2 = gb_v2.predict_proba(X_test_clean)[:, 1]

# Metricas globais
def metrics_dict(y_true, y_pred, y_proba):
    return {
        'acuracia': float(accuracy_score(y_true, y_pred)),
        'precisao': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'roc_auc': float(roc_auc_score(y_true, y_proba)),
        'cm': confusion_matrix(y_true, y_pred).tolist(),
    }

m_v1 = metrics_dict(y_test_v, y_pred_v1, y_proba_v1)
m_v2 = metrics_dict(y_test_v, y_pred_v2, y_proba_v2)

# Overfitting gap (train vs test) para o modelo padrao
y_proba_train_v1 = gb_v1.predict_proba(X_train_pool)[:, 1]
auc_train_v1 = float(roc_auc_score(y_train_pool_v, y_proba_train_v1))
overfit_gap_v1 = auc_train_v1 - m_v1['roc_auc']

print(f'\n=== Resultados no teste (800 clientes) ===')
print(f'{"Metrica":<12} {"GB padrao":>12} {"GB balanced":>14}')
print(f'{"Acuracia":<12} {m_v1["acuracia"]:>12.4f} {m_v2["acuracia"]:>14.4f}')
print(f'{"Recall":<12} {m_v1["recall"]:>12.4f} {m_v2["recall"]:>14.4f}')
print(f'{"Precision":<12} {m_v1["precisao"]:>12.4f} {m_v2["precisao"]:>14.4f}')
print(f'{"F1":<12} {m_v1["f1"]:>12.4f} {m_v2["f1"]:>14.4f}')
print(f'{"AUC":<12} {m_v1["roc_auc"]:>12.4f} {m_v2["roc_auc"]:>14.4f}')
print(f'\nGap AUC train-test (GB padrao): {overfit_gap_v1:+.4f}')

# Metricas por persona no holdout
per_persona = []
for c in range(4):
    mask = cluster_test_new == c
    n_cluster = int(mask.sum())
    if n_cluster == 0:
        continue
    per_persona.append({
        'cluster_id': c,
        'n_test': n_cluster,
        'churn_rate_test': float(y_test_v[mask].mean()),
        # Modelo padrao
        'recall_padrao': float(recall_score(y_test_v[mask], y_pred_v1[mask], zero_division=0)),
        'precision_padrao': float(precision_score(y_test_v[mask], y_pred_v1[mask], zero_division=0)),
        # Modelo balanceado
        'recall_balanced': float(recall_score(y_test_v[mask], y_pred_v2[mask], zero_division=0)),
        'precision_balanced': float(precision_score(y_test_v[mask], y_pred_v2[mask], zero_division=0)),
    })

print(f'\n=== Metricas por persona no teste ===')
print(f'{"Persona":<15} {"n":>5} {"Churn":>8} {"Recall pad":>12} {"Recall bal":>12}')
PERSONA_NAMES = {0: 'Renata', 1: 'Elisa', 2: 'Rafael', 3: 'Julia'}
for p in per_persona:
    print(f'C{p["cluster_id"]} {PERSONA_NAMES[p["cluster_id"]]:<10} {p["n_test"]:>5} {p["churn_rate_test"]:>8.1%} {p["recall_padrao"]:>12.4f} {p["recall_balanced"]:>12.4f}')

# Comparacao com modelo original (com leakage)
auc_original = next(r['roc_auc'] for r in model_results if r['modelo'] == 'Gradient Boosting')
recall_original = next(r['recall'] for r in model_results if r['modelo'] == 'Gradient Boosting')

# Empacotar
validation_data = {
    'plan': {
        'leaky_features_removed': LEAKY,
        'features_used': features_clean,
        'n_features': len(features_clean),
        'test_size_pct': 0.20,
        'random_state': 42,
    },
    'partitions': {
        'persona_0_renata': {'n': parts_train[0]['n'], 'churn_rate': parts_train[0]['churn_rate']},
        'persona_1_elisa':  {'n': parts_train[1]['n'], 'churn_rate': parts_train[1]['churn_rate']},
        'persona_2_rafael': {'n': parts_train[2]['n'], 'churn_rate': parts_train[2]['churn_rate']},
        'persona_3_julia':  {'n': parts_train[3]['n'], 'churn_rate': parts_train[3]['churn_rate']},
        'test_holdout':     {'n': len(idx_test), 'churn_rate': float(y_test_v.mean())},
    },
    'cluster_overlap': {
        'overlap_pct': float(overlap_pct),
        'confusion_matrix_orig_vs_new': cluster_compare_train,
    },
    'global_metrics': {
        'gb_padrao': m_v1,
        'gb_balanced': m_v2,
        'gb_padrao_auc_train': auc_train_v1,
        'gb_padrao_overfit_gap': float(overfit_gap_v1),
        'gb_original_com_leakage_auc': float(auc_original),
        'gb_original_com_leakage_recall': float(recall_original),
    },
    'per_persona': per_persona,
}

# ---------------------------------------------------------------------------
# 6. Serializa
# ---------------------------------------------------------------------------
output = {
    'meta': {
        'generated_at': pd.Timestamp.now().isoformat(),
        'dataset': 'gym_churn_us.csv (4.000 assinantes Vitaliza)',
        'ticket_medio_mensal': TICKET_MEDIO,
        'cac': CAC,
        'churn_global': churn_global,
        'n_total': len(df),
    },
    'eda': {
        'churn_global': churn_global,
        'contract_breakdown': contract_breakdown,
        'lifetime_breakdown': lifetime_breakdown,
        'freq_breakdown': freq_breakdown,
        'correlations': correlations,
    },
    'clustering': {
        'k_final': K_FINAL,
        'elbow_silhouette': elbow_data,
    },
    'clusters': clusters,
    'models': {
        'results': model_results,
        'best_model': best_model_name,
        'confusion_matrix': cm,
        'feature_importance': feature_importance,
        'tree_rules': tree_rules,
    },
    'matrix': matrix_data,
    'validation': validation_data,
}

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'OK -> {OUT_PATH}')
print(f'  Tamanho: {OUT_PATH.stat().st_size / 1024:.1f} KB')
print(f'  Clusters: {len(clusters)}')
print(f'  Modelos: {len(model_results)} (lider: {best_model_name})')
