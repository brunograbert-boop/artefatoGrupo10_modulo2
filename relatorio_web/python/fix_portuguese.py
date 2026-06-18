"""
Reaplica acentuação portuguesa nos arquivos .tsx do frontend.
Matching case-insensitive, replacement preservando a capitalização da palavra original.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent / 'frontend' / 'src'

# Dicionário sem acento -> com acento. Tudo em lowercase aqui; a capitalização
# do texto original é preservada no replacement.
SUBS = {
    # Conectivos / particulas
    'nao': 'não',
    'sao': 'são',
    'estao': 'estão',
    'vao': 'vão',
    'tao': 'tão',
    'entao': 'então',
    'ja': 'já',
    'ate': 'até',
    'alem': 'além',
    'atras': 'atrás',
    'apos': 'após',
    'voce': 'você',
    'voces': 'vocês',
    'porem': 'porém',
    'tres': 'três',
    'la': 'lá',
    'so': 'só',
    'tambem': 'também',
    'porque': 'porque',
    'ate': 'até',
    'ha': 'há',
    've': 'vê',

    # Cao / coes
    'acao': 'ação',
    'acoes': 'ações',
    'decisao': 'decisão',
    'decisoes': 'decisões',
    'informacao': 'informação',
    'informacoes': 'informações',
    'intervencao': 'intervenção',
    'intervencoes': 'intervenções',
    'comparacao': 'comparação',
    'comparacoes': 'comparações',
    'validacao': 'validação',
    'execucao': 'execução',
    'transformacao': 'transformação',
    'padronizacao': 'padronização',
    'personalizacao': 'personalização',
    'selecao': 'seleção',
    'segmentacao': 'segmentação',
    'instrumentacao': 'instrumentação',
    'sofisticacao': 'sofisticação',
    'automacao': 'automação',
    'operacao': 'operação',
    'operacoes': 'operações',
    'distribuicao': 'distribuição',
    'instalacao': 'instalação',
    'aceleracao': 'aceleração',
    'correlacao': 'correlação',
    'correlacoes': 'correlações',
    'nocao': 'noção',
    'posicao': 'posição',
    'posicoes': 'posições',
    'inovacao': 'inovação',
    'avaliacao': 'avaliação',
    'avaliacoes': 'avaliações',
    'aplicacao': 'aplicação',
    'aplicacoes': 'aplicações',
    'producao': 'produção',
    'calibracao': 'calibração',
    'explicacao': 'explicação',
    'geracao': 'geração',
    'geracoes': 'gerações',
    'caracterizacao': 'caracterização',
    'classificacao': 'classificação',
    'opcao': 'opção',
    'opcoes': 'opções',
    'aquisicao': 'aquisição',
    'aquisicoes': 'aquisições',
    'retencao': 'retenção',
    'detencao': 'detenção',
    'intencao': 'intenção',
    'reducao': 'redução',
    'solucao': 'solução',
    'solucoes': 'soluções',
    'condicao': 'condição',
    'condicoes': 'condições',
    'duracao': 'duração',
    'descricao': 'descrição',
    'reconciliacao': 'reconciliação',
    'transacao': 'transação',
    'transacoes': 'transações',
    'indicacao': 'indicação',
    'indicacoes': 'indicações',
    'atuacao': 'atuação',
    'renovacao': 'renovação',
    'renovacoes': 'renovações',
    'interpretacao': 'interpretação',
    'recomendacao': 'recomendação',
    'recomendacoes': 'recomendações',
    'situacao': 'situação',
    'situacoes': 'situações',
    'reativacao': 'reativação',
    'reativacoes': 'reativações',
    'integracao': 'integração',
    'integracoes': 'integrações',
    'configuracao': 'configuração',
    'configuracoes': 'configurações',
    'migracao': 'migração',
    'migracoes': 'migrações',
    'fricao': 'fricção',
    'friccao': 'fricção',
    'alocacao': 'alocação',
    'extracao': 'extração',
    'exclusao': 'exclusão',
    'exclusoes': 'exclusões',

    # Termos com cedilha
    'preco': 'preço',
    'precos': 'preços',
    'comeco': 'começo',
    'forca': 'força',
    'cabeca': 'cabeça',
    'crianca': 'criança',
    'crancas': 'crianças',
    'esforco': 'esforço',
    'esforcos': 'esforços',
    'orcamento': 'orçamento',
    'orcamentos': 'orçamentos',
    'servico': 'serviço',
    'servicos': 'serviços',
    'lancamento': 'lançamento',
    'lancamentos': 'lançamentos',

    # Til
    'mae': 'mãe',
    'irmao': 'irmão',
    'manha': 'manhã',
    'tarde': 'tarde',
    'sessao': 'sessão',
    'sessoes': 'sessões',
    'mensao': 'menção',
    'cartao': 'cartão',
    'cartoes': 'cartões',
    'feijao': 'feijão',
    'pao': 'pão',

    # Acento agudo / circunflexo - substantivos / adjetivos
    'modulo': 'módulo',
    'modulos': 'módulos',
    'negocio': 'negócio',
    'negocios': 'negócios',
    'calculo': 'cálculo',
    'calculos': 'cálculos',
    'metodo': 'método',
    'metodos': 'métodos',
    'metrica': 'métrica',
    'metricas': 'métricas',
    'criterio': 'critério',
    'criterios': 'critérios',
    'tecnico': 'técnico',
    'tecnica': 'técnica',
    'tecnicos': 'técnicos',
    'tecnicas': 'técnicas',
    'publico': 'público',
    'publica': 'pública',
    'publicos': 'públicos',
    'tipico': 'típico',
    'tipica': 'típica',
    'tipicos': 'típicos',
    'concorrencia': 'concorrência',
    'experiencia': 'experiência',
    'experiencias': 'experiências',
    'estrategia': 'estratégia',
    'estrategias': 'estratégias',
    'estrategico': 'estratégico',
    'estrategica': 'estratégica',
    'frequencia': 'frequência',
    'frequencias': 'frequências',
    'dependencia': 'dependência',
    'evidencia': 'evidência',
    'evidencias': 'evidências',
    'presenca': 'presença',
    'agencia': 'agência',
    'audiencia': 'audiência',
    'aderencia': 'aderência',
    'saida': 'saída',
    'saidas': 'saídas',
    'duvida': 'dúvida',
    'duvidas': 'dúvidas',
    'ultimo': 'último',
    'ultima': 'última',
    'ultimos': 'últimos',
    'ultimas': 'últimas',
    'maximo': 'máximo',
    'maxima': 'máxima',
    'minimo': 'mínimo',
    'minima': 'mínima',
    'media': 'média',
    'medias': 'médias',
    'medio': 'médio',
    'medios': 'médios',
    'rapido': 'rápido',
    'rapida': 'rápida',
    'distancia': 'distância',
    'numero': 'número',
    'numeros': 'números',
    'unico': 'único',
    'unica': 'única',
    'unicos': 'únicos',
    'unicas': 'únicas',
    'proximo': 'próximo',
    'proxima': 'próxima',
    'proximos': 'próximos',
    'proximas': 'próximas',
    'periodo': 'período',
    'periodos': 'períodos',
    'nivel': 'nível',
    'niveis': 'níveis',
    'facil': 'fácil',
    'faceis': 'fáceis',
    'dificil': 'difícil',
    'dificeis': 'difíceis',
    'possivel': 'possível',
    'possiveis': 'possíveis',
    'defensavel': 'defensável',
    'defensaveis': 'defensáveis',
    'interpretavel': 'interpretável',
    'interpretaveis': 'interpretáveis',
    'variavel': 'variável',
    'variaveis': 'variáveis',
    'notavel': 'notável',
    'notaveis': 'notáveis',
    'razoavel': 'razoável',
    'razoaveis': 'razoáveis',
    'necessario': 'necessário',
    'necessaria': 'necessária',
    'necessarios': 'necessários',
    'necessarias': 'necessárias',
    'proprio': 'próprio',
    'propria': 'própria',
    'proprios': 'próprios',
    'proprias': 'próprias',
    'obrigatorio': 'obrigatório',
    'obrigatoria': 'obrigatória',
    'automatico': 'automático',
    'automatica': 'automática',
    'automaticos': 'automáticos',
    'automaticas': 'automáticas',
    'estavel': 'estável',
    'estaveis': 'estáveis',
    'binaria': 'binária',
    'binarias': 'binárias',
    'binario': 'binário',
    'demografica': 'demográfica',
    'demograficas': 'demográficas',
    'demografico': 'demográfico',
    'demograficos': 'demográficos',
    'coincidencia': 'coincidência',
    'obvio': 'óbvio',
    'obvia': 'óbvia',
    'inacessivel': 'inacessível',
    'inacessiveis': 'inacessíveis',
    'disponivel': 'disponível',
    'disponiveis': 'disponíveis',
    'sumario': 'sumário',
    'inicio': 'início',
    'arvore': 'árvore',
    'arvores': 'árvores',
    'regiao': 'região',
    'regioes': 'regiões',
    'industria': 'indústria',
    'industrias': 'indústrias',
    'historia': 'história',
    'historico': 'histórico',
    'historica': 'histórica',
    'grafico': 'gráfico',
    'graficos': 'gráficos',
    'genero': 'gênero',
    'generos': 'gêneros',
    'classico': 'clássico',
    'classica': 'clássica',
    'classicos': 'clássicos',
    'classicas': 'clássicas',
    'ambiguo': 'ambíguo',
    'ambigua': 'ambígua',
    'usuario': 'usuário',
    'usuarios': 'usuários',
    'mensual': 'mensal',
    'mes': 'mês',
    'meses': 'meses',
    'dicionario': 'dicionário',
    'cliente': 'cliente',
    'clientes': 'clientes',
    'trafego': 'tráfego',
    'declinio': 'declínio',
    'exogeno': 'exógeno',
    'exogena': 'exógena',
    'exogenos': 'exógenos',
    'exogenas': 'exógenas',
    'previo': 'prévio',
    'previa': 'prévia',
    'previos': 'prévios',
    'previas': 'prévias',
    'ferramenta': 'ferramenta',
    'analise': 'análise',
    'analises': 'análises',
    'analitico': 'analítico',
    'analitica': 'analítica',
    'analiticos': 'analíticos',
    'analiticas': 'analíticas',
    'matematicamente': 'matematicamente',
    'matematica': 'matemática',
    'matematico': 'matemático',
    'cooperativo': 'cooperativo',
    'auditoria': 'auditoria',
    'auditavel': 'auditável',
    'critica': 'crítica',
    'critico': 'crítico',
    'criticas': 'críticas',
    'criticos': 'críticos',
    'pratica': 'prática',
    'praticas': 'práticas',
    'pratico': 'prático',
    'praticos': 'práticos',
    'consequencia': 'consequência',
    'consequencias': 'consequências',
    'sequencia': 'sequência',
    'sequencias': 'sequências',
    'preferencia': 'preferência',
    'preferencias': 'preferências',
    'eficiencia': 'eficiência',
    'inteligencia': 'inteligência',
    'sinal': 'sinal',
    'sinais': 'sinais',
    'midia': 'mídia',
    'midias': 'mídias',
    'conteudo': 'conteúdo',
    'conteudos': 'conteúdos',
    'mudanca': 'mudança',
    'mudancas': 'mudanças',
    'esporadicos': 'esporádicos',
    'esporadico': 'esporádico',
    'parceria': 'parceria',
    'gratis': 'grátis',
    'navegacao': 'navegação',
    'visualizacao': 'visualização',
    'visualizacoes': 'visualizações',
    'modificacao': 'modificação',
    'simulacao': 'simulação',
    'simulacoes': 'simulações',
    'estabilizou': 'estabilizou',
    'manualmente': 'manualmente',
    'pessima': 'péssima',
    'otima': 'ótima',
    'otimo': 'ótimo',
    'otimos': 'ótimos',
    'otimas': 'ótimas',
    'pessimo': 'péssimo',
    'avancado': 'avançado',
    'avancada': 'avançada',
    'avancou': 'avançou',
    'avancar': 'avançar',
    'aviso': 'aviso',
    'pos': 'pós',
    'pre': 'pré',
    'pos-pandemia': 'pós-pandemia',
    'pre-aula': 'pré-aula',
    'tres-dimensional': 'tridimensional',
    'nao-opcional': 'não-opcional',
    'apos': 'após',
    'agua': 'água',
    'sera': 'será',
    'serao': 'serão',
    'havera': 'haverá',
    'havia': 'havia',
    'tera': 'terá',
    'terao': 'terão',
    'sob': 'sob',
    'sobre': 'sobre',
    'ate': 'até',
    'devera': 'deverá',
    'fica': 'fica',
    'iremos': 'iremos',
    'venha': 'venha',

    # Verbo ser/estar 3a pessoa (cuidado!)
    'esta': 'está',     # quase sempre é verbo
    'estao': 'estão',   # plural
    # 'e' -> 'é' é arriscado — pular
    # 'tem' -> 'tem' (já está) ou 'têm' (plural) — pular

    # Erros típicos do meu draft
    'onica': 'única',
    'onico': 'único',
    'onicos': 'únicos',
    'onicas': 'únicas',
}

# Remove no-ops
SUBS = {o: n for o, n in SUBS.items() if o.lower() != n.lower()}


def preserve_case(original: str, replacement: str) -> str:
    """Aplica a capitalização de `original` em `replacement`.
    - ALL CAPS -> ALL CAPS
    - Capitalized -> Capitalized
    - lowercase -> lowercase
    - misto -> usa replacement como veio
    """
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


def sub_word(pattern: str, replacement: str, text: str) -> tuple[str, int]:
    """Substitui palavra inteira case-insensitive, preservando case."""
    count = 0

    def repl(match):
        nonlocal count
        count += 1
        return preserve_case(match.group(0), replacement)

    regex = re.compile(rf'\b{re.escape(pattern)}\b', re.IGNORECASE)
    new_text, n = regex.subn(repl, text)
    return new_text, n


def fix_file(path: Path) -> int:
    text = path.read_text(encoding='utf-8')
    original = text
    total = 0
    for old, new in SUBS.items():
        text, count = sub_word(old, new, text)
        total += count
    if text != original:
        path.write_text(text, encoding='utf-8')
    return total


def main():
    total_subs = 0
    files_changed = 0
    for tsx in sorted(ROOT.rglob('*.tsx')):
        if 'node_modules' in str(tsx):
            continue
        subs = fix_file(tsx)
        if subs > 0:
            rel = tsx.relative_to(ROOT)
            print(f'  {rel}: {subs} substituicoes')
            total_subs += subs
            files_changed += 1
    print(f'\nTotal: {total_subs} substituicoes em {files_changed} arquivos.')


if __name__ == '__main__':
    main()
