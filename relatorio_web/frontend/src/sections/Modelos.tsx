import { Section } from '../components/Section';
import type { AnalysisData } from '../types';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts';

const FAMILY_TABLE = [
  { familia: 'Lineares', algoritmo: 'Regressão Logística', pergunta: 'Uma combinação linear das variáveis separa bem?', vantagem: 'Interpretável, calibrada, baseline forte', limite: 'Só captura relações lineares' },
  { familia: 'Árvores', algoritmo: 'Decision Tree', pergunta: 'Posso chegar à decisão por sequência de perguntas?', vantagem: 'Máxima interpretabilidade', limite: 'Tende a overfit' },
  { familia: 'Árvores (Bagging)', algoritmo: 'Random Forest', pergunta: 'Combinar muitas árvores reduz erro?', vantagem: 'Robusto, feature importance', limite: 'Menos interpretável' },
  { familia: 'Árvores (Boosting)', algoritmo: 'Gradient Boosting', pergunta: 'Cada árvore nova corrige os erros da anterior?', vantagem: 'Maior performance + prob. calibrada', limite: 'Sensível a hiperparâmetros' },
  { familia: 'Distância', algoritmo: 'KNN', pergunta: 'Clientes parecidos tiveram comportamento parecido?', vantagem: 'Simples, sem premissa de forma', limite: 'Sensível a escala e dimensionalidade' },
  { familia: 'Probabilísticos', algoritmo: 'Naive Bayes', pergunta: 'Dadas estas evidências, qual classe é mais provável?', vantagem: 'Rápido, funciona com pouco dado', limite: 'Premissa de independência entre features' },
  { familia: 'Redes Neurais', algoritmo: 'MLP', pergunta: 'Existe padrão complexo combinando variáveis?', vantagem: 'Flexível', limite: 'Caixa preta, precisa mais dado' },
];

export function Modelos({ data }: { data: AnalysisData }) {
  const results = data.models.results;
  const best = data.models.best_model;
  const cm = data.models.confusion_matrix;
  const importance = data.models.feature_importance;

  return (
    <Section
      id="modelos"
      track="tech"
      number="6."
      title="Modelos Preditivos"
      subtitle="9 classificadores comparados · Gradient Boosting eleito para produção"
    >
      {/* 6.1 - Familias */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">6.1 As famílias de classificadores</h3>
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-inteli-navy text-white">
              <th className="text-left px-3 py-2">Família</th>
              <th className="text-left px-3 py-2">Algoritmo</th>
              <th className="text-left px-3 py-2">Pergunta intuitiva</th>
              <th className="text-left px-3 py-2">Vantagem</th>
              <th className="text-left px-3 py-2">Limite</th>
            </tr>
          </thead>
          <tbody>
            {FAMILY_TABLE.map((f, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-inteli-gray-bg'}>
                <td className="px-3 py-2 font-semibold text-inteli-navy">{f.familia}</td>
                <td className="px-3 py-2 font-mono text-xs">{f.algoritmo}</td>
                <td className="px-3 py-2 text-inteli-gray-muted italic">{f.pergunta}</td>
                <td className="px-3 py-2">{f.vantagem}</td>
                <td className="px-3 py-2 text-inteli-gray-muted">{f.limite}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 6.2 - Comparativo de métricas */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">6.2 Comparativo de métricas (ordenado por AUC)</h3>
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-inteli-navy text-white">
              <th className="text-left px-3 py-2">Modelo</th>
              <th className="text-left px-3 py-2">Família</th>
              <th className="text-right px-3 py-2">Acuracia</th>
              <th className="text-right px-3 py-2">Precisao</th>
              <th className="text-right px-3 py-2">Recall</th>
              <th className="text-right px-3 py-2">F1</th>
              <th className="text-right px-3 py-2 bg-inteli-red">AUC</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => {
              const isBest = r.modelo === best;
              const isTree = r.modelo === 'Árvore de Decisão';
              return (
                <tr key={i} className={isBest ? 'bg-green-50 font-semibold' : isTree ? 'bg-blue-50' : (i % 2 === 0 ? 'bg-white' : 'bg-inteli-gray-bg')}>
                  <td className="px-3 py-2">
                    {r.modelo}
                    {isBest && <span className="ml-2 text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">Produção</span>}
                    {isTree && <span className="ml-2 text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">Narrativa</span>}
                  </td>
                  <td className="px-3 py-2 text-inteli-gray-muted text-xs">{r.familia}</td>
                  <td className="px-3 py-2 text-right">{(r.acuracia * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2 text-right">{(r.precisao * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2 text-right">{(r.recall * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2 text-right">{(r.f1 * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2 text-right font-bold">{r.roc_auc.toFixed(3)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 6.3 - Confusion matrix + Feature importance */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">6.3 Matriz de confusão · além da acurácia</h3>
      <p className="text-sm text-inteli-gray-muted mb-4">
        A acurácia de {(data.models.results[0].acuracia * 100).toFixed(1)}% sozinha mascara duas perguntas críticas: <em>quantos cancelamentos o modelo deixa escapar?</em> e <em>quantos clientes saudáveis ele alarma desnecessariamente?</em> A matriz abaixo decompõe os {cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]} clientes do conjunto de teste em quatro categorias.
      </p>

      {/* Matriz expandida no padrão do slide */}
      <div className="bg-white border border-inteli-gray-border rounded-lg p-5 mb-6 overflow-x-auto">
        <div className="text-xs uppercase tracking-wider text-inteli-gray-muted mb-4">Modelo: <strong className="text-inteli-navy">{best}</strong> · n = {cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]} clientes de teste</div>

        <table className="w-full text-sm border-collapse" style={{ minWidth: 720 }}>
          <thead>
            <tr>
              <th className="p-2" colSpan={2} rowSpan={2}></th>
              <th className="bg-blue-100 text-blue-900 p-2 text-center font-semibold" colSpan={2}>PREVISTO</th>
              <th className="bg-orange-100 text-orange-900 p-2 text-center font-semibold" rowSpan={2}>Métrica derivada</th>
            </tr>
            <tr>
              <th className="bg-blue-50 text-blue-900 p-2 text-center text-xs font-semibold border border-inteli-gray-border">Cancelou (+)</th>
              <th className="bg-blue-50 text-blue-900 p-2 text-center text-xs font-semibold border border-inteli-gray-border">Retido (−)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th className="bg-green-100 text-green-900 p-2 text-center font-semibold align-middle" rowSpan={2}>REAL</th>
              <th className="bg-green-50 text-green-900 p-2 text-xs font-semibold border border-inteli-gray-border">Cancelou (+)</th>
              <td className="bg-green-50 text-center p-4 border border-inteli-gray-border align-top">
                <div className="font-bold text-2xl text-green-900">{cm[1][1]}</div>
                <div className="text-[10px] uppercase tracking-wider text-green-800 font-semibold mt-1">TP · True Positive</div>
                <div className="text-[10px] text-green-700 italic">acerto</div>
              </td>
              <td className="bg-red-50 text-center p-4 border border-inteli-gray-border align-top">
                <div className="font-bold text-2xl text-red-900">{cm[1][0]}</div>
                <div className="text-[10px] uppercase tracking-wider text-red-800 font-semibold mt-1">FN · False Negative</div>
                <div className="text-[10px] text-red-700 italic">churn que escapou</div>
              </td>
              <td className="bg-orange-50 text-center p-3 border border-inteli-gray-border align-top">
                <div className="text-[10px] uppercase tracking-wider text-orange-900 font-semibold">Recall</div>
                <div className="text-[10px] text-orange-700 italic">(Sensitivity)</div>
                <div className="font-mono text-[10px] text-orange-800 mt-1">TP / (TP+FN)</div>
                <div className="font-bold text-lg text-orange-900 mt-1">{(cm[1][1] / (cm[1][1] + cm[1][0]) * 100).toFixed(1)}%</div>
              </td>
            </tr>
            <tr>
              <th className="bg-green-50 text-green-900 p-2 text-xs font-semibold border border-inteli-gray-border">Retido (−)</th>
              <td className="bg-red-50 text-center p-4 border border-inteli-gray-border align-top">
                <div className="font-bold text-2xl text-red-900">{cm[0][1]}</div>
                <div className="text-[10px] uppercase tracking-wider text-red-800 font-semibold mt-1">FP · False Positive</div>
                <div className="text-[10px] text-red-700 italic">falso alarme</div>
              </td>
              <td className="bg-green-50 text-center p-4 border border-inteli-gray-border align-top">
                <div className="font-bold text-2xl text-green-900">{cm[0][0]}</div>
                <div className="text-[10px] uppercase tracking-wider text-green-800 font-semibold mt-1">TN · True Negative</div>
                <div className="text-[10px] text-green-700 italic">acerto</div>
              </td>
              <td className="bg-orange-50 text-center p-3 border border-inteli-gray-border align-top">
                <div className="text-[10px] uppercase tracking-wider text-orange-900 font-semibold">Specificity</div>
                <div className="font-mono text-[10px] text-orange-800 mt-1">TN / (TN+FP)</div>
                <div className="font-bold text-lg text-orange-900 mt-1">{(cm[0][0] / (cm[0][0] + cm[0][1]) * 100).toFixed(1)}%</div>
              </td>
            </tr>
            <tr>
              <th className="bg-orange-100 text-orange-900 p-2 text-center font-semibold" colSpan={2}>Métrica derivada</th>
              <td className="bg-orange-50 text-center p-3 border border-inteli-gray-border align-top">
                <div className="text-[10px] uppercase tracking-wider text-orange-900 font-semibold">Precision</div>
                <div className="font-mono text-[10px] text-orange-800 mt-1">TP / (TP+FP)</div>
                <div className="font-bold text-lg text-orange-900 mt-1">{(cm[1][1] / (cm[1][1] + cm[0][1]) * 100).toFixed(1)}%</div>
              </td>
              <td className="bg-orange-50 text-center p-3 border border-inteli-gray-border align-top">
                <div className="text-[10px] uppercase tracking-wider text-orange-900 font-semibold">NPV</div>
                <div className="text-[9px] text-orange-700 italic">Negative Predictive Value</div>
                <div className="font-mono text-[10px] text-orange-800 mt-1">TN / (TN+FN)</div>
                <div className="font-bold text-lg text-orange-900 mt-1">{(cm[0][0] / (cm[0][0] + cm[1][0]) * 100).toFixed(1)}%</div>
              </td>
              <td className="bg-inteli-navy text-center p-3 border border-inteli-navy align-top">
                <div className="text-[10px] uppercase tracking-wider text-white opacity-90 font-semibold">Accuracy</div>
                <div className="font-mono text-[10px] text-gray-300 mt-1">(TP+TN) / total</div>
                <div className="font-bold text-lg text-white mt-1">{((cm[0][0] + cm[1][1]) / (cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]) * 100).toFixed(1)}%</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Leitura executiva */}
      <h4 className="text-base font-semibold text-inteli-navy mb-3">Leitura executiva</h4>
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-inteli-navy text-white">
              <th className="text-left px-3 py-2">Métrica</th>
              <th className="text-center px-3 py-2">Valor</th>
              <th className="text-left px-3 py-2">O que significa para a Vitaliza</th>
            </tr>
          </thead>
          <tbody>
            <tr className="bg-white">
              <td className="px-3 py-3 font-semibold">Recall</td>
              <td className="px-3 py-3 text-center font-bold text-inteli-red">{(cm[1][1] / (cm[1][1] + cm[1][0]) * 100).toFixed(1)}%</td>
              <td className="px-3 py-3">De cada 100 clientes que cancelariam, capturamos <strong>{((cm[1][1] / (cm[1][1] + cm[1][0])) * 100).toFixed(0)}</strong>. <strong>{cm[1][0]} clientes escapam</strong> — é o custo real que escapa pelos dedos.</td>
            </tr>
            <tr className="bg-inteli-gray-bg">
              <td className="px-3 py-3 font-semibold">Precision</td>
              <td className="px-3 py-3 text-center font-bold text-inteli-navy">{(cm[1][1] / (cm[1][1] + cm[0][1]) * 100).toFixed(1)}%</td>
              <td className="px-3 py-3">De cada 100 clientes que flagueamos como churn, <strong>{((cm[1][1] / (cm[1][1] + cm[0][1])) * 100).toFixed(0)}</strong> realmente cancelariam. <strong>{cm[0][1]} falsos alarmes</strong> — recebem intervenção mas ficariam mesmo.</td>
            </tr>
            <tr className="bg-white">
              <td className="px-3 py-3 font-semibold">Specificity</td>
              <td className="px-3 py-3 text-center font-bold text-inteli-navy">{(cm[0][0] / (cm[0][0] + cm[0][1]) * 100).toFixed(1)}%</td>
              <td className="px-3 py-3">De cada 100 clientes saudáveis, identificamos {((cm[0][0] / (cm[0][0] + cm[0][1])) * 100).toFixed(0)} corretamente. <strong>Quase nunca incomodamos quem fica.</strong></td>
            </tr>
            <tr className="bg-inteli-gray-bg">
              <td className="px-3 py-3 font-semibold">Accuracy</td>
              <td className="px-3 py-3 text-center font-bold text-inteli-navy">{((cm[0][0] + cm[1][1]) / (cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]) * 100).toFixed(1)}%</td>
              <td className="px-3 py-3">Número bonito para o slide do Board, mas <strong>enganoso isoladamente</strong> — a classe majoritária ("Retido") já daria 73,5% mesmo num modelo trivial que sempre prevê "fica".</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Discussão de custo / threshold */}
      <div className="bg-inteli-navy text-white rounded-lg p-5 mb-6">
        <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-3">Discussão para o Conselho · custo de cada tipo de erro</div>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-xs uppercase tracking-wider text-red-300 font-semibold mb-1">Falso Negativo · o erro caro</div>
            <div className="text-2xl font-bold mb-1">{cm[1][0]} clientes</div>
            <div className="text-sm leading-relaxed">
              Cancelaram, mas o modelo disse "fica". Em LTV: <strong>~R$ {(cm[1][0] * 287).toLocaleString('pt-BR')}</strong> escapando só nesta amostra de teste. Extrapolando para a base de 27.901 ativos: <strong>~R$ {Math.round(cm[1][0] * 287 * 27.901).toLocaleString('pt-BR')}/mês</strong> de receita perdida invisível.
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-xs uppercase tracking-wider text-yellow-300 font-semibold mb-1">Falso Positivo · o erro barato</div>
            <div className="text-2xl font-bold mb-1">{cm[0][1]} clientes</div>
            <div className="text-sm leading-relaxed">
              Receberam intervenção sem precisar. Custo baixo se for nudge (~R$ 0,50/email). Alto se for desconto agressivo (até R$ 39,90 de margem perdida por cliente). <strong>Sempre prefira nudges leves no início.</strong>
            </div>
          </div>
        </div>

        <div className="bg-white/5 rounded p-4 border-l-4 border-inteli-red">
          <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-1">Recomendação técnica</div>
          <p className="text-sm leading-relaxed">
            O modelo atual é <strong>conservador</strong> (FN &gt; FP). Em produção, vale ajustar o <em>threshold</em> de classificação (hoje em 0,5) para baixo — algo entre 0,3 e 0,4. Sacrifica precisão para ganhar recall. Cada ponto de recall adicional ≈ <strong>R$ 24 mil/mês recuperados</strong> em LTV, ao custo de mais alguns falsos alarmes (que são baratos se forem só nudges).
          </p>
        </div>
      </div>

      {/* Feature importance */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">6.4 Feature importance · o que o modelo realmente usa</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        As 3 features no topo (em destaque) carregam quase 80% do poder preditivo do modelo. Essa é a evidência empírica das hipóteses formuladas na EDA.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={importance.slice(0, 10)} layout="vertical" margin={{ left: 130, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis type="number" tick={{ fontSize: 10 }} />
            <YAxis type="category" dataKey="feature" tick={{ fontSize: 10 }} width={130} />
            <Tooltip formatter={(v) => Number(v).toFixed(3)} />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
              {importance.slice(0, 10).map((_, i) => (
                <Cell key={i} fill={i === 0 ? '#E63946' : i < 3 ? '#F39C12' : '#3498DB'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 6.4 - Regras da árvore */}
      <h3 className="text-lg font-semibold text-inteli-navy mb-2">6.5 Árvore de decisão · regras extraídas</h3>
      <p className="text-sm text-inteli-gray-muted mb-3">
        Visualização dos 3 primeiros níveis da árvore. Cada caixa mostra a pergunta (split), a proporção de clientes que cai naquele nó e a classe majoritária (azul = Retido, laranja = Cancelou). Essas regras viram a definição operacional das personas no slide do Board.
      </p>
      <div className="bg-white border border-inteli-gray-border rounded-lg p-3 overflow-x-auto">
        <img
          src="./arvore_decisao.png"
          alt="Árvore de decisão · 3 primeiros níveis"
          className="w-full h-auto"
        />
      </div>
      <details className="mt-3">
        <summary className="text-xs text-inteli-gray-muted cursor-pointer hover:text-inteli-navy">Ver regras em formato texto</summary>
        <pre className="bg-inteli-navy-dark text-green-300 text-xs p-4 rounded-lg overflow-x-auto whitespace-pre mt-2">
{data.models.tree_rules}
        </pre>
      </details>

      {/* 6.5 - Por que dois modelos */}
      <div className="mt-6 grid md:grid-cols-2 gap-4 mb-12">
        <div className="bg-blue-50 border-l-4 border-blue-600 rounded p-4">
          <div className="text-xs uppercase tracking-wider text-blue-900 font-semibold mb-1">Modelo de Narrativa</div>
          <div className="font-semibold mb-2">Árvore de Decisão</div>
          <p className="text-sm leading-relaxed">
            Não é o de maior AUC, mas é o mais <strong>interpretável</strong>. As regras viram a definição operacional das personas para o slide do board: "o cliente Early Dropout é definido por essas 3 perguntas".
          </p>
        </div>
        <div className="bg-green-50 border-l-4 border-green-600 rounded p-4">
          <div className="text-xs uppercase tracking-wider text-green-900 font-semibold mb-1">Modelo de Produção</div>
          <div className="font-semibold mb-2">Gradient Boosting</div>
          <p className="text-sm leading-relaxed">
            <strong>Maior AUC</strong> e probabilidades calibradas. É ele que alimenta o eixo Risco da matriz Valor × Risco da próxima seção.
          </p>
        </div>
      </div>

      {/* ====== 6.6 - VALIDAÇÃO RIGOROSA · PIPELINE ANTI-LEAKAGE ====== */}
      <div className="border-t-4 border-inteli-red pt-8 mt-8">
        <div className="bg-gradient-to-r from-inteli-red to-inteli-red-dark text-white rounded-lg p-5 mb-6">
          <div className="text-xs uppercase tracking-widest opacity-90 mb-1">Aula 6 · Métricas e Validação</div>
          <h3 className="text-2xl font-bold mb-2">6.6 Validação Rigorosa · Pipeline Anti-Leakage</h3>
          <p className="text-sm leading-relaxed opacity-95">
            Resposta às perguntas dos slides 36-39 da Aula 6 sobre sobreajuste, desbalanceamento e variáveis com vazamento de target. Substituímos o pipeline ingênuo por uma rotina honesta — e os números mudam.
          </p>
        </div>

        {/* O pipeline em 5 partes */}
        <h4 className="text-base font-semibold text-inteli-navy mb-3">As 5 partições do dataset</h4>
        <p className="text-sm text-inteli-gray-muted mb-4">
          Antes de qualquer modelagem, removemos as 2 variáveis identificadas como vazadoras (<code className="bg-inteli-gray-bg px-1 rounded">Avg_class_frequency_current_month</code> e <code className="bg-inteli-gray-bg px-1 rounded">Month_to_end_contract</code>) e separamos o dataset em 5 partes: 4 grupos de treino por persona + 1 holdout de teste intocado.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          {[
            { id: 'C0', name: 'Baixo Risco', n: data.validation.partitions.persona_0_renata.n, churn: data.validation.partitions.persona_0_renata.churn_rate, color: '#27AE60' },
            { id: 'C1', name: 'Médio', n: data.validation.partitions.persona_1_elisa.n, churn: data.validation.partitions.persona_1_elisa.churn_rate, color: '#3498DB' },
            { id: 'C2', name: 'Médio-Alto', n: data.validation.partitions.persona_2_rafael.n, churn: data.validation.partitions.persona_2_rafael.churn_rate, color: '#F39C12' },
            { id: 'C3', name: 'Alto Risco', n: data.validation.partitions.persona_3_julia.n, churn: data.validation.partitions.persona_3_julia.churn_rate, color: '#E74C3C' },
            { id: 'TEST', name: 'Holdout', n: data.validation.partitions.test_holdout.n, churn: data.validation.partitions.test_holdout.churn_rate, color: '#1B1F3B' },
          ].map(p => (
            <div key={p.id} className="bg-white border border-inteli-gray-border rounded-lg overflow-hidden">
              <div className="px-3 py-2 text-white text-xs font-semibold uppercase tracking-wider" style={{ backgroundColor: p.color }}>
                {p.id === 'TEST' ? 'TESTE' : `Treino · ${p.id}`}
              </div>
              <div className="p-3 text-center">
                <div className="text-xs text-inteli-gray-muted uppercase tracking-wider mb-1">{p.name}</div>
                <div className="text-2xl font-bold text-inteli-navy">{p.n.toLocaleString('pt-BR')}</div>
                <div className="text-xs text-inteli-gray-muted">clientes</div>
                <div className="mt-2 text-xs"><span className="text-inteli-gray-muted">churn: </span><strong style={{ color: p.color }}>{(p.churn * 100).toFixed(1)}%</strong></div>
              </div>
            </div>
          ))}
        </div>

        {/* ACHADO IMPORTANTE: personas mudam */}
        <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-r-lg p-5 mb-6">
          <div className="text-xs uppercase tracking-wider text-yellow-900 font-semibold mb-2">⚠ Achado importante</div>
          <h4 className="text-lg font-bold text-yellow-900 mb-2">As personas originais estavam parcialmente fundadas em leakage</h4>
          <p className="text-sm leading-relaxed text-yellow-900 mb-3">
            Ao re-clusterizar sem as variáveis vazadoras, a estrutura natural do dataset é <strong>diferente</strong>. O overlap entre clusters antigos (Renata/Elisa/Rafael/Júlia) e os novos é de apenas <strong>{(data.validation.cluster_overlap.overlap_pct * 100).toFixed(1)}%</strong>.
          </p>
          <p className="text-sm leading-relaxed text-yellow-900">
            <strong>Implicação:</strong> as personas narrativas do relatório (seções 4-5) continuam válidas como descrição do comportamento dos clientes, mas a <strong>operacionalização preditiva</strong> precisa usar os clusters limpos. Por isso aqui usamos apelidos técnicos (Baixo Risco, Médio, Médio-Alto, Alto Risco) — não Renata/Elisa/Rafael/Júlia.
          </p>
        </div>

        {/* Matriz orig vs novo */}
        <h4 className="text-base font-semibold text-inteli-navy mb-3">Como as personas se redistribuíram</h4>
        <div className="overflow-x-auto mb-6">
          <table className="w-full text-sm border-collapse" style={{ minWidth: 600 }}>
            <thead>
              <tr>
                <th className="p-2" rowSpan={2}></th>
                <th className="p-2 bg-inteli-petrol text-white text-center" colSpan={4}>Cluster NOVO (sem leakage)</th>
              </tr>
              <tr>
                <th className="bg-inteli-petrol text-white p-2 border border-inteli-gray-border text-xs">C0 · Baixo</th>
                <th className="bg-inteli-petrol text-white p-2 border border-inteli-gray-border text-xs">C1 · Médio</th>
                <th className="bg-inteli-petrol text-white p-2 border border-inteli-gray-border text-xs">C2 · Médio-Alto</th>
                <th className="bg-inteli-petrol text-white p-2 border border-inteli-gray-border text-xs">C3 · Alto</th>
              </tr>
            </thead>
            <tbody>
              {['C0 Renata (Leais)', 'C1 Elisa (Engajados)', 'C2 Rafael (Risco Médio)', 'C3 Júlia (Early Dropout)'].map((label, i) => {
                const row = data.validation.cluster_overlap.confusion_matrix_orig_vs_new[i];
                const total = row.reduce((a, b) => a + b, 0);
                return (
                  <tr key={i}>
                    <th className="bg-inteli-navy text-white p-2 border border-inteli-gray-border text-xs text-left">{label}</th>
                    {row.map((v, j) => {
                      const pct = total > 0 ? v / total : 0;
                      const intensity = Math.min(pct, 1);
                      const bg = i === j
                        ? `rgba(39, 174, 96, ${intensity * 0.6})`
                        : `rgba(231, 76, 60, ${intensity * 0.4})`;
                      return (
                        <td key={j} className="text-center p-3 border border-inteli-gray-border" style={{ backgroundColor: bg }}>
                          <div className="font-bold text-base">{v}</div>
                          <div className="text-[10px] text-inteli-gray-muted">{(pct * 100).toFixed(0)}%</div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Matrizes de confusão lado a lado - 3 cenários explorados */}
        <h4 className="text-base font-semibold text-inteli-navy mb-2">Matrizes de confusão · 3 cenários explorados</h4>
        <p className="text-sm text-inteli-gray-muted mb-4">
          Construímos três versões do modelo para entender o trade-off entre <strong>performance aparente</strong> (com leakage), <strong>performance honesta</strong> (sem leakage) e <strong>otimização para o problema de negócio</strong> (sem leakage + balanceamento). Cada matriz mostra TP/FN/FP/TN absolutos e as métricas derivadas.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {[
            {
              label: '🔴 Original',
              subtitle: 'GB COM leakage',
              note: 'Performance inflada',
              borderColor: 'border-red-500',
              bgHeader: 'bg-red-50',
              textHeader: 'text-red-900',
              n: data.models.confusion_matrix[0][0] + data.models.confusion_matrix[0][1] + data.models.confusion_matrix[1][0] + data.models.confusion_matrix[1][1],
              cm: data.models.confusion_matrix,
              acc: 0.937, rec: 0.849, prec: 0.907, f1: 0.877, auc: 0.978,
            },
            {
              label: '🟡 Sem leakage',
              subtitle: 'GB padrão',
              note: 'Honesto, mas conservador',
              borderColor: 'border-yellow-500',
              bgHeader: 'bg-yellow-50',
              textHeader: 'text-yellow-900',
              n: data.validation.partitions.test_holdout.n,
              cm: data.validation.global_metrics.gb_padrao.cm,
              acc: data.validation.global_metrics.gb_padrao.acuracia,
              rec: data.validation.global_metrics.gb_padrao.recall,
              prec: data.validation.global_metrics.gb_padrao.precisao,
              f1: data.validation.global_metrics.gb_padrao.f1,
              auc: data.validation.global_metrics.gb_padrao.roc_auc,
            },
            {
              label: '🟢 Sem leakage + balanced',
              subtitle: "class_weight='balanced'",
              note: 'Recall maximizado · ESCOLHIDO',
              borderColor: 'border-green-600',
              bgHeader: 'bg-green-50',
              textHeader: 'text-green-900',
              n: data.validation.partitions.test_holdout.n,
              cm: data.validation.global_metrics.gb_balanced.cm,
              acc: data.validation.global_metrics.gb_balanced.acuracia,
              rec: data.validation.global_metrics.gb_balanced.recall,
              prec: data.validation.global_metrics.gb_balanced.precisao,
              f1: data.validation.global_metrics.gb_balanced.f1,
              auc: data.validation.global_metrics.gb_balanced.roc_auc,
            },
          ].map((m, idx) => {
            const [[tn, fp], [fn, tp]] = m.cm;
            const recall = tp / (tp + fn) * 100;
            const specificity = tn / (tn + fp) * 100;
            const precision = tp / (tp + fp) * 100;
            const npv = tn / (tn + fn) * 100;
            const accuracy = (tp + tn) / m.n * 100;
            return (
              <div key={idx} className={`bg-white border-2 ${m.borderColor} rounded-lg overflow-hidden shadow-card`}>
                {/* Header */}
                <div className={`${m.bgHeader} px-4 py-3`}>
                  <div className={`text-xs uppercase tracking-widest font-bold ${m.textHeader}`}>{m.label}</div>
                  <div className={`text-sm font-semibold ${m.textHeader}`}>{m.subtitle}</div>
                  <div className="text-xs text-inteli-gray-muted mt-1 italic">{m.note} · n = {m.n}</div>
                </div>

                {/* Matriz 2x2 */}
                <div className="p-3">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr>
                        <th className="p-1"></th>
                        <th className="bg-blue-50 text-blue-900 p-1 text-center text-[10px] font-semibold border border-inteli-gray-border">Prev Canc</th>
                        <th className="bg-blue-50 text-blue-900 p-1 text-center text-[10px] font-semibold border border-inteli-gray-border">Prev Ret</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th className="bg-green-50 text-green-900 p-1 text-[10px] font-semibold border border-inteli-gray-border whitespace-nowrap">Real Canc</th>
                        <td className="bg-green-100 text-center p-2 border border-inteli-gray-border">
                          <div className="font-bold text-lg text-green-900">{tp}</div>
                          <div className="text-[9px] uppercase tracking-wider text-green-800 font-semibold">TP</div>
                        </td>
                        <td className="bg-red-100 text-center p-2 border border-inteli-gray-border">
                          <div className="font-bold text-lg text-red-900">{fn}</div>
                          <div className="text-[9px] uppercase tracking-wider text-red-800 font-semibold">FN</div>
                        </td>
                      </tr>
                      <tr>
                        <th className="bg-green-50 text-green-900 p-1 text-[10px] font-semibold border border-inteli-gray-border whitespace-nowrap">Real Ret</th>
                        <td className="bg-red-100 text-center p-2 border border-inteli-gray-border">
                          <div className="font-bold text-lg text-red-900">{fp}</div>
                          <div className="text-[9px] uppercase tracking-wider text-red-800 font-semibold">FP</div>
                        </td>
                        <td className="bg-green-100 text-center p-2 border border-inteli-gray-border">
                          <div className="font-bold text-lg text-green-900">{tn}</div>
                          <div className="text-[9px] uppercase tracking-wider text-green-800 font-semibold">TN</div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Métricas derivadas */}
                <div className="px-3 pb-3 grid grid-cols-2 gap-1.5 text-xs">
                  <div className="bg-orange-50 rounded p-1.5 text-center">
                    <div className="text-[9px] uppercase tracking-wider text-orange-900 font-semibold">Recall</div>
                    <div className="font-bold text-orange-900">{recall.toFixed(1)}%</div>
                  </div>
                  <div className="bg-orange-50 rounded p-1.5 text-center">
                    <div className="text-[9px] uppercase tracking-wider text-orange-900 font-semibold">Specificity</div>
                    <div className="font-bold text-orange-900">{specificity.toFixed(1)}%</div>
                  </div>
                  <div className="bg-orange-50 rounded p-1.5 text-center">
                    <div className="text-[9px] uppercase tracking-wider text-orange-900 font-semibold">Precision</div>
                    <div className="font-bold text-orange-900">{precision.toFixed(1)}%</div>
                  </div>
                  <div className="bg-orange-50 rounded p-1.5 text-center">
                    <div className="text-[9px] uppercase tracking-wider text-orange-900 font-semibold">NPV</div>
                    <div className="font-bold text-orange-900">{npv.toFixed(1)}%</div>
                  </div>
                  <div className="bg-inteli-navy text-white rounded p-1.5 text-center col-span-2">
                    <div className="text-[9px] uppercase tracking-wider opacity-90 font-semibold">Accuracy · F1 · AUC</div>
                    <div className="font-bold">{accuracy.toFixed(1)}% · {m.f1.toFixed(3)} · {m.auc.toFixed(3)}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Leitura comparativa */}
        <div className="bg-inteli-gray-bg rounded-lg p-4 mb-6 border-l-4 border-inteli-navy">
          <div className="text-xs uppercase tracking-wider text-inteli-navy font-semibold mb-2">Leitura comparativa das 3 matrizes</div>
          <ul className="text-sm leading-relaxed space-y-1 list-disc list-inside">
            <li><strong>Original</strong> tem só 40 FN, mas a base de teste é 1.000 (25%). Em proporção, deixa escapar 15,1% dos churners. Performance inflada por leakage.</li>
            <li><strong>Padrão sem leakage</strong> erra mais (47 FN em 800 = 22,2% escapando). É o "custo da honestidade" — variáveis vazadoras realmente ajudavam a separação aparente.</li>
            <li><strong>Balanced</strong> reduz FN para 26 (apenas <strong>12,3% escapando</strong>) — melhor que o original sem trapacear. Custo: 60 FP (clientes saudáveis flagueados) vs 23 no original.</li>
          </ul>
        </div>

        {/* Tabela comparativa 3 modelos */}
        <h4 className="text-base font-semibold text-inteli-navy mb-3">Comparação consolidada das métricas (no holdout de {data.validation.partitions.test_holdout.n} clientes)</h4>
        <div className="overflow-x-auto mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-inteli-navy text-white">
                <th className="text-left px-3 py-2">Métrica</th>
                <th className="text-center px-3 py-2">GB original<br/><span className="text-xs font-normal opacity-80">(com leakage)</span></th>
                <th className="text-center px-3 py-2">GB padrão<br/><span className="text-xs font-normal opacity-80">(sem leakage)</span></th>
                <th className="text-center px-3 py-2 bg-inteli-red">GB balanced<br/><span className="text-xs font-normal opacity-90">(sem leakage + class_weight)</span></th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Acurácia', orig: 0.937, pad: data.validation.global_metrics.gb_padrao.acuracia, bal: data.validation.global_metrics.gb_balanced.acuracia, fmt: 'pct' },
                { name: 'Recall (Sensitivity)', orig: 0.849, pad: data.validation.global_metrics.gb_padrao.recall, bal: data.validation.global_metrics.gb_balanced.recall, fmt: 'pct', highlight: true },
                { name: 'Precision', orig: 0.907, pad: data.validation.global_metrics.gb_padrao.precisao, bal: data.validation.global_metrics.gb_balanced.precisao, fmt: 'pct' },
                { name: 'F1 Score', orig: 0.877, pad: data.validation.global_metrics.gb_padrao.f1, bal: data.validation.global_metrics.gb_balanced.f1, fmt: 'dec3' },
                { name: 'ROC AUC', orig: data.validation.global_metrics.gb_original_com_leakage_auc, pad: data.validation.global_metrics.gb_padrao.roc_auc, bal: data.validation.global_metrics.gb_balanced.roc_auc, fmt: 'dec3' },
              ].map((r, i) => {
                const f = (v: number) => r.fmt === 'pct' ? `${(v * 100).toFixed(1)}%` : v.toFixed(3);
                return (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-inteli-gray-bg'}>
                    <td className="px-3 py-3 font-semibold">{r.name}</td>
                    <td className="px-3 py-3 text-center text-inteli-gray-muted">{f(r.orig)}</td>
                    <td className="px-3 py-3 text-center">{f(r.pad)}</td>
                    <td className={`px-3 py-3 text-center font-bold ${r.highlight ? 'bg-red-100 text-inteli-red' : 'text-inteli-navy'}`}>{f(r.bal)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Insight: GB balanced supera o original */}
        <div className="bg-green-50 border-l-4 border-green-600 rounded-r-lg p-4 mb-6">
          <div className="text-xs uppercase tracking-wider text-green-900 font-semibold mb-1">✓ Insight crítico</div>
          <p className="text-sm leading-relaxed text-green-900">
            <strong>O GB balanced (sem leakage) supera o GB original (com leakage) no Recall</strong> — {(data.validation.global_metrics.gb_balanced.recall * 100).toFixed(1)}% vs {(data.validation.global_metrics.gb_original_com_leakage_recall * 100).toFixed(1)}%. Ou seja: removendo o leakage e ajustando para o desbalanceamento, capturamos <em>mais</em> clientes em risco do que com o modelo inflado. Ganhamos credibilidade e performance no que importa.
          </p>
        </div>

        {/* Sobreajuste */}
        <h4 className="text-base font-semibold text-inteli-navy mb-3">Diagnóstico de sobreajuste</h4>
        <div className="bg-white border border-inteli-gray-border rounded-lg p-4 mb-6">
          <table className="w-full text-sm">
            <tbody>
              <tr>
                <td className="py-2 text-inteli-gray-muted">AUC no treino (3.200 clientes)</td>
                <td className="py-2 text-right font-bold text-inteli-navy">{data.validation.global_metrics.gb_padrao_auc_train.toFixed(4)}</td>
              </tr>
              <tr>
                <td className="py-2 text-inteli-gray-muted">AUC no teste ({data.validation.partitions.test_holdout.n} clientes)</td>
                <td className="py-2 text-right font-bold text-inteli-navy">{data.validation.global_metrics.gb_padrao.roc_auc.toFixed(4)}</td>
              </tr>
              <tr className="border-t-2 border-inteli-gray-border">
                <td className="py-2 font-semibold">Gap train-test</td>
                <td className="py-2 text-right font-bold text-green-700">+{data.validation.global_metrics.gb_padrao_overfit_gap.toFixed(4)}</td>
              </tr>
            </tbody>
          </table>
          <p className="text-xs text-inteli-gray-muted mt-3 italic">
            Gap menor que 0,05 indica sobreajuste sob controle. Modelos com gap &gt; 0,10 estariam memorizando o treino.
          </p>
        </div>

        {/* Recall por persona */}
        <h4 className="text-base font-semibold text-inteli-navy mb-3">Performance por cluster no holdout</h4>
        <div className="overflow-x-auto mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-inteli-navy text-white">
                <th className="text-left px-3 py-2">Cluster</th>
                <th className="text-center px-3 py-2">n no teste</th>
                <th className="text-center px-3 py-2">Churn observado</th>
                <th className="text-center px-3 py-2">Recall padrão</th>
                <th className="text-center px-3 py-2 bg-inteli-red">Recall balanced</th>
              </tr>
            </thead>
            <tbody>
              {data.validation.per_persona.map(p => {
                const names = ['C0 · Baixo Risco', 'C1 · Médio', 'C2 · Médio-Alto', 'C3 · Alto Risco'];
                const colors = ['#27AE60', '#3498DB', '#F39C12', '#E74C3C'];
                return (
                  <tr key={p.cluster_id} className={p.cluster_id % 2 === 0 ? 'bg-white' : 'bg-inteli-gray-bg'}>
                    <td className="px-3 py-3 font-semibold" style={{ color: colors[p.cluster_id] }}>{names[p.cluster_id]}</td>
                    <td className="px-3 py-3 text-center">{p.n_test}</td>
                    <td className="px-3 py-3 text-center">{(p.churn_rate_test * 100).toFixed(1)}%</td>
                    <td className="px-3 py-3 text-center text-inteli-gray-muted">{(p.recall_padrao * 100).toFixed(1)}%</td>
                    <td className="px-3 py-3 text-center font-bold text-inteli-red">{(p.recall_balanced * 100).toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Conclusão */}
        <div className="bg-inteli-navy text-white rounded-lg p-5">
          <div className="text-xs uppercase tracking-wider text-inteli-red font-semibold mb-2">Conclusão da validação rigorosa</div>
          <p className="text-sm leading-relaxed mb-3">
            Removendo as variáveis com vazamento e aplicando <code className="bg-white/10 px-1 rounded">class_weight='balanced'</code>, o modelo <strong>generaliza melhor</strong> que o original. Recall de {(data.validation.global_metrics.gb_balanced.recall * 100).toFixed(1)}% em dados <em>nunca vistos</em> — superior aos {(data.validation.global_metrics.gb_original_com_leakage_recall * 100).toFixed(1)}% do modelo "inflado" pelo leakage.
          </p>
          <p className="text-sm leading-relaxed">
            Para a Camila levar ao Conselho: o modelo <strong>existe</strong>, é <strong>defensável tecnicamente</strong> (sem vazamento), tem <strong>performance honesta</strong> validada num holdout, e <strong>captura proporcionalmente os clusters de maior risco</strong> ({(data.validation.per_persona[2].recall_balanced * 100).toFixed(1)}% de recall no C2 e {(data.validation.per_persona[3].recall_balanced * 100).toFixed(1)}% no C3 — onde está o problema real).
          </p>
        </div>
      </div>
    </Section>
  );
}
