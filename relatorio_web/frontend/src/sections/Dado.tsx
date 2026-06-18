import { Section } from '../components/Section';
import type { AnalysisData } from '../types';

const VARS = [
  { var: 'gender', tipo: 'binária', desc: 'Gênero (0/1, anonimizado)' },
  { var: 'Near_Location', tipo: 'binária', desc: 'Mora próximo a região de atuação' },
  { var: 'Partner', tipo: 'binária', desc: 'Veio por parceria corporativa' },
  { var: 'Promo_friends', tipo: 'binária', desc: 'Veio por indicação de amigo' },
  { var: 'Phone', tipo: 'binária', desc: 'Forneceu telefone no cadastro' },
  { var: 'Contract_period', tipo: 'inteiro', desc: 'Duração do plano em meses (1/6/12)' },
  { var: 'Group_visits', tipo: 'binária', desc: 'Participa de desafios em grupo' },
  { var: 'Age', tipo: 'inteiro', desc: 'Idade' },
  { var: 'Avg_additional_charges_total', tipo: 'float (R$)', desc: 'Total acumulado em serviços extras (não é a mensalidade)' },
  { var: 'Month_to_end_contract', tipo: 'float', desc: 'Meses até o fim do contrato vigente' },
  { var: 'Lifetime', tipo: 'inteiro', desc: 'Tempo total na Vitaliza, em meses' },
  { var: 'Avg_class_frequency_total', tipo: 'float', desc: 'Frequência semanal média (vida toda)' },
  { var: 'Avg_class_frequency_current_month', tipo: 'float', desc: 'Frequência semanal média (mês corrente)' },
  { var: 'Churn', tipo: 'binária (alvo)', desc: '1 = cancelou nos últimos 6 meses' },
];

export function Dado({ data }: { data: AnalysisData }) {
  return (
    <Section
      id="dado"
      track="tech"
      number="2."
      title="O Dado"
      subtitle="A amostra reconciliada manualmente pelo CTO Diego"
    >
      <p className="mb-6 leading-relaxed">
        O CTO Diego Almeida dedicou a tarde de quinta-feira a um esforço manual de reconciliação entre PostgreSQL (transações e perfil), Mixpanel (eventos do app) e GA4 (tráfego). O resultado, entregue na manhã de sexta, é o arquivo <code className="bg-inteli-gray-bg px-1.5 py-0.5 rounded text-sm">gym_churn_us.csv</code>: amostra anonimizada de <strong>4.000 assinantes</strong>, com 13 variáveis comportamentais e demográficas mais a flag de churn.
      </p>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">Ticket médio</div>
          <div className="text-xl font-bold text-inteli-navy">R$ {data.meta.ticket_medio_mensal.toFixed(2).replace('.', ',')}</div>
          <div className="text-xs text-inteli-gray-muted mt-1">por assinante / mês</div>
        </div>
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">CAC blended</div>
          <div className="text-xl font-bold text-inteli-navy">R$ {data.meta.cac.toFixed(2).replace('.', ',')}</div>
          <div className="text-xs text-inteli-gray-muted mt-1">aquisição por cliente</div>
        </div>
        <div className="bg-inteli-gray-bg rounded-lg p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-1">LTV atual</div>
          <div className="text-xl font-bold text-inteli-red">R$ 287</div>
          <div className="text-xs text-inteli-gray-muted mt-1">caiu de R$ 412 no Q1/25</div>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">Dicionário de variáveis</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-inteli-navy text-white">
              <th className="text-left px-4 py-2 font-semibold">Variável</th>
              <th className="text-left px-4 py-2 font-semibold">Tipo</th>
              <th className="text-left px-4 py-2 font-semibold">Interpretação Vitaliza</th>
            </tr>
          </thead>
          <tbody>
            {VARS.map((v, i) => (
              <tr key={v.var} className={i % 2 === 0 ? 'bg-white' : 'bg-inteli-gray-bg'}>
                <td className="px-4 py-2 font-mono text-xs">{v.var}</td>
                <td className="px-4 py-2 text-inteli-gray-muted">{v.tipo}</td>
                <td className="px-4 py-2">{v.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-xs text-inteli-gray-muted italic">
        A amostra <strong>não</strong> inclui eventos granulares do Mixpanel — esses permanecem inacessíveis sem o pipeline unificado que custaria 6 semanas. O que está disponível são agregados mensais por usuário.
      </div>
    </Section>
  );
}
