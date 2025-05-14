from typing import TypeVar

# Переменная для аннотации методов класса Locator, возвращающих экземпляр Locator
T = TypeVar('T', bound='Locator')


class Locator:
    """
    Класс для удобного хранения и использования локаторов html.
    """

    def __init__(self, by: str, selector: str, description: str):
        """
        :param by: может иметь одно из значений полей класса By модуля Selenium
        :param selector: селектор, соответствующий заявленному полю by
        :param description: информативное описание локатора (страница, положение, состояние системы и т.п.)
        """
        if isinstance(by, str) and isinstance(selector, str) and isinstance(description, str):
            self._by = by
            self._selector = selector
            self._description = description
        else:
            raise TypeError('Неверный тип входного значения для построения локатора.')

    def __call__(self) -> tuple:
        """
        Вызов используется для передачи аргументов в стандартные методы объекта WebDriver.
        :return: кортеж с типом локатора и селектором
        """
        return self._by, self._selector

    def __str__(self) -> str:
        return f'{self._description} {self._selector}'

    def __repr__(self) -> str:
        return str(self)

    def replace_keys(self, has_streaks: bool = False, **kwargs) -> T:  # type: ignore
        """
        Некоторые локаторы могут требовать введения в них чисел или слов.

        :param has_streaks: Флаг необходимости добавления кавычек/апострофов к ставляемому фрагменту.
        :param kwargs: Указание названий и значений для вставок.
        :return: Локатор с вставками.
        """
        new_locator = self._selector
        for key, value in kwargs.items():
            if has_streaks:
                if '\'' in value and '"' in value:
                    raise ValueError('Невозможно обработать ставку содержащую кавычки и апострофы!')
                elif '"' in value:
                    value = f'\'{value}\''
                else:
                    value = f'"{value}"'
            new_locator = new_locator.replace(f'{{{key}}}', str(value))
        return Locator(self._by, new_locator, self._description)  # type: ignore

    @property
    def description(self) -> str:
        """
        Возвращаем описание локатора.

        :return: Описание локатора.
        """
        return self._description

    @property
    def selector(self) -> str:
        """
        Возвращаем селектор локатора.

        :return: Селектор локатора.
        """
        return self._selector
