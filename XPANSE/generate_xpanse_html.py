import json
import os
import re
import openpyxl

def extract_employees_list(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    
    employees = []
    for row in rows:
        if not row or not row[0] or str(row[0]).strip().lower() == 'nome':
            continue
        try:
            nome = str(row[0]).strip()
            idade = int(row[1])
            regime = str(row[2]).strip() if len(row) > 2 and row[2] else 'CLT'
            employees.append({
                'name': nome,
                'age': idade,
                'regime': regime
            })
        except:
            continue
    employees.sort(key=lambda x: x['name'].lower())
    return employees

def map_company_name(name):
    n = name.strip().lower()
    if 'amil' in n and 'bronze' in n: return 'Amil Bronze'
    if 'linha amil' in n: return 'Linha Amil'
    if 'amil selecionada' in n: return 'Amil Selecionada'
    if 'bradesco' in n: return 'Bradesco'
    if 'hapvida' in n and 'smart' in n: return 'HapVida Smart'
    if 'hapvida' in n and 'advance' in n: return 'HapVida Advance'
    if 'porto' in n and 'linha' in n: return 'Linha Porto Sa\xfade'
    if 'porto seguro' in n: return 'Porto Seguro'
    if 'unimed' in n: return 'Seguros Unimed'
    if 'sulam' in n or 'sul am' in n: return 'SulAm\xe9rica'
    return name

def format_reembolso_list(reembolso_dict, plans_count):
    if not reembolso_dict:
        return ["-"] * plans_count
    ps_list = reembolso_dict.get("PS", [])
    eletiva_list = reembolso_dict.get("eletiva", [])
    
    formatted = []
    for idx in range(plans_count):
        ps_val = ps_list[idx] if idx < len(ps_list) else None
        eletiva_val = eletiva_list[idx] if idx < len(eletiva_list) else None
        
        parts = []
        if ps_val is not None and ps_val != "**" and ps_val != "***":
            if isinstance(ps_val, (int, float)):
                parts.append(f"Urgência: R$ {ps_val:.2f}".replace('.', ','))
            else:
                parts.append(f"Urgência: {ps_val}")
                
        if eletiva_val is not None and eletiva_val != "**" and eletiva_val != "***":
            if isinstance(eletiva_val, (int, float)):
                parts.append(f"Eletiva: R$ {eletiva_val:.2f}".replace('.', ','))
            else:
                parts.append(f"Eletiva: {eletiva_val}")
                
        if parts:
            formatted.append(" / ".join(parts))
        else:
            formatted.append("-")
    return formatted

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to scratch assets
    scratch_dir = r"C:\Users\Danilo\.gemini\antigravity-ide\brain\403bb0ee-8c5e-4b96-8da1-c977795af698\scratch"
    
    # Load JSON data
    with open(os.path.join(base_dir, 'xpanse_data.json'), encoding='utf-8') as f:
        data = json.load(f)
        
    vidas_data = data['vidas']
    total_vidas = vidas_data['total_vidas']
    idades_path = os.path.join(base_dir, 'Idades.xlsx')
    employees_list = extract_employees_list(idades_path)
    
    # Load Salus assets from scratch
    with open(os.path.join(scratch_dir, "salus_logos.json"), encoding='utf-8') as f:
        logos_dict = json.load(f)
    with open(os.path.join(scratch_dir, "salus_metadata.json"), encoding='utf-8') as f:
        metadata_dict = json.load(f)
    with open(os.path.join(scratch_dir, "salus_style.css"), encoding='utf-8') as f:
        style_content = f.read()
    with open(os.path.join(scratch_dir, "salus_body.html"), encoding='utf-8') as f:
        body_content = f.read()
    with open(os.path.join(scratch_dir, "salus_script_full.js"), encoding='utf-8') as f:
        script_content = f.read()
        
    # Map each company in xpanse_data to COMPANIES structure for JS
    companies_list = []
    for plan in data['planos']:
        name = plan['company']
        mapped_name = map_company_name(name)
        
        logo = logos_dict.get(mapped_name, "")
        meta = metadata_dict.get(mapped_name, {})
        
        # Prepend ../ to relative rede PDF file paths
        redes = []
        for r in meta.get("redes", []):
            file_path = r.get("file", "")
            if file_path and not file_path.startswith("../") and not file_path.startswith("http"):
                file_path = "../" + file_path
            redes.append({
                "label": r.get("label", ""),
                "file": file_path
            })
            
        # Format sections
        sections = []
        for sec in plan['sections']:
            new_tables = []
            for tbl in sec['tables']:
                plans_count = len(tbl['plans'])
                
                # Format reembolso list
                reembolso_list = format_reembolso_list(tbl.get('reembolso'), plans_count)
                
                # Format acomodacao list
                acom_list = []
                for a in tbl.get('acomodacao', []):
                    if a is None:
                        acom_list.append("-")
                    elif 'apart' in a.lower():
                        acom_list.append("Apt.")
                    elif 'enferm' in a.lower() or 'enf' in a.lower():
                        acom_list.append("Enf.")
                    else:
                        acom_list.append(a)
                        
                # Ensure age data exists and maps correctly
                age_data = []
                for r in tbl.get('age_data', []):
                    age_data.append({
                        'label': r['label'].strip(),
                        'values': r['values']
                    })
                    
                new_tables.append({
                    'plans': tbl['plans'],
                    'acomodacao': acom_list,
                    'abrangencia': tbl.get('abrangencia', ['Nacional'] * plans_count),
                    'reembolso': reembolso_list,
                    'total': tbl.get('total'),
                    'age_data': age_data
                })
            sections.append({
                'name': sec['name'],
                'tables': new_tables
            })
            
        companies_list.append({
            'company': name,
            'logo': logo,
            'color': meta.get('color', '#30569c'),
            'domain': meta.get('domain', ''),
            'resumo': meta.get('resumo', ''),
            'redes': redes,
            'diferenciais': meta.get('diferenciais', []),
            'sections': sections
        })
        
    # Serialize companies to JSON for JS embedding
    companies_js_json = json.dumps(companies_list, ensure_ascii=False, indent=2)
    
    # 1. Update scripts with dynamic data
    js_code = script_content
    
    # Replace COMPANIES placeholder
    lives_data_json = json.dumps(vidas_data, ensure_ascii=False, indent=2)
    employees_json = json.dumps(employees_list, ensure_ascii=False, indent=2)
    js_code = js_code.replace("const COMPANIES = [];", f"const COMPANIES = {companies_js_json};\nconst LIVES_DATA = {lives_data_json};\nconst EMPLOYEES = {employees_json};")
    
    # Make lives count dynamic in JS
    js_code = js_code.replace("66 vidas", f"{total_vidas} vidas")
    js_code = js_code.replace("66 Vidas", f"{total_vidas} Vidas")
    
    # 2. Update body HTML with dynamic data
    body_html = body_content
    # Use regex to replace the header paragraph cleanly regardless of bullet characters
    body_html = re.sub(r'<p>\s*Grupo Salus.*?</p>', f'<p>XPANSE &nbsp;&bull;&nbsp; {total_vidas} vidas &nbsp;&bull;&nbsp; 2026</p>', body_html)
    # Fix the word "Saúde" in the header title if it has a replacement char
    body_html = body_html.replace("Sa\ufffdde", "Sa\xfade")
    
    # Create index.html template
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Estudo de Planos de Saúde – XPANSE | FBN RE</title>
  <meta name="description" content="Comparativo de planos de saúde empresariais para a XPANSE. Compare coberturas, faixas etárias e preços de Amil, HapVida, Porto Seguro, SulAmérica, Bradesco e Unimed." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />

  <style>
    {style_content}
  </style>
</head>
<body>
  {body_html}

  <script>
    {js_code}
  </script>
</body>
</html>
'''
    
    out_path = os.path.join(base_dir, 'xpanse_index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML saved to {out_path}")

if __name__ == '__main__':
    main()
