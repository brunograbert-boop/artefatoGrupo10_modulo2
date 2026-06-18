import { Section } from '../components/Section';
import type { AnalysisData } from '../types';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine,
} from 'recharts';

export function Segmentacao({ data }: { data: AnalysisData }) {
  const elbow = data.clustering.elbow_silhouette;
  const kFinal = data.clustering.k_final;

  return (
    <Section
      id="segmentacao"
      track="tech"
      number="4."
      title="Segmentação via KMeans"
      subtitle="Quatro segmentos comportamentais com perfis distintos de risco"
    >
      <p className="mb-6 leading-relaxed">
        Aplicamos KMeans nas 13 features comportamentais e demográficas, depois de padronizar (StandardScaler) — KMeans usa distância euclidiana e é sensível à escala. Dois critérios para escolher quantos clusters fazem sentido:
      </p>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white border border-inteli-gray-border rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-2">Método do cotovelo (Inertia)</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={elbow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="k" tick={{ fontSize: 11 }} label={{ value: 'k', position: 'insideBottom', offset: -5, fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => Number(v).toFixed(0)} />
              <Line type="monotone" dataKey="inertia" stroke="#3498DB" strokeWidth={2} dot={{ r: 5, fill: '#3498DB' }} />
              <ReferenceLine x={kFinal} stroke="#E63946" strokeDasharray="4 4" label={{ value: `k=${kFinal}`, position: 'top', fontSize: 11, fill: '#E63946' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white border border-inteli-gray-border rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-2">Silhouette score</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={elbow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="k" tick={{ fontSize: 11 }} />
              <YAxis
                tick={{ fontSize: 11 }}
                domain={['dataMin - 0.01', 'dataMax + 0.01']}
                tickFormatter={(v) => Number(v).toFixed(3)}
                width={50}
              />
              <Tooltip formatter={(v) => Number(v).toFixed(4)} />
              <Line type="monotone" dataKey="silhouette" stroke="#27AE60" strokeWidth={2} dot={{ r: 5, fill: '#27AE60' }} />
              <ReferenceLine x={kFinal} stroke="#E63946" strokeDasharray="4 4" label={{ value: `k=${kFinal}`, position: 'top', fontSize: 11, fill: '#E63946' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-inteli-gray-bg rounded-lg p-4 mb-8">
        <div className="text-xs uppercase tracking-wider text-inteli-navy font-semibold mb-1">Escolha justificada: k = {kFinal}</div>
        <p className="text-sm leading-relaxed">
          A inércia tem queda acentuada até k=3-4 e desacelera. O silhouette score tem pico em k=2, mas com k=2 perdemos nuance executiva. <strong>k=4 dá uma matriz Valor × Risco com quadrantes legíveis</strong> (Early Dropout, Risco Médio, Engajados Mensais, Leais), preservando granularidade sem fragmentar a narrativa.
        </p>
      </div>

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Os 4 segmentos identificados</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {data.clusters.map(c => (
          <div key={c.id} className="bg-white border border-inteli-gray-border rounded-lg overflow-hidden shadow-card">
            <div className="px-4 py-2 text-white font-semibold text-sm" style={{ backgroundColor: c.color }}>
              C{c.id} · {c.name}
            </div>
            <div className="p-4">
              <div className="text-xs text-inteli-gray-muted uppercase tracking-wider mb-1">{c.archetype}</div>
              <div className="flex justify-between items-end mt-3 mb-3">
                <div>
                  <div className="text-2xl font-bold text-inteli-navy">{c.n.toLocaleString('pt-BR')}</div>
                  <div className="text-xs text-inteli-gray-muted">{(c.share * 100).toFixed(1)}% da base</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold" style={{ color: c.color }}>{(c.churn_rate * 100).toFixed(1)}%</div>
                  <div className="text-xs text-inteli-gray-muted">churn · lift {c.lift.toFixed(2)}x</div>
                </div>
              </div>
              <div className="text-xs space-y-1 pt-3 border-t border-inteli-gray-border">
                <div className="flex justify-between"><span className="text-inteli-gray-muted">Contrato:</span><span className="font-medium">{c.contract.toFixed(1)}m</span></div>
                <div className="flex justify-between"><span className="text-inteli-gray-muted">Lifetime:</span><span className="font-medium">{c.lifetime.toFixed(1)}m</span></div>
                <div className="flex justify-between"><span className="text-inteli-gray-muted">Freq atual:</span><span className="font-medium">{c.freq_current.toFixed(2)}/sem</span></div>
                <div className="flex justify-between"><span className="text-inteli-gray-muted">Extras:</span><span className="font-medium">R$ {c.extras.toFixed(0)}</span></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}
