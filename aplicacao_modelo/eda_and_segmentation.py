"""
EDA + Segmentacao de Clientes - Case Vitaliza (Inteli Modulo 2).

Saidas:
    - charts/01_churn_rate.png
    - charts/02_churn_by_contract.png
    - charts/03_churn_by_lifetime.png
    - charts/04_churn_by_frequency.png
    - charts/05_correlation.png
    - charts/06_cluster_sizes.png
    - charts/07_cluster_churn_rates.png
    - charts/08_cluster_radar.png
    - segmentation_artifact.joblib (KMeans + scaler + features + meta)
    - segmentation_report.json (resumo numerico para os artefatos)
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "gym_churn_us.csv"
CHARTS_DIR = BASE_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)
SEG_ARTIFACT = BASE_DIR / "segmentation_artifact.joblib"
SEG_REPORT = BASE_DIR / "segmentation_report.json"

RANDOM_STATE = 42
N_CLUSTERS = 4
TARGET = "Churn"

# Mesmas features co-temporais removidas no modelo servido (ver train_churn_model.py).
# Clusterizamos SEM elas para que a persona atribuida a um cliente novo use
# exatamente os mesmos campos que o preditor de churn, sem vazamento.
LEAKY_FEATURES = ["Avg_class_frequency_current_month", "Month_to_end_contract"]

# Paleta consistente
PALETTE = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]
plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 120,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    print(f"Linhas: {len(df)} | colunas: {df.shape[1]} | churn base: {df[TARGET].mean():.2%}")
    return df


def chart_churn_rate(df: pd.DataFrame) -> None:
    churn = df[TARGET].value_counts(normalize=True).sort_index()
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    bars = ax.bar(["Permanece", "Cancela"], churn.values * 100, color=[PALETTE[1], PALETTE[4]])
    for b, v in zip(bars, churn.values * 100):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontweight="bold")
    ax.set_ylabel("% da base")
    ax.set_title("Distribuicao geral de churn (base 4.000 clientes)")
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "01_churn_rate.png")
    plt.close()


def chart_churn_by_contract(df: pd.DataFrame) -> None:
    grouped = df.groupby("Contract_period")[TARGET].agg(["mean", "count"]).reset_index()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(
        grouped["Contract_period"].astype(str) + " m",
        grouped["mean"] * 100,
        color=PALETTE[0],
    )
    for b, m, c in zip(bars, grouped["mean"] * 100, grouped["count"]):
        ax.text(
            b.get_x() + b.get_width() / 2,
            m + 1,
            f"{m:.1f}%\n(n={c})",
            ha="center",
            fontsize=8,
        )
    ax.set_ylabel("Taxa de churn (%)")
    ax.set_xlabel("Duracao do contrato")
    ax.set_title("Churn por periodo de contrato")
    ax.set_ylim(0, max(grouped["mean"] * 100) + 10)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "02_churn_by_contract.png")
    plt.close()


def chart_churn_by_lifetime(df: pd.DataFrame) -> None:
    bins = [-1, 1, 3, 6, 12, 100]
    labels = ["0-1m", "2-3m", "4-6m", "7-12m", "13m+"]
    df = df.copy()
    df["life_bin"] = pd.cut(df["Lifetime"], bins=bins, labels=labels)
    grouped = df.groupby("life_bin", observed=True)[TARGET].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(grouped.index.astype(str), grouped.values, color=PALETTE[2])
    for b, v in zip(bars, grouped.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_title("Churn por tempo desde a primeira visita (Lifetime)")
    ax.set_ylabel("Taxa de churn (%)")
    ax.set_xlabel("Faixa de lifetime")
    ax.set_ylim(0, max(grouped.values) + 10)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "03_churn_by_lifetime.png")
    plt.close()


def chart_churn_by_frequency(df: pd.DataFrame) -> None:
    bins = [-0.01, 0.5, 1.5, 2.5, 3.5, 10]
    labels = ["<0,5", "0,5-1,5", "1,5-2,5", "2,5-3,5", "3,5+"]
    df = df.copy()
    df["freq_bin"] = pd.cut(df["Avg_class_frequency_current_month"], bins=bins, labels=labels)
    grouped = df.groupby("freq_bin", observed=True)[TARGET].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(grouped.index.astype(str), grouped.values, color=PALETTE[3])
    for b, v in zip(bars, grouped.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_title("Churn por frequencia media de aulas no mes corrente")
    ax.set_ylabel("Taxa de churn (%)")
    ax.set_xlabel("Aulas/semana no mes atual")
    ax.set_ylim(0, max(grouped.values) + 10)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "04_churn_by_frequency.png")
    plt.close()


def chart_correlation(df: pd.DataFrame) -> None:
    corr = df.corr(numeric_only=True)[TARGET].drop(TARGET).sort_values()
    fig, ax = plt.subplots(figsize=(6.5, 5))
    colors = [PALETTE[1] if v < 0 else PALETTE[4] for v in corr.values]
    ax.barh(corr.index, corr.values, color=colors)
    for i, v in enumerate(corr.values):
        ax.text(v + (0.01 if v >= 0 else -0.01), i, f"{v:.2f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.axvline(0, color="#444", linewidth=0.8)
    ax.set_title("Correlacao das features com Churn")
    ax.set_xlabel("Correlacao de Pearson")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "05_correlation.png")
    plt.close()


def run_clustering(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    # Clusteriza apenas com features nao-vazadoras (alinhado ao modelo servido).
    feature_cols = [c for c in df.columns if c not in {TARGET, *LEAKY_FEATURES}]
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols])

    km = KMeans(n_clusters=N_CLUSTERS, n_init=20, random_state=RANDOM_STATE)
    cluster = km.fit_predict(X)
    df = df.copy()
    df["cluster"] = cluster

    # Ordenar clusters pelo churn rate (0 = menor risco, N-1 = maior risco)
    order = (
        df.groupby("cluster")[TARGET].mean().sort_values().index.tolist()
    )
    remap = {old: new for new, old in enumerate(order)}
    df["cluster"] = df["cluster"].map(remap)

    # Reordenar centroides correspondentemente
    centroids_scaled = km.cluster_centers_
    centroids_scaled = np.array([centroids_scaled[old] for old in order])
    centroids_original = scaler.inverse_transform(centroids_scaled)
    centroids_df = pd.DataFrame(centroids_original, columns=feature_cols)
    centroids_df.index.name = "cluster"

    artifact = {
        "kmeans": km,
        "scaler": scaler,
        "cluster_remap": remap,
        "feature_cols": feature_cols,
        "centroids_original": centroids_df,
    }
    return df, artifact


def cluster_profiles(df: pd.DataFrame) -> list[dict]:
    profiles = []
    feature_cols = [c for c in df.columns if c not in {TARGET, "cluster"}]
    base_churn = df[TARGET].mean()
    for c in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == c]
        prof = {
            "cluster": int(c),
            "size": int(len(sub)),
            "share": float(len(sub) / len(df)),
            "churn_rate": float(sub[TARGET].mean()),
            "lift_vs_base": float(sub[TARGET].mean() / base_churn),
            "means": {col: float(sub[col].mean()) for col in feature_cols},
        }
        profiles.append(prof)
    return profiles


def name_clusters(profiles: list[dict]) -> dict[int, dict]:
    """Nomeia os 4 segmentos por faixa de risco.

    Os clusters ja chegam ordenados por churn (0 = menor risco ... 3 = maior),
    entao o id do cluster e o proprio rank de risco. Cada nome combina a faixa de
    risco com um tracejado comportamental derivado das medias reais do segmento,
    garantindo 4 nomes distintos e data-driven (sem depender de features vazadoras)."""
    risk_labels = [
        "Leais - Baixo Risco",
        "Engajados - Risco Baixo a Medio",
        "Atencao - Risco Medio",
        "Criticos - Alto Risco",
    ]
    names: dict[int, dict] = {}
    base_life = float(np.mean([p["means"]["Lifetime"] for p in profiles]))
    base_contract = float(np.mean([p["means"]["Contract_period"] for p in profiles]))
    for p in profiles:
        c = int(p["cluster"])
        m = p["means"]
        rank = min(c, len(risk_labels) - 1)
        # Tracejado comportamental dominante do segmento
        tracos = []
        if m["Contract_period"] >= base_contract + 1:
            tracos.append("contratos mais longos")
        elif m["Contract_period"] <= max(1.0, base_contract - 1):
            tracos.append("contratos curtos/mensais")
        if m["Lifetime"] >= base_life + 1:
            tracos.append("tempo de casa maduro")
        elif m["Lifetime"] <= max(1.0, base_life - 1):
            tracos.append("entrada recente")
        if m.get("Avg_class_frequency_total", 0) >= 2.0:
            tracos.append("frequencia alta")
        elif m.get("Avg_class_frequency_total", 0) <= 1.5:
            tracos.append("frequencia baixa")
        traco_txt = ", ".join(tracos) if tracos else "perfil misto"
        names[c] = {
            "nome": risk_labels[rank],
            "descricao": (
                f"Churn de {p['churn_rate']:.0%} ({p['lift_vs_base']:.1f}x a base). "
                f"Perfil: {traco_txt}."
            ),
        }
    return names


def chart_cluster_sizes(profiles: list[dict], names: dict[int, dict]) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    labels = [f"C{p['cluster']} - {names[p['cluster']]['nome']}" for p in profiles]
    sizes = [p["size"] for p in profiles]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(profiles))]
    bars = ax.barh(labels, sizes, color=colors)
    for b, s in zip(bars, sizes):
        ax.text(b.get_width() + 30, b.get_y() + b.get_height() / 2,
                f"{s} ({s/4000:.0%})", va="center", fontsize=9)
    ax.set_xlabel("Numero de clientes")
    ax.set_title("Tamanho de cada segmento")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "06_cluster_sizes.png")
    plt.close()


def chart_cluster_churn(profiles: list[dict], names: dict[int, dict]) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    labels = [f"C{p['cluster']}\n{names[p['cluster']]['nome']}" for p in profiles]
    churn_rates = [p["churn_rate"] * 100 for p in profiles]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(profiles))]
    bars = ax.bar(labels, churn_rates, color=colors)
    for b, v in zip(bars, churn_rates):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%",
                ha="center", fontweight="bold")
    ax.axhline(26.5, color="#888", linestyle="--", linewidth=1)
    ax.text(len(churn_rates) - 0.5, 28, "Base global 26,5%", fontsize=8, color="#666")
    ax.set_ylabel("Taxa de churn no segmento (%)")
    ax.set_title("Taxa de churn por segmento")
    ax.set_ylim(0, max(churn_rates) + 12)
    plt.xticks(fontsize=8)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "07_cluster_churn_rates.png")
    plt.close()


def chart_cluster_radar(profiles: list[dict], names: dict[int, dict]) -> None:
    """Radar comparativo de 6 features chave (normalizadas 0-1) por cluster."""
    key_feats = [
        "Lifetime",
        "Contract_period",
        "Age",
        "Avg_class_frequency_current_month",
        "Avg_additional_charges_total",
        "Month_to_end_contract",
    ]
    # normalizar pelo max global de cada feature usando os centroides
    centroid_means = pd.DataFrame([p["means"] for p in profiles])[key_feats]
    norm = (centroid_means - centroid_means.min()) / (
        centroid_means.max() - centroid_means.min() + 1e-9
    )

    angles = np.linspace(0, 2 * np.pi, len(key_feats), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))
    for i, p in enumerate(profiles):
        values = norm.iloc[i].tolist() + [norm.iloc[i].tolist()[0]]
        ax.plot(angles, values, color=PALETTE[i % len(PALETTE)],
                label=f"C{p['cluster']} {names[p['cluster']]['nome']}")
        ax.fill(angles, values, color=PALETTE[i % len(PALETTE)], alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(key_feats, fontsize=8)
    ax.set_yticklabels([])
    ax.set_title("Perfil comparativo dos clusters (normalizado)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=8)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "08_cluster_radar.png", bbox_inches="tight")
    plt.close()


def prioritization(profiles: list[dict], names: dict[int, dict]) -> list[dict]:
    """Score = churn_rate * tamanho relativo, classifica acao."""
    out = []
    for p in profiles:
        score = p["churn_rate"] * p["share"]
        if p["churn_rate"] >= 0.45:
            acao = "Intervencao IMEDIATA - Caminho B (proativo) + Caminho A no clique"
        elif p["churn_rate"] >= 0.20:
            acao = "Monitoramento ativo + nudges - Caminho B leve"
        else:
            acao = "Manter engajamento - foco em upsell, sem intervencao agressiva"
        out.append(
            {
                "cluster": p["cluster"],
                "nome": names[p["cluster"]]["nome"],
                "share": p["share"],
                "churn_rate": p["churn_rate"],
                "score_prioridade": float(score),
                "acao_recomendada": acao,
            }
        )
    return sorted(out, key=lambda x: x["score_prioridade"], reverse=True)


def main() -> None:
    df = load()

    chart_churn_rate(df)
    chart_churn_by_contract(df)
    chart_churn_by_lifetime(df)
    chart_churn_by_frequency(df)
    chart_correlation(df)

    df_clustered, artifact = run_clustering(df)
    profiles = cluster_profiles(df_clustered)
    names = name_clusters(profiles)
    priority = prioritization(profiles, names)

    chart_cluster_sizes(profiles, names)
    chart_cluster_churn(profiles, names)
    chart_cluster_radar(profiles, names)

    # Salva artefato e relatorio
    joblib.dump(
        {
            "kmeans": artifact["kmeans"],
            "scaler": artifact["scaler"],
            "feature_cols": artifact["feature_cols"],
            "cluster_remap": artifact["cluster_remap"],
            "centroids_original": artifact["centroids_original"].to_dict(orient="index"),
            "names": names,
            "profiles": profiles,
            "priority": priority,
        },
        SEG_ARTIFACT,
    )

    # Estatisticas adicionais que vao para os artefatos
    extras = {
        "n_clientes": int(len(df)),
        "churn_global": float(df[TARGET].mean()),
        "churn_por_contrato": {
            int(k): float(v) for k, v in df.groupby("Contract_period")[TARGET].mean().items()
        },
        "churn_por_promo_friends": {
            int(k): float(v) for k, v in df.groupby("Promo_friends")[TARGET].mean().items()
        },
        "churn_por_group_visits": {
            int(k): float(v) for k, v in df.groupby("Group_visits")[TARGET].mean().items()
        },
        "churn_por_partner": {
            int(k): float(v) for k, v in df.groupby("Partner")[TARGET].mean().items()
        },
        "media_lifetime_churners": float(df.loc[df[TARGET] == 1, "Lifetime"].mean()),
        "media_lifetime_loyal": float(df.loc[df[TARGET] == 0, "Lifetime"].mean()),
        "media_freq_churners": float(df.loc[df[TARGET] == 1, "Avg_class_frequency_current_month"].mean()),
        "media_freq_loyal": float(df.loc[df[TARGET] == 0, "Avg_class_frequency_current_month"].mean()),
    }

    with open(SEG_REPORT, "w", encoding="utf-8") as f:
        json.dump(
            {
                "profiles": profiles,
                "names": {str(k): v for k, v in names.items()},
                "priority": priority,
                "extras": extras,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n=== RESUMO ===")
    for p in priority:
        print(
            f"C{p['cluster']} {p['nome']:<35} share={p['share']:.1%} "
            f"churn={p['churn_rate']:.1%} score={p['score_prioridade']:.3f}"
        )
    print(f"\nArtefato: {SEG_ARTIFACT}")
    print(f"Relatorio: {SEG_REPORT}")
    print(f"Charts: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
