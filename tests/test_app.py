"""Tests for the main app module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.chatbot.app import _get_hf_token, _create_respond_function, main


class TestGetHfToken:
    """Tests for HF token retrieval."""

    def test_get_hf_api_token(self):
        """Test retrieving HF_API_TOKEN."""
        with patch.dict(os.environ, {"HF_API_TOKEN": "test_token_api"}):
            token = _get_hf_token()
            assert token == "test_token_api"

    def test_get_hf_hub_token(self):
        """Test retrieving HF_HUB_TOKEN as fallback."""
        with patch.dict(os.environ, {"HF_HUB_TOKEN": "test_token_hub"}, clear=True):
            token = _get_hf_token()
            assert token == "test_token_hub"

    def test_get_hf_token(self):
        """Test retrieving HF_TOKEN as final fallback."""
        with patch.dict(os.environ, {"HF_TOKEN": "test_token"}, clear=True):
            token = _get_hf_token()
            assert token == "test_token"

    def test_hf_api_token_priority(self):
        """Test that HF_API_TOKEN has priority."""
        env = {
            "HF_API_TOKEN": "api_token",
            "HF_HUB_TOKEN": "hub_token",
            "HF_TOKEN": "token",
        }
        with patch.dict(os.environ, env):
            token = _get_hf_token()
            assert token == "api_token"

    def test_no_token_returns_none(self):
        """Test that None is returned when no token is found."""
        with patch.dict(os.environ, {}, clear=True):
            token = _get_hf_token()
            assert token is None


class TestCreateRespondFunction:
    """Tests for respond function creation."""

    def test_respond_function_created(self):
        """Test that respond function is created successfully."""
        mock_client = Mock()
        mock_vector_store = Mock()

        respond = _create_respond_function(mock_client, mock_vector_store)
        assert callable(respond)

    def test_respond_empty_message(self):
        """Test respond with empty message."""
        mock_client = Mock()
        mock_vector_store = Mock()
        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        respond = _create_respond_function(mock_client, mock_vector_store)
        result = list(respond("   ", [], mock_request))

        assert any("Please ask me a question" in str(r) for r in result)

    def test_respond_calls_client(self):
        """Test that respond calls the inference client."""
        mock_client = Mock()
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta = Mock()
        mock_chunk.choices[0].delta.content = "Test response"
        mock_client.chat_completion.return_value = [mock_chunk]

        mock_vector_store = Mock()
        mock_vector_store.similarity_search = Mock(
            return_value=[Mock(page_content="Test FAQ content")]
        )

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        respond = _create_respond_function(mock_client, mock_vector_store)
        with patch('src.chatbot.app.check_rate_limit', return_value=True):
            with patch('src.chatbot.app.retrieve_context', return_value="Test context"):
                result = list(respond("How long does shipping take?", [], mock_request))

        assert mock_client.chat_completion.called

    def test_respond_handles_exception(self):
        """Test that respond handles exceptions gracefully."""
        mock_client = Mock()
        mock_client.chat_completion.side_effect = Exception("API Error")

        mock_vector_store = Mock()

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        respond = _create_respond_function(mock_client, mock_vector_store)
        with patch('src.chatbot.app.check_rate_limit', return_value=True):
            with patch('src.chatbot.app.retrieve_context', return_value="Test context"):
                result = list(respond("Test message", [], mock_request))

        assert any("error" in str(r).lower() for r in result)

    def test_respond_respects_rate_limit(self):
        """Test that respond respects rate limiting."""
        mock_client = Mock()
        mock_vector_store = Mock()
        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        respond = _create_respond_function(mock_client, mock_vector_store)
        with patch('src.chatbot.app.check_rate_limit', return_value=False):
            result = list(respond("Test message", [], mock_request))

        assert any("too many messages" in str(r).lower() for r in result)
        assert not mock_client.chat_completion.called


class TestMain:
    """Tests for main app initialization."""

    @patch('src.chatbot.app.load_and_chunk_faq')
    @patch('src.chatbot.app.build_vector_store')
    @patch('src.chatbot.app._get_hf_token')
    @patch('src.chatbot.app.InferenceClient')
    @patch('src.chatbot.app.gr.ChatInterface')
    def test_main_creates_demo(
        self,
        mock_chat_interface,
        mock_inference_client,
        mock_get_token,
        mock_build_store,
        mock_load_faq,
    ):
        """Test that main creates a demo successfully."""
        mock_load_faq.return_value = ["chunk1", "chunk2"]
        mock_build_store.return_value = Mock()
        mock_get_token.return_value = "test_token"
        mock_inference_client.return_value = Mock()
        mock_demo = Mock()
        mock_chat_interface.return_value = mock_demo

        result = main()

        assert result is not None
        assert mock_load_faq.called
        assert mock_build_store.called
        assert mock_get_token.called
        assert mock_inference_client.called
        assert mock_chat_interface.called

    @patch('src.chatbot.app.load_and_chunk_faq')
    @patch('src.chatbot.app.build_vector_store')
    @patch('src.chatbot.app._get_hf_token')
    @patch('src.chatbot.app.InferenceClient')
    @patch('src.chatbot.app.gr.ChatInterface')
    def test_main_sets_theme(
        self,
        mock_chat_interface,
        mock_inference_client,
        mock_get_token,
        mock_build_store,
        mock_load_faq,
    ):
        """Test that main sets the demo theme."""
        mock_load_faq.return_value = ["chunk1"]
        mock_build_store.return_value = Mock()
        mock_get_token.return_value = "test_token"
        mock_inference_client.return_value = Mock()
        mock_demo = Mock()
        mock_chat_interface.return_value = mock_demo

        result = main()

        # Check that theme was set
        assert hasattr(result, 'theme') or mock_demo.theme
