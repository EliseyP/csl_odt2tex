# _*_ coding: utf-8
"""
Классы ошибок
Функции проверки аргументов
с вощможностью генерировать исключения или возвращать bool(непустые аргументы)
"""


class MyError(Exception):
    """Общий класс ошибок"""


class MyErrorNoArgs(MyError):
    """Нет аргументов"""


class MyErrorNoArgsNone(MyErrorNoArgs):
    """Нет аргументов - None"""
    def __init__(self, message=''):
        _out_string = ''
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}Arg is None!'
        super().__init__(self.message)


class MyErrorNoArgsEmpty(MyErrorNoArgs):
    """Нет аргументов - Empty"""
    def __init__(self, message='', _type: str = None):
        if not message:
            message = ''
        if not _type:
            _type = ''
        _out_string = ''
        _type_str = ''
        if _type:
            _type_str = f' ({_type})'
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}Arg{_type_str} is Empty!'
        super().__init__(self.message)


class MyErrorModules(MyError):
    """Проблемы с модулями"""


class MyErrorOperation(MyError):
    """Неудачное выполнение операции"""


class MyErrorSettings(MyError):
    """Неудачная операция с настройками."""
    """Неудачная операция с настройками."""


class MyErrorSettingsRead(MyErrorSettings):
    """Неудачная операция с чтением настроек."""


class MyErrorSettingsWrite(MyErrorSettings):
    """Неудачная операция с сохранением настроек."""


class MyErrorPathNoExists(MyErrorOperation):
    """Путь не существует."""


class MyErrorSqlite(MyErrorOperation):
    """Sqlite errors"""


class MyErrorSoffice(MyErrorOperation):
    """Soffice bin errors"""
    def __init__(self, message='', _type: str = None):
        if not message:
            message = ''
        if not _type:
            _type = ''
        _out_string = ''
        _type_str = ''
        if _type:
            _type_str = f' ({_type})'
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}Soffice bin{_type_str} not found!'
        super().__init__(self.message)


class MyErrorSqliteLocked(MyErrorSqlite):
    """Sqlite DB locked"""
    # База; данных заблокирована!
    def __init__(self, message=''):
        _out_string = ''
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}База данных заблокирована!'
        super().__init__(self.message)


def check_args_handler(_args_list=None, _type_out='', _string=''):
    # Raise or return if one arg is None or Emty
    if _args_list is None:
        _args_list = []
    assert _args_list, f'Invalid usage: no arg list for checking!'
    if _string is None:
        _string = ''
    for _arg in _args_list:
        _type = type(_arg)
        if _arg is None:
            if _type_out == 'return':
                return False
            elif _type_out == 'raise':
                raise MyErrorNoArgsNone(_string)
        elif (_type is str and _arg == '') or \
                (_type is list and _arg == []) or \
                (_type is tuple and _arg == ()) or \
                (_type is dict and _arg == {}) or \
                (_type is set and _arg == set()):
            if _type_out == 'return':
                return False
            elif _type_out == 'raise':
                raise MyErrorNoArgsEmpty(_string, _type.__name__)
    return True


def check_args_and_raise(_args_list=None, _string=''):
    """Проверка аргументов и Raise if one arg is None or Empty.

    :param _args_list: спикок аргументов для проверки.
    :param _string: строка для вывода.
    """
    assert _args_list, f'check_args_and_raise: Invalid usage: no arg list for checking!'
    check_args_handler(_args_list=_args_list, _string=_string, _type_out='raise')


def check_args(_args_list=None) -> bool:
    """Проверка аргументов и return bool


    **False** if one arg is None or Empty\n
    **True** if all not None or not Empty

    :param _args_list: спикок аргументов для проверки.
    :return: bool
    """
    assert _args_list, f'check_args: Invalid usage: no arg list for checking!'
    return check_args_handler(_args_list=_args_list, _type_out='return')
