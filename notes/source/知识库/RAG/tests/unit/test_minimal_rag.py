from __future__ import annotations

import sys
from pathlib import Path

import pytest


EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "minimal-rag"
sys.path.insert(0, str(EXAMPLE_DIR))

from minimal_rag import (  # noqa: E402
    DEFAULT_CORPUS,
    NO_ANSWER,
    Document,
    cosine_similarity,
    embed,
    run_rag,
)


def test_normal_run_exposes_pipeline_and_valid_citation_positions() -> None:
    result = run_rag("RAG 如何回答问题？", top_k=2)

    assert result.corpus == DEFAULT_CORPUS
    assert result.chunks
    assert result.query_embedding
    assert 0 < len(result.retrieved) <= 2
    assert "<UNTRUSTED_CONTEXT>" in result.prompt
    assert result.answer != NO_ANSWER
    assert result.citations

    documents = {document.document_id: document for document in result.corpus}
    chunks = {chunk.chunk_id: chunk for chunk in result.chunks}
    for citation in result.citations:
        source_text = documents[citation.document_id].text
        cited_text = source_text[citation.start : citation.end]
        assert cited_text == chunks[citation.chunk_id].text
        assert f"[{citation.rank}]" in result.answer


def test_empty_corpus_returns_explicit_no_answer() -> None:
    result = run_rag("RAG 是什么？", corpus=[], top_k=2)

    assert result.chunks == ()
    assert result.retrieved == ()
    assert result.context == "（无可用上下文）"
    assert result.answer == NO_ANSWER
    assert result.citations == ()


@pytest.mark.parametrize("query", ["", "   ", "\n\t"])
def test_empty_query_is_rejected(query: str) -> None:
    with pytest.raises(ValueError, match="query 不能为空"):
        run_rag(query)


def test_top_k_overflow_returns_only_available_positive_matches() -> None:
    result = run_rag("RAG Chunk 引用", top_k=999)

    assert 0 < len(result.retrieved) <= len(result.chunks)
    assert len(result.retrieved) == len(result.citations)
    assert [item.score for item in result.retrieved] == sorted(
        (item.score for item in result.retrieved), reverse=True
    )


def test_zero_vector_returns_explicit_no_answer() -> None:
    result = run_rag("!!!", top_k=2)

    assert embed(result.query) == {}
    assert result.retrieved == ()
    assert result.answer == NO_ANSWER
    assert result.citations == ()


def test_cosine_similarity_handles_zero_vectors() -> None:
    assert cosine_similarity({}, embed("RAG")) == 0.0
    assert cosine_similarity(embed("RAG"), {}) == 0.0


def test_empty_document_is_a_valid_empty_corpus_member() -> None:
    result = run_rag("RAG", corpus=[Document("empty", "空文档", "")])

    assert len(result.corpus) == 1
    assert result.chunks == ()
    assert result.answer == NO_ANSWER
