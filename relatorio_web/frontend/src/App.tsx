import { useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Sumario } from './sections/Sumario';
import { Contexto } from './sections/Contexto';
import { Dado } from './sections/Dado';
import { EDA } from './sections/EDA';
import { Segmentacao } from './sections/Segmentacao';
import { Personas } from './sections/Personas';
import { Modelos } from './sections/Modelos';
import { Matriz } from './sections/Matriz';
import { Recomendacoes } from './sections/Recomendacoes';
import { Limitacoes } from './sections/Limitacoes';
import { Aplicacao, APP_URL } from './sections/Aplicacao';
import dataJson from './data/analysis_data.json';
import type { AnalysisData } from './types';

const data = dataJson as AnalysisData;

// Pré-aquece o app do Streamlit assim que o relatório abre, para que ele já
// esteja de pé quando o leitor chegar na Seção 10. Apps no Community Cloud
// "dormem" por inatividade; um GET inicial dispara o boot e o keep-alive evita
// que ele volte a dormir durante a leitura. Requisição fire-and-forget em
// no-cors (não precisamos da resposta; só queremos que o request chegue ao
// servidor). Observação: se o app estiver em sono profundo, o Streamlit exibe
// um botão "wake up" que exige clique — para garantia total, mantenha um pinger
// externo (cron-job.org / UptimeRobot) batendo na URL a cada ~5 min.
function prewarmApp() {
  if (!APP_URL) return;
  const ping = () => {
    fetch(APP_URL, { mode: 'no-cors', cache: 'no-store' }).catch(() => {});
    fetch(APP_URL + '_stcore/health', { mode: 'no-cors', cache: 'no-store' }).catch(() => {});
  };
  ping();
  return window.setInterval(ping, 4 * 60 * 1000); // keep-alive a cada 4 min
}

function App() {
  useEffect(() => {
    const id = prewarmApp();
    return () => {
      if (id) window.clearInterval(id);
    };
  }, []);

  return (
    <div className="min-h-screen bg-inteli-gray-bg">
      <Header />
      <div className="max-w-7xl mx-auto flex">
        <Sidebar />
        <main className="flex-1 px-4 md:px-8 py-8 max-w-5xl">
          <Sumario data={data} />
          <Contexto />
          <Dado data={data} />
          <EDA data={data} />
          <Segmentacao data={data} />
          <Personas data={data} />
          <Modelos data={data} />
          <Matriz data={data} />
          <Recomendacoes data={data} />
          <Limitacoes />
          <Aplicacao />
        </main>
      </div>
      <footer className="bg-inteli-navy-dark text-gray-400 text-xs py-4 px-6 mt-16">
        <div className="max-w-7xl mx-auto flex justify-between flex-wrap gap-2">
          <div>MBA em IA e Dados · Módulo 2 · Inteli · Semana 10 · 2026</div>
          <div>Grupo 10 · Gerado em {new Date(data.meta.generated_at).toLocaleDateString('pt-BR')}</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
