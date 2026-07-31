import json
import os
from collections.abc import Callable

import pika

from .logging_config import get_logger

logger = get_logger(__name__)

EXCHANGE = "apolo"
QUEUE_GENERATED = "apolo.generated"
QUEUE_PROCESSED = "apolo.processed"


class MessageBroker:
    def __init__(self) -> None:
        host = os.getenv("RABBITMQ_HOST", "")
        self._enabled = bool(host)
        if not self._enabled:
            return

        user = os.getenv("RABBITMQ_DEFAULT_USER", "")
        password = os.getenv("RABBITMQ_DEFAULT_PASS", "")
        credentials = (
            pika.PlainCredentials(user, password)
            if user and password
            else pika.ConnectionParameters.DEFAULT_CREDENTIALS
        )

        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, credentials=credentials))
            self._channel = self._connection.channel()
            self._channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
            logger.info("Conectado a RabbitMQ en %s", host)
        except Exception as e:
            logger.warning("No se pudo conectar a RabbitMQ: %s", e)
            self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def publish(self, routing_key: str, data: dict) -> None:
        if not self._enabled:
            return
        try:
            self._channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(data, default=str),
            )
        except Exception as e:
            logger.error("Error publicando mensaje: %s", e)

    def consume(self, queue: str, callback: Callable[[dict], None], timeout: float = 1.0) -> bool:
        if not self._enabled:
            return False

        method_frame, _, body = self._channel.basic_get(queue=queue)
        if method_frame:
            try:
                data = json.loads(body)
                callback(data)
            except Exception as e:
                logger.error("Error procesando mensaje: %s", e)
            self._channel.basic_ack(method_frame.delivery_tag)
            return True
        return False

    def close(self) -> None:
        if self._enabled:
            try:
                self._connection.close()
            except Exception:
                pass
