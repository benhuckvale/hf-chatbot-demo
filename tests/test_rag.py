"""Tests for RAG functionality."""

import pytest
import tempfile
from pathlib import Path

from src.chatbot.rag import load_and_chunk_faq, build_vector_store, retrieve_context


class TestLoadAndChunkFaq:
    """Tests for FAQ loading and chunking."""

    def test_load_existing_file(self):
        """Test loading an existing FAQ file."""
        # Use the actual faq.md if it exists in the repo root
        chunks = load_and_chunk_faq("faq.md")
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_load_nonexistent_file_uses_sample(self):
        """Test that missing file falls back to sample FAQ."""
        chunks = load_and_chunk_faq("nonexistent_faq.md")
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        # Sample FAQ should contain shipping info
        assert any("shipping" in chunk.lower() for chunk in chunks)

    def test_chunks_not_empty(self):
        """Test that chunks are not empty strings."""
        chunks = load_and_chunk_faq("nonexistent_faq.md")
        assert all(chunk.strip() for chunk in chunks)

    def test_chunk_overlap(self):
        """Test that chunks may have overlapping content."""
        chunks = load_and_chunk_faq("nonexistent_faq.md")
        # With overlap, some content might appear in multiple chunks
        assert len(chunks) >= 1


class TestBuildVectorStore:
    """Tests for vector store building."""

    def test_build_vector_store_from_chunks(self):
        """Test building a vector store from chunks."""
        chunks = [
            "This is a test chunk about shipping",
            "This is a test chunk about returns",
            "This is a test chunk about products",
        ]
        vector_store = build_vector_store(chunks)
        assert vector_store is not None

    def test_empty_chunks(self):
        """Test vector store with empty chunk list."""
        chunks = []
        # This may raise an error depending on implementation
        with pytest.raises(Exception):
            build_vector_store(chunks)


class TestRetrieveContext:
    """Tests for context retrieval."""

    def test_retrieve_context_with_relevant_query(self):
        """Test retrieving context for a relevant query."""
        chunks = [
            "Shipping takes 5-7 business days",
            "Returns are accepted within 30 days",
            "Our products are eco-friendly",
        ]
        vector_store = build_vector_store(chunks)

        context = retrieve_context(vector_store, "How long does shipping take?", k=1)
        assert isinstance(context, str)
        assert len(context) > 0

    def test_retrieve_context_k_parameter(self):
        """Test that k parameter controls number of results."""
        chunks = [
            "Shipping takes 5-7 business days",
            "Express shipping takes 2-3 business days",
            "International shipping takes 10-14 days",
            "Returns are accepted within 30 days",
        ]
        vector_store = build_vector_store(chunks)

        context_k1 = retrieve_context(vector_store, "shipping", k=1)
        context_k3 = retrieve_context(vector_store, "shipping", k=3)

        # More results should generally give more content
        assert len(context_k3) >= len(context_k1)

    def test_retrieve_context_returns_string(self):
        """Test that retrieve_context returns a string."""
        chunks = [
            "Test chunk 1",
            "Test chunk 2",
            "Test chunk 3",
        ]
        vector_store = build_vector_store(chunks)
        context = retrieve_context(vector_store, "test", k=1)
        assert isinstance(context, str)

    def test_retrieve_context_empty_query(self):
        """Test retrieving context with empty query."""
        chunks = [
            "Test chunk 1",
            "Test chunk 2",
        ]
        vector_store = build_vector_store(chunks)
        context = retrieve_context(vector_store, "", k=1)
        # Should still return something (based on embedding distance)
        assert isinstance(context, str)
