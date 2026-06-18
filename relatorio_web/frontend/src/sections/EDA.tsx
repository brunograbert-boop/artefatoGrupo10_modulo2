import { Section } from '../components/Section';
import type { AnalysisData } from '../types';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  ReferenceLine, CartesianGrid,
} from 'recharts';

const FMT_PCT = (v: number) => `${(v * 100).toFixed(1)}%`;
const FMT_INT = (v: number) => v.toLocaleString('pt-BR');

function pctColor(rate: number, mean: number) {
  if (rate > mean * 1.5) return '#E74C3C';
  if (rate > mean) return '#F39C12';
  if (rate > mean / 2) return '#3498DB';
  return '#27AE60';
}

export function EDA({ data }: { data: AnalysisData }) {
  const churnMean = data.eda.churn_global;

  const contractData = data.eda.contract_breakdown.map(d => ({
    label: `${d.contract} ${d.contract === 1 ? 'mês' : 'meses'}`,
    rate_pct: d.churn_rate * 100,
    rate: d.churn_rate,
    n: d.n,
  }));

  const lifetimeData = data.eda.lifetime_breakdown.map(d => ({
    label: d.bucket,
    rate_pct: d.churn_rate * 100,
    rate: d.churn_rate,
    n: d.n,
  }));

  const freqData = data.eda.freq_breakdown.map(d => ({
    label: d.bucket,
    rate_pct: d.churn_rate * 100,
    rate: d.churn_rate,
    n: d.n,
  }));

  const corrData = [...data.eda.correlations].sort((a, b) => a.corr - b.corr);

  return (
    <Section
      id="eda"
      track="tech"
      number="3."
      title="Análise Exploratória"
      subtitle="O sinal não está uniformemente distribuído — concentra-se em contrato, lifetime e frequência"
    >
      {/* Distribuição do alvo */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">3.1 Distribuição do alvo</h3>
      <div className="bg-inteli-gray-bg rounded-lg p-5 mb-6 flex items-center gap-6">
        <div className="text-center">
          <div className="text-5xl font-bold text-inteli-red">{FMT_PCT(churnMean)}</div>
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mt-1">Churn global</div>
        </div>
        <div className="text-sm leading-relaxed text-inteli-gray-text">
          De <strong>{data.meta.n_total.toLocaleString('pt-BR')}</strong> assinantes na amostra,
          {' '}<strong>{Math.round(data.meta.n_total * churnMean).toLocaleString('pt-BR')}</strong> cancelaram nos últimos 6 meses.
          Esse é o nível global. Os clusters da seção 4 revelam que esse {FMT_PCT(churnMean)} é profundamente assimétrico.
        </div>
      </div>

      {/* Churn por contrato */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">3.2 Churn por duração do contrato</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        Contratos mensais cancelam ~18x mais que anuais. A alavanca contratual mais óbvia.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={contractData} margin={{ top: 20, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, _name, props) => {
                const n = (props as { payload?: { n?: number } })?.payload?.n ?? 0;
                return [`${Number(value).toFixed(1)}% (${FMT_INT(n)} clientes)`, 'Churn'];
              }}
              labelStyle={{ color: '#1B1F3B', fontWeight: 600 }}
            />
            <ReferenceLine
              y={churnMean * 100}
              stroke="#6B7280"
              strokeDasharray="4 4"
              label={{ value: `Média: ${FMT_PCT(churnMean)}`, position: 'top', fontSize: 10, fill: '#6B7280' }}
            />
            <Bar dataKey="rate_pct" radius={[4, 4, 0, 0]}>
              {contractData.map((d, i) => <Cell key={i} fill={pctColor(d.rate, churnMean)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Churn por lifetime */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">3.3 Churn por tempo de plataforma</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        Clientes com menos de 1 mês concentram o maior risco. Quem chega a 4+ meses, raramente sai.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={lifetimeData} margin={{ top: 20, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, _name, props) => {
                const n = (props as { payload?: { n?: number } })?.payload?.n ?? 0;
                return [`${Number(value).toFixed(1)}% (${FMT_INT(n)} clientes)`, 'Churn'];
              }}
            />
            <ReferenceLine y={churnMean * 100} stroke="#6B7280" strokeDasharray="4 4" />
            <Bar dataKey="rate_pct" radius={[4, 4, 0, 0]}>
              {lifetimeData.map((d, i) => <Cell key={i} fill={pctColor(d.rate, churnMean)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Churn por frequência */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">3.4 Churn por frequência no mês corrente</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        Frequência atual e <strong>momentum</strong>: quem usa hoje, não cancela amanha. Acima de 3,5 sessões/sem, churn e virtualmente zero.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={freqData} margin={{ top: 20, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, _name, props) => {
                const n = (props as { payload?: { n?: number } })?.payload?.n ?? 0;
                return [`${Number(value).toFixed(1)}% (${FMT_INT(n)} clientes)`, 'Churn'];
              }}
            />
            <ReferenceLine y={churnMean * 100} stroke="#6B7280" strokeDasharray="4 4" />
            <Bar dataKey="rate_pct" radius={[4, 4, 0, 0]}>
              {freqData.map((d, i) => <Cell key={i} fill={pctColor(d.rate, churnMean)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Correlações */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">3.5 Correlação das features com o churn</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        Negativas (verde) reduzem churn. Positivas (vermelho) aumentam.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={corrData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis type="number" domain={[-0.5, 0.5]} tickFormatter={(v) => v.toFixed(2)} tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="feature" tick={{ fontSize: 11 }} width={170} />
            <Tooltip formatter={(value) => Number(value).toFixed(3)} />
            <ReferenceLine x={0} stroke="#000" />
            <Bar dataKey="corr" radius={[0, 4, 4, 0]}>
              {corrData.map((d, i) => (
                <Cell key={i} fill={d.corr < 0 ? '#27AE60' : '#E74C3C'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Sintese */}
      <div className="bg-inteli-navy text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-2">Sintese da EDA</div>
        <p className="text-sm leading-relaxed">
          Três variáveis carregam a maior parte do sinal: <strong>Lifetime</strong>, <strong>Contract_period</strong> e <strong>Avg_class_frequency_current_month</strong>. Três sinais sociais (desafios em grupo, indicação de amigo, parceria corporativa) reduzem o churn pela metade quando presentes. Esses cinco vetores são a matéria-prima da segmentação da próxima seção.
        </p>
      </div>
    </Section>
  );
}
