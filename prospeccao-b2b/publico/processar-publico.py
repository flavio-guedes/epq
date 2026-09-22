#!/usr/bin/env python3
"""
PROSPECÇÃO PÚBLICA — Carregador e processador de negócios do Rio de Janeiro.
Usa Node.js para extrair os seeds do JS (b2b-groups/js/data.js) e converte para JSON.
"""
import json
import re
import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path("/Users/mac/HermesWorkspace/prospeccao-b2b")
B2B_GROUPS = Path("/Users/mac/HermesWorkspace/b2b-groups")
SAIDA = BASE / "publico" / "fila-publica.json"
SAIDA_AMOSTRA = BASE / "publico" / "amostra-20.json"
MODELO_MENSAGENS = Path("/Users/mac/HermesWorkspace/automacoes/templates.json")
EXTRATOR_JS = BASE / "publico" / "extrair-seeds.js"

def normalizar_telefone(raw):
    """Normaliza telefone para E.164 Brasil ou None se inválido."""
    if not raw or str(raw).strip() in ('', 'n/a', 'None', 'undefined'):
        return None
    s = str(raw).strip()
    digits = re.sub(r'\D', '', s)
    # Rio DDD é 21
    if len(digits) == 11 and digits.startswith('21'):
        # (21) 9XXXX-XXXX → +55 21 9XXXX-XXXX (11 dígitos com DDD)
        return f"+55{digits}"
    elif len(digits) == 10 and digits.startswith('21'):
        # (21) XXXX-XXXX → +55 21 XXXX-XXXX (fixo, 10 dígitos com DDD)
        return f"+55{digits}"
    elif len(digits) == 11:
        # Outro DDD de 11 dígitos
        return f"+55{digits}"
    elif len(digits) == 10:
        return f"+55{digits}"
    elif len(digits) == 12 and digits.startswith('55'):
        return f"+{digits}"
    return None

def detectar_bairro_nome(nome, descricao, contexto):
    text = f"{nome} {descricao} {contexto}".lower()
    for bairro, regiao in REGIOES_MAP.items():
        if bairro in text:
            return bairro.title()
    return None

def detectar_segmento(nome, descricao, contexto, grupo_nome):
    text = f"{nome} {descricao} {contexto} {grupo_nome}".lower()
    
    if any(w in text for w in ['educação', 'escola', 'matricula', 'admissions', 'ensino', 'turma', 'aula', ' curso ', 'cursos']):
        return "Educação"
    if any(w in text for w in ['beleza', 'estética', 'estetica', 'salão de beleza', 'clinica de beleza', 'spa']):
        return "Beleza e Estética"
    if any(w in text for w in ['startup', 'tecnologia', 'software', 'app', 'digital', 'inovação', 'inovacao', 'saas']):
        return "Tecnologia e Inovação"
    if any(w in text for w in ['marketing', 'publicidade', 'agência', 'agencia', 'tráfego', 'traco', 'branding', 'design']):
        return "Marketing e Publicidade"
    if any(w in text for w in ['saúde', 'medico', 'clinica', 'hospital', ' consultorio', 'odontologia', 'dentista']):
        return "Saúde"
    if any(w in text for w in ['alimentação', 'restaurante', 'food', 'comida', 'bar', 'cantina', 'padaria']):
        return "Alimentação"
    if any(w in text for w in ['construção', 'arquitetura', 'engenharia', 'reforma', 'design de interiores']):
        return "Construção e Design"
    if any(w in text for w in ['venda', 'varejo', 'loja', 'shopping', 'e-commerce', 'comércio', 'comercio']):
        return "Comércio e Varejo"
    if any(w in text for w in ['advocacia', 'juridico', 'direito', 'lawyer', 'law firm']):
        return "Jurídico"
    if any(w in text for w in ['consultoria', 'consultor', 'gestão', 'gestao', 'gestor']):
        return "Consultoria"
    if any(w in text for w in ['musica', 'show', 'evento', 'cultura', 'arte', 'teatro', 'musica']):
        return "Cultura e Eventos"
    if any(w in text for w in ['finança', 'banco', 'seguro', 'investimento', 'fintech']):
        return "Finanças"
    if any(w in text for w in ['imobiliário', 'imobiliario', 'imoveis', 'imóveis', 'correto', 'corretor', 'aluguel']):
        return "Imobiliário"
    return "Serviços Gerais"

# Regiões mapping (bairro → região)
REGIOES_MAP = {
    "méier": "Zona Norte",
    "cachambi": "Zona Norte",
    "tijuca": "Zona Norte",
    "vila isabel": "Zona Norte",
    "maracanã": "Zona Norte",
    "são cristóvão": "Zona Norte",
    "mangueira": "Zona Norte",
    "benfica": "Zona Norte",
    "andaraí": "Zona Norte",
    "praça da bandeira": "Zona Norte",
    "pilares": "Zona Norte",
    "del castilho": "Zona Norte",
    "engenho novo": "Zona Norte",
    "engenho de dentro": "Zona Norte",
    "todos os santos": "Zona Norte",
    "ilha do governador": "Zona Norte",
    "centro": "RJ Capital",
    "santa teresa": "RJ Capital",
    "lapa": "RJ Capital",
    "cidade nova": "RJ Capital",
    "santo cristo": "RJ Capital",
    "gamboa": "RJ Capital",
    "caju": "RJ Capital",
    "saúde": "RJ Capital",
    "praça xv": "RJ Capital",
    "bastos": "RJ Capital",
    "laranjeiras": "RJ Capital",
    "ipanema": "Zona Sul",
    "leblon": "Zona Sul",
    "copacabana": "Zona Sul",
    "botafogo": "Zona Sul",
    "flamengo": "Zona Sul",
    "urca": "Zona Sul",
    "catete": "Zona Sul",
    "glória": "Zona Sul",
    "barra": "Zona Oeste",
    "recreio": "Zona Oeste",
    "duque de caxias": "Baixada Fluminense",
    "nova iguaçu": "Baixada Fluminense",
    "belford roxo": "Baixada Fluminense",
    "são joão de meriti": "Baixada Fluminense",
    "mesquita": "Baixada Fluminense",
    "niterói": "Baixada Fluminense",
    "são gonçalo": "Baixada Fluminense",
    "itaboraí": "Baixada Fluminense",
    "japeri": "Baixada Fluminense",
    "mage": "Baixada Fluminense",
}

def extrair_seeds_node():
    """Extrai os seeds usando Node.js e retorna dict {grupos, leads, oportunidades}."""
    if not EXTRATOR_JS.exists():
        print(f"⚠ Extrator Node não encontrado: {EXTRATOR_JS}")
        return None
    
    try:
        result = subprocess.run(
            ['node', str(EXTRATOR_JS)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(BASE)
        )
        if result.returncode != 0:
            print(f"⚠ Node retornou erro: {result.stderr}")
            return None
        output = json.loads(result.stdout)
        return output
    except subprocess.TimeoutExpired:
        print("⚠ Node iniou (timeout 30s)")
        return None
    except Exception as e:
        print(f"⚠ Erro ao executar Node: {e}")
        return None

def extrair_seeds_regex(content):
    """Parser regex fallback para extração dos seeds do JS."""
    seed_grupos = []
    seed_leads = []
    seed_oportunidades = []
    
    # Regex para objetos JS (sem aspas nos nomes de campos)
    # Padrão: { campo: "valor", ... }
    
    def parse_js_obj(obj_str):
        """Parse um objeto JavaScript simples para dict Python."""
        result = {}
        # Campos com aspas: "campo": "valor"
        for m in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', obj_str):
            result[m.group(1)] = m.group(2)
        # Campos sem aspas: campo: "valor" ou campo: valor
        for m in re.finditer(r'([a-zA-Z_]\w*)\s*:\s*"([^"]*)"', obj_str):
            if m.group(1) not in result:
                result[m.group(1)] = m.group(2)
        # Campos numéricos: campo: 123
        for m in re.finditer(r'([a-zA-Z_]\w*)\s*:\s*(\d+)', obj_str):
            if m.group(1) not in result:
                result[m.group(1)] = int(m.group(2))
        # Campos booleanos: campo: true/false
        for m in re.finditer(r'([a-zA-Z_]\w*)\s*:\s*(true|false)', obj_str):
            if m.group(1) not in result:
                result[m.group(1)] = m.group(2) == 'true'
        return result
    
    # Extrair arrays: const SEED_GRUPS = [ ... ]
    for match in re.finditer(r'(?:const|let|var)\s+SEED_GRUPS\s*=\s*\[(.*?)\]\s*;', content, re.DOTALL):
        array_content = match.group(1)
        # Extrair objetos individuais
        for obj_match in re.finditer(r'\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', array_content):
            obj_str = '{' + obj_match.group(1) + '}'
            try:
                obj = parse_js_obj(obj_str)
                if 'id' in obj:
                    seed_grupos.append(obj)
            except:
                pass
    
    # SEED_LEADS
    for match in re.finditer(r'(?:const|let|var)\s+SEED_LEADS\s*=\s*\[(.*?)\]\s*;', content, re.DOTALL):
        array_content = match.group(1)
        for obj_match in re.finditer(r'\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', array_content):
            obj_str = '{' + obj_match.group(1) + '}'
            try:
                obj = parse_js_obj(obj_str)
                if 'id' in obj:
                    seed_leads.append(obj)
            except:
                pass
    
    # SEED_OPORTUNIDADES
    for match in re.finditer(r'(?:const|let|var)\s+SEED_OPORTUNIDADES\s*=\s*\[(.*?)\]\s*;', content, re.DOTALL):
        array_content = match.group(1)
        for obj_match in re.finditer(r'\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', array_content):
            obj_str = '{' + obj_match.group(1) + '}'
            try:
                obj = parse_js_obj(obj_str)
                if 'id' in obj:
                    seed_oportunidades.append(obj)
            except:
                pass
    
    return {
        'grupos': seed_grupos,
        'leads': seed_leads,
        'oportunidades': seed_oportunidades
    }

def carregar_seeds():
    """Carrega os seeds da melhor forma disponível."""
    # 1. Tenta Node.js
    seeds_node = extrair_seeds_node()
    if seeds_node and (seeds_node.get('grupos') or seeds_node.get('leads')):
        print(f"✓ Seeds extraídos via Node: {len(seeds_node.get('grupos',[]))} grupos, {len(seeds_node.get('leads',[]))} leads, {len(seeds_node.get('oportunidades',[]))} oportunidades")
        return seeds_node
    
    # 2. Parser regex
    print("⚠ Node não disponível ou falhou. Usando parser regex...")
    for js_file in [B2B_GROUPS / "js" / "data.js", B2B_GROUPS / "js" / "seed-inline.js"]:
        if js_file.exists():
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            seeds = extrair_seeds_regex(content)
            if seeds['grupos'] or seeds['leads']:
                print(f"✓ Parser regex extraiu: {len(seeds['grupos'])} grupos, {len(seeds['leads'])} leads")
                return seeds
    
    print("⚠ Nenhum seed encontrado")
    return {'grupos': [], 'leads': [], 'oportunidades': []}

def montar_registro_publico(grupo, lead=None, oportunidade=None, templates=None):
    """Monta registro PROSPECÇÃO PÚBLICA."""
    agora = datetime.now().isoformat()
    
    nome_negocio = lead.get('empresa') if lead else grupo.get('nome', '')
    telefone_raw = lead.get('telefone') if lead else None
    telefone_normalizado = normalizar_telefone(telefone_raw) if telefone_raw else None
    
    regiao = grupo.get('regiao', '')
    bairro = None
    if regiao:
        parts = regiao.split(',')
        if len(parts) > 1:
            bairro = parts[0].strip()
    if not bairro and lead:
        bairro = detectar_bairro_nome(lead.get('nome',''), lead.get('empresa',''), lead.get('contexto',''))
    
    segmento = lead.get('segmento') if lead else grupo.get('segmento', '')
    if not segmento and lead:
        segmento = detectar_segmento(
            lead.get('nome',''), lead.get('empresa',''), 
            lead.get('contexto',''), grupo.get('nome','')
        )
    
    mensagem = ""
    mensagem_tipo = ""
    if templates and lead:
        template = templates.get('outreach', {})
        mensagem = template.get('text', '')
        mensagem_tipo = template.get('id', 'outreach')
    
    return {
        "id": lead.get('id') if lead else f"pub-{grupo.get('id','grupo')}-{datetime.now().strftime('%H%M%S')}",
        "nome_negocio": nome_negocio,
        "telefone": telefone_raw,
        "telefone_normalizado": telefone_normalizado,
        "regiao": regiao,
        "bloco": bairro,
        "bairro": bairro,
        "segmento": segmento or "Não classificado",
        "origem": "b2b-groups",
        "arquivo_origem": str(B2B_GROUPS / "js" / "data.js"),
        "status": "NOVO",
        "mensagem": mensagem,
        "mensagem_tipo": mensagem_tipo,
        "data_processamento": agora,
        "grupo_origem": grupo.get('nome', ''),
        "categoria": grupo.get('categoria', ''),
        "cidade": grupo.get('cidade', 'Rio de Janeiro'),
        "observacoes": lead.get('observacoes', '') if lead else ''
    }

def filtrar_estrutura_regioes(registros):
    regioes = {}
    for r in registros:
        reg = r.get('regiao', 'Não classificado')
        bairro = r.get('bairro') or r.get('bloco') or 'Não identificado'
        
        if reg not in regioes:
            regioes[reg] = {'blocos': set(), 'total': 0, 'validos': 0}
        regioes[reg]['blocos'].add(bairro)
        regioes[reg]['total'] += 1
        if r['status'] != 'INVALIDO' and r['telefone_normalizado']:
            regioes[reg]['validos'] += 1
    
    resultado = {}
    for reg, data in sorted(regioes.items()):
        resultado[reg] = {
            'blocos': sorted(data['blocos']),
            'total_negocios': data['total'],
            'telefones_validos': data['validos']
        }
    return resultado

def amostra_20_registros(registros):
    if len(registros) <= 20:
        return registros
    
    por_regiao = {}
    for r in registros:
        reg = r.get('regiao', 'Não classificado')
        if reg not in por_regiao:
            por_regiao[reg] = []
        por_regiao[reg].append(r)
    
    amostra = []
    for reg, lista in por_regiao.items():
        alvo = min(20 // len(por_regiao), len(lista))
        amostra.extend(lista[:alvo])
    
    if len(amostra) < 20:
        restantes = [r for r in registros if r not in amostra]
        amostra.extend(restantes[:20 - len(amostra)])
    
    return amostra

def main():
    print("=== PROSPECÇÃO PÚBLICA — Processamento ===")
    
    # Carregar templates
    templates = {}
    if MODELO_MENSAGENS.exists():
        with open(MODELO_MENSAGENS, encoding='utf-8') as f:
            templates = json.load(f)
        print(f"✓ Modelo de mensagens carregado: {len(templates)} templates")
    else:
        print("⚠ Modelo de mensagens não encontrado")
    
    # Carregar seeds
    seeds = carregar_seeds()
    grupos = {g['id']: g for g in seeds.get('grupos', [])}
    leads_raw = {l['id']: l for l in seeds.get('leads', [])}
    oportunidades = {o['id']: o for o in seeds.get('oportunidades', [])}
    
    print(f"✓ Grupos carregados: {len(grupos)}")
    print(f"✓ Leads carregados: {len(leads_raw)}")
    print(f"✓ Oportunidades carregadas: {len(oportunidades)}")
    
    # Montar registros
    registros = []
    seen_ids = set()
    telefones_validos = set()
    duplicados = []
    
    # Processar leads com telefone — prioridade
    for l_id, lead in leads_raw.items():
        grupo_id = lead.get('grupo_id')
        grupo_nome = lead.get('grupo_nome')
        grupo = None
        if grupo_id and grupo_id in grupos:
            grupo = grupos[grupo_id]
        elif grupo_nome:
            for g in grupos.values():
                if g.get('nome') == grupo_nome:
                    grupo = g
                    break
        if not grupo:
            continue
        
        registro = montar_registro_publico(grupo, lead, None, templates)
        
        if registro['telefone_normalizado']:
            if registro['telefone_normalizado'] in telefones_validos:
                duplicados.append(registro['id'])
                registro['status'] = 'INVALIDO'
                registro['observacoes'] = (registro['observacoes'] + '; DUPLICADO').strip('; ')
            else:
                telefones_validos.add(registro['telefone_normalizado'])
        elif registro['telefone']:
            registro['status'] = 'INVALIDO'
            registro['observacoes'] = (registro['observacoes'] + '; SEM WA VALIDO').strip('; ')
        
        if registro['id'] in seen_ids:
            registro['status'] = 'INVALIDO'
            registro['observacoes'] = (registro['observacoes'] + '; DUPLICADO ID').strip('; ')
        
        seen_ids.add(registro['id'])
        registros.append(registro)
    
    # Grupos sem leads como registros simples
    for g_id, grupo in grupos.items():
        if any(l.get('grupo_id') == g_id for l in leads_raw.values()):
            continue
        registro = montar_registro_publico(grupo, None, None, templates)
        registro['observacoes'] = 'Sem lead associado ainda'
        if registro['id'] in seen_ids:
            continue
        seen_ids.add(registro['id'])
        registros.append(registro)
    
    # Estatísticas
    total = len(registros)
    validos = sum(1 for r in registros if r['status'] != 'INVALIDO' and r['telefone_normalizado'])
    invalidos = sum(1 for r in registros if r['status'] == 'INVALIDO')
    com_mensagem = sum(1 for r in registros if r['mensagem'])
    por_regiao = filtrar_estrutura_regioes(registros)
    amostra = amostra_20_registros(registros)
    
    print(f"\n=== ESTATÍSTICAS GERAIS ===")
    print(f"Total de registros: {total}")
    print(f"Telefones válidos (E.164): {validos}")
    print(f"Telefones inválidos/sem WA: {invalidos}")
    print(f"Duplicados detectados: {len(duplicados)}")
    print(f"Mensagens prontas (RASCUNHO): {com_mensagem}")
    
    print(f"\n=== ESTRUTURA DE REGIÕES ===")
    for reg, data in por_regiao.items():
        print(f"  {reg}: {data['total_negocios']} negócios, {data['telefones_validos']} tel válidos, blocos: {', '.join(data['blocos'])}")
    
    print(f"\n=== AMOSTRA DE 20 REGISTROS ===")
    print(f"Registros na amostra: {len(amostra)}")
    
    # Salvar dados completos
    os.makedirs(SAIDA.parent, exist_ok=True)
    
    dados_completos = {
        "meta": {
            "projeto": "PROSPECCAO PUBLICA",
            "criado_em": datetime.now().isoformat(),
            "total_registros": total,
            "validos": validos,
            "invalidos": invalidos,
            "duplicados": len(duplicados),
            "com_mensagem": com_mensagem,
            "separacao_obrigatoria": "PROSPECCAO PUBLICA NÃO MISTURADO COM EPQ/B2B FLAVIO"
        },
        "estrutura_regioes": por_regiao,
        "estatisticas": {
            "total": total,
            "validos": validos,
            "invalidos": invalidos,
            "duplicados": len(duplicados),
            "mensagens_prontas": com_mensagem
        },
        "registros": registros,
        "amostra_20": amostra
    }
    
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(dados_completos, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Dados salvos em: {SAIDA}")
    
    # Salvar amostra
    with open(SAIDA_AMOSTRA, 'w', encoding='utf-8') as f:
        json.dump({
            "meta": {
                "projeto": "PROSPECCAO PUBLICA — AMOSTRA 20",
                "descricao": "Amostra de 20 registros para teste do painel",
                "criado_em": datetime.now().isoformat(),
                "total_na_amostra": len(amostra)
            },
            "registros": amostra
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Amostra de 20 salvos em: {SAIDA_AMOSTRA}")
    return 0

if __name__ == '__main__':
    exit(main())
