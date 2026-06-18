import { Section } from '../components/Section';
import type { AnalysisData } from '../types';
import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine, Cell,
} from 'recharts';

interface MatrixTooltipPayload {
  payload: {
    persona: string;
    archetype: string;
    quadrant: string;
    x_risco: number;
    y_valor_agregado: number;
    n: number;
    churn_rate: number;
    ltv: number;
  };
}

function MatrixTooltip({ active, payload }: { active?: boolean; payload?: MatrixTooltipPayload[] }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-inteli-gray-border rounded-lg shadow-card p-3 text-xs">
      <div className="font-bold text-inteli-navy text-sm mb-1">{d.persona}</div>
      <div className="text-inteli-gray-muted italic mb-2">{d.archetype}</div>
      <div className="space-y-1">
        <div className="flex justify-between gap-4"><span>Risco (P. churn):</span><strong>{(d.x_risco * 100).toFixed(1)}%</strong></div>
        <div className="flex justify-between gap-4"><span>Valor agregado:</span><strong>R$ {(d.y_valor_agregado / 1000).toFixed(0)}k</strong></div>
        <div className="flex justify-between gap-4"><span>Tamanho:</span><strong>{d.n.toLocaleString('pt-BR')}</strong></div>
        <div className="flex justify-between gap-4"><span>Churn observado:</span><strong>{(d.churn_rate * 100).toFixed(1)}%</strong></div>
        <div className="flex justify-between gap-4"><span>LTV individual:</span><strong>R$ {d.ltv.toFixed(0)}</strong></div>
        <div className="border-t pt-1 mt-1"><span className="text-inteli-red font-semibold">{d.quadrant}</span></div>
      </div>
    </div>
  );
}

export function Matriz({ data }: { data: AnalysisData }) {
  const points = data.matrix;

  // Limites dos eixos
  const maxX = 1.0;
  const maxY = Math.max(...points.map(p => p.y_valor_agregado)) * 1.15;
  const midX = 0.5;
  const midY = maxY / 2;

  return (
    <Section
      id="matriz"
      track="business"
      number="7."
      title="Matriz Valor x Risco"
      subtitle="Onde investir, onde monitorar, onde manter — o framework de decisão executiva"
    >
      <p className="mb-6 leading-relaxed">
        A matriz Valor x Risco cruza <strong>dois eixos quantificaveis</strong> que orientam a decisão de alocação de orçamento. <strong>Eixo Y (Valor):</strong> valor agregado do cluster — LTV individual estimado (ticket mensal de R$ 39,90 projetado pelo lifetime esperado, mais receita acessoria) multiplicado pelo tamanho do cluster. <strong>Eixo X (Risco):</strong> probabilidade média de churn calculada pelo Gradient Boosting (secao 6). O tamanho de cada bolha representa o número de clientes no cluster.
      </p>

      {/* Matriz interativa */}
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6 relative">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 30, right: 30, bottom: 50, left: 70 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              type="number"
              dataKey="x_risco"
              domain={[0, maxX]}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              tick={{ fontSize: 12 }}
              label={{ value: 'Risco · Probabilidade média de churn', position: 'insideBottom', offset: -15, fontSize: 12, fill: '#1B1F3B' }}
            />
            <YAxis
              type="number"
              dataKey="y_valor_agregado"
              domain={[0, maxY]}
              tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
              label={{ value: 'Valor agregado do cluster (R$)', angle: -90, position: 'insideLeft', offset: 0, fontSize: 12, fill: '#1B1F3B' }}
            />
            <ZAxis type="number" dataKey="n" range={[500, 4000]} />

            {/* Linhas dos quadrantes */}
            <ReferenceLine x={midX} stroke="#9CA3AF" strokeDasharray="6 6" />
            <ReferenceLine y={midY} stroke="#9CA3AF" strokeDasharray="6 6" />

            <Tooltip content={<MatrixTooltip />} />

            <Scatter data={points} fill="#1B1F3B">
              {points.map((p, i) => (
                <Cell key={i} fill={p.color} fillOpacity={0.75} stroke={p.color} strokeWidth={2} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>

        {/* Labels dos quadrantes */}
        <div className="absolute top-8 left-24 text-[11px] font-bold text-inteli-gray-muted uppercase tracking-wider opacity-60">True Friends</div>
        <div className="absolute top-8 right-12 text-[11px] font-bold text-inteli-gray-muted uppercase tracking-wider opacity-60">Barnacles</div>
        <div className="absolute bottom-16 left-24 text-[11px] font-bold text-inteli-gray-muted uppercase tracking-wider opacity-60">Butterflies</div>
        <div className="absolute bottom-16 right-12 text-[11px] font-bold text-inteli-gray-muted uppercase tracking-wider opacity-60">Strangers</div>

        {/* Labels das personas */}
        {points.map((p) => (
          <div
            key={p.id}
            className="absolute text-xs font-bold pointer-events-none"
            style={{
              color: p.color,
              left: `${10 + (p.x_risco / maxX) * 80}%`,
              top: `${85 - (p.y_valor_agregado / maxY) * 75}%`,
              transform: 'translate(-50%, -150%)',
            }}
          >
            {p.persona}
          </div>
        ))}
      </div>

      {/* Legenda dos quadrantes */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Os 4 quadrantes (Reinartz & Kumar, HBR 2002)</h3>
      <div className="grid md:grid-cols-2 gap-3 mb-6">
        <div className="bg-green-50 border-l-4 border-green-600 rounded-r p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="font-bold text-green-900">True Friends</span>
            <span className="text-xs text-inteli-gray-muted">Alto Valor + Baixo Risco</span>
          </div>
          <p className="text-xs leading-relaxed">Clientes leais e rentáveis. <strong>Manter</strong>, evitar intervenção agressiva (risco sleeping dog). Focar em upsell e renovação.</p>
        </div>
        <div className="bg-blue-50 border-l-4 border-blue-600 rounded-r p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="font-bold text-blue-900">Butterflies</span>
            <span className="text-xs text-inteli-gray-muted">Alto Valor + Risco Médio</span>
          </div>
          <p className="text-xs leading-relaxed">Engajados sem amarra contratual. Lucrativos enquanto duram. <strong>Maximizar enquanto estão</strong> + tentar converter para contrato longo.</p>
        </div>
        <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-r p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="font-bold text-yellow-900">Barnacles</span>
            <span className="text-xs text-inteli-gray-muted">Baixo Valor + Alto Risco</span>
          </div>
          <p className="text-xs leading-relaxed">Pegajosos mas pouco rentáveis. <strong>Monitorar com cuidado</strong>. Cuidado: pode haver sleeping dogs aqui.</p>
        </div>
        <div className="bg-red-50 border-l-4 border-red-600 rounded-r p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="font-bold text-red-900">Strangers</span>
            <span className="text-xs text-inteli-gray-muted">Risco Altíssimo</span>
          </div>
          <p className="text-xs leading-relaxed">Provavelmente vão sair, baixo valor individual <strong>mas alto volume agregado</strong>. Intervenção proativa é a única chance.</p>
        </div>
      </div>

      {/* Leitura executiva */}
      <div className="bg-inteli-navy text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-2">Leitura executiva</div>
        <p className="text-sm leading-relaxed mb-3">
          A persona <strong>Julia (Early Dropout)</strong> ocupa o quadrante de maior urgência: risco próximo a 100% e o maior valor agregado da base (massa de 1.470 clientes). É o quadrante onde <strong>Caminho A não funciona</strong> — Julia some sem clicar em "Cancelar". Apenas o Caminho B (proativo) consegue chegar nela antes da saída.
        </p>
        <p className="text-sm leading-relaxed">
          A persona <strong>Renata (Leais)</strong> ocupa o oposto: alto valor, baixíssimo risco. A recomendação aqui é <em>não mexer</em> — qualquer intervenção corre risco de acordar sleeping dogs. Foco único: oferta de renovação 60 dias antes do vencimento anual.
        </p>
      </div>
    </Section>
  );
}
