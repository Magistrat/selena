from time import sleep
from .base_settings import POLL_FREQUENCY


def sleep_poll_frequency() -> None:
    """
    Метод для ожидания в пределах переменной POLL_FREQUENCY
    :return:
    """
    sleep(POLL_FREQUENCY)
