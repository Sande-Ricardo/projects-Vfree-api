from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

# Generic Splitter
def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=[
            "\n## ",
            "\n# ",
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )