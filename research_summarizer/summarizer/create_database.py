import os
from PyPDF2 import PdfReader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings


class CreateChromaDatabase:
    """
    This class handles the processing of a single PDF research paper by:
    1. Extracting text from the PDF.
    2. Splitting the text into semantic chunks.
    3. Storing the chunks in a persistent ChromaDB vector store using OpenAI embeddings.
    """

    def __init__(self, openai_key: str, chroma_path: str = 'chroma_db/'):
        """
        Initializes the database processor with API key and target ChromaDB path.

        Args:
            openai_key (str): Your OpenAI API key for generating embeddings.
            chroma_path (str): Directory path to store the Chroma database.
        """
        self.chroma_path = chroma_path
        self.openai_key = openai_key

    def process_single_paper(self, paper_path: str, paper_id: str, original_filename: str) -> None:
        """
        Main method to extract, split, and store a single research paper into ChromaDB.

        Args:
            paper_path (str): Absolute path to the PDF file.
            paper_id (str): Unique UUID identifier for this paper.
            original_filename (str): The original filename uploaded by the user.
        """
        print(f"[INFO] Processing paper: {original_filename}")

        text = self._extract_text(paper_path)
        chunks = self._split_into_chunks(text, paper_path, paper_id, original_filename)
        self._store_in_chroma(chunks)

        print(f"[SUCCESS] Stored chunks for '{original_filename}' in ChromaDB.")

    def _extract_text(self, file_path: str) -> str:
        """
        Extracts text content from a PDF file.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            str: Concatenated text content from all pages.
        """
        pdf_reader = PdfReader(file_path)
        full_text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

        return full_text

    def _split_into_chunks(self, text: str, file_path: str, paper_id: str, original_filename: str) -> list[Document]:
        """
        Splits a large block of text into smaller overlapping chunks and attaches metadata.

        Args:
            text (str): Raw extracted text from the PDF.
            file_path (str): Path to the source file.
            paper_id (str): UUID for the paper.
            original_filename (str): The user-uploaded filename.

        Returns:
            list[Document]: A list of LangChain Document objects with metadata.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=750,
            chunk_overlap=200
        )

        chunks = splitter.split_text(text)
        base_filename = os.path.basename(file_path)

        return [
            Document(
                page_content=chunk,
                metadata={
                    "paper_id": paper_id,
                    "filename": base_filename,
                    "original_filename": original_filename,
                    "source": file_path
                }
            )
            for chunk in chunks
        ]

    def _store_in_chroma(self, documents: list[Document]) -> None:
        """
        Stores the processed document chunks in a Chroma vector store with OpenAI embeddings.

        Args:
            documents (list[Document]): List of preprocessed chunks with metadata.
        """
        embeddings = OpenAIEmbeddings(openai_api_key=self.openai_key)
        db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=self.chroma_path
        )
        db.persist()
