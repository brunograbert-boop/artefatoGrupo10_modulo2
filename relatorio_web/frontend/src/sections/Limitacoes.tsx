import { Section } from '../components/Section';

const LIMITS = [
  {
    titulo: 'Ausência de dados granulares do Mixpanel',
    detalhe: 'O dataset agregado não permite construir features de série temporal (declínio semana a semana, tempo desde última sessão, sequência de eventos). A hipótese "declínio de engajamento prevê churn" do Head de Produto não pode ser testada com o que temos.',
  },
  {
    titulo: 'Snapshot, não trajetória',
    detalhe: 'As variáveis Avg_class_frequency_total e Avg_class_frequency_current_month são snapshots, não trajetórias. Perdemos sinais de momentum (cliente que estava em 4/sem e desceu para 1/sem).',
  },
  {
    titulo: 'Churn invisível não representado',
    detalhe: 'Cancelamentos via falha de pagamento, chargeback ou abandono silencioso (~33% do fenômeno total, segundo o case) não estão rotulados no dataset. Qualquer modelo treinado aqui tem recall máximo teórico de ~67% do fenômeno real.',
  },
  {
    titulo: 'Possível target leakage',
    detalhe: 'Avg_class_frequency_current_month e Month_to_end_contract são co-temporais ao evento. Para produção, é necessário reconstruir features em snapshot point-in-time (T-30 dias).',
  },
  {
    titulo: 'Sem holdout temporal',
    detalhe: 'O split aleatório sub-estima a deterioração do modelo no tempo (drift). Recomendado teste com split temporal (treino jan-jun, teste jul-set) antes do deploy.',
  },
  {
    titulo: 'Variáveis ausentes que importariam',
    detalhe: 'Motivo de cancelamento, NPS, ticket de suporte aberto, fonte de aquisição (orgânico vs paid), histórico de pagamento. A própria instrumentação de saída do app (que a Patrícia removeu em 2021) precisaria ser reconstruída.',
  },
];

const NEXT_STEPS = [
  { semana: '1-3', titulo: 'Reconciliar PostgreSQL × Mixpanel × GA4 por user_id', detalhe: 'Sem isso, Rafael e Júlia permanecem indistinguíveis em produção.' },
  { semana: '3-5', titulo: 'Reconstruir snapshot point-in-time T-30 e retreinar', detalhe: 'Atual GB AUC=0,98 tem risco de leakage. Validar com holdout temporal.' },
  { semana: '5-7', titulo: 'Integrar segmentação à interface', detalhe: 'CS e Marketing recebem o cluster do cliente em tempo real no CRM.' },
  { semana: '8-10', titulo: 'Piloto A/B no segmento Júlia', detalhe: 'Intervir em 50% do C3 com Caminho B (proativo) e comparar churn vs grupo controle. Validar que a intervenção CAUSA retenção.' },
];

export function Limitacoes() {
  return (
    <Section
      id="limitacoes"
      track="all"
      number="9."
      title="Limitações e Próximos Passos"
      subtitle="Onde a análise para e o que precisa ser feito antes do deploy"
    >
      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Limitações materiais</h3>
      <div className="space-y-3 mb-8">
        {LIMITS.map((l, i) => (
          <div key={i} className="bg-white border border-inteli-gray-border rounded-lg p-4 flex gap-4">
            <div className="text-2xl font-bold text-inteli-red w-8 flex-shrink-0">{i + 1}</div>
            <div>
              <div className="font-semibold text-inteli-navy mb-1">{l.titulo}</div>
              <p className="text-sm leading-relaxed text-inteli-gray-text">{l.detalhe}</p>
            </div>
          </div>
        ))}
      </div>

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Próximos passos · roadmap de 10 semanas</h3>
      <div className="space-y-3">
        {NEXT_STEPS.map((s, i) => (
          <div key={i} className="bg-white border border-inteli-gray-border rounded-lg p-4 flex gap-4">
            <div className="bg-inteli-navy text-white text-center w-20 py-3 rounded font-bold text-sm flex-shrink-0">
              <div className="text-[10px] uppercase tracking-wider opacity-80">Semana</div>
              <div className="text-lg">{s.semana}</div>
            </div>
            <div className="flex-1">
              <div className="font-semibold text-inteli-navy mb-1">{s.titulo}</div>
              <p className="text-sm leading-relaxed text-inteli-gray-text">{s.detalhe}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 bg-inteli-petrol text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider opacity-80 font-semibold mb-2">Encerramento</div>
        <p className="text-sm leading-relaxed">
          Esta segmentação é um <strong>ponto de partida defensável</strong>, não um produto final. Ela responde à pergunta da Camila para o Conselho de 14 de novembro com evidência data-driven. Mas o sistema de inteligência de retenção da Vitaliza ainda precisa ser construído — e é o que a aprovação dos R$ 600 mil viabiliza.
        </p>
      </div>
    </Section>
  );
}
