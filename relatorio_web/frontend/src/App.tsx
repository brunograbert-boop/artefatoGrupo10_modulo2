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
import { Aplicacao } from './sections/Aplicacao';
import dataJson from './data/analysis_data.json';
import type { AnalysisData } from './types';

const data = dataJson as AnalysisData;

function App() {
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
