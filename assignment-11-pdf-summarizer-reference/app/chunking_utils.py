from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 1500, chunk_overlap: int = 200) -> list[str]:
    """
    Periya text-ah chinna chunks ah split pannum.

    chunk_size: ovvoru chunk-la evlo characters irukanum (approx)
    chunk_overlap: adutha chunk-oda ethana characters common ah
                   repeat aganum (context lose aagama irukka)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(text)
    return chunks