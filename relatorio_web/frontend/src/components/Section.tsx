import type { ReactNode } from 'react';

interface SectionProps {
  id: string;
  track: 'business' | 'tech' | 'all';
  number?: string;
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function Section({ id, track, number, title, subtitle, children }: SectionProps) {
  const trackLabel =
    track === 'business' ? 'Negócios · Esta Aula' :
    track === 'tech' ? 'Tecnologia · Jornada Nicola' :
    'Integrado';

  const headerClass =
    track === 'business' ? 'bg-inteli-petrol' :
    track === 'tech' ? 'bg-inteli-navy' :
    'bg-gradient-to-r from-inteli-petrol to-inteli-navy';

  return (
    <section id={id} className="mb-12 scroll-mt-24">
      <div className={`${headerClass} text-white px-6 py-3 rounded-t-lg`}>
        <div className="text-[11px] font-semibold uppercase tracking-widest opacity-80">
          {trackLabel}
        </div>
        <h2 className="text-xl md:text-2xl font-bold text-white mt-0.5">
          {number && <span className="opacity-50 mr-2">{number}</span>}{title}
        </h2>
        {subtitle && <p className="text-sm text-gray-200 mt-1">{subtitle}</p>}
      </div>
      <div className="bg-white border border-inteli-gray-border border-t-0 rounded-b-lg p-6 md:p-8 shadow-card">
        {children}
      </div>
    </section>
  );
}
