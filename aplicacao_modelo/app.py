"""
Pipeline de INFERENCIA + interface web - Preditor de Churn Vitaliza (Inteli M2).

Este e o "pipeline de inferencia" do Artefato 2 (Aula 07, slide 13): NAO treina
nada; carrega os artefatos serializados produzidos pelo pipeline de treinamento
(churn_model.joblib + segmentation_artifact.joblib) e serve predicoes.

Como executar:
    streamlit run app.py

Para um cliente novo, o app:
  1. valida os campos contra as faixas observadas no dataset (variaveis mapeadas);
  2. atribui o cluster/persona (KMeans serializado, sem features vazadoras);
  3. estima a probabilidade de churn (modelo serializado, sem vazamento);
  4. explica o porque com SHAP (contribuicao por variavel) + a escala de threshold;
  5. gera uma explicacao em linguagem natural fiel ao SHAP (Aula 08/09),
     com o "plugue" do OpenRouter pronto para producao.

Secoes:
  - Novo cliente   : formulario + predicao + cluster + SHAP + explicacao
  - Thresholds     : escala de risco e matriz de confusao recalculada ao vivo
  - Explicabilidade: importancia global (SHAP + modelo)
  - Validacao      : overfit, vazamento, desbalanceamento (Aula 06)
  - Lote (CSV)     : predicao em massa
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import streamlit as st

matplotlib.use("Agg")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "churn_model.joblib"
SEG_PATH = BASE_DIR / "segmentation_artifact.joblib"

# ---------------------------------------------------------------------------
# Metadados de UI
# ---------------------------------------------------------------------------
FEATURE_HELP = {
    "gender": "Genero (0 = feminino, 1 = masculino).",
    "Near_Location": "Mora/trabalha perto da academia (0 = nao, 1 = sim).",
    "Partner": "Cliente de empresa parceira (0 = nao, 1 = sim).",
    "Promo_friends": "Aderiu a promocao indique-um-amigo (0 = nao, 1 = sim).",
    "Phone": "Deixou telefone de contato (0 = nao, 1 = sim).",
    "Contract_period": "Duracao do contrato em meses (1, 3, 6 ou 12).",
    "Group_visits": "Participa de aulas em grupo (0 = nao, 1 = sim).",
    "Age": "Idade do cliente (anos).",
    "Avg_additional_charges_total": "Gasto medio extra (cafe, massagens, etc) em dolares.",
    "Lifetime": "Tempo (meses) desde a primeira visita.",
    "Avg_class_frequency_total": "Frequencia media de aulas/semana desde o inicio.",
}
FEATURE_LABEL = {
    "gender": "Genero",
    "Near_Location": "Mora perto",
    "Partner": "Empresa parceira",
    "Promo_friends": "Promo indique-amigo",
    "Phone": "Telefone informado",
    "Contract_period": "Duracao do contrato (meses)",
    "Group_visits": "Aulas em grupo",
    "Age": "Idade",
    "Avg_additional_charges_total": "Gasto extra medio (US$)",
    "Lifetime": "Tempo de casa (meses)",
    "Avg_class_frequency_total": "Frequencia historica (aulas/sem)",
}
BINARY_FEATURES = {"gender", "Near_Location", "Partner", "Promo_friends", "Phone", "Group_visits"}

# Escala de threshold (faixas de risco). O threshold operacional (tau) e a linha
# de decisao churn/permanece; estas faixas dao a leitura qualitativa do score.
RISK_BANDS = [
    (0.00, 0.30, "BAIXO", "#2a9d8f"),
    (0.30, 0.50, "MEDIO", "#e9c46a"),
    (0.50, 0.70, "ALTO", "#f4a261"),
    (0.70, 1.01, "CRITICO", "#d7263d"),
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-4o-mini"


# ---------------------------------------------------------------------------
# Carregamento dos artefatos serializados (cache)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_model_artifact() -> dict:
    if not MODEL_PATH.exists():
        st.error(f"Artefato {MODEL_PATH.name} nao encontrado. Rode: python train_churn_model.py")
        st.stop()
    return joblib.load(MODEL_PATH)


@st.cache_resource(show_spinner=False)
def load_seg_artifact() -> dict | None:
    if not SEG_PATH.exists():
        return None
    return joblib.load(SEG_PATH)


@st.cache_resource(show_spinner=False)
def get_explainer(_artifact: dict):
    """Cria o explainer SHAP adequado ao tipo de modelo servido."""
    pipe = _artifact["model"]
    scaler = pipe.named_steps["scaler"]
    clf = pipe.named_steps["clf"]
    features = _artifact["features"]
    bg = _artifact["background_sample"][features]
    bg_scaled = scaler.transform(bg)
    if _artifact.get("model_kind") == "tree":
        explainer = shap.TreeExplainer(clf)
    else:
        explainer = shap.LinearExplainer(clf, bg_scaled)
    return {"explainer": explainer, "scaler": scaler, "clf": clf, "features": features}


def shap_values_for(art: dict, X_raw: pd.DataFrame):
    """Retorna (sv_2d, base_value, X_scaled) para as linhas de X_raw."""
    ex = get_explainer(art)
    Xs = ex["scaler"].transform(X_raw[ex["features"]])
    sv = ex["explainer"].shap_values(Xs)
    sv = np.array(sv)
    if sv.ndim == 3:  # alguns explainers devolvem (n, features, classes)
        sv = sv[..., 1]
    base = float(np.ravel(ex["explainer"].expected_value)[0])
    return sv, base, Xs


# ---------------------------------------------------------------------------
# Regras de negocio
# ---------------------------------------------------------------------------
def risk_band(prob: float) -> tuple[str, str]:
    for lo, hi, label, color in RISK_BANDS:
        if lo <= prob < hi:
            return label, color
    return "CRITICO", "#d7263d"


def assign_cluster(seg: dict, X_raw: pd.DataFrame) -> dict | None:
    if seg is None:
        return None
    cols = seg["feature_cols"]
    Xs = seg["scaler"].transform(X_raw[cols])
    raw = int(seg["kmeans"].predict(Xs)[0])
    final = seg["cluster_remap"][raw]
    nome = seg["names"][final]["nome"]
    desc = seg["names"][final]["descricao"]
    profile = next((p for p in seg["profiles"] if p["cluster"] == final), {})
    acao = next(
        (p["acao_recomendada"] for p in seg.get("priority", []) if p["cluster"] == final), ""
    )
    return {
        "cluster": final,
        "nome": nome,
        "descricao": desc,
        "churn_segmento": float(profile.get("churn_rate", 0.0)),
        "acao": acao,
    }


def recommend(prob: float, cluster_info: dict | None) -> str:
    if cluster_info and cluster_info.get("acao"):
        base = f"**Segmento {cluster_info['nome']}** - acao do playbook: {cluster_info['acao']}"
    else:
        base = ""
    if prob >= 0.70:
        tip = "Risco CRITICO: intervencao imediata (Caminho B proativo + oferta no clique de cancelar)."
    elif prob >= 0.50:
        tip = "Risco ALTO: incluir em campanha de retencao ativa nas proximas 72h."
    elif prob >= 0.30:
        tip = "Risco MEDIO: monitorar e aplicar nudges de engajamento; reavaliar em 2 semanas."
    else:
        tip = "Risco BAIXO: low touch; foco em upsell, evitar intervencao desnecessaria."
    return (base + "  \n" + tip) if base else tip


def fmt_value(feat: str, val: float) -> str:
    if feat in BINARY_FEATURES:
        return "Sim" if round(val) == 1 else "Nao"
    if feat in {"Age", "Contract_period"}:
        return f"{int(round(val))}"
    return f"{val:.2f}"


# ---------------------------------------------------------------------------
# Explicacao em linguagem natural (fiel ao SHAP) + plugue OpenRouter
# ---------------------------------------------------------------------------
def top_contributions(features, sv_row, row_values, k=3):
    pairs = [
        {"feature": f, "valor": float(row_values[f]), "shap": float(s)}
        for f, s in zip(features, sv_row)
    ]
    ups = sorted([p for p in pairs if p["shap"] > 0], key=lambda p: p["shap"], reverse=True)[:k]
    downs = sorted([p for p in pairs if p["shap"] < 0], key=lambda p: p["shap"])[:k]
    return ups, downs


def natural_language_explanation(prob, band, tau, cluster_info, ups, downs) -> str:
    decisao = (
        "sinalizado para acao (classificado como provavel churn)"
        if prob >= tau
        else "nao sinalizado (classificado como provavel permanencia)"
    )
    seg_txt = f" Foi atribuido ao segmento **{cluster_info['nome']}**." if cluster_info else ""
    out = [
        f"Este cliente tem **{prob:.0%}** de probabilidade estimada de cancelamento, "
        f"o que o coloca na faixa de risco **{band}**. Com o threshold operacional em "
        f"**{tau:.0%}**, ele e {decisao}.{seg_txt}"
    ]
    if ups:
        u = "; ".join(f"{FEATURE_LABEL.get(p['feature'], p['feature'])} = {fmt_value(p['feature'], p['valor'])}" for p in ups)
        out.append(f"Os fatores que mais **elevaram** o risco previsto foram: {u}.")
    if downs:
        d = "; ".join(f"{FEATURE_LABEL.get(p['feature'], p['feature'])} = {fmt_value(p['feature'], p['valor'])}" for p in downs)
        out.append(f"Os fatores que mais **reduziram** o risco foram: {d}.")
    out.append(
        "_Observacao: esta explicacao descreve o comportamento **aprendido pelo modelo** "
        "(valores SHAP), e nao uma relacao de causa e efeito do mundo real._"
    )
    return " ".join(out)


def build_llm_prompt(prob, band, tau, cluster_info, ups, downs) -> str:
    """Prompt estruturado conforme a Aula 09 (contexto, previsao, variaveis +
    direcao SHAP, publico-alvo, restricoes anti-causalidade)."""
    def linhas(ps, sinal):
        return "\n".join(
            f"  - {FEATURE_LABEL.get(p['feature'], p['feature'])} = "
            f"{fmt_value(p['feature'], p['valor'])} (SHAP {p['shap']:+.3f}, {sinal} o risco)"
            for p in ps
        )

    seg = cluster_info["nome"] if cluster_info else "nao definido"
    return (
        "CONTEXTO DE NEGOCIO: Vitaliza, app/rede de academias. Prevemos churn "
        "(cancelamento) de clientes para acionar retencao.\n"
        "TIPO DE PREVISAO: classificacao binaria (churn = 1 / permanece = 0).\n"
        f"CASO ESPECIFICO: probabilidade de churn = {prob:.1%} (faixa {band}); "
        f"threshold operacional = {tau:.0%}; segmento = {seg}.\n"
        "VARIAVEIS QUE AUMENTARAM O RISCO (SHAP > 0):\n" + (linhas(ups, "aumenta") or "  - (nenhuma relevante)") + "\n"
        "VARIAVEIS QUE REDUZIRAM O RISCO (SHAP < 0):\n" + (linhas(downs, "reduz") or "  - (nenhuma relevante)") + "\n"
        "PUBLICO-ALVO: equipe de Customer Success (negocio, nao tecnica).\n"
        "RESTRICOES: NAO afirme causalidade; NAO invente fatores ausentes; "
        "explique apenas o que os SHAP indicam; seja claro, objetivo e verificavel.\n"
        "TAREFA: escreva 1 paragrafo curto explicando o risco deste cliente e "
        "sugira 1 acao de retencao coerente com a faixa de risco."
    )


def call_openrouter(prompt: str, api_key: str) -> str:
    payload = json.dumps(
        {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "Voce traduz explicacoes tecnicas (SHAP) em linguagem de negocio, fiel aos numeros, sem inventar causalidade."},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def get_openrouter_key() -> str | None:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    try:
        return st.secrets["OPENROUTER_API_KEY"]  # type: ignore[index]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Threshold helpers
# ---------------------------------------------------------------------------
def confusion_at_threshold(y, proba, tau: float) -> dict:
    y = np.asarray(y)
    proba = np.asarray(proba)
    pred = (proba >= tau).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    acc = (tp + tn) / len(y) if len(y) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "recall": rec, "f1": f1, "accuracy": acc}


# ---------------------------------------------------------------------------
# Componentes de UI
# ---------------------------------------------------------------------------
def shap_bar(features, sv_row, row_values, base, prob):
    pairs = sorted(zip(features, sv_row), key=lambda t: abs(t[1]), reverse=True)
    labels = [f"{FEATURE_LABEL.get(f, f)} = {fmt_value(f, row_values[f])}" for f, _ in pairs]
    vals = [v for _, v in pairs]
    colors = ["#d7263d" if v > 0 else "#2a9d8f" for v in vals]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1])
    ax.axvline(0, color="#444", linewidth=0.8)
    ax.set_xlabel("Contribuicao SHAP (log-odds) -> direita aumenta churn, esquerda reduz")
    ax.set_title(f"Por que {prob:.0%}? Contribuicao de cada variavel (base={base:+.2f})")
    fig.tight_layout()
    return fig


def sidebar(art: dict, tau: float) -> None:
    st.sidebar.header("Modelo servido")
    st.sidebar.write(f"**{art['best_model_name']}** (sem vazamento)")
    sm = art["served_metrics"]
    st.sidebar.metric("ROC-AUC (teste)", f"{sm['roc_auc']:.3f}")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Recall", f"{sm['recall']:.3f}")
    c2.metric("Precision", f"{sm['precision']:.3f}")
    c1.metric("F1", f"{sm['f1']:.3f}")
    c2.metric("Gap overfit", f"{sm['overfit_gap']:+.3f}")
    st.sidebar.caption(
        f"Churn base: {art['churn_rate']:.1%} | {len(art['features'])} features | "
        f"threshold operacional atual: {tau:.0%}"
    )


def section_novo(art: dict, seg: dict | None, tau: float) -> None:
    st.subheader("Novo cliente - predicao, segmento e explicacao")
    st.caption(
        "Preencha os dados do cliente. Os campos sao validados contra as faixas "
        "observadas no dataset (variaveis mapeadas). As 2 variaveis co-temporais ao "
        "churn (frequencia do mes corrente e meses ate o fim do contrato) NAO sao "
        "pedidas: foram removidas para evitar vazamento."
    )
    ranges = art["feature_ranges"]
    features = art["features"]

    with st.form("form_novo"):
        cols = st.columns(2)
        inputs: dict[str, float] = {}
        for i, feat in enumerate(features):
            col = cols[i % 2]
            info = ranges[feat]
            label = FEATURE_LABEL.get(feat, feat)
            help_txt = FEATURE_HELP.get(feat, "")
            if feat in BINARY_FEATURES:
                inputs[feat] = col.selectbox(label, [0, 1], index=int(round(info["median"])), help=help_txt)
            elif feat == "Contract_period":
                opts = [1, 3, 6, 12]
                dv = min(opts, key=lambda o: abs(o - info["median"]))
                inputs[feat] = col.selectbox(label, opts, index=opts.index(dv), help=help_txt)
            elif feat == "Age":
                inputs[feat] = col.number_input(
                    label, min_value=int(info["min"]), max_value=int(info["max"]),
                    value=int(round(info["median"])), step=1, help=help_txt,
                )
            elif feat == "Lifetime":
                inputs[feat] = col.number_input(
                    label, min_value=float(info["min"]), max_value=float(info["max"]),
                    value=float(info["median"]), step=1.0, help=help_txt,
                )
            else:
                inputs[feat] = col.number_input(
                    label, min_value=float(info["min"]), max_value=float(info["max"]),
                    value=float(info["median"]), step=0.1, format="%.2f", help=help_txt,
                )
        submitted = st.form_submit_button("Analisar cliente", type="primary")
        if submitted:
            st.session_state["novo_input"] = inputs

    if "novo_input" not in st.session_state:
        st.info("Preencha o formulario e clique em **Analisar cliente**.")
        return

    row = st.session_state["novo_input"]
    X = pd.DataFrame([row], columns=features)
    prob = float(art["model"].predict_proba(X)[0, 1])
    band, color = risk_band(prob)
    cinfo = assign_cluster(seg, X)

    m1, m2, m3 = st.columns(3)
    m1.metric("Probabilidade de churn", f"{prob:.1%}")
    m2.metric("Decisao (tau=%.0f%%)" % (tau * 100), "CHURN" if prob >= tau else "PERMANECE")
    m3.markdown(
        f"<div style='padding:14px;border-radius:8px;background:{color};color:white;"
        f"text-align:center;font-weight:bold;'>Risco {band}</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(max(prob, 0.0), 1.0))

    if cinfo:
        st.markdown(
            f"**Segmento:** {cinfo['nome']} &nbsp;|&nbsp; churn medio do segmento: "
            f"{cinfo['churn_segmento']:.0%}  \n_{cinfo['descricao']}_"
        )

    # SHAP local
    sv, base, _ = shap_values_for(art, X)
    sv_row = sv[0]
    ups, downs = top_contributions(features, sv_row, row, k=3)
    st.pyplot(shap_bar(features, sv_row, row, base, prob))

    # Explicacao em linguagem natural (fiel ao SHAP)
    st.markdown("#### Explicacao em linguagem natural")
    st.success(natural_language_explanation(prob, band, tau, cinfo, ups, downs))

    st.markdown("#### Recomendacao de retencao")
    st.info(recommend(prob, cinfo))

    # Plugue OpenRouter (Aula 09) - pronto, opcional
    with st.expander("Integracao com LLM (OpenRouter) - prompt e geracao opcional"):
        prompt = build_llm_prompt(prob, band, tau, cinfo, ups, downs)
        st.code(prompt, language="text")
        key = get_openrouter_key()
        if key:
            if st.button("Gerar explicacao com LLM (OpenRouter)"):
                try:
                    st.write(call_openrouter(prompt, key))
                except Exception as exc:
                    st.error(f"Falha na chamada ao OpenRouter: {exc}")
        else:
            st.caption(
                "Defina OPENROUTER_API_KEY (variavel de ambiente ou st.secrets) para "
                "habilitar a geracao ao vivo. Sem a chave, usamos a explicacao por "
                "template acima (fiel aos mesmos SHAP)."
            )

    with st.expander("Ver entrada enviada ao modelo"):
        st.dataframe(X, hide_index=True, width="stretch")


def section_thresholds(art: dict, tau: float) -> None:
    st.subheader("Escala de threshold e trade-off precision x recall")
    st.caption(
        "O modelo gera um score continuo (0-100%). O threshold operacional (tau) e o "
        "ponto de corte que decide churn x permanece. Use o slider na barra lateral "
        "para mover tau e ver a matriz de confusao recalculada no conjunto de teste."
    )
    y = art["test_y"]
    proba = art["test_proba"]

    # Faixas de risco (a "escala")
    st.markdown("**Escala de risco (faixas):**")
    cols = st.columns(len(RISK_BANDS))
    for col, (lo, hi, label, color) in zip(cols, RISK_BANDS):
        hi_show = min(hi, 1.0)
        col.markdown(
            f"<div style='padding:10px;border-radius:6px;background:{color};color:white;"
            f"text-align:center;'><b>{label}</b><br>{lo:.0%}-{hi_show:.0%}</div>",
            unsafe_allow_html=True,
        )

    # Curvas precision/recall/F1 por threshold
    grid = np.linspace(0.05, 0.95, 19)
    sweep = [confusion_at_threshold(y, proba, t) for t in grid]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(grid, [s["precision"] for s in sweep], label="Precision", color="#264653")
    ax.plot(grid, [s["recall"] for s in sweep], label="Recall", color="#e76f51")
    ax.plot(grid, [s["f1"] for s in sweep], label="F1", color="#2a9d8f")
    ax.axvline(tau, color="#888", linestyle="--", label=f"tau={tau:.2f}")
    ax.set_xlabel("Threshold (tau)")
    ax.set_ylabel("Metrica")
    ax.set_title("Precision, Recall e F1 em funcao do threshold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)

    f1_star = max(grid, key=lambda t: confusion_at_threshold(y, proba, t)["f1"])
    st.caption(
        f"Threshold de maior F1 no teste: **{f1_star:.2f}**. Para churn, custo de FN "
        "(perder quem ia cancelar) costuma ser maior que o de FP (intervir em quem "
        "ficaria) - o que justifica operar com tau menor para priorizar recall."
    )

    # Matriz de confusao no tau atual
    cm = confusion_at_threshold(y, proba, tau)
    st.markdown(f"**Matriz de confusao no teste (tau = {tau:.0%}):**")
    cm_df = pd.DataFrame(
        [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]],
        index=["Real: permanece", "Real: churn"],
        columns=["Previu permanece", "Previu churn"],
    )
    c1, c2 = st.columns([1.2, 1])
    c1.dataframe(cm_df, width="stretch")
    c2.metric("Recall", f"{cm['recall']:.3f}")
    c2.metric("Precision", f"{cm['precision']:.3f}")
    c2.metric("F1", f"{cm['f1']:.3f}")
    c2.metric("Accuracy", f"{cm['accuracy']:.3f}")


def section_explicabilidade(art: dict) -> None:
    st.subheader("Explicabilidade global do modelo")
    st.caption(
        "Importancia global = quanto cada variavel pesa, em media, nas predicoes. "
        "Complementa a explicacao local (SHAP por cliente) da aba 'Novo cliente'."
    )

    # SHAP global: media |SHAP| sobre a amostra de background
    bg = art["background_sample"][art["features"]]
    sv, _, _ = shap_values_for(art, bg)
    mean_abs = np.abs(sv).mean(axis=0)
    glob = pd.DataFrame(
        {"feature": [FEATURE_LABEL.get(f, f) for f in art["features"]], "shap_medio": mean_abs}
    ).sort_values("shap_medio")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(glob["feature"], glob["shap_medio"], color="#264653")
    ax.set_xlabel("Media |SHAP| (impacto medio na predicao)")
    ax.set_title("Importancia global por SHAP")
    fig.tight_layout()
    st.pyplot(fig)

    imp = art.get("importance") or []
    if imp:
        st.markdown("**Importancia segundo o proprio modelo (|coeficiente| / ganho):**")
        imp_df = pd.DataFrame(imp)
        imp_df["feature"] = imp_df["feature"].map(lambda f: FEATURE_LABEL.get(f, f))
        st.dataframe(imp_df, hide_index=True, width="stretch")


def section_validacao(art: dict) -> None:
    st.subheader("Validacao do modelo (Aula 06 + Aula 07)")

    sm = art["served_metrics"]
    st.markdown("##### 1. Sobreajuste (overfit)")
    c1, c2, c3 = st.columns(3)
    c1.metric("AUC treino", f"{sm['auc_train']:.3f}")
    c2.metric("AUC teste", f"{sm['roc_auc']:.3f}")
    c3.metric("Gap (treino-teste)", f"{sm['overfit_gap']:+.3f}")
    c1.metric("CV AUC (5 folds)", f"{sm['cv_auc_mean']:.3f}")
    c2.metric("Desvio CV", f"{sm['cv_auc_std']:.3f}")
    st.caption(
        "Regra pratica: gap > 0.10 indica overfit. Aqui o gap e proximo de zero e o "
        "AUC de validacao cruzada confirma a generalizacao."
    )

    st.markdown("##### 2. Vazamento de dados (com vs sem features vazadoras)")
    comp = art["comparison"]
    rows = []
    for cen_key, cen in [("COM vazamento", comp["com_vazamento"]), ("SEM vazamento (servido)", comp["sem_vazamento"])]:
        melhor = cen["melhor"]
        m = cen["modelos"][melhor]
        rows.append(
            {
                "Cenario": cen_key,
                "Melhor modelo": melhor,
                "ROC-AUC": round(m["roc_auc"], 4),
                "Recall": round(m["recall"], 4),
                "F1": round(m["f1"], 4),
                "Gap overfit": round(m["overfit_gap"], 4),
                "# features": len(cen["features"]),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption(
        f"Remover as 2 variaveis co-temporais custou ~{comp['delta_auc_vazamento']:.3f} de "
        "ROC-AUC, mas entrega um modelo honesto, que so usa informacao disponivel ANTES "
        "do churn - utilizavel para intervir a tempo."
    )

    st.markdown("##### 3. Classificacao das variaveis (vazamento / futuro / aceitavel)")
    lk = pd.DataFrame(art["leakage_table"])
    lk["corr_churn"] = lk["corr_churn"].round(3)
    lk = lk.rename(
        columns={
            "feature": "Variavel",
            "corr_churn": "Corr. c/ churn",
            "classe": "Classificacao",
            "justificativa": "Justificativa",
            "usada_no_modelo_servido": "Usada?",
        }
    )
    st.dataframe(lk, hide_index=True, width="stretch")

    st.markdown("##### 4. Desbalanceamento")
    st.caption(
        f"Base com {art['churn_rate']:.1%} de churn (desbalanceada ~73/27). Tratamento: "
        "class_weight='balanced' no modelo servido (penaliza erro na classe minoritaria) "
        "e foco em recall/F1/ROC-AUC em vez de acuracia (que premiaria prever 'todos ficam')."
    )

    st.markdown("##### 5. Comparativo completo (cenario sem vazamento)")
    st.dataframe(pd.DataFrame(art["metrics"]).T.round(4), width="stretch")


def section_batch(art: dict) -> None:
    st.subheader("Predicao em lote (CSV)")
    st.write(
        f"Suba um CSV contendo, no minimo, estas {len(art['features'])} colunas: "
        f"{', '.join(art['features'])}. A coluna Churn (se existir) e ignorada."
    )
    uploaded = st.file_uploader("Arquivo CSV", type=["csv"])
    if uploaded is None:
        return
    try:
        batch = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Falha ao ler CSV: {exc}")
        return
    missing = [c for c in art["features"] if c not in batch.columns]
    if missing:
        st.error(f"Colunas ausentes no CSV: {missing}")
        return
    X = batch[art["features"]]
    proba = art["model"].predict_proba(X)[:, 1]
    result = batch.copy()
    result["churn_probability"] = np.round(proba, 4)
    result["risk_band"] = [risk_band(p)[0] for p in proba]
    st.success(f"{len(result)} linhas processadas.")
    st.dataframe(result, width="stretch", hide_index=True)
    st.download_button(
        "Baixar predicoes",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="predicoes_churn.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="Preditor de Churn - Vitaliza", layout="wide")
    st.title("Preditor de Churn - Case Vitaliza")
    st.write(
        "Pipeline de inferencia servindo o modelo serializado (sem vazamento): "
        "predicao de churn, atribuicao de segmento e explicabilidade (SHAP) para um "
        "cliente novo, com escala de threshold e validacao do modelo."
    )

    art = load_model_artifact()
    seg = load_seg_artifact()

    tau = st.sidebar.slider("Threshold operacional (tau)", 0.05, 0.95, 0.50, 0.01)
    sidebar(art, tau)

    tabs = st.tabs(
        ["Novo cliente", "Thresholds", "Explicabilidade", "Validacao", "Lote (CSV)"]
    )
    with tabs[0]:
        section_novo(art, seg, tau)
    with tabs[1]:
        section_thresholds(art, tau)
    with tabs[2]:
        section_explicabilidade(art)
    with tabs[3]:
        section_validacao(art)
    with tabs[4]:
        section_batch(art)


if __name__ == "__main__":
    main()
