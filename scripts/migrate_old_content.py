import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = os.path.expanduser('~/.hermes/google_token.json')
creds = Credentials.from_authorized_user_file(token_path, [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata'
])
service = build('drive', 'v3', credentials=creds)
root_id = '1z6Y3JwfKfupA95KT_Il_X8xs5vqfMNeJ'

def list_children(parent_id):
    results = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            fields="nextPageToken, files(id,name,mimeType)",
            pageToken=page_token,
            pageSize=1000
        ).execute()
        results.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return results

def move_file(file_id, new_parent_id):
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))
    service.files().update(fileId=file_id, addParents=new_parent_id, removeParents=previous_parents, fields='id,parents').execute()

def create_folder(name, parent_id):
    metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    folder = service.files().create(body=metadata, fields='id,name').execute()
    return folder['id']

# Find all jobs in Concursos editoria
concursos_id = '1usMncTFL0PPiz4Jg42nScI6L6GFt-R1j'
formatos = {f['name']: f['id'] for f in list_children(concursos_id) if f['mimeType'] == 'application/vnd.google-apps.folder'}

# Build job map: categoria/format -> job folder id
job_map = {}
for formato_name, formato_id in formatos.items():
    cats = list_children(formato_id)
    for cat in cats:
        if cat['mimeType'] == 'application/vnd.google-apps.folder':
            jobs = list_children(cat['id'])
            for job in jobs:
                if job['mimeType'] == 'application/vnd.google-apps.folder':
                    job_map[(cat['name'], formato_name)] = job['id']

print(f'Jobs encontrados: {len(job_map)}')

# Create month folders in all jobs
months = ['08 - Agosto', '09 - Setembro', '10 - Outubro', '11 - Novembro', '12 - Dezembro']
for (cat, fmt), job_id in job_map.items():
    final_id = None
    for child in list_children(job_id):
        if child['name'] == '03 - Arquivo Finalizado':
            final_id = child['id']
            break
    if not final_id:
        continue
    existing = {c['name'] for c in list_children(final_id)}
    for m in months:
        if m not in existing:
            create_folder(m, final_id)

print('Pastas de meses criadas.')

# Migrate old Social Media content
old_social_id = '1eWMsO0r0a5PhYN7DVp-iCaZsRjqny1O7'
old_social = list_children(old_social_id)

# Mapping old folders to new jobs
migrations = []

# Cards folder -> feed/carrossel/stories jobs
cards_id = next((f['id'] for f in old_social if f['name'] == '01 - Cards'), None)
if cards_id:
    for item in list_children(cards_id):
        migrations.append((item, 'social', 'Feed'))
        migrations.append((item, 'social', 'Stories'))
        migrations.append((item, 'social', 'Carrossel'))

# Carrosseis -> Carrossel jobs
carrosseis_id = next((f['id'] for f in old_social if f['name'] == '02 - Carrosseis'), None)
if carrosseis_id:
    for item in list_children(carrosseis_id):
        migrations.append((item, 'social', 'Carrossel'))

# Videos -> Reels jobs
videos_id = next((f['id'] for f in old_social if f['name'] == '03 - Videos'), None)
if videos_id:
    for item in list_children(videos_id):
        migrations.append((item, 'social', 'Reels'))

# Publicados -> OLD folders
publicados_id = next((f['id'] for f in old_social if f['name'] == '04 - Publicados'), None)
if publicados_id:
    for item in list_children(publicados_id):
        migrations.append((item, None, 'OLD'))

# Aprovados -> Reference folders
aprovados_id = next((f['id'] for f in old_social if f['name'] == '03 - Aprovados'), None)
if aprovados_id:
    for item in list_children(aprovados_id):
        migrations.append((item, 'reference', None))

# Execute migrations
for item, categoria, formato in migrations:
    if formato == 'OLD':
        # Move to OLD folder of first social job
        target_job = job_map.get(('social', 'Stories'))
        if target_job:
            old_id = next((c['id'] for c in list_children(target_job) if c['name'] == '03 - Arquivo Finalizado'), None)
            if old_id:
                old_folder = next((c['id'] for c in list_children(old_id) if c['name'] == 'OLD'), None)
                if old_folder:
                    try:
                        move_file(item['id'], old_folder)
                    except Exception as e:
                        print(f'Erro ao mover {item["name"]} para OLD: {e}')
    elif categoria == 'reference':
        # Move to reference folder of first job
        target_job = job_map.get(('social', 'Stories'))
        if target_job:
            apoio_id = next((c['id'] for c in list_children(target_job) if c['name'] == '01 - Apoio'), None)
            if apoio_id:
                ref_id = next((c['id'] for c in list_children(apoio_id) if c['name'] == '01 - Referencia'), None)
                if ref_id:
                    try:
                        move_file(item['id'], ref_id)
                    except Exception as e:
                        print(f'Erro ao mover {item["name"]} para Referencia: {e}')
    else:
        target_job = job_map.get((categoria, formato))
        if target_job:
            apoio_id = next((c['id'] for c in list_children(target_job) if c['name'] == '01 - Apoio'), None)
            if apoio_id:
                ref_id = next((c['id'] for c in list_children(apoio_id) if c['name'] == '01 - Referencia'), None)
                if ref_id:
                    try:
                        move_file(item['id'], ref_id)
                    except Exception as e:
                        print(f'Erro ao mover {item["name"]}: {e}')

print('Migração concluída!')
