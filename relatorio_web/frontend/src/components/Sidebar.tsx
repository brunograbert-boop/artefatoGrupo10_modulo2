import { useEffect, useState } from 'react';

const SECTIONS = [
  { id: 'sumario', label: 'Sumário Executivo', track: 'all' },
  { id: 'contexto', label: '1. Contexto do Case', track: 'business' },
  { id: 'dado', label: '2. O Dado', track: 'tech' },
  { id: 'eda', label: '3. Análise Exploratória', track: 'tech' },
  { id: 'segmentacao', label: '4. Segmentação (KMeans)', track: 'tech' },
  { id: 'personas', label: '5. Personas', track: 'business' },
  { id: 'modelos', label: '6. Modelos Preditivos', track: 'tech' },
  { id: 'matriz', label: '7. Matriz Valor × Risco', track: 'business' },
  { id: 'recomendacoes', label: '8. Recomendações', track: 'business' },
  { id: 'limitacoes', label: '9. Limitações', track: 'all' },
  { id: 'aplicacao', label: '10. Aplicação Interativa', track: 'all' },
];

export function Sidebar() {
  const [active, setActive] = useState('sumario');

  useEffect(() => {
    const handleScroll = () => {
      const positions = SECTIONS.map(s => {
        const el = document.getElementById(s.id);
        if (!el) return { id: s.id, top: Infinity };
        return { id: s.id, top: el.getBoundingClientRect().top };
      });
      // Secao ativa: a primeira cujo topo está acima de 200px (zona do header)
      const visible = positions.filter(p => p.top < 200);
      if (visible.length > 0) {
        setActive(visible[visible.length - 1].id);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const trackBadge = (track: string) => {
    if (track === 'business') {
      return <span className="text-[10px] font-semibold text-inteli-petrol uppercase tracking-wider">Neg</span>;
    }
    if (track === 'tech') {
      return <span className="text-[10px] font-semibold text-inteli-red uppercase tracking-wider">Tec</span>;
    }
    return <span className="text-[10px] font-semibold text-inteli-gray-muted uppercase tracking-wider">·</span>;
  };

  return (
    <aside className="w-64 bg-white border-r border-inteli-gray-border sticky top-[88px] h-[calc(100vh-88px)] overflow-y-auto py-6">
      <div className="px-6 mb-4">
        <div className="text-xs font-semibold text-inteli-gray-muted uppercase tracking-widest">Navegação</div>
      </div>
      <nav className="space-y-1 px-3">
        {SECTIONS.map(s => (
          <a
            key={s.id}
            href={`#${s.id}`}
            className={`flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors ${
              active === s.id
                ? 'bg-inteli-navy text-white font-medium'
                : 'text-inteli-gray-text hover:bg-inteli-gray-bg'
            }`}
          >
            <span>{s.label}</span>
            {trackBadge(s.track)}
          </a>
        ))}
      </nav>
      <div className="px-6 mt-8 pt-6 border-t border-inteli-gray-border">
        <div className="text-xs text-inteli-gray-muted">
          <div className="font-semibold text-inteli-petrol uppercase tracking-wider mb-1">Neg</div>
          <div>Customer Segmentation Report</div>
          <div className="font-semibold text-inteli-red uppercase tracking-wider mb-1 mt-3">Tec</div>
          <div>Análise Exploratória + Classificadores</div>
        </div>
      </div>
    </aside>
  );
}
