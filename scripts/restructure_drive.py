import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def create_folder(name, parent_id):
    metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    folder = service.files().create(body=metadata, fields='id,name').execute()
    return folder['id']

def move_file(file_id, new_parent_id):
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))
    service.files().update(fileId=file_id, addParents=new_parent_id, removeParents=previous_parents, fields='id,parents').execute()

print('Criando estrutura de editorias e formatos...')
editorias = ['Concursos', 'Dicas de Estudo', 'Institucional']
formatos = ['Feed', 'Stories', 'Carrossel', 'Reels', 'Ads', 'Banner', 'Impresso']

editoria_ids = {}
for ed in editorias:
    ed_id = create_folder(ed, root_id)
    editoria_ids[ed] = ed_id
    print(f'Editoria: {ed} ({ed_id})')
    for fmt in formatos:
        fmt_id = create_folder(fmt, ed_id)
        print(f'  Formato: {fmt} ({fmt_id})')

print('\nAplicando estrutura interna padronizada nos jobs...')
# Map job -> editoria/formato/categoria
jobs = [
    ('EPQ_social_stories_1080x1920', 'Concursos', 'Stories', 'social'),
    ('EPQ_social_feed_1080x1080', 'Concursos', 'Feed', 'social'),
    ('EPQ_social_carrossel_1080x1080', 'Concursos', 'Carrossel', 'social'),
    ('EPQ_social_reels_1080x1920', 'Concursos', 'Reels', 'social'),
    ('EPQ_ads_feed_1080x1080', 'Concursos', 'Feed', 'ads'),
    ('EPQ_ads_stories_1080x1920', 'Concursos', 'Stories', 'ads'),
    ('EPQ_banner_1920x500', 'Concursos', 'Banner', 'banner'),
    ('EPQ_impresso_a4_210x297mm', 'Concursos', 'Impresso', 'impresso'),
]

all_root = list_children(root_id)
for job_name, editoria, formato, categoria in jobs:
    job_id = next((f['id'] for f in all_root if f['name'] == job_name and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    if not job_id:
        print(f'Job não encontrado na raiz: {job_name}')
        continue

    formato_id = next((f['id'] for f in list_children(editoria_ids[editoria]) if f['name'] == formato), None)
    if not formato_id:
        print(f'Formato não encontrado: {editoria}/{formato}')
        continue

    cat_id = create_folder(categoria, formato_id)
    move_file(job_id, cat_id)
    print(f'Movido: {job_name} → {editoria}/{formato}/{categoria}')

print('\nPadronizando estrutura interna dos jobs...')
# Update each job to: 01 - Apoio / 01 - Referencia + 02 - Briefing ; 03 - Arquivo Finalizado / OLD
standardize_targets = []
for ed in editorias:
    for fmt in formatos:
        for cat in ['social', 'ads', 'banner', 'impresso']:
            # We'll find all jobs moved under this path by searching categoria folders
            pass

# Simpler: get all job folders anywhere under root and normalize their children
all_folders = list_children(root_id)
job_ids = [f['id'] for f in all_folders if f['name'].startswith('EPQ_') and f['mimeType'] == 'application/vnd.google-apps.folder']
for job_id in job_ids:
    children = list_children(job_id)
    child_names = {c['name']: c['id'] for c in children}

    # Rename generic folders if needed
    if '01 - Apoio' in child_names:
        apoio_id = child_names['01 - Apoio']
        apoio_children = list_children(apoio_id)
        apoio_child_names = {c['name']: c['id'] for c in apoio_children}

        if '01 - Referencia' not in apoio_child_names:
            ref_id = create_folder('01 - Referencia', apoio_id)
            print(f'Criado 01 - Referencia em {job_id}')

        if '02 - Briefing' not in apoio_child_names:
            # Briefing might be at job root named "02 - Briefing"
            if '02 - Briefing' in child_names:
                move_file(child_names['02 - Briefing'], apoio_id)
                print(f'Movido Briefing para 01 - Apoio em {job_id}')
            else:
                create_folder('02 - Briefing', apoio_id)
                print(f'Criado 02 - Briefing em {job_id}/01 - Apoio')

        # Move anything else inside apoio to 01 - Referencia to keep apoio clean
        for c in apoio_children:
            if c['name'] not in ['01 - Referencia', '02 - Briefing']:
                ref_id = apoio_child_names.get('01 - Referencia')
                if ref_id:
                    move_file(c['id'], ref_id)
                    print(f'Movido {c["name"]} para 01 - Referencia em {job_id}')

    if '03 - Arquivo Finalizado' in child_names:
        final_id = child_names['03 - Arquivo Finalizado']
        final_children = list_children(final_id)
        final_child_names = {c['name']: c['id'] for c in final_children}
        if 'OLD' not in final_child_names:
            create_folder('OLD', final_id)
            print(f'Criado OLD em {job_id}/03 - Arquivo Finalizado')

print('\nReestruturação concluída!')
