from json import dumps
from os import chdir
from os import curdir
from os import pardir
from os.path import join
from typing import Any
from typing import List
from typing import NoReturn
from typing import Tuple
from typing import Union

from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from testit import step  # type: ignore

from .base_settings import EXPLICITLY_TIMEOUT
from .base_settings import IGNORED_EXCEPTIONS
from .base_settings import POLL_FREQUENCY
from .base_settings import SCREENSHOTS_DIRECTORY
from .base_settings import SCREENSHOTS_EXTENSION
from .custom_webdriver_wait import CustomWebDriverWait
from .locator import Locator
from .utils import sleep_poll_frequency


class BaseActions:
    """
    Класс абстракций для обобщения низкоуровневых действий браузера.
    """

    _IS_ABSTRACT_CLASS = True
    ATTEMPTS_NUMBER = int(EXPLICITLY_TIMEOUT // POLL_FREQUENCY)

    def __init__(self, emulator: Firefox, test_method_name: str):
        if self._IS_ABSTRACT_CLASS:
            raise NotImplementedError(
                'Невозможно создать экземпляр абстрактного базового класса'
            )
        else:
            self._emulator = emulator
            self._test_method_name = test_method_name

    @property
    def emulator(self) -> Firefox:
        """
        Возвращает объект вебдрайвера.

        :return: webdriver
        """
        return self._emulator

    def __errors_handler(
            self,
            error: Exception,
            desc: str = 'Необрабатываемое исключение.'
    ) -> None:
        """
        Обработчик ошибок.

        :param error: Поднятая ошибка
        :param desc: Описание ошибки если она не подходит под условия
        :return:
        """

        if isinstance(error, IGNORED_EXCEPTIONS):
            sleep_poll_frequency()
        else:
            self.make_screenshot()
            error.__traceback__ = None
            raise AssertionError(desc)

    def screenshot_and_raise_error(self, desc: str) -> NoReturn:
        """
        Делает скриншот и поднимает ошибку с типом AssertionError и описанием из аргумента функции

        :param desc: Описание ошибки
        :return:
        """
        self.make_screenshot()
        raise AssertionError(desc)

    def emulator_refresh(self) -> None:
        """
        Перезагружает текущую страницу
        """
        self._emulator.refresh()

    def find_element_return_bool(self, locator: Locator) -> bool:
        """
        Возвращает True/False в зависимости от наличия элемента.

        :param locator: Locator - локатор элемента
        :return: Возвращает True/False в зависимости от наличия элемента
        """
        with step('Проверка элемента на видимость (возвращение значения True/False)', locator.description):
            try:
                self.find_element(locator)
                return True
            except AssertionError:
                return False

    def find_element(self, locator: Locator) -> WebElement:
        """
        Находит элемент по локатору.

        :param locator: Локатор искомого элемента.
        :return: Объект WebElement.
        """
        with step('Поиск элемента по локатору', locator.description):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    return self._emulator.find_element(*locator())
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно найти элемент {locator.description}. Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Невозможно найти элемент {locator.description}. Истекло количество попыток.'
            )

    def find_elements(self, locator: Locator) -> List[WebElement]:
        """
        Находит элементы с одинаковым локатором.
        :param locator: Локатор искомого элемента.
        :return: Список объектов WebElement.
        """
        with step('Поиск элементов по локатору', locator.description):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    return self._emulator.find_elements(*locator())
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно найти элементы {locator.description}. Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Невозможно найти элементы {locator.description}. Истекло количество попыток.'
            )

    def make_screenshot(self) -> None:
        """
        Создаёт скриншот страницы браузера.

        :return: None
        """
        chdir(path=join(curdir, SCREENSHOTS_DIRECTORY))
        self._emulator.save_screenshot(f'{self._test_method_name}.{SCREENSHOTS_EXTENSION}')
        chdir(path=pardir)

    def check_element_visibility(self, locator: Locator) -> None:
        """
        Проверяет присутствие элемента в DOM и его видимость.

        :param locator: Locator
        :return: None
        """
        with step('Проверка присутствие элемента в DOM и его видимость', locator.description):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.visibility_of_element_located(
                    locator()
                ),
                f'Элемент {locator.description} не отображается.'
            )

    def check_element_invisibility(self, locator: Locator) -> None:
        """
        Проверяет невидимость элемента.

        :param locator: Locator
        :return: None
        """
        with step('Проверка на невидимость элемента', locator.description):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.invisibility_of_element(
                    self.find_element(
                        locator
                    )
                ),
                f'Элемент {locator.description} отображается.'
            )

    def check_element_clickability(self, locator: Locator) -> None:
        """
        Проверяет кликабельность элемента.

        :param locator: Locator
        :return: None
        """
        with step('Проверка кликабельности элемента', locator.description):
            self.check_element_visibility(locator)
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.element_to_be_clickable(
                    locator()
                ),
                f'Элемент {locator.description} не кликабельный.'
            )

    def click_element_by_webdriver(self, locator: Locator, has_check_clickability=True) -> None:
        """
        Проверяет, что элемент видим, после чего нажимает на него.

        :param locator: Locator.
        :param has_check_clickability: Флаг доступности элемента для клика.
        :return: None.
        """
        with step('Нажатие на элемент при помощи Webdriver', locator.description):
            if has_check_clickability:
                self.check_element_clickability(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    self.find_element(locator).click()
                    return None
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Элемент {locator.description} не кликабельный. Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Элемент {locator.description} не кликабельный. Истекло количество попыток.'
            )

    def click_element_by_action_chance(self, locator: Locator) -> None:
        """
        Нажимает на элемент через ActionChance, предварительно перемещая курсор к нему.

        :param locator: Locator селектор элемента
        :return: None
        """
        with step('Нажатие на элемент при помощи ActionChance', locator.description):
            self.check_element_visibility(locator)
            ActionChains(self._emulator).click(self.find_element(locator)).perform()

    def click_element_by_action_chance_with_move(self, locator: Locator) -> None:
        """
        Нажимает на элемент через ActionChance, предварительно перемещая курсор к нему.

        :param locator: Locator селектор элемента
        :return: None
        """
        with step('Нажатие на элемент при помощи ActionChance', locator.description):
            self.check_element_visibility(locator)
            ActionChains(
                self._emulator
            ).move_to_element(self.find_element(locator)).click(self.find_element(locator)).perform()

    def click_element_by_javascript(self, locator: Locator) -> None:
        """
        Нажимает на элемент при помощи javascript скрипта.

        :param locator: Locator селектор элемента
        :return: None
        """
        with step('Нажатие на элемент при помощи JavaScript', locator.description):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    self._emulator.execute_script('$(arguments[0]).click();', self.find_element(locator))
                    return None
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Элемент {locator.description} не кликабельный. Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Элемент {locator.description} не кликабельный. Истекло количество попыток.'
            )

    def get_value_from_element(self, locator: Locator, has_check_visibility=True) -> str:
        """
        Находит элемент, и возвращает значение из него. Использовать для получения текста из текстовых полей.

        :param has_check_visibility: Флаг проверки видимости элемента.
        :param locator: Locator
        :return: Возвращает значение из элемента
        """
        with step('Получение значения с элемента', locator.description):
            if has_check_visibility:
                self.check_element_visibility(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    return self.find_element(locator).get_attribute('value').strip(' \n\t')  # type: ignore
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно получить значение из элемента {locator.description}. '
                             'Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(f'Элемент {locator.description} не позволяет прочитать текст.')

    def get_text_from_element(self, locator: Locator) -> str:
        """
        Находит элемент и возвращает текст из него.

        :param locator: Locator
        :return: Возвращает текст из элемента
        """
        with step('Получение текста из элемента', locator.description):
            self.check_element_visibility(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    return self.find_element(locator).text.strip()
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно получить текст из элемента {locator.description}. '
                             'Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(f'Элемент {locator.description} не позволяет прочитать текст.')

    def get_text_from_elements_with_different_locators(
            self,
            locators: Tuple[Locator]
    ) -> Union[Tuple[str], Tuple[str, ...]]:
        """
        Находит элементы по локаторам из кортежа locators и возвращаем кортеж строк текста из них.

        :param locators: кортеж локаторов.
        :return: кортеж с текстами элементов.
        """
        with step('Получение списка текстов из списка элементов', [locator.description + '; ' for locator in locators]):
            strings_from_elements = []
            for locator in locators:
                strings_from_elements.append(
                    self.get_text_from_element(locator)
                )
            return tuple(strings_from_elements)

    def get_texts_from_elements_with_identical_locators(self, locator: Locator) -> Union[Tuple[str], Tuple[str, ...]]:
        """
        Находит элементы с одинаковым локатором и возвращает кортеж строк с текстом из них.

        :param locator: Locator элементов.
        :return: кортеж со строками текста из элементов.
        """
        with step('Получение списка текстов из элемента', locator.description):
            self.check_element_visibility(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    strings_from_elements = [
                        element.text.strip() for element in self.find_elements(locator)
                    ]
                    return tuple(strings_from_elements)
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно получить текст со всех элементов {locator.description}. '
                             'Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(f'Элементы {locator.description} не позволют прочитать текст.')

    def wait_for_elements_text_correspond_to_given_set(self, locator: Locator, target_texts: tuple) -> None:
        """
        Ждёт пока текст в элементах с одинаковым локатором не станет соответствовать целевому множеству.

        :param locator: Локатор проверяемых элементов.
        :param target_texts: Кортеж со строками целевого текста.
        :return: None.
        """
        with step('Ожидания до тех пор пока текст в элементах с одинаковым локатором '
                  'не станет соответствовать целевому значению', locator.description):
            target_texts_set = set(target_texts)
            for _ in range(self.ATTEMPTS_NUMBER):
                current_texts_set = set(self.get_texts_from_elements_with_identical_locators(locator))
                if current_texts_set.issubset(target_texts_set):
                    return None
                else:
                    sleep_poll_frequency()
            self.screenshot_and_raise_error(f'Текст на элементе {locator.description} не изменился.')

    def wait_for_change_text(self, locator: Locator, new_text: str, is_strong_coincidence=True) -> None:
        """
        Проверяет, что текст в элементе на странице полностью или частично совпадает с заданным.

        :param locator: Locator
        :param new_text: текст, который мы ожидаем увидеть в элементе
        :param is_strong_coincidence: Флаг определяет будет проверка строгой или не строгой
        :return: None
        """
        with step('Ожидания до тех пор пока текст не станет '
                  'полностью или частично соответствовать целевому значению', locator.description):
            new_text = new_text.replace('\xa0', ' ')  # Иногда попадается текст с пробелами без разрыва "\xa0"

            self.check_element_visibility(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                element_text = self.get_text_from_element(locator)
                if is_strong_coincidence and new_text == element_text or not \
                        is_strong_coincidence and new_text in element_text:
                    return None
                else:
                    sleep_poll_frequency()
            self.screenshot_and_raise_error(
                f'Текст на элементе {locator.description} не изменился. '
                f'Ожидаемое значение: {new_text}. Текущее значение: {element_text}')

    def wait_for_change_value(
            self,
            locator: Locator,
            new_value: str,
            is_strong_coincidence: bool = True,
            has_check_visibility: bool = True
    ) -> None:
        """
        Проверяет, что текст в элементе на странице полностью или частично совпадает с заданным.

        :param locator: Локатор элемента.
        :param new_value: Текст, который мы ожидаем увидеть в элементе.
        :param is_strong_coincidence: Флаг строгости проверки. По умолчанию True.
        :param has_check_visibility: Флаг проверки видимости элемента. По умолчанию True.
        :return: None.
        """
        with step('Ожидания до тех пор пока значение не станет '
                  'полностью или частично совпадает с заданным', locator.description):
            if has_check_visibility:
                self.check_element_visibility(locator)
            for _ in range(self.ATTEMPTS_NUMBER):
                current_value = self.get_value_from_element(locator, has_check_visibility=has_check_visibility)
                has_strong_coincidence = is_strong_coincidence and new_value == current_value
                has_not_strong_coincidence = not is_strong_coincidence and new_value in self.get_value_from_element(
                    locator,
                    has_check_visibility=has_check_visibility
                )
                if has_strong_coincidence or has_not_strong_coincidence:
                    return None
                else:
                    sleep_poll_frequency()
            self.screenshot_and_raise_error(f'Значение в элементе {locator.description} не изменилось.')

    def fill_text(self, locator: Locator, text: str) -> None:
        """
        Нажимает на элемент и вводит в него текст.

        :param locator: Locator
        :param text: текст для ввода
        :return: None
        """
        with step('Ввод текста после нажатия на элемент', locator.description):
            self.click_element_by_webdriver(locator)
            for attempt in range(self.ATTEMPTS_NUMBER):
                try:
                    self.find_element(locator).clear()
                    break
                except IGNORED_EXCEPTIONS:
                    if attempt == self.ATTEMPTS_NUMBER - 1:
                        self.screenshot_and_raise_error(
                            f'Невозможно очистить поле {locator.description}. Истекло количество попыток.'
                        )
                    sleep_poll_frequency()
                except Exception as exc:
                    self.make_screenshot()
                    exc.__traceback__ = None
                    raise AssertionError(
                        f'Невозможно очистить поле {locator.description}. Необрабатываемое исключение.'
                    )
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    self.find_element(locator).send_keys(text)
                    return None
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Невозможно записать текст в поле {locator.description}. Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Невозможно записать текст в поле {locator.description}. Истекло количество попыток.'
            )

    def check_title(self, text: str) -> None:
        """
        Проверяет заголовок страницы на соответствие заданному тексту.

        :param text: Ожидаемый текст в заголовке страницы
        :return: None
        """
        with step('Проверка заголовка страницы на соответствие заданному тексту'):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.title_is(
                    text
                ),
                f'Заголовок страницы {text} не совпадает с {self._emulator.title}.'
            )

    def get_attribute(self, locator: Locator, attribute_name: str, has_check_visibility: bool = True) -> str:
        """
        Возвращает значение указанного атрибута из элемента.

        :param locator:
        :param attribute_name: Ключ атрибута в Html-коде
        :param has_check_visibility: Флаг проверки видимости элемента.
        :return: Значение атрибута
        """
        with step('Получение значения атрибута в элементе', locator.description):
            if has_check_visibility:
                self.check_element_visibility(locator)
            return self.find_element(locator).get_attribute(attribute_name)  # type: ignore

    def get_attribute_from_elements_with_identical_locators(
            self,
            locator: Locator,
            attribute_name: str
    ) -> Union[Tuple[str], Tuple[str, ...]]:
        """
        Находит элементы с одинаковым локатором, и возвращает кортеж со значениями указанного атрибута из них.

        :param attribute_name: Ключ атрибута в Html-коде.
        :param locator: Locator элементов.
        :return: Кортеж со значениями указанного атрибута из элементов.
        """
        with step('Получение значений атрибута во всех элементах на странице', locator.description):
            self.check_element_visibility(locator)
            attribute_values_from_elements = [
                element.get_attribute(attribute_name) for element in self.find_elements(locator)
            ]
            return tuple(attribute_values_from_elements)  # type: ignore

    def find_value_in_attribut(self, locator: Locator, attribute_name: str, expected_value: str) -> None:
        """
        Поиск на вхождение ожидаемого значения в значение атрибута
        :param locator: Locator элементов.
        :param attribute_name: Ключ атрибута в Html-коде.
        :param expected_value: Ожидаемое значение атрибута.
        :return: None
        """
        with step('Сравнение на вхождение ожидаемого и действительного значения в атрибуте элемента',
                  locator.description):
            self.check_element_presence_in_dom(locator)
            try:
                if expected_value in self.get_attribute(locator, attribute_name):
                    return None
                else:
                    self.screenshot_and_raise_error(
                        f"Элемент {locator.description} не содержит в атрибуте значение {expected_value}"
                    )
            except Exception as exc:
                self.__errors_handler(
                    error=exc,
                    desc=f'Необрабатываемое исключение. {attribute_name} {expected_value}, '
                         'не входит в настоящий атрибут'
                )

    def attributes_compare(self, locator: Locator, attribute_name: str, expected_value: str) -> None:
        """
        Прямое сравнивает ожидаемого и текущего значения атрибута
        :param locator: Locator элементов.
        :param attribute_name: Ключ атрибута в Html-коде.
        :param expected_value: ожидаемое значение атрибута.
        :return: None
        """
        with step('Сравнение ожидаемого и действительного значения в атрибуте элемента', locator.description):
            self.check_element_presence_in_dom(locator)
            try:
                if expected_value == self.get_attribute(locator, attribute_name):
                    return None
                else:
                    self.screenshot_and_raise_error(
                        f'В "{locator.description}" атрибут "{attribute_name}" не равен "{expected_value}"'
                    )
            except Exception as exc:
                self.__errors_handler(
                    error=exc,
                    desc=f'Необрабатываемое исключение. Атрибут {attribute_name} {expected_value}, '
                         'не равен настоящему атрибуту'
                )

    def count_of_elements(self, locator: Locator, has_check_visibility: bool = True) -> int:
        """
        Возвращает количество элементов на странице.

        :param locator: Locator
        :param has_check_visibility: Флаг проверки видимости элемента.
        :return: Количество элементов на странице с таким локатором
        """
        with step('Получение кол-ва элементов с одинаковым локатором', locator.description):
            if has_check_visibility:
                self.check_element_visibility(locator)
            return len(self.find_elements(locator))

    def check_element_presence_in_dom(self, locator: Locator) -> None:
        """
        Проверяем наличие элемента в DOM.

        :param locator: Locator - локатор элемента
        :return: None
        """
        with step('Проверка на наличие элемента в DOM', locator.description):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.presence_of_element_located(
                    locator()
                ),
                f'Элемент {locator.description} отсутствует в DOM страницы.'
            )

    def check_element_not_presence_in_dom(self, locator: Locator) -> None:
        """
        Проверяет отсутствие элемента в DOM.

        :param locator: Locator - локатор элемента
        :return: None
        """
        with step('Проверка на отсутствие элемента в DOM', locator.description):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until_not(
                EC.presence_of_element_located(
                    locator()
                ),
                f'Элемент {locator.description} присутствует в DOM страницы.'
            )

    def scroll_web_element_to_page_up(self, locator: Locator) -> None:
        """
        Берёт веб элемент и пролистывает его до верха страницы.

        :param locator: Locator - локатор элемента
        :return: None
        """
        with step('Нажатие на элемент и пролистывание его до верха страницы', locator.description):
            ActionChains(self._emulator).drag_and_drop_by_offset(
                self.find_element(locator),
                0,
                -300
            ).perform()

    def scroll_to_element_by_javascript(self, locator) -> None:
        """
        Прокручивает страницу до элемента с указанным локатором при помощи javascript скрипта.
        :param locator: Locator - локатор элемента
        :return:
        """
        with step('Прокручивает страницу до элемента с указанным локатором при помощи JavaScript', locator.description):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    self._emulator.execute_script('arguments[0].scrollIntoView(true)', self.find_element(locator))
                    return None
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Не получается прокрутить страницу до элемента: {locator.description}. '
                             'Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'Не получается прокрутить страницу до элемента: {locator.description}. Истекло количество попыток.'
            )

    def send_by_devtools_protocol(self, cmd: str, params: Any = None) -> Any:
        """
        Отправляет команду по DevTools протоколу на Webdriver Selenoid
        :param cmd: команда согласно DevTools протоколу.
        :param params: словарь с параметрами.

        :return: Возврат ответ от ChromeDriver после выполнения команды
        """
        if not params:
            params = dict()

        resource = "/session/%s/chromium/send_command_and_get_result" % self._emulator.session_id
        url = self._emulator.command_executor._url + resource  # type: ignore
        body = dumps({'cmd': cmd, 'params': params})
        return self._emulator.command_executor._request('POST', url, body)  # type: ignore

    def turn_off_internet(self) -> None:
        """
        Передает параметр через DevTool протокол для отлючения интернета
        :return: None
        """
        with step('Отключение интернета в браузере через DevTools протокол'):
            network_conditions = {
                'offline': True,
                'latency': 0,
                'downloadThroughput': 0,
                'uploadThroughput': 0,
                'connectionType': 'none'
            }

            self.send_by_devtools_protocol('Network.emulateNetworkConditions', network_conditions)
            self.send_by_devtools_protocol('Network.enable', {})

    def turn_on_internet(self) -> None:
        """
        Удаляет emulateNetworkConditions из DevTool, чтобы возобнавить работу интернета
        :return: None
        """
        with step('Включение интернета в браузере через DevTools протокол'):
            self.send_by_devtools_protocol('Network.disable', {})

    def clear_cash_and_logs(self) -> None:
        """
        Отчистка Логов и Кеша в Chrome Webdriver
        :return: None
        """
        self.send_by_devtools_protocol('Log.clear', {})
        self.send_by_devtools_protocol('Network.clearBrowserCache', {})

    def click_ok_alert(self) -> None:
        """
        Клик на всплывающее окно алерта
        :return: None
        """
        with step('Нажатие на всплывающее окно алерта'):
            CustomWebDriverWait(
                self,
                EXPLICITLY_TIMEOUT
            ).until(
                EC.alert_is_present(),
                'Алерт не отображается.'
            )

            try:
                self._emulator.switch_to.alert.accept()
            except Exception as exc:
                self.make_screenshot()
                exc.__traceback__ = None
                raise AssertionError(
                    'Невозможно кликнуть на всплывающий алерт'
                )

    def check_without_timeout_and_click(self, locator_one: Locator, locator_two: Locator) -> None:
        """
        Пытается достучаться до первого доступного локатара, в пределах ATTEMPTS_NUMBER
        :param locator_one: Locator - локатор элемента.
        :param locator_two: Locator - локатор элемента.
        :return: None
        """
        with step('Попытка достучаться (кликнуть) до первого ближайшего элемента',
                  f'{locator_two.description}; {locator_one.description}'):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    try:
                        self._emulator.find_element(*locator_two())
                        return None
                    except IGNORED_EXCEPTIONS:
                        self._emulator.find_element(*locator_one()).click()
                        return None
                except IGNORED_EXCEPTIONS:
                    sleep_poll_frequency()

    def sleep_until_update_attribute(self, locator: Locator, attribute_name: str, desired_value: str) -> None:
        """
        Ждет обновление значения атрибута, в пределах ATTEMPTS_NUMBER
        :param locator: Locator - локатор элемента.
        :param attribute_name: Ключ атрибута в Html-коде.
        :param desired_value: Ожидаемое значение атрибута
        :return: None
        """
        with step('Ожидание обновления значения атрибута', locator.description):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    if desired_value == self.get_attribute(locator, attribute_name):
                        return None
                    else:
                        sleep_poll_frequency()
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc='Необрабатываемое исключение.'
                    )
            self.screenshot_and_raise_error(
                f'{locator.description} не содержит в атрибуте {attribute_name} значение {desired_value}'
            )

    def compare_counts_of_two_locators(self, locator_one: Locator, locator_two: Locator) -> None:
        """
        Бросает ошибку если кол-во элемента(ов) локатора не сходится со вторым локатором

        :param locator_one: Locator - Первый локатор для сравнения.
        :param locator_two: Locator - Второй локатор для сравнения.
        """
        with step('Сравнение кол-ва элементов', f'{locator_one.description}; {locator_two.description}'):
            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    if self.count_of_elements(locator_one) == self.count_of_elements(locator_two):
                        return None
                    else:
                        sleep_poll_frequency()
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc='Необрабатываемое исключение, '
                             f'кол-во {locator_one.description} не равно {locator_two.description}'
                    )
            self.screenshot_and_raise_error(
                f'Количество элементов {locator_one.description} не равно {locator_two.description}'
            )

    def compare_counts_of_different_locators(self, locators: tuple, description: str = '') -> None:
        """
        Сравнивает количество элементов на странице из кортежа locators

        :param locators: кортеж локаторов
        :param description: Описание ошибки
        :return:
        """
        with step('Сравнение количество элементов на странице'):

            for _ in range(self.ATTEMPTS_NUMBER):
                try:
                    counts_of_elements = []
                    for locator in locators:
                        counts_of_elements.append(self.count_of_elements(locator))
                except Exception as exc:
                    self.__errors_handler(
                        error=exc,
                        desc=f'Необрабатываемое исключение, не удалось получить кол-во {locator.description}'
                    )
                assert len(set(counts_of_elements)) == 1, \
                    f'Количество элементов на странице не равно между собой: {description}'
                return None

    def compare_two_numbers(self, number_one: int, number_two: int, description: str = '') -> None:
        """
        Сравнивает два числа на равенство, если не равны бросает ошибку (AssertionError) с описанием

        :param number_one: Первое число для сравнения.
        :param number_two: Второе число для сравнения.
        :param description: Описание ошибки.
        """
        with step('Сравнение двух чисел'):
            if number_one == number_two:
                return None
            else:
                self.screenshot_and_raise_error(f'Числа не равны ({number_one} и {number_two}): {description}')

    def switch_to_iframe(self, locator: Locator) -> None:
        """
        Переключение на iframe по локатору

        :param locator: Локатор iframe
        :return: None
        """
        self.emulator.switch_to.frame(
            self.find_element(locator)
        )

    def switch_to_default_page(self) -> None:
        """
        Переключение с iframe на основную страницу

        :return: None
        """
        self.emulator.switch_to.default_content()
