from unittest.mock import patch

import json
from unittest.mock import MagicMock
import pytest
from apolo_11.src.messaging import MessageBroker, QUEUE_GENERATED


class TestMessageBrokerDisabled:
    def test_disabled_when_no_env(self):
        broker = MessageBroker()
        assert not broker.enabled

    def test_publish_noop_when_disabled(self):
        broker = MessageBroker()
        broker.publish(QUEUE_GENERATED, {"data": "test"})

    def test_consume_returns_false_when_disabled(self):
        broker = MessageBroker()
        result = broker.consume(QUEUE_GENERATED, lambda x: None)
        assert not result

    def test_close_noop_when_disabled(self):
        broker = MessageBroker()
        broker.close()


class TestMessageBrokerEnabled:
    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_publish_calls_pika(self, mock_connection):
        broker = MessageBroker()
        assert broker.enabled

        mock_channel = mock_connection.return_value.channel.return_value
        broker.publish(QUEUE_GENERATED, {"cycle": 1})

        mock_channel.basic_publish.assert_called_once()

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_consume_gets_message(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_get.return_value = (type("Frame", (), {"delivery_tag": 1})(), None, b'{"cycle": 1}')

        broker = MessageBroker()
        results = []

        def cb(data):
            results.append(data)

        broker.consume(QUEUE_GENERATED, cb)
        assert results == [{"cycle": 1}]

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_close_calls_connection_close(self, mock_connection):
        broker = MessageBroker()
        broker.close()
        mock_connection.return_value.close.assert_called_once()

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection", side_effect=Exception("connection failed"))
    def test_fallback_disabled_on_connection_error(self, mock_connection):
        broker = MessageBroker()
        assert not broker.enabled

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_publish_error_handled(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_publish.side_effect = Exception("publish error")

        broker = MessageBroker()
        broker.publish(QUEUE_GENERATED, {"cycle": 1})

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_consume_no_message(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_get.return_value = (None, None, None)

        broker = MessageBroker()
        result = broker.consume(QUEUE_GENERATED, lambda x: None)
        assert not result

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_consume_callback_error_handled(self, mock_connection):
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_get.return_value = (
            MagicMock(delivery_tag=1), None, b'{"cycle": 1}')

        broker = MessageBroker()
        broker.consume(QUEUE_GENERATED, lambda x: 1/0)

        mock_channel.basic_ack.assert_called_once()

    @patch.dict("os.environ", {"RABBITMQ_HOST": "localhost"})
    @patch("pika.BlockingConnection")
    def test_close_error_handled(self, mock_connection):
        mock_connection.return_value.close.side_effect = Exception("close error")

        broker = MessageBroker()
        broker.close()
