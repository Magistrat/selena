from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException


# Игнорируемые ошибки
IGNORED_EXCEPTIONS = (
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

# Как долго нужно спать между вызовами метода, при явном ожидании
POLL_FREQUENCY = 0.1

# Явное ожидание для отклика элемента
EXPLICITLY_TIMEOUT = 12.0

# Директория для создания скриншотов
SCREENSHOTS_DIRECTORY = 'screenshots'

# Расширение скриншота
SCREENSHOTS_EXTENSION = 'png'
