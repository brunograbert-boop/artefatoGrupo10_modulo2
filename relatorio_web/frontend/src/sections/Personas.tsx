import { Section } from '../components/Section';
import type { AnalysisData, Cluster } from '../types';

const PERSONA_NARRATIVES: Record<number, { headline: string; profile: string; hipoteses: string[]; cs_quote: string }> = {
  0: {
    headline: 'Profissional jovem-adulta, contrato anual fechado, indicada por amigo, parceria corporativa. Alta retenção, alta receita acessória.',
    profile: 'Tem 30 anos, está na Vitaliza há quase 5 meses e fechou contrato anual (média 10,7 meses). Acessa o app cerca de 2 vezes por semana, gasta R$ 161 em extras (top entre os clusters), participa de desafios em grupo (53%), entrou indicada por amigo (57%) e na maioria das vezes via parceria corporativa (78%). É o cliente com o maior valor relativo da base.',
    hipoteses: [
      'Cancelamentos esporádicos por mudança de vida (cidade, emprego, fim do contrato corporativo). Eventos exógenos, difíceis de prever.',
      'Risco real está na renovação, não no churn mensal — monitorar Month_to_end_contract <= 2 e acionar renovação 60 dias antes.',
      'Risco "sleeping dog": intervir aqui pode acordar quem não estava pensando em sair.',
    ],
    cs_quote: 'A Renata a gente nem deveria estar olhando — ela paga, usa, indica amigos. Se eu ligar pra ela pra perguntar como está, eu corro o risco de dar ideia.',
  },
  1: {
    headline: 'Power user da plataforma — usa intensamente, mas optou por contrato mensal. Candidata ideal para upsell.',
    profile: 'Tem 30 anos, está na Vitaliza há mais de 4 meses e usa intensamente (2,70 sessões/semana — a maior frequência entre os clusters). Optou por contrato mensal (média 2,4 meses), gasta R$ 157 em extras, participa de desafios em grupo (45%). Não veio por indicação nem parceria. Já "comprou" a Vitaliza emocionalmente — falta amarrar contratualmente.',
    hipoteses: [
      'Vulnerabilidade a saída por motivos exógenos (preço, concorrência, mudança de rotina). Sem amarra contratual, qualquer fricção puxa pra fora.',
      'O alto uso atual é real, não inflacionado por evento único. Engajamento estável.',
      'A migração para plano semestral/anual reduziria o churn estrutural sem desconto agressivo — basta um incentivo pequeno (1 mês grátis na renovação anual).',
    ],
    cs_quote: 'A Elisa usa pra caramba, mas não se compromete. A gente precisa fazer ela migrar pra anual.',
  },
  2: {
    headline: 'No limbo: frequenta, mas a frequência caiu. Pode reagir bem a intervenção, pode ser sleeping dog parcial.',
    profile: 'Tem 29 anos, está na Vitaliza há 3,9 meses, com contrato semestral (média 4,8 meses). Frequência total razoável (1,85/sem) mas a frequência do mês corrente caiu (1,72/sem) — sinal clássico de desengajamento gradual. Gasta menos em extras (R$ 144), aderência social média. Cluster pequeno mas comportamentalmente o mais ambíguo da base.',
    hipoteses: [
      '"Cliente no limbo" — ainda usa, mas a frequência atual caiu vs. a média histórica. Sinal temporal de declínio.',
      'O contrato semestral em vigor cria atraso na decisão — o churn vai materializar quando o contrato terminar.',
      'Risco "sleeping dog" parcial — intervenção agressiva pode acelerar a saída em vez de prevenir.',
    ],
    cs_quote: 'O Rafael é o pesadelo. Pode ficar, pode sair. Se eu mexer demais, eu acordo ele. Se não mexer nada, eu perco.',
  },
  3: {
    headline: 'O alvo principal de ROI. Concentra 37% da base e responde por mais de 70% dos cancelamentos absolutos.',
    profile: 'Tem 28 anos (cluster mais jovem), está na Vitaliza há pouco mais de 2 meses, escolheu contrato mensal (média 1,9 meses) e já está despencando a frequência (0,95 sessões/semana — quase 1/3 da da Elisa). Gasta menos em extras (R$ 130), participa pouco de desafios em grupo (29%), não veio por indicação (19%).',
    hipoteses: [
      'Onboarding falho — quem chega ao mês 2 sem ritmo de uso (>1,5 sessões/sem) tem probabilidade > 50% de cancelar.',
      'Mismatch de plano — contratos mensais são porta de entrada e porta de saída. Sem amarra, qualquer atrito puxa pra fora.',
      'Isolamento social — <30% participam de desafios em grupo. Quem participa cancela metade.',
      'Cego para o Caminho A — ~33% dessas Julias saem sem clicar em "Cancelar" (cartão expirado, exclusão do app, chargeback).',
    ],
    cs_quote: 'A Julia a gente nem vê. Ela entra, abre o app duas vezes, deixa o cartão expirar e some. Se eu não for atrás dela nas primeiras 4 semanas, eu não recupero.',
  },
};

function PersonaCard({ cluster, idx }: { cluster: Cluster; idx: number }) {
  const narrative = PERSONA_NARRATIVES[cluster.id];
  const isHigh = cluster.churn_rate > 0.4;

  return (
    <div className="bg-white border border-inteli-gray-border rounded-lg shadow-card overflow-hidden mb-6">
      {/* Header colorido por persona */}
      <div className="text-white p-5 flex items-center gap-4" style={{ backgroundColor: cluster.color }}>
        <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-3xl font-bold">
          {cluster.name[0]}
        </div>
        <div className="flex-1">
          <div className="text-xs uppercase tracking-widest opacity-80">Persona C{cluster.id} · {idx}</div>
          <div className="text-2xl font-bold">{cluster.name}</div>
          <div className="text-sm opacity-90">{cluster.archetype}</div>
        </div>
        {isHigh && (
          <div className="bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
            Prioridade
          </div>
        )}
      </div>

      {/* Números */}
      <div className="grid grid-cols-4 border-b border-inteli-gray-border">
        <div className="p-3 text-center border-r border-inteli-gray-border">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted">Tamanho</div>
          <div className="text-lg font-bold text-inteli-navy">{cluster.n.toLocaleString('pt-BR')}</div>
          <div className="text-xs text-inteli-gray-muted">{(cluster.share * 100).toFixed(1)}%</div>
        </div>
        <div className="p-3 text-center border-r border-inteli-gray-border">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted">Churn</div>
          <div className="text-lg font-bold" style={{ color: cluster.color }}>{(cluster.churn_rate * 100).toFixed(1)}%</div>
          <div className="text-xs text-inteli-gray-muted">lift {cluster.lift.toFixed(2)}x</div>
        </div>
        <div className="p-3 text-center border-r border-inteli-gray-border">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted">LTV est.</div>
          <div className="text-lg font-bold text-inteli-navy">R$ {cluster.ltv_estimado.toFixed(0)}</div>
          <div className="text-xs text-inteli-gray-muted">por cliente</div>
        </div>
        <div className="p-3 text-center">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted">Valor agregado</div>
          <div className="text-lg font-bold text-inteli-navy">R$ {(cluster.valor_agregado / 1000).toFixed(0)}k</div>
          <div className="text-xs text-inteli-gray-muted">cluster total</div>
        </div>
      </div>

      <div className="p-5">
        {/* Headline */}
        <p className="text-sm font-semibold text-inteli-navy mb-3 leading-relaxed">
          {narrative.headline}
        </p>

        {/* Perfil detalhado */}
        <h4 className="text-xs uppercase tracking-wider text-inteli-gray-muted font-semibold mb-1">Perfil</h4>
        <p className="text-sm leading-relaxed mb-4">{narrative.profile}</p>

        {/* Detalhes em grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs mb-4 bg-inteli-gray-bg rounded p-3">
          <div><span className="text-inteli-gray-muted">Idade:</span> <strong>{cluster.age.toFixed(0)} anos</strong></div>
          <div><span className="text-inteli-gray-muted">Contrato:</span> <strong>{cluster.contract.toFixed(1)} meses</strong></div>
          <div><span className="text-inteli-gray-muted">Lifetime:</span> <strong>{cluster.lifetime.toFixed(1)} meses</strong></div>
          <div><span className="text-inteli-gray-muted">Freq atual:</span> <strong>{cluster.freq_current.toFixed(2)}/sem</strong></div>
          <div><span className="text-inteli-gray-muted">Desafios grupo:</span> <strong>{(cluster.group_visits * 100).toFixed(0)}%</strong></div>
          <div><span className="text-inteli-gray-muted">Parceria corp:</span> <strong>{(cluster.partner * 100).toFixed(0)}%</strong></div>
        </div>

        {/* Hipoteses */}
        <h4 className="text-xs uppercase tracking-wider text-inteli-gray-muted font-semibold mb-2">Hipoteses de driver de churn</h4>
        <ul className="space-y-1.5 text-sm mb-4">
          {narrative.hipoteses.map((h, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-inteli-red font-bold mt-0.5">H{i + 1}</span>
              <span className="leading-relaxed">{h}</span>
            </li>
          ))}
        </ul>

        {/* CS quote */}
        <div className="bg-inteli-navy/5 border-l-4 rounded-r p-3" style={{ borderLeftColor: cluster.color }}>
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Como o CS a descreve</div>
          <p className="text-sm italic text-inteli-gray-text">"{narrative.cs_quote}"</p>
        </div>
      </div>
    </div>
  );
}

export function Personas({ data }: { data: AnalysisData }) {
  return (
    <Section
      id="personas"
      track="business"
      number="5."
      title="Personas Data-Driven"
      subtitle="Renata, Elisa, Rafael, Julia — quatro nomes, quatro estratégias"
    >
      <p className="mb-6 leading-relaxed">
        Cada cluster recebe uma persona — uma narrativa executiva que sintetiza o perfil comportamental do segmento, suas hipóteses de driver de churn, e como o Customer Success a descreveria internamente. As personas são insumo direto para a matriz Valor × Risco (próxima seção) e para a recomendação executiva.
      </p>

      {data.clusters.map((c, i) => (
        <PersonaCard key={c.id} cluster={c} idx={i + 1} />
      ))}
    </Section>
  );
}
