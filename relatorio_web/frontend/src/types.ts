// Tipos do analysis_data.json

export interface Meta {
  generated_at: string;
  dataset: string;
  ticket_medio_mensal: number;
  cac: number;
  churn_global: number;
  n_total: number;
}

export interface EDAData {
  churn_global: number;
  contract_breakdown: { contract: number; n: number; churn_rate: number }[];
  lifetime_breakdown: { bucket: string; n: number; churn_rate: number }[];
  freq_breakdown: { bucket: string; n: number; churn_rate: number }[];
  correlations: { feature: string; corr: number }[];
}

export interface Cluster {
  id: number;
  name: string;
  archetype: string;
  color: string;
  quadrant: string;
  action: string;
  channel: string;
  n: number;
  share: number;
  churn_rate: number;
  lift: number;
  contract: number;
  lifetime: number;
  freq_total: number;
  freq_current: number;
  age: number;
  extras: number;
  group_visits: number;
  promo_friends: number;
  partner: number;
  ltv_estimado: number;
  valor_agregado: number;
  prob_churn_modelo: number;
}

export interface ModelResult {
  modelo: string;
  familia: string;
  acuracia: number;
  precisao: number;
  recall: number;
  f1: number;
  roc_auc: number;
}

export interface MatrixPoint {
  id: number;
  persona: string;
  archetype: string;
  color: string;
  quadrant: string;
  x_risco: number;
  y_valor_agregado: number;
  n: number;
  share: number;
  churn_rate: number;
  ltv: number;
}

export interface AnalysisData {
  meta: Meta;
  eda: EDAData;
  clustering: {
    k_final: number;
    elbow_silhouette: { k: number; inertia: number; silhouette: number }[];
  };
  clusters: Cluster[];
  models: {
    results: ModelResult[];
    best_model: string;
    confusion_matrix: number[][];
    feature_importance: { feature: string; importance: number }[];
    tree_rules: string;
  };
  matrix: MatrixPoint[];
  validation: ValidationData;
}

export interface GlobalMetrics {
  acuracia: number;
  precisao: number;
  recall: number;
  f1: number;
  roc_auc: number;
  cm: number[][];
}

export interface PerPersonaMetric {
  cluster_id: number;
  n_test: number;
  churn_rate_test: number;
  recall_padrao: number;
  precision_padrao: number;
  recall_balanced: number;
  precision_balanced: number;
}

export interface ValidationData {
  plan: {
    leaky_features_removed: string[];
    features_used: string[];
    n_features: number;
    test_size_pct: number;
    random_state: number;
  };
  partitions: {
    persona_0_renata: { n: number; churn_rate: number };
    persona_1_elisa: { n: number; churn_rate: number };
    persona_2_rafael: { n: number; churn_rate: number };
    persona_3_julia: { n: number; churn_rate: number };
    test_holdout: { n: number; churn_rate: number };
  };
  cluster_overlap: {
    overlap_pct: number;
    confusion_matrix_orig_vs_new: number[][];
  };
  global_metrics: {
    gb_padrao: GlobalMetrics;
    gb_balanced: GlobalMetrics;
    gb_padrao_auc_train: number;
    gb_padrao_overfit_gap: number;
    gb_original_com_leakage_auc: number;
    gb_original_com_leakage_recall: number;
  };
  per_persona: PerPersonaMetric[];
}
