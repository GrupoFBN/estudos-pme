import zipfile
import xml.etree.ElementTree as ET
import os
import shutil

z = zipfile.ZipFile('ESTUDOS CONVÊNIOS MÉDICOS - GRUPO SALUS.xlsx')
namespaces = {
    'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships'
}

wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
sheets = {sheet.attrib['sheetId']: sheet.attrib['name'] for sheet in wb_tree.findall('.//ns:sheet', namespaces)}
wb_rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
rel_to_sheet = {rel.attrib['Id']: rel.attrib['Target'] for rel in wb_rels.findall('.//pr:Relationship', namespaces)}

sheet_images = {}
for sheet_element in wb_tree.findall('.//ns:sheet', namespaces):
    r_id = sheet_element.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
    sheet_name = sheet_element.attrib['name']
    sheet_target = rel_to_sheet[r_id]
    sheet_rels_path = f'xl/worksheets/_rels/{os.path.basename(sheet_target)}.rels'
    if sheet_rels_path not in z.namelist(): continue
    
    s_rels = ET.fromstring(z.read(sheet_rels_path))
    for s_rel in s_rels.findall('.//pr:Relationship', namespaces):
        if 'drawing' in s_rel.attrib['Type']:
            draw_target = s_rel.attrib['Target']
            draw_path = f'xl/drawings/{os.path.basename(draw_target)}'
            draw_rels_path = f'xl/drawings/_rels/{os.path.basename(draw_target)}.rels'
            
            if draw_rels_path not in z.namelist(): continue
            d_rels = ET.fromstring(z.read(draw_rels_path))
            draw_rel_dict = {rel.attrib['Id']: rel.attrib['Target'] for rel in d_rels.findall('.//pr:Relationship', namespaces)}
            
            draw_tree = ET.fromstring(z.read(draw_path))
            for pic in draw_tree.findall('.//xdr:pic', namespaces):
                blip = pic.find('.//a:blip', namespaces)
                if blip is not None:
                    embed_id = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if embed_id and embed_id in draw_rel_dict:
                        media_target = draw_rel_dict[embed_id]
                        media_path = f'xl/media/{os.path.basename(media_target)}'
                        if sheet_name not in sheet_images:
                            sheet_images[sheet_name] = []
                        sheet_images[sheet_name].append(media_path)

out_dir = 'extracted_images'
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

for sheet, images in sheet_images.items():
    clean_sheet = "".join(c if c.isalnum() else "_" for c in sheet)
    sheet_dir = os.path.join(out_dir, clean_sheet)
    os.makedirs(sheet_dir)
    
    unique_images = list(set(images))
    unique_images.sort(key=lambda x: z.getinfo(x).file_size, reverse=True)
    
    for i, media_path in enumerate(unique_images):
        ext = os.path.splitext(media_path)[1]
        out_name = f'{i+1:03d}_{os.path.basename(media_path)}'
        with open(os.path.join(sheet_dir, out_name), 'wb') as f:
            f.write(z.read(media_path))
    
print(f'Extracted images to {out_dir}')
