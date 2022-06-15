from __future__ import annotations
import re
from shutil import copy2
from pathlib import Path
from Utils import *
from Colors import bcolors

OKGREEN = bcolors.OKGREEN
GREEN = bcolors.GREEN
FAIL = bcolors.FAIL
ENDC = bcolors.ENDC
OKBLUE = bcolors.OKBLUE
LCIAN = bcolors.LCIAN

COLOR_NO = f'{bcolors.FAIL}NO{bcolors.ENDC}'
COLOR_OK = f'{bcolors.OKGREEN}OK{bcolors.ENDC}'
COLOR_PLUS_PAR = f'{bcolors.OKGREEN}[+]{bcolors.ENDC}'
COLOR_EXISTS = f'{bcolors.FAIL}EXISTS{bcolors.ENDC}'
COLOR_NOT_EXISTS = f'{bcolors.FAIL}NOT EXISTS{bcolors.ENDC}'
COLOR_MINUS_PAR = f'{bcolors.FAIL}[-]{bcolors.ENDC}'
COLOR_EXLAM_MARK_PAR = f'{bcolors.FAIL}[!]{bcolors.ENDC}'
COLOR_EXLAM_MARK = f'{bcolors.FAIL}!{bcolors.ENDC}'

dots = '.' * 5

pwa = 72  # Ширина для выравнивания вывода
pw = 60
pwc = pw + 9  # для выравнивания в случае одного цветного фрагмента
pwcc = pw + 18  # для выравнивания в случае 2-х цветных фрагментов


def lcian(x: str) -> str:
    return LCIAN + '[' + x + ']' + ENDC


def green(x: str) -> str:
    return GREEN + '[' + x + ']' + ENDC


def csl_odt2tex(
        odt_path: Path = None,
        copy_from_init: bool = False,
        color: bool = False,
        title: str = '',
        title_ru: str = '',
):
    """Конвертация ODT->TEX для CSL-текста.

    Odt файл (filename.odt) конвертируется в TeX файл filename.init.tex.
    Если указано через опцию copy_from_init,
    filename.init.tex копируется в файл filename.tex.
    :param odt_path:
    # :param tex_init_url:
    :param copy_from_init:
    :param color: Цветной вывод (для отладки).
    :param title: Заголовок (csl)
    :param title_ru: Заголовок (Русский гражданский)
    :return:
    """

    debh = 'tex_init'
    titlo_s = 'ⷭ҇'
    zvatelce = '҆'
    iso = '҆́'
    apostrof = '҆̀'
    cu_cap_letters_text = \
        "АБВГДЕЄѢЖЗЅꙀИІѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦЧШЩЪЫЬЮѦꙖЯѮѰ"
    cu_small_letters_text = \
        "абвгдеєѣжзѕꙁиіѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ"
    cu_letters = cu_cap_letters_text + cu_small_letters_text
    # titlo = '҃'
    _accents = f'{titlo_s}|{zvatelce}|{iso}|{apostrof}'
    _rus_regex_avikos_str = \
        r"""(?xu)
        (
            (?:\s+|^|«)  # м.б. в начале предложения.
            [АВИКОСУЯавикосуя]
            \}?  # если внутри макроса.
        )
        \s+
        (\w)  # первая буква следующего слова. 
        """
    _csl_regex_avikos_str = r'''(?xu)
        (
            (?:\\KI\{)?
            [АИѠаиѡ]
            ҆ # zvatelce
            [,:]?
            \}?
          | # 
            (?:\s+|^|«)
            (?:
                (?:\\KI\{)?  
                [ВКСвкс]
                \}?
                ъ
              | 
                (?:\\KI\{)?
                [ѿѾѼѽ]
                \,?
                \}?
            )
          | # Для случаев \KI{з҃.~В}ъ~нощѝ
            ~
            (?:
             [ВКСвкс]}ъ
             |[ѿѾѼѽ]}
             |[АИѠаиѡ]҆}
            )
          | # с исо и апостроф
            [єиюѧ](҆́|҆̀)
          #| \s+ѽ\,
          #| ~Ѽ~} 
        )
        \s+
    '''
    regs_multi = [
        [r'(\\ \\ \* %\n)\[', r'\1\\lbrack{}', 'mxs'],
        # Киноварь первой буквы в абзаце с буквицами.
        [r'(\\culB?\{%%\[BEGIN_culB?\]\n)\\KI\{(\w+?)\}', r'\1\2', 'mxs'],
        [r'Трⷪ҇ц', r'\\Troic{}', 'x'],
        [r'Трⷪ҇ч', r'\\Troich{}', 'x'],
        [r'Трⷭ҇т', r'\\Trisvjat{}', 'x'],
        [r'Прⷪ҇ро́', r'\\Proro{}', 'x'],
        # Кроме случаев буквицы.
        [r'\\(culB?){%%\[BEGIN_culB?\]\n\\Troic{}', r'\\\1{%%[BEGIN_\1]\nТрⷪ҇ц', 'mxs'],
        [r'\\(culB?){%%\[BEGIN_culB?\]\n\\Troich{}', r'\\\1{%%[BEGIN_\1]\nТрⷪ҇ч', 'mxs'],
        [r'\\(culB?){%%\[BEGIN_culB?\]\n\\Trisvjat{}', r'\\\1{%%[BEGIN_\1]\nТрⷭ҇т', 'mxs'],
        [r'\\(culB?){%%\[BEGIN_culB?\]\n\\Proro{}', r'\\\1{%%[BEGIN_\1]\nПрⷪ҇ро́', 'mxs'],
    ]
    rus_regex_avikosuja = re.compile(_rus_regex_avikos_str)
    csl_regex_avikosuja = re.compile(_csl_regex_avikos_str)

    odt_tmp_path = odt_path.with_suffix('.tmp.odt')
    tex_path = odt_path.with_suffix('.tex')
    tex_init_url = odt_path.with_suffix('.init.tex')

    def tex_init_text_process_line_by_line(_tex_init_url: Path):
        import fileinput
        _debh = 'tex_init_text_process_line_by_line'
        _str_info = f'Обработка (построчная) {green(_tex_init_url.name)} '
        print(f'{_str_info:.<{pwc}}', end='')

        if not _tex_init_url.exists():
            print(f'{COLOR_NO} File {_tex_init_url.name} NOT EXISTS!')
            raise MyErrorOperation(f'{debh}.{_debh}: File {_tex_init_url.name} NOT EXISTS!')

        _russian_para_flag: bool = False
        for line in fileinput.input(files=[_tex_init_url], inplace=True):

            if re.match(r'^\\(SinaksarRUL?|TxtRU).*$', line):
                _russian_para_flag = True
            if re.match(r'}%%\[.*END_(TxtRU|SinaksarRU).*', line):
                _russian_para_flag = False

            # Аналог АВИКОСУЯ
            # TODO: ??? перенести в OdtTextPortion.TpList.make_string()
            #  тогда без TEX команд.
            line = csl_regex_avikosuja.sub(r'\1~', line)
            if _russian_para_flag:
                line = rus_regex_avikosuja.sub(r'\1~\2', line)

            line = re.sub(r'(?u)^(Конда́къ|І҆́косъ|Пѣ́снь)\s+([авгдєѕзиѳі]҃|[авг]҃і)', r'\1~\2', line)
            line = re.sub(r'(?ui)(глаⷭ҇)\s+([авгдєѕзи]҃)', r'\1~\2', line)
            line = re.sub(r'(?u)^И҆\s+нн҃ѣ:$', r'И҆~нн҃ѣ:', line)
            line = re.sub(r'(?u)\\KI(?:small)?{\*}', r'\\AR', line)
            line = re.sub(r'(?u)(renewcommand{\\TITLE}{)(})', fr'\1{title}\2', line)
            line = re.sub(r'(?u)(renewcommand{\\TITLERU}{)(})', fr'\1{title_ru}\2', line)
            line = re.sub(r'(?u)\\CULS{}(..)', r'\\CULS{\1}', line)
            line = re.sub(r'(?u)(~[Ѽѽ])~}', r'\1}~', line)

            # Киноварь для первой буквы греческого слова (начало).
            line = re.sub(
                r'(?u)\\KI{(.)}\\Greek{',
                r'\\Greek{\\KIGR{\1}', line)
            # Извлечение из \KI{} одной (первой) буквы слова
            # (с надстрочниками).
            line = re.sub(
                r'(?u)\\KI{([' + cu_letters + ']' + rf'(?:{_accents})?' + r')}', r'\\KI \1', line)

            # Киноварь для первой буквы греческого слова (завершение).
            line = re.sub(r'(?u)\\KIGR', r'\\KI', line)
            print(line, end='')  # В строке уже есть '\n'.

        print(f'{COLOR_OK}')

    def tex_init_text_process_multiline(_tex_init_url: Path):
        _debh = 'tex_init_text_process_multiline'
        _str_info = f'Обработка (многострочная) {green(_tex_init_url.name)} '
        print(f'{_str_info:.<{pwc}}', end='')
        try:
            regex_sub_in_whole_txt_file(tex_init_url.as_posix(), _regs_list=regs_multi)
        except re.error as r_er:
            print(f'{COLOR_NO}')
            raise MyErrorOperation(f'{debh}.{_debh}: Error regex! {r_er}')
        else:
            print(f'{COLOR_OK}')

    def copy_odt_to_tmp():
        _debh = 'copy_odt_to_tmp'
        _str_info = f'Copy {green(odt_path.name)} -> {green(odt_tmp_path.name)} '
        print(f'{_str_info:.<{pwcc}}', end='')
        try:
            copy2(odt_path, odt_tmp_path)
        except Exception as _e:
            print(COLOR_NO)
            raise MyErrorOperation(f'{debh}.{_debh}: Error copy {odt_path} -> {odt_tmp_path}! {_e}')
        else:
            print(f'{COLOR_OK}')

    def remove_tmp_odt():
        _debh = 'remove_tmp_odt'
        _str_info = f'Удаление {green(odt_tmp_path.name)} '
        print(f'{_str_info:.<{pwc}}', end='')
        try:
            odt_tmp_path.unlink()
        except Exception as _e:
            print(COLOR_NO)
            raise MyErrorOperation(f'{debh}.{_debh}: Error remove tmp {odt_tmp_path}! {_e}')
        else:
            print(f'{COLOR_OK}')

    def odt2tex_styled(_odt_path: Path, _tex_init_url: Path = None):
        """Получение TeX файла из ODT.

        Без запуска Libre Office. На основе стилей.

        :param _odt_path:
        :param _tex_init_url:
        :return:
        """
        from OdtTextPortion import TpList
        from ProcessOdtByXML import Odt

        def record_init_tex_file(_string: str = None, _url: Path = None):
            # Запись в TEX файл
            # Обрабатывается 0001.tmp.odt
            # Конвертированный текст -> tex/0001.init.tex
            _str_info = f'Запись {green(_url.name)} '
            print(f'{_str_info:.<{pwc}}', end='')
            try:
                with open(_url, mode='wt', encoding='utf-8') as f:
                    f.write(f'{_string}')
            except OSError as err:
                print(COLOR_NO)
                # print(f'Ошибка записи файла: {_url.name}!')
                raise MyErrorOperation from err
            else:
                print(f'{COLOR_OK}')
                # print(f'Файл: {_url.name} записан!')

        _debh = 'odt2tex styled'
        try:
            odt_obj = Odt(_odt_path)
        except Exception as er:
            raise er
        tp_list: TpList = odt_obj.make_tp_list()
        tp_list = tp_list.open_and_close()
        all_string = tp_list.make_string()
        all_string = replace_in_string_as_one_string(all_string)
        try:
            record_init_tex_file(_string=all_string, _url=_tex_init_url)
        except MyError as er:
            raise er

    global LCIAN, GREEN, COLOR_NO, COLOR_OK, COLOR_EXLAM_MARK_PAR, \
        COLOR_MINUS_PAR, COLOR_PLUS_PAR, COLOR_EXISTS, ENDC

    if not color:
        LCIAN = ''
        GREEN = ''
        ENDC = ''
        COLOR_OK = 'OK'
        COLOR_NO = 'NO'
        COLOR_EXISTS = 'EXISTS'

    print(f'Create Init.TEX file from ODT for {lcian(odt_path.name)}')
    print('-'*20)

    # title = db.get_field_value(_code=code, _field_name=Fields.TITLE_IN_TEXT)
    # title_ru = db.get_field_value(_code=code, _field_name=Fields.TITLE)

    copy_odt_to_tmp()

    try:
        odt2tex_styled(_odt_path=odt_tmp_path, _tex_init_url=tex_init_url)
    except MyError as e:
        raise e

    try:
        remove_tmp_odt()
    except MyError as e:
        raise e

    # Многострочная обработка текста.
    try:
        tex_init_text_process_multiline(tex_init_url)
    except MyError as e:
        raise e

    # Обработка текста построчно.
    try:
        tex_init_text_process_line_by_line(tex_init_url)
    except MyError as e:
        raise e

    def _copy_from_init():
        _debh = 'copy_from_init'
        _str_info = f'Copy {green(tex_init_url.name)} -> {green(tex_path.name)} '
        print(f'{_str_info:.<{pwcc}}', end='')
        try:
            copy2(tex_init_url, tex_path)
        except Exception as _e:
            print(COLOR_NO)
            raise MyErrorOperation(f'{debh}.{_debh}: Error copy {tex_init_url} -> {tex_path}! {_e}')
        else:
            print(f'{COLOR_OK}')

    if copy_from_init:
        _copy_from_init()


def regex_sub_in_whole_txt_file(_file: str = None, _regs_list=None, _search='', _replace='', _flags=0, _amount=0):
    """Поиск и замена (regex) в текстовом файле (in-place)

    :param _file: Путь к файлу
    :param _regs_list: Список рег.выр-й
    :param _search: Выражение поиска (r'\\d')
    :param _replace: Выражение замены
    :param _flags: строка флагов 'mxsu'
    :param _amount: int, def=0
    :return:
    """
    debh = 'regex_sub_in_whole_txt_file'
    check_args_and_raise([_file], f'{debh}')

    import re
    import functools
    import operator

    if _regs_list is None:
        _regs_list = []

    def string_to_rflags(_flags_str):
        """Переводит строку re-флагов 'mxs' в число, соответствующее сумме re-флагов

        :param _flags_str: Строка флагов
        :return: Сумма
        """

        def flags_summing(_flags_list) -> int:
            return functools.reduce(operator.or_, _flags_list)

        flags_list = []
        # Составление списка флагов из строки
        if _flags_str != 0 and type(_flags_str) is str:
            if 'u' in _flags_str:
                flags_list.append(re.U)
            if 'x' in _flags_str:
                flags_list.append(re.X)
            if 'm' in _flags_str:
                flags_list.append(re.M)
            if 's' in _flags_str:
                flags_list.append(re.S)

            _rflags = flags_summing(flags_list)
            return _rflags
        else:
            return None

    # Read in the file
    try:
        with open(_file, encoding='utf-8', mode='r') as file:
            filedata = file.read()
    except Exception as e:
        raise MyErrorOperation(f'{debh}: Error oprn {_file}! {e}')

    _regs_list_inner = []
    if not _regs_list:
        _regs_list_inner.append([_search, _replace, _flags, _amount])
    else:
        _regs_list_inner = _regs_list

    for _reg_rec in _regs_list_inner:
        _search_str = ''
        _replace_str = ''
        _flags_str_or_int = 0  # используется как временное хранилище для строки флагов если она задана в списке.
        _flags_rflags = 0  # будет передан как флаг в re.compile
        _amount_int = 0
        _len_of_rec = len(_reg_rec)

        if _len_of_rec == 2:
            _search_str, _replace_str = _reg_rec
        elif _len_of_rec == 3:
            _search_str, _replace_str, _flags_str_or_int = _reg_rec
        elif _len_of_rec == 4:
            _search_str, _replace_str, _flags_str_or_int, _amount_int = _reg_rec

        if type(_flags_str_or_int) is str:
            _flags_rflags = string_to_rflags(_flags_str_or_int)
        elif type(_flags_str_or_int) is int:
            _flags_rflags = _flags_str_or_int

        try:
            # rx объект с учетом флагов.
            re_obj = re.compile(_search_str, flags=_flags_rflags)
        except (TypeError, AttributeError, re.error) as e:
            raise MyErrorOperation(f'{debh}: Ошибка компиляции regex-шаблона! {e}')

        # Замена
        filedata = re_obj.sub(_replace_str, filedata, _amount_int)

    # Применить изменения.
    try:
        with open(_file, encoding='utf-8', mode='w') as file:
            file.write(filedata)
    except Exception:
        raise MyErrorOperation(f'{debh}: Error open and write to file: {_file}!')

    return None


def replace_in_string_as_one_string(_one_string: str) -> str:
    # !!! Весь текст - одна строка. Новые абзацы - \n

    _one_string = _one_string.replace('\\tableofcontents', '\\TABLEOFCONTENTS')

    _one_string = re.sub(r'(\S)\\cub{(\s+)', r'\1\2\\cub{', _one_string)
    _one_string = re.sub(r'\s+//', r'\\DC', _one_string)
    _one_string = re.sub(r'\s+/', r'\\Dv', _one_string)
    _one_string = re.sub(r'—', '---', _one_string)
    _one_string = re.sub(r'\s+---', '~---', _one_string)
    _one_string = re.sub(r'\\Dv~---', r'\\Dv ---', _one_string)

    # line = re.sub(r'\s{2,}', ' ', line)  # в \s попадает \n!!!
    _one_string = re.sub(r' {2,}', ' ', _one_string)
    _one_string = re.sub('ї', 'ї', _one_string)
    _one_string = re.sub('ѷ', 'ѷ', _one_string)
    _one_string = re.sub(r' {2,}', r'~', _one_string)
    _one_string = re.sub(r' ', r'\\,', _one_string)
    # Пробелы в конце строки.
    _one_string = re.sub(r'\s+%\n', '%\n', _one_string)
    # Linebreak два или более подряд -> в один.
    _one_string = re.sub(r'(\\\\\*%\n)+', r'\\\\*%\n', _one_string)
    return _one_string
