"""
Pipeline de TREINAMENTO do modelo de churn - Case Vitaliza (Modulo 2 Inteli).

Este script e o "pipeline de treinamento" do Artefato 2. Ele NAO serve predicoes
(isso e responsabilidade do app.py, o pipeline de inferencia); ele apenas APRENDE
e SERIALIZA os artefatos que o app.py carrega depois.

Dataset: gym_churn_us.csv (4000 linhas, 14 colunas) | Target: Churn (0/1).

O que este pipeline produz e por que (mapeado aos criterios das Aulas 06 e 07):

  1. Treina DOIS cenarios para evidenciar o vazamento de dados (Aula 06, slides 30-34):
       - COM vazamento : usa as 13 features (inclui as 2 co-temporais ao churn).
       - SEM vazamento : remove Avg_class_frequency_current_month e
                         Month_to_end_contract (disponiveis tarde demais p/ intervir).
     O modelo servido em producao (churn_model.joblib) e o SEM vazamento.

  2. Para cada cenario compara 3 classificadores (LogReg, RandomForest,
     GradientBoosting) num Pipeline com StandardScaler embutido.

  3. Mede sobreajuste (Aula 06, slides 10-12): gap AUC treino-teste + validacao
     cruzada estratificada (StratifiedKFold, 5 folds).

  4. Trata desbalanceamento (Aula 06, slides 16-17): class_weight / sample_weight.

  5. Faz fine tuning de hiperparametros do modelo servido (Aula 07, slide 11):
     GridSearchCV sobre o Gradient Boosting.

  6. Guarda y_test + probabilidade no teste para que o app recalcule a matriz de
     confusao em QUALQUER threshold (Aula 06, slides 18-19 / secao de Thresholds).

  7. Classifica cada variavel como Vazamento direto / Variavel futura / Proxy tardio
     / Aceitavel (Aula 06, slide 33), gravando a tabela no artefato.

Saidas:
    - churn_model.joblib       (modelo SEM vazamento; servido pelo app)
    - churn_model_full.joblib  (modelo COM vazamento; so para comparacao didatica)
    - model_metrics.json       (comparacao completa dos dois cenarios)
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "gym_churn_us.csv"
MODEL_PATH = BASE_DIR / "churn_model.joblib"        # SEM vazamento (servido)
MODEL_FULL_PATH = BASE_DIR / "churn_model_full.joblib"  # COM vazamento (comparacao)
METRICS_PATH = BASE_DIR / "model_metrics.json"

TARGET = "Churn"
RANDOM_STATE = 42

# Features co-temporais ao evento de churn -> vazam o alvo (Aula 06, slides 30-34).
# Sao removidas no cenario "sem vazamento", que e o modelo levado a producao.
LEAKY_FEATURES = ["Avg_class_frequency_current_month", "Month_to_end_contract"]

# Classificacao de cada variavel segundo o esquema da Aula 06 (slide 33).
# corr e preenchida em runtime; aqui ficam classe + justificativa.
FEATURE_DESIGN = {
    "gender": ("Aceitavel", "Atributo estavel do cliente, conhecido no cadastro."),
    "Near_Location": ("Aceitavel", "Conhecido no cadastro; nao depende do futuro."),
    "Partner": ("Aceitavel", "Vinculo com empresa parceira, conhecido no cadastro."),
    "Promo_friends": ("Aceitavel", "Adesao a promocao, conhecida no cadastro."),
    "Phone": ("Aceitavel", "Dado de contato, conhecido no cadastro."),
    "Contract_period": ("Aceitavel", "Duracao contratada, conhecida na assinatura."),
    "Group_visits": ("Aceitavel", "Habito de aulas em grupo, observavel cedo."),
    "Age": ("Aceitavel", "Atributo estavel do cliente."),
    "Avg_additional_charges_total": (
        "Aceitavel",
        "Gasto extra acumulado; disponivel progressivamente, usavel com cautela.",
    ),
    "Lifetime": ("Aceitavel", "Tempo de casa; cresce de forma previsivel e antecipada."),
    "Avg_class_frequency_total": (
        "Aceitavel",
        "Frequencia historica media; sinal de engajamento usavel com cautela.",
    ),
    "Avg_class_frequency_current_month": (
        "Proxy tardio",
        "Frequencia DO mes corrente: quem ja esta saindo parou de ir. "
        "Altamente correlacionada, mas so se materializa junto com o churn - "
        "tarde demais para intervir.",
    ),
    "Month_to_end_contract": (
        "Proxy tardio",
        "Meses ate o fim do contrato: mecanicamente ligado ao momento de nao "
        "renovar. Co-temporal ao evento, indisponivel para intervencao antecipada.",
    ),
}


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset carregado: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(f"Taxa de churn: {df[TARGET].mean():.2%}")
    return df


def build_candidates() -> dict[str, Pipeline]:
    """3 classificadores num Pipeline com scaler embutido (consistencia treino/inferencia)."""
    return {
        "LogisticRegression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",  # trata desbalanceamento
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "RandomForest": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=8,  # limita complexidade -> controla overfit
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "GradientBoosting": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "clf",
                    GradientBoostingClassifier(
                        n_estimators=200,
                        max_depth=3,  # arvores rasas -> menor overfit
                        learning_rate=0.08,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def evaluate(model: Pipeline, X_train, y_train, X_test, y_test) -> dict:
    """Metricas no teste + AUC no treino + gap (overfit) + AUC de validacao cruzada."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    y_proba_train = model.predict_proba(X_train)[:, 1]

    auc_test = roc_auc_score(y_test, y_proba)
    auc_train = roc_auc_score(y_train, y_proba_train)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_auc = cross_val_score(model, X_train, y_train, cv=skf, scoring="roc_auc")

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(auc_test),
        "auc_train": float(auc_train),
        "overfit_gap": float(auc_train - auc_test),
        "cv_auc_mean": float(cv_auc.mean()),
        "cv_auc_std": float(cv_auc.std()),
        "cm": confusion_matrix(y_test, y_pred).tolist(),
    }


def feature_importance(model: Pipeline, features: list[str]) -> list[dict]:
    clf = model.named_steps["clf"]
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
    elif hasattr(clf, "coef_"):
        importances = np.abs(clf.coef_[0])
    else:
        return []
    ranking = sorted(
        [{"feature": f, "importance": float(i)} for f, i in zip(features, importances)],
        key=lambda x: x["importance"],
        reverse=True,
    )
    return ranking


def train_scenario(df: pd.DataFrame, features: list[str], label: str) -> dict:
    """Treina e compara os 3 modelos para um conjunto de features."""
    X = df[features]
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    results: dict[str, dict] = {}
    trained: dict[str, Pipeline] = {}
    print(f"\n{'='*64}\nCENARIO: {label}  ({len(features)} features)\n{'='*64}")
    for name, pipe in build_candidates().items():
        pipe.fit(X_train, y_train)
        m = evaluate(pipe, X_train, y_train, X_test, y_test)
        results[name] = m
        trained[name] = pipe
        print(
            f"  {name:<20} AUC_test={m['roc_auc']:.4f} | AUC_train={m['auc_train']:.4f} "
            f"| gap={m['overfit_gap']:+.4f} | CV_AUC={m['cv_auc_mean']:.4f}"
            f"+-{m['cv_auc_std']:.4f} | recall={m['recall']:.3f} | F1={m['f1']:.3f}"
        )

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    print(f"  >>> melhor por ROC-AUC: {best_name}")

    return {
        "features": features,
        "results": results,
        "trained": trained,
        "best_name": best_name,
        "split": (X_train, X_test, y_train, y_test),
    }


def _tune(pipe: Pipeline, grid: dict, X_train, y_train) -> GridSearchCV:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=skf, n_jobs=-1)
    search.fit(X_train, y_train)
    return search


def fine_tune_and_select(X_train, y_train, X_test, y_test) -> dict:
    """Fine tuning de hiperparametros (Aula 07, slide 11) de DOIS candidatos
    (Gradient Boosting e Regressao Logistica) e selecao do melhor por ROC-AUC no
    teste. Para churn priorizamos um modelo com bom recall e baixo overfit; a
    selecao por AUC e desempatada na pratica pelo recall/gap reportados."""

    # --- Gradient Boosting (arvore: nao linear, explicavel via SHAP TreeExplainer)
    gb = Pipeline(
        steps=[("scaler", StandardScaler()), ("clf", GradientBoostingClassifier(random_state=RANDOM_STATE))]
    )
    gb_search = _tune(
        gb,
        {
            "clf__n_estimators": [150, 200, 300],
            "clf__max_depth": [2, 3],
            "clf__learning_rate": [0.05, 0.08, 0.1],
        },
        X_train,
        y_train,
    )

    # --- Regressao Logistica (linear: baseline interpretavel, SHAP LinearExplainer)
    lr = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]
    )
    lr_search = _tune(
        lr,
        {"clf__C": [0.05, 0.1, 0.5, 1.0, 2.0], "clf__penalty": ["l2"]},
        X_train,
        y_train,
    )

    candidates = {
        "GradientBoosting (tunado)": ("tree", gb_search),
        "LogisticRegression (tunada)": ("linear", lr_search),
    }
    metrics = {}
    for name, (_kind, search) in candidates.items():
        metrics[name] = evaluate(search.best_estimator_, X_train, y_train, X_test, y_test)
        params = {k.replace("clf__", ""): v for k, v in search.best_params_.items()}
        print(f"\nFine tuning {name}: {params}")
        print(
            f"  AUC_test={metrics[name]['roc_auc']:.4f} | gap={metrics[name]['overfit_gap']:+.4f} "
            f"| recall={metrics[name]['recall']:.3f} | F1={metrics[name]['f1']:.3f}"
        )

    served_name = max(metrics, key=lambda n: metrics[n]["roc_auc"])
    served_kind = candidates[served_name][0]
    served_model = candidates[served_name][1].best_estimator_
    served_params = {
        k.replace("clf__", ""): v for k, v in candidates[served_name][1].best_params_.items()
    }
    print(f"\n>>> Modelo servido escolhido: {served_name} ({served_kind})")

    return {
        "served_name": served_name,
        "served_kind": served_kind,
        "served_model": served_model,
        "served_params": served_params,
        "tuned_metrics": metrics,
    }


def main() -> None:
    df = load_data()
    all_features = [c for c in df.columns if c != TARGET]
    clean_features = [c for c in all_features if c not in LEAKY_FEATURES]

    # --- Dois cenarios: com vs sem vazamento ---
    sc_full = train_scenario(df, all_features, "COM vazamento (13 features)")
    sc_clean = train_scenario(df, clean_features, "SEM vazamento (11 features)")

    # --- Fine tuning + selecao do modelo servido (cenario limpo) ---
    X_train_c, X_test_c, y_train_c, y_test_c = sc_clean["split"]
    tune = fine_tune_and_select(X_train_c, y_train_c, X_test_c, y_test_c)
    served_name = tune["served_name"]
    served_kind = tune["served_kind"]
    served_model = tune["served_model"]
    best_params = tune["served_params"]
    served_metrics = tune["tuned_metrics"][served_name]

    # Inclui os candidatos tunados na tabela de metricas reportada
    sc_clean["results"].update(tune["tuned_metrics"])

    # --- Probabilidades no teste (para a secao de Thresholds recalcular ao vivo) ---
    test_proba = served_model.predict_proba(X_test_c)[:, 1]

    # --- Tabela de classificacao de features (Aula 06, slide 33) ---
    corr = df.corr(numeric_only=True)[TARGET].drop(TARGET)
    leakage_table = []
    for feat in all_features:
        classe, justificativa = FEATURE_DESIGN.get(feat, ("Aceitavel", ""))
        leakage_table.append(
            {
                "feature": feat,
                "corr_churn": float(corr.get(feat, np.nan)),
                "classe": classe,
                "justificativa": justificativa,
                "usada_no_modelo_servido": feat in clean_features,
            }
        )

    feature_ranges = {
        col: {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
        }
        for col in clean_features
    }

    importance = feature_importance(served_model, clean_features)
    print("\nTop 5 features (modelo servido):")
    for r in importance[:5]:
        print(f"  {r['feature']:<40} {r['importance']:.4f}")

    # Comparacao compacta com vs sem vazamento (melhor modelo de cada cenario)
    comparison = {
        "com_vazamento": {
            "features": all_features,
            "modelos": sc_full["results"],
            "melhor": sc_full["best_name"],
        },
        "sem_vazamento": {
            "features": clean_features,
            "modelos": sc_clean["results"],
            "melhor": served_name,
        },
        "delta_auc_vazamento": float(
            sc_full["results"][sc_full["best_name"]]["roc_auc"] - served_metrics["roc_auc"]
        ),
    }

    # Amostra de background para o SHAP (modelos lineares precisam de referencia)
    bg_n = min(200, len(X_train_c))
    background_sample = X_train_c.sample(n=bg_n, random_state=RANDOM_STATE)

    # --- Artefato servido (SEM vazamento) ---
    artifact = {
        "model": served_model,
        "model_kind": served_kind,  # "tree" ou "linear" -> escolhe o explainer SHAP
        "features": clean_features,
        "best_model_name": served_name,
        "best_params": best_params,
        "metrics": sc_clean["results"],
        "served_metrics": served_metrics,
        "importance": importance,
        "feature_ranges": feature_ranges,
        "churn_rate": float(df[TARGET].mean()),
        "test_y": y_test_c.tolist(),
        "test_proba": [float(p) for p in test_proba],
        "background_sample": background_sample.reset_index(drop=True),
        "leakage_table": leakage_table,
        "leaky_features": LEAKY_FEATURES,
        "comparison": comparison,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"\nModelo SERVIDO (sem vazamento) salvo em: {MODEL_PATH}")

    # --- Artefato COM vazamento (apenas para comparacao didatica) ---
    full_best = sc_full["trained"][sc_full["best_name"]]
    joblib.dump(
        {
            "model": full_best,
            "features": all_features,
            "best_model_name": sc_full["best_name"],
            "metrics": sc_full["results"],
            "churn_rate": float(df[TARGET].mean()),
        },
        MODEL_FULL_PATH,
    )
    print(f"Modelo COM vazamento salvo em: {MODEL_FULL_PATH}")

    # --- Metricas em JSON (comparacao completa) ---
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "served_model": f"{served_name} (sem vazamento)",
                "model_kind": served_kind,
                "best_params": best_params,
                "served_metrics": served_metrics,
                "comparison": comparison,
                "leakage_table": leakage_table,
                "importance": importance,
                "feature_ranges": feature_ranges,
                "churn_rate": float(df[TARGET].mean()),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Metricas salvas em: {METRICS_PATH}")


if __name__ == "__main__":
    main()
