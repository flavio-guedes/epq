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

# 1. Create month folders in all jobs
print('Criando pastas de meses...')
months = ['08 - Agosto', '09 - Setembro', '10 - Outubro', '11 - Novembro', '12 - Dezembro']

# Get all jobs under Concursos
concursos_id = '1usMncTFL0PPiz4Jg42nScI6L6GFt-R1j'
formatos = list_children(concursos_id)
jobs = []
for fmt in formatos:
    if fmt['mimeType'] == 'application/vnd.google-apps.folder':
        cats = list_children(fmt['id'])
        for cat in cats:
            if cat['mimeType'] == 'application/vnd.google-apps.folder':
                jobs.extend(list_children(cat['id']))

for job in jobs:
    if job['mimeType'] == 'application/vnd.google-apps.folder':
        final_id = next((c['id'] for c in list_children(job['id']) if c['name'] == '03 - Arquivo Finalizado'), None)
        if final_id:
            existing = {c['name'] for c in list_children(final_id)}
            for m in months:
                if m not in existing:
                    create_folder(m, final_id)
                    print(f'Criado {m} em {job["name"]}')

# 2. Migrate old Social Media content
print('\nMigrando conteúdo de Social Media...')
old_social_id = '1eWMsO0r0a5PhYN7DVp-iCaZsRjqny1O7'
old_items = list_children(old_social_id)

# Get reference to jobs
social_stories_job = None
social_feed_job = None
social_carrossel_job = None
social_reels_job = None

for ed in list_children(root_id):
    if ed['name'] == 'Concursos':
        for fmt in list_children(ed['id']):
            if fmt['name'] == 'Stories':
                for cat in list_children(fmt['id']):
                    if cat['name'] == 'social':
                        social_stories_job = next((f['id'] for f in list_children(cat['id']) if f['name'] == 'EPQ_social_stories_1080x1920'), None)
            if fmt['name'] == 'Feed':
                for cat in list_children(fmt['id']):
                    if cat['name'] == 'social':
                        social_feed_job = next((f['id'] for f in list_children(cat['id']) if f['name'] == 'EPQ_social_feed_1080x1080'), None)
            if fmt['name'] == 'Carrossel':
                for cat in list_children(fmt['id']):
                    if cat['name'] == 'social':
                        social_carrossel_job = next((f['id'] for f in list_children(cat['id']) if f['name'] == 'EPQ_social_carrossel_1080x1080'), None)
            if fmt['name'] == 'Reels':
                for cat in list_children(fmt['id']):
                    if cat['name'] == 'social':
                        social_reels_job = next((f['id'] for f in list_children(cat['id']) if f['name'] == 'EPQ_social_reels_1080x1920'), None)

def get_ref_folder(job_id):
    apoio = next((c['id'] for c in list_children(job_id) if c['name'] == '01 - Apoio'), None)
    if apoio:
        ref = next((c['id'] for c in list_children(apoio) if c['name'] == '01 - Referencia'), None)
        return ref
    return None

def get_old_folder(job_id):
    final = next((c['id'] for c in list_children(job_id) if c['name'] == '03 - Arquivo Finalizado'), None)
    if final:
        old = next((c['id'] for c in list_children(final) if c['name'] == 'OLD'), None)
        return old
    return None

# Migrate each old folder
for item in old_items:
    if item['mimeType'] != 'application/vnd.google-apps.folder':
        continue
    ref = None
    if item['name'] in ['01 - Cards', '02 - Carrosseis', '03 - Videos', '00 - Planejamento', '00 - PLanejamento']:
        # These go to reference
        if social_stories_job:
            ref = get_ref_folder(social_stories_job)
    elif item['name'] in ['04 - Publicados']:
        # These go to OLD
        if social_stories_job:
            old = get_old_folder(social_stories_job)
            if old:
                try:
                    move_file(item['id'], old)
                    print(f'Movido {item["name"]} → OLD')
                except Exception as e:
                    print(f'Erro: {e}')
    elif item['name'] == '03 - Aprovados':
        if social_stories_job:
            ref = get_ref_folder(social_stories_job)
    
    if ref:
        try:
            move_file(item['id'], ref)
            print(f'Movido {item["name"]} → Referencia')
        except Exception as e:
            print(f'Erro ao mover {item["name"]}: {e}')

# 3. Migrate old Anuncios if any
print('\nMigrando conteúdo de Anúncios...')
old_ads_id = '1EKaz0tElLGA_bneNehxu4Ju8dK6HUs2w'
for item in list_children(old_ads_id):
    if item['mimeType'] != 'application/vnd.google-apps.folder':
        continue
    # Find first ads job
    ads_job = None
    for ed in list_children(root_id):
        if ed['name'] == 'Concursos':
            for fmt in list_children(ed['id']):
                if fmt['name'] == 'Ads':
                    for cat in list_children(fmt['id']):
                        if cat['name'] == 'ads':
                            jobs = list_children(cat['id'])
                            if jobs:
                                ads_job = jobs[0]['id']
    if ads_job:
        ref = get_ref_folder(ads_job)
        if ref:
            try:
                move_file(item['id'], ref)
                print(f'Movido {item["name"]} → Ads Referencia')
            except Exception as e:
                print(f'Erro: {e}')

print('\nMigração concluída!')
