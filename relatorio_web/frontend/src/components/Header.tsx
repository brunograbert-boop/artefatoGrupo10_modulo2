export function Header() {
  return (
    <header className="bg-inteli-navy text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-widest text-inteli-red font-semibold">
            MBA M2 · Inteli · Grupo 10
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-white mt-1">
            Customer Segmentation Report · Vitaliza
          </h1>
        </div>
        <div className="text-right hidden md:block">
          <div className="text-xs text-gray-300">Semana 10 · Artefato Final</div>
          <div className="text-xs text-gray-400 mt-1">Negócios + Tecnologia</div>
        </div>
      </div>
    </header>
  );
}
