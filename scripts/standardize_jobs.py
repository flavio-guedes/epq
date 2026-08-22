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

def create_folder(name, parent_id):
    metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    folder = service.files().create(body=metadata, fields='id,name').execute()
    return folder['id']

def move_file(file_id, new_parent_id):
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))
    service.files().update(fileId=file_id, addParents=new_parent_id, removeParents=previous_parents, fields='id,parents').execute()

# Padronizar estrutura interna dos jobs: Briefing dentro de Apoio e OLD em Arquivo Finalizado
all_jobs = []
for ed in ['Concursos', 'Dicas de Estudo', 'Institucional']:
    for fmt in ['Feed', 'Stories', 'Carrossel', 'Reels', 'Ads', 'Banner', 'Impresso']:
        for cat in ['social', 'ads', 'banner', 'impresso']:
            all_jobs.append((ed, fmt, cat))

for ed, fmt, cat in all_jobs:
    root_folders = list_children(root_id)
    editoria = next((f for f in root_folders if f['name'] == ed and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    if not editoria:
        continue
    formato = next((f for f in list_children(editoria['id']) if f['name'] == fmt and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    if not formato:
        continue
    categoria = next((f for f in list_children(formato['id']) if f['name'] == cat and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    if not categoria:
        continue
    jobs_here = [f for f in list_children(categoria['id']) if f['mimeType'] == 'application/vnd.google-apps.folder']
    for job in jobs_here:
        job_id = job['id']
        children = list_children(job_id)
        child_names = {c['name']: c['id'] for c in children}

        apoio_id = child_names.get('01 - Apoio')
        if apoio_id:
            apoio_children = list_children(apoio_id)
            apoio_child_names = {c['name']: c['id'] for c in apoio_children}

            if '02 - Briefing' not in apoio_child_names:
                if '02 - Briefing' in child_names:
                    move_file(child_names['02 - Briefing'], apoio_id)
                else:
                    create_folder('02 - Briefing', apoio_id)

            if '01 - Referencia' not in apoio_child_names:
                create_folder('01 - Referencia', apoio_id)

            for c in apoio_children:
                if c['name'] not in ['01 - Referencia', '02 - Briefing']:
                    move_file(c['id'], apoio_child_names['01 - Referencia'] if '01 - Referencia' in apoio_child_names else apoio_id)

        final_id = child_names.get('03 - Arquivo Finalizado')
        if final_id:
            final_children = list_children(final_id)
            final_child_names = {c['name']: c['id'] for c in final_children}
            if 'OLD' not in final_child_names:
                create_folder('OLD', final_id)

print('Padronização concluída!')
