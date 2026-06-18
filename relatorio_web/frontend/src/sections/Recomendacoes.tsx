import { Section } from '../components/Section';
import type { AnalysisData } from '../types';

const RECOMMENDATIONS: Record<number, {
  priority: 'CRÍTICA' | 'ALTA' | 'MÉDIA' | 'BAIXA';
  budget_share: string;
  caminho: 'A' | 'B' | 'AB' | 'nenhum';
  metric: string;
  detalhe: string;
}> = {
  0: {
    priority: 'BAIXA',
    budget_share: '5%',
    caminho: 'nenhum',
    metric: 'Taxa de renovação do contrato anual',
    detalhe: 'NÃO acionar intervenção ativa. Risco de acordar sleeping dogs (~3% do cluster). Única ação: monitorar Month_to_end_contract <= 2 e disparar email de renovação 60 dias antes. Eventualmente, programa de indicação de amigos (esses já indicam 57%).',
  },
  1: {
    priority: 'MÉDIA',
    budget_share: '20%',
    caminho: 'B',
    metric: 'Taxa de conversão para plano semestral/anual',
    detalhe: 'Foco em UPSELL contratual. Oferta de 1 mês grátis na migração para plano anual. Push notification contextual ("você treinou 12 vezes esse mês — economize com o plano anual"). NÃO oferecer desconto agressivo.',
  },
  2: {
    priority: 'MÉDIA',
    budget_share: '15%',
    caminho: 'B',
    metric: 'Reativação no mês corrente (volta a >1,5 sessões/sem)',
    detalhe: 'Monitoramento ativo + nudges leves. Programa novo (desafio em grupo, modalidade nova, conteúdo curado). NUNCA ofertar desconto — pode acelerar a saída em sleeping dogs parciais. Ação A/B para validar.',
  },
  3: {
    priority: 'CRÍTICA',
    budget_share: '60%',
    caminho: 'B',
    metric: 'Redução de churn nos primeiros 60 dias de vida do cliente',
    detalhe: 'INTERVENÇÃO PROATIVA nas primeiras 4 semanas. Caminho B obrigatório: ~33% deste cluster sai sem clicar em "Cancelar". Onboarding gamificado, desafio em grupo na primeira semana, mensagem personalizada no mês 1 se freq < 1,5/sem. ROI marginal mais alto do orçamento.',
  },
};

export function Recomendacoes({ data }: { data: AnalysisData }) {
  return (
    <Section
      id="recomendacoes"
      track="business"
      number="8."
      title="Recomendações Executivas"
      subtitle="O slide que vai para o Conselho de 14 de novembro"
    >
      <p className="mb-6 leading-relaxed">
        Recomendação por persona, com nível de prioridade, percentual sugerido do orçamento de R$ 600 mil, caminho do case (A/B/ambos/nenhum), e métrica de sucesso. <strong>60% do esforço vai para Júlia (Early Dropout)</strong> — onde estão 70% dos cancelamentos absolutos e onde só o Caminho B funciona.
      </p>

      <div className="space-y-4 mb-6">
        {data.clusters.map(cluster => {
          const rec = RECOMMENDATIONS[cluster.id];
          const priorityColor =
            rec.priority === 'CRÍTICA' ? 'bg-red-100 text-red-900 border-red-600' :
            rec.priority === 'ALTA' ? 'bg-orange-100 text-orange-900 border-orange-600' :
            rec.priority === 'MÉDIA' ? 'bg-yellow-100 text-yellow-900 border-yellow-600' :
            'bg-green-100 text-green-900 border-green-600';
          const caminhoText =
            rec.caminho === 'A' ? 'Caminho A (Win-back)' :
            rec.caminho === 'B' ? 'Caminho B (Proativo)' :
            rec.caminho === 'AB' ? 'Caminho A + B' : 'Nenhum (só monitoramento)';

          return (
            <div key={cluster.id} className="bg-white border border-inteli-gray-border rounded-lg shadow-card overflow-hidden">
              <div className="grid md:grid-cols-12 gap-0">
                {/* Coluna esquerda: persona */}
                <div className="md:col-span-3 p-5 text-white" style={{ backgroundColor: cluster.color }}>
                  <div className="text-xs uppercase tracking-widest opacity-80">Persona C{cluster.id}</div>
                  <div className="text-xl font-bold">{cluster.name}</div>
                  <div className="text-sm opacity-90 mt-1">{cluster.archetype}</div>
                  <div className="mt-3 text-xs opacity-80">
                    {cluster.n.toLocaleString('pt-BR')} clientes · {(cluster.share * 100).toFixed(1)}% da base
                  </div>
                </div>

                {/* Coluna direita: recomendação */}
                <div className="md:col-span-9 p-5">
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`text-xs font-bold px-3 py-1 rounded-full border ${priorityColor}`}>
                      PRIORIDADE {rec.priority}
                    </span>
                    <span className="text-xs font-medium px-3 py-1 rounded-full bg-inteli-navy text-white">
                      Orçamento sugerido · {rec.budget_share}
                    </span>
                    <span className="text-xs font-medium px-3 py-1 rounded-full bg-inteli-gray-bg text-inteli-gray-text border border-inteli-gray-border">
                      {caminhoText}
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-wider text-inteli-gray-muted font-semibold mb-1">Ação recomendada</div>
                      <p className="text-sm font-semibold text-inteli-navy mb-2">{cluster.action}</p>
                    </div>
                    <div>
                      <div className="text-xs uppercase tracking-wider text-inteli-gray-muted font-semibold mb-1">Canal sugerido</div>
                      <p className="text-sm">{cluster.channel}</p>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-inteli-gray-border">
                    <div className="text-xs uppercase tracking-wider text-inteli-gray-muted font-semibold mb-1">Detalhe operacional</div>
                    <p className="text-sm leading-relaxed text-inteli-gray-text">{rec.detalhe}</p>
                  </div>

                  <div className="mt-3 bg-inteli-gray-bg rounded p-2">
                    <span className="text-xs text-inteli-gray-muted">Métrica de sucesso: </span>
                    <span className="text-xs font-semibold text-inteli-navy">{rec.metric}</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Resumo da decisão */}
      <div className="bg-inteli-navy text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-2">Recomendação final ao Conselho</div>
        <p className="text-sm leading-relaxed mb-3">
          Aprovar a alocação dos R$ 600 mil priorizando <strong>Caminho B (proativo)</strong>, com foco no segmento Júlia (Early Dropout). O Caminho A — embora mais rápido de implementar — é estruturalmente cego para 70% do problema. A virada do Strava Premium confirma o piso competitivo do mercado em personalização preditiva.
        </p>
        <p className="text-sm leading-relaxed">
          Distribuição sugerida: <strong>60% Júlia (Caminho B onboarding)</strong> · 20% Elisa (Caminho B upsell) · 15% Rafael (Caminho B leve) · 5% Renata (monitoramento de renovação).
        </p>
      </div>
    </Section>
  );
}
