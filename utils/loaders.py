from langchain_community.document_loaders import TextLoader, PyPDFLoader

def get_loader(file_path: str, file_type: str):
    loaders = {
        "txt": lambda: TextLoader(file_path, encoding="utf-8"),
        "md":  lambda: TextLoader(file_path, encoding="utf-8"),
        "pdf": lambda: PyPDFLoader(file_path),
    }

    if file_type not in loaders:
        raise ValueError(f"Unsupported file type: {file_type}")

    return loaders[file_type]()