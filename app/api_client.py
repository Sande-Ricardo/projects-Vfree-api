import requests

BASE_URL = "http://localhost:8000"

def get_projects() -> list:
    r = requests.get(f"{BASE_URL}/projects/")
    r.raise_for_status()
    return r.json()

def create_project(title:str, instructions:str) -> dict:
    r = requests.post(f"{BASE_URL}/projects/", json={
        "title":title,
        "instructions":instructions
    })
    return r.json()

def delete_project(project_id:str)-> None:
    r = requests.delete(f"{BASE_URL}/projects/{project_id}")
    r.raise_for_status()
    
def update_project(project_id:str, title:str, instructions:str) ->  dict:
    r = requests.patch(f"{BASE_URL}/projects/{project_id}", json= {
        "title": title,
        "instructions": instructions
    })
    r.raise_for_status()
    return r.json()

def send_message(project_id:str, question:str) -> dict:
    r = requests.post(f"{BASE_URL}/query/", json= {
        "project_id": project_id,
        "question": question
    })
    r.raise_for_status()
    return r.json()

def clear_history(project_id:str) -> None:
    r = requests.delete(f"{BASE_URL}/query/{project_id}/history")
    r.raise_for_status()
    
def get_documents(project_id:str)-> list:
    r = requests.get(f"{BASE_URL}/documents/", params= {"project_id": project_id})
    r.raise_for_status()
    return r.json()

def upload_document(project_id:str, title:str, file_bytes:bytes, file_name:str) -> dict:
    r = requests.post(
        f"{BASE_URL}/ingest/",
        data={"project_id": project_id, "title": title},
        files={"file": (file_name, file_bytes)}
    )
    r.raise_for_status()
    return r.json()

def delete_document(document_id:str) -> None:
    r = requests.delete(f"{BASE_URL}/documents/{document_id}")
    r.raise_for_status()
    
def get_memory(project_id:str) -> list:
    r = requests.get(f"{BASE_URL}/projects/{project_id}/memory")
    r.raise_for_status()
    return r.json()

def clear_memory(project_id:str) -> None:
    r = requests.delete(f"{BASE_URL}/projects/{project_id}/memory")
    r.raise_for_status()