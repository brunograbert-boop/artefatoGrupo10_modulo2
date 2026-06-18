import { Section } from '../components/Section';
import type { AnalysisData } from '../types';

export function Sumario({ data }: { data: AnalysisData }) {
  const churnGlobalPct = (data.eda.churn_global * 100).toFixed(1);
  const earlyDropout = data.clusters[3];
  const bestModel = data.models.best_model;
  const bestAuc = data.models.results[0].roc_auc;

  return (
    <Section
      id="sumario"
      track="all"
      title="Sumário Executivo"
      subtitle="Customer Segmentation Report + Análise Exploratória · Vitaliza"
    >
      <p className="text-base leading-relaxed mb-6">
        A Vitaliza opera com churn mensal de <strong>10,2%</strong>, contra meta contratada de 6,0% — descompasso que já levou o LTV/CAC para <strong>2,02</strong>, abaixo do piso de 3,0 exigido pelo term sheet da Série B. Em 19 dias, a VP Camila Ferraz precisa levar ao Conselho uma recomendação defensável sobre <strong>onde investir os R$ 600 mil aprovados em retenção</strong>.
      </p>

      {/* Números-chave */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Amostra</div>
          <div className="text-2xl font-bold text-inteli-navy">{data.meta.n_total.toLocaleString('pt-BR')}</div>
          <div className="text-xs text-inteli-gray-muted mt-1">assinantes analisados</div>
        </div>
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Churn observado</div>
          <div className="text-2xl font-bold text-inteli-red">{churnGlobalPct}%</div>
          <div className="text-xs text-inteli-gray-muted mt-1">6 meses</div>
        </div>
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Segmentos</div>
          <div className="text-2xl font-bold text-inteli-navy">{data.clusters.length}</div>
          <div className="text-xs text-inteli-gray-muted mt-1">clusters via KMeans</div>
        </div>
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Modelo líder</div>
          <div className="text-2xl font-bold text-inteli-navy">{bestAuc.toFixed(3)}</div>
          <div className="text-xs text-inteli-gray-muted mt-1">AUC · {bestModel}</div>
        </div>
      </div>

      {/* Três achados */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Três achados centrais</h3>
      <div className="space-y-3">
        <div className="flex gap-4 p-4 bg-red-50 border-l-4 border-inteli-red rounded">
          <div className="text-2xl">1</div>
          <div>
            <strong>{earlyDropout.name} (Early Dropout)</strong> concentra {(earlyDropout.share * 100).toFixed(0)}% da base mas responde por mais de 75% dos cancelamentos previstos. <strong>É o alvo de ROI mais agressivo.</strong>
          </div>
        </div>
        <div className="flex gap-4 p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
          <div className="text-2xl">2</div>
          <div>
            Clientes em contrato anual cancelam ~18x menos que mensais (2,4% vs 42,3%). <strong>Migrar engajados mensais para plano anual é a alavanca contratual mais óbvia.</strong>
          </div>
        </div>
        <div className="flex gap-4 p-4 bg-blue-50 border-l-4 border-inteli-navy rounded">
          <div className="text-2xl">3</div>
          <div>
            O Caminho A (win-back reativo) é <strong>estruturalmente cego</strong> para o Early Dropout, que sai sem clicar em "Cancelar". A matriz Valor × Risco indica que o <strong>Caminho B (proativo) é não-opcional</strong> para esse quadrante.
          </div>
        </div>
      </div>
    </Section>
  );
}
