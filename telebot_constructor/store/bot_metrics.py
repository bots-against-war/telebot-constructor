from telebot.metrics import TelegramUpdateMetrics, TelegramUpdateMetricsHandler
from telebot_components.redis_utils.interface import RedisInterface


class MetricsStore:
    PREFIX = "telebot-constructor/bot-metrics"

    def __init__(self, redis: RedisInterface) -> None:
        # TODO: some internal stores here
        pass

    def get_update_metrics_handler(self, bot_id: str) -> TelegramUpdateMetricsHandler:

        async def handler(metrics: TelegramUpdateMetrics) -> None:
            pass

        return handler
