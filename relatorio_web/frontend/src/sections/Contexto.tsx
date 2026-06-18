import { Section } from '../components/Section';

export function Contexto() {
  return (
    <Section
      id="contexto"
      track="business"
      number="1."
      title="Contexto do Case"
      subtitle="Vitaliza, Camila Ferraz e a decisão do Conselho em 19 dias"
    >
      <p className="mb-4 leading-relaxed">
        A <strong>Vitaliza</strong> é um aplicativo B2C de assinatura para bem-estar digital — programas guiados em fitness, meditação, nutrição e sono, em modelo similar ao Calm e ao Centr, adaptado para o mercado brasileiro. Fundada em 2019, surfou a curva de adoção acelerada da pandemia e cresceu a 47% ao trimestre até o final de 2022. Em março de 2023 captou Série A+ de R$ 22M ancorada na tese de retenção no mês 6 superior a 32,5% — 30% acima da média de mercado.
      </p>
      <p className="mb-6 leading-relaxed">
        A partir do Q3 de 2024, o setor entrou no que analistas chamam de <em>"vale da desilusão pós-pandemia"</em>: o Calm registrou queda de 18% em receita líquida, o Headspace demitiu 15% do quadro. A Vitaliza acompanhou: a base estabilizou em ~27.901 assinantes e o churn mensal subiu de ~7% para <strong>10,2%</strong> em setembro de 2025 — equivalente a churn anualizado de 73% e 2.847 cancelamentos por mês.
      </p>

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">O mandato da Camila</h3>
      <p className="mb-6 leading-relaxed">
        Camila Ferraz foi contratada em outubro de 2025 como VP de Crescimento e Retenção, vinda de uma fintech onde reduziu churn de 5,1% para 2,8% em nove meses. Seu mandato: <strong>derrubar o churn mensal da Vitaliza para 6,0% até Q4 de 2026</strong>. Em 19 dias, ela precisa apresentar ao Conselho um plano com modelo preditivo demonstrável.
      </p>

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">O dilema arquitetural</h3>
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="border-l-4 border-inteli-petrol bg-inteli-gray-bg rounded-r p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-petrol font-semibold mb-1">Caminho A</div>
          <div className="font-semibold mb-2">Win-back Reativo</div>
          <p className="text-sm leading-relaxed text-inteli-gray-text">
            Dispara quando o usuário clica em "Cancelar". MVP em 4 semanas, recupera 15-25% (Bain 2024). <strong>Limitação crítica:</strong> ~33% dos cancelamentos acontecem sem clique (cartão expirado, abandono, chargeback). Para esse terço, o Caminho A vale zero.
          </p>
        </div>
        <div className="border-l-4 border-inteli-red bg-inteli-gray-bg rounded-r p-4">
          <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-1">Caminho B</div>
          <div className="font-semibold mb-2">Engagement Forecasting Proativo</div>
          <p className="text-sm leading-relaxed text-inteli-gray-text">
            Score contínuo de churn para os 27.901 ativos. Reduz churn 30-50% em 6-9 meses. <strong>Limitações:</strong> 6 semanas de engenharia de dados antes do modelo; risco <em>"sleeping dogs"</em> (~8% da base paga sem usar).
          </p>
        </div>
      </div>

      <div className="bg-inteli-navy text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-2">A virada das 17h42</div>
        <p className="text-sm leading-relaxed">
          Na sexta em que Camila revisava as anotações, o <strong>Strava Premium</strong> anunciou camada de personalização para o Brasil em Q1/2026 — funcionalmente equivalente ao Caminho B. O Caminho B deixou de ser opcional e virou <strong>piso competitivo declarado pelo mercado</strong>.
        </p>
      </div>
    </Section>
  );
}
