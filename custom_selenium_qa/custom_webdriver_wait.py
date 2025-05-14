from time import time
from time import sleep

from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import TimeoutException

from .base_settings import IGNORED_EXCEPTIONS
from .base_settings import POLL_FREQUENCY


class CustomWebDriverWait(object):
    """
    Кастомный WebDriver c кастомным ожиданием
    """

    def __init__(
            self,
            page_object,
            timeout: float,
            poll_frequency: float = POLL_FREQUENCY
    ):
        """
        Конструктор, принимает экземпляр WebDriver и тайм-аут в секундах.

        :Аргументы:
        - driver - Экземпляр WebDriver (Ie, Firefox, Chrome или удаленный)
        - timeout - Количество секунд до истечения времени ожидания
        - poll_frequency - интервал ожидания между вызовами
        По умолчанию это 0,5 секунды.
        """
        self._page_object = page_object
        self._timeout = float(timeout)
        self._poll = poll_frequency

        # avoid the divide by zero
        if self._poll == 0:
            self._poll = POLL_FREQUENCY
        self._ignored_exceptions = IGNORED_EXCEPTIONS

    def __repr__(self) -> str:
        return '<{0.__module__}.{0.__name__} (session="{1}")>'.format(
            type(self),
            self._page_object.emulator.session_id
        )

    def until(self, method, message=''):
        """
        Вызывает метод, предоставленный драйвером в качестве аргумента, до тех
        пор, пока возвращаемое значение не оценивается как 'False'.

        :param method: callable(WebDriver)
        :param message: optional message for :exc:'TimeoutException'
        :returns: the result of the last call to 'method'
        :raises: :exc:'selenium.common.exceptions.TimeoutException' if timeout
        occurs
        """
        end_time = time() + self._timeout

        while True:
            try:
                value = method(self._page_object.emulator)
                if value:
                    return value
            except InvalidSelectorException as exc:
                self._page_object.make_screenshot()
                raise exc
            except self._ignored_exceptions:
                pass
            sleep(self._poll)
            if time() > end_time:
                break
        self._page_object.make_screenshot()
        raise TimeoutException(message)

    def until_not(self, method, message=''):
        """
        Вызывает метод, предоставленный драйвером в качестве аргумента, до тех
        пор, пока возвращаемое значение равно 'False'.

        :param method: callable(WebDriver)
        :param message: optional message for :exc:'TimeoutException'
        :returns: the result of the last call to 'method', or
                  'True' if 'method' has raised one of the ignored exceptions
        :raises: :exc:'selenium.common.exceptions.TimeoutException' if timeout
                 occurs
        """
        end_time = time() + self._timeout

        while True:
            try:
                value = method(self._page_object.emulator)
                if not value:
                    return value
            except InvalidSelectorException as exc:
                self._page_object.make_screenshot()
                raise exc
            except self._ignored_exceptions:
                return True
            sleep(self._poll)
            if time() > end_time:
                break
        self._page_object.make_screenshot()
        raise TimeoutException(message)
