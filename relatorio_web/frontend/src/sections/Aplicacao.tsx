import { useEffect, useState } from 'react';
import { Section } from '../components/Section';

// URL pública do app (Streamlit Community Cloud). Deixe vazio ('') enquanto não
// houver deploy — a seção mostra as instruções para rodar localmente.
// Exportada para o App pré-aquecer o app (acordar do standby) já na abertura.
export const APP_URL = 'https://artefatogrupo10modulo2.streamlit.app/';
// embed=true remove a barra/rodapé do Streamlit para incorporar limpo no iframe.
const APP_EMBED_URL = APP_URL + (APP_URL.includes('?') ? '&' : '?') + 'embed=true';

const TABS = [
  {
    nome: '🧍 Novo cliente',
    desc: 'Formulário que valida os dados contra as faixas mapeadas, atribui o segmento/persona, estima a probabilidade de churn e explica o porquê com SHAP + a escala de threshold.',
  },
  {
    nome: '🎚️ Thresholds',
    desc: 'Escala de risco (faixas) e matriz de confusão recalculada ao vivo conforme o ponto de corte (τ), evidenciando o trade-off precision × recall.',
  },
  {
    nome: '🔍 Explicabilidade',
    desc: 'Importância global das variáveis por SHAP e pelo próprio modelo (complemento da explicação local por cliente).',
  },
  {
    nome: '✅ Validação',
    desc: 'Overfit (gap treino-teste + validação cruzada), vazamento (com vs sem as features co-temporais) e tratamento de desbalanceamento.',
  },
  {
    nome: '📦 Lote (CSV)',
    desc: 'Predição em massa: sobe um CSV e baixa as probabilidades e faixas de risco de cada cliente.',
  },
];

// Notificação (toast) exibida quando o leitor entra na Seção 10, lembrando que
// o app do Streamlit pode estar adormecido e exige o clique em "Yes, get this
// app back up!" para iniciar. Some sozinha após alguns segundos ou ao fechar.
function WakeNotice() {
  const [visible, setVisible] = useState(false);
  const [closed, setClosed] = useState(false);

  useEffect(() => {
    if (!APP_URL) return; // sem app embutido, nada a avisar
    const el = document.getElementById('aplicacao');
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setVisible(true);
          obs.disconnect(); // dispara só uma vez por carregamento
        }
      },
      { threshold: 0.15 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    const t = window.setTimeout(() => setClosed(true), 14000); // auto-hide 14s
    return () => window.clearTimeout(t);
  }, [visible]);

  if (!visible || closed) return null;

  return (
    <div
      role="alert"
      className="fixed bottom-6 right-6 z-[60] w-[22rem] max-w-[calc(100vw-2rem)] rounded-lg border border-amber-300 bg-amber-50 shadow-2xl ring-1 ring-black/5"
    >
      <div className="flex items-start gap-3 p-4">
        <span className="text-xl leading-none" aria-hidden>💤</span>
        <div className="flex-1">
          <div className="text-sm font-semibold text-amber-900">
            Iniciar a aplicação
          </div>
          <p className="mt-1 text-sm leading-relaxed text-amber-800">
            Se o app abaixo aparecer <strong>adormecido</strong>, clique em{' '}
            <strong>“Yes, get this app back up!”</strong> dentro do quadro para
            iniciá-lo. Ele leva alguns segundos para subir.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setClosed(true)}
          aria-label="Fechar aviso"
          className="-mt-1 -mr-1 rounded p-1 text-amber-700 hover:bg-amber-100 hover:text-amber-900 transition-colors"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

export function Aplicacao() {
  return (
    <>
    <WakeNotice />
    <Section
      id="aplicacao"
      track="all"
      number="10."
      title="Aplicação Interativa (Modelo no Ar)"
      subtitle="A camada operacional: o modelo servido como serviço web, com explicabilidade por cliente"
    >
      <p className="text-sm leading-relaxed text-inteli-gray-text mb-6">
        Esta seção entrega o que o roadmap da Seção 9 antecipa: um <strong>serviço de
        inferência</strong> que serve o modelo <strong>sem vazamento</strong> (treinado sem
        as variáveis co-temporais ao churn), <strong>atribui o segmento/persona</strong> de
        um cliente novo e <strong>explica a previsão com SHAP</strong> — tudo numa interface
        web. Treino e inferência são separados (pipeline de treinamento → artefato
        serializado <code>.joblib</code> → app de inferência).
      </p>

      {APP_URL ? (
        <div className="mb-6">
          <a
            href={APP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-inteli-petrol text-white font-semibold px-5 py-3 rounded-lg hover:opacity-90 transition-opacity"
          >
            ▶ Abrir aplicação em nova aba
          </a>
          <div className="mt-4 border border-inteli-gray-border rounded-lg overflow-hidden">
            <iframe
              src={APP_EMBED_URL}
              title="Preditor de Churn Vitaliza"
              className="w-full"
              style={{ height: '720px', border: 'none' }}
            />
          </div>
        </div>
      ) : (
        <div className="mb-6 bg-inteli-gray-bg border border-inteli-gray-border rounded-lg p-5">
          <div className="font-semibold text-inteli-navy mb-2">Como acessar o app</div>
          <p className="text-sm text-inteli-gray-text mb-3">
            O aplicativo está em <code>aplicacao_modelo/</code> (pipeline de inferência em Streamlit).
            Para rodar localmente:
          </p>
          <pre className="bg-inteli-navy-dark text-gray-100 text-xs rounded-md p-4 overflow-x-auto">
{`cd aplicacao_modelo
pip install -r requirements.txt
streamlit run app.py     # abre em http://localhost:8501`}
          </pre>
          <p className="text-xs text-inteli-gray-muted mt-3">
            Após publicar no Streamlit Community Cloud, cole a URL na constante
            <code> APP_URL </code> em <code>src/sections/Aplicacao.tsx</code> para incorporar
            o app aqui (botão + iframe).
          </p>
        </div>
      )}

      <h3 className="text-lg font-semibold text-inteli-navy mb-3">O que o app faz</h3>
      <div className="grid md:grid-cols-2 gap-3 mb-6">
        {TABS.map((t, i) => (
          <div key={i} className="bg-white border border-inteli-gray-border rounded-lg p-4">
            <div className="font-semibold text-inteli-navy mb-1">{t.nome}</div>
            <p className="text-sm leading-relaxed text-inteli-gray-text">{t.desc}</p>
          </div>
        ))}
      </div>

      <div className="bg-inteli-navy text-white rounded-lg p-5">
        <div className="text-xs uppercase tracking-wider opacity-80 font-semibold mb-2">
          Modelo servido
        </div>
        <p className="text-sm leading-relaxed">
          Regressão Logística tunada, <strong>sem as 2 features vazadoras</strong> —
          ROC-AUC <strong>0,957</strong>, recall <strong>0,915</strong>, gap de overfit
          <strong> ~0</strong>. Explicabilidade local por <strong>SHAP</strong> (com
          ressalva de não-causalidade) e explicação em linguagem natural pronta para o LLM
          (OpenRouter). Detalhes em <code>aplicacao_modelo/REAVALIACAO_MODELO.md</code>.
        </p>
      </div>
    </Section>
    </>
  );
}
