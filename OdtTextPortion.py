import re

from typing import List
from Colors import (
    GREEN,
    FAIL,
    ENDC,
    OKBLUE,
    LCIAN,
)


class StyleName:
    class Para:
        TITLE = "Title"
        SUBTITLE = "Subtitle"
        TEXT_BODY = "Text body"
        SMALL_18 = "Малый 18"
        SMALL_18_WITHOUT_REDLN = "Малый 18 без красной строки"
        HIRMOS_18 = "Ирмос 18"
        SMALL_16 = "Малый 16"
        HIRMOS_16 = "Ирмос 16"
        INSERTION_NARROW = "Вставка узкая"
        LONG_LINE = "Длинная строка"
        WITHOUT_REDLN = "Без красной строки"
        HANG = "Обратный отступ"
        TEXT_BODY_WITH_HANG = "Основной текст с отступом"
        HANGS = "Отступы"
        FIRST_LINE_WITH_INDENT = "Первая строка с отступом"
        BY_CENTER = "По центру"
        STIH_BOLD = "Стих жирный"
        NOTES = "Заметки"
        CROSS = "Крест вверху"
        BIG_LETTRINE = "Абзац с большой буквицей"
        BIG_LETTRINE_WITH_SUBSCRIPT = "Абзац с большой буквицей и надстрочник"
        BIG_LETTRINE_WITH_TWO_SUBSCRIPTS = "Абзац с большой буквицей и два надстрочника"
        LETTRINE = "Абзац с буквицей"
        LETTRINE_WITH_SUBSCRIPT = "Абзац с буквицей и надстрочник"
        LETTRINE_WITH_TWO_SUBSCRIPTS = "Абзац с буквицей и два надстрочника"
        USTAV = "Устав"
        USTAV_LEFT = "Устав влево"
        USTAV_CENTER = "Устав по центру"
        GLAS = "Глас"
        DATE = "Дата и место"
        DATE_IN_TEXT = "Дата и место в тексте"
        RUS = "Русский текст"
        RUS_SINAKSAR = "Русский Синаксарь"
        RUS_SINAKSAR_LETTRINE = "Русский Синаксарь с буквицей"
        H1 = "Heading 1"
        H2 = "Heading 2"
        H3 = "Heading 3"
        H4 = "Heading 4"
        H5 = "Heading 5"
    
    class Char:
        NOSTYLE = "Без стиля символа"
        SMALL_18 = "Малый 18"
        KINOVAR_BIG_LETTRINE = "Киноварь Буквица большая"
        KINOVAR_BIG_LETTRINE_BLACK = "Киноварь Буквица большая черный"
        KINOVAR_INDICT = "киноварь индикт"
        KINOVAR_INDICT_BLACK = "киноварь индикт черный"
        KINOVAR = "киноварь"
        KINOVAR_BOLD = "киноварь жирная"
        KINOVAR_BlACK = "киноварь черная"
        KINOVAR_16 = "киноварь 16"
        KINOVAR_16_BLACK = "киноварь 16 черная"
        KINOVAR_18 = "киноварь 18"
        KINOVAR_18_BLACK = "киноварь 18 черная"
        KINOVAR_30 = "киноварь 30"
        SPACED = "разрядка"
        SPACED_BOLD = "разрядка жирная"
        SPACED_18 = "разрядка 18"
        SPACED_18_BOLD = "разрядка 18 жирная"
        SPACED_22 = "разрядка 22"
        SPACED_22_BOLD = "разрядка 22 жирная"
        RUS = "Русский текст"
        RUS_KINOVAR_SINAKSAR = "Киноварь Русский Синаксарь"
        HEBREW = "Еврейский"
        HEBREW_KIOVAR_18 = "Еврейский киноварь 18"
        GREEK = "Греческий"
        GREEK_KINOVAR = "Греческий киноварь"
        LATIN = "Латинский текст"
        LATIN_KINOVAR = "Латинский текст киноварь"


para_dic = {
    StyleName.Para.TITLE: {
        # TODO: перенести добавочный код в другое место (TEX-Init).
        'before': '\\renewcommand{\\TITLE}{}%\n'
                  '\\renewcommand{\\TITLERU}{}%\n'
                  '\\section[tocentry={\\TOCENTRY},head={\\TITLE}]{%\n',
        'after': '%\n}%%[END_section]\n'},
    StyleName.Para.SUBTITLE: {
        'before': '\\sSubtitle{%%[BEGIN_sSubtitle]\n',
        'after': '%\n}%%[END_sSubtitle]\n'},
    StyleName.Para.TEXT_BODY: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.SMALL_18: {
        'before': '\\Small{%%[BEGIN_Small]\n',
        'after': '%\n}%%[END_Small]\n'},
    StyleName.Para.SMALL_18_WITHOUT_REDLN: {
        'before': '\\Small{%%[BEGIN_Small]\n\\noindent%\n',
        'after': '%\n}%%[END_Small]\n'},
    StyleName.Para.HIRMOS_18: {
        'before': '\\Small{%%[BEGIN_Small]\n',
        'after': '%\n}%%[END_Small]\n'},
    StyleName.Para.SMALL_16: {
        'before': '\\Smaller{%%[BEGIN_Smaller]\n',
        'after': '%\n}%%[END_Smaller]\n'},
    StyleName.Para.HIRMOS_16: {
        'before': '\\Smaller{%%[BEGIN_Smaller]\n',
        'after': '%\n}%%[END_Smaller]\n'},

    StyleName.Para.INSERTION_NARROW: {
        'before': '\\FrameNarrow{%%[BEGIN_FrameNarrow]\n',
        'after': '%\n}%%[END_FrameNarrow]\n'},
    StyleName.Para.LONG_LINE: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.WITHOUT_REDLN: {
        'before': '\\Txt{%%[BEGIN_Txt]\n\\noindent%\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.HANG: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.TEXT_BODY_WITH_HANG: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.HANGS: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.FIRST_LINE_WITH_INDENT: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.BY_CENTER: {
        'before': '\\TxtC{%%[BEGIN_TxtC]\n',
        'after': '%\n}%%[END_TxtC]\n'},
    StyleName.Para.STIH_BOLD: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.NOTES: {
        'before': '\\Txt{%%[BEGIN_Txt]\n',
        'after': '%\n}%%[END_Txt]\n'},
    StyleName.Para.CROSS: {
        'before': '\\Cross%\n',
        'after': ''},
    StyleName.Para.BIG_LETTRINE: {
        'before': '\\culB{%%[BEGIN_culB]\n',
        'after': '%\n}%%[END_culB]\n'},
    StyleName.Para.BIG_LETTRINE_WITH_SUBSCRIPT: {
        'before': '\\culs{%%[BEGIN_culs]\n\\CULS{}',
        'after': '%\n}%%[END_culs]\n'},
    StyleName.Para.BIG_LETTRINE_WITH_TWO_SUBSCRIPTS: {
        'before': '\\culs{%%[BEGIN_culs]\n\\CULS{}',
        'after': '%\n}%%[END_culs]\n'},
    StyleName.Para.LETTRINE: {
        'before': '\\cul{%%[BEGIN_cul]\n',
        'after': '%\n}%%[END_cul]\n'},
    StyleName.Para.LETTRINE_WITH_SUBSCRIPT: {
        'before': '\\cul{%%[BEGIN_cul]\n',
        'after': '%\n}%%[END_cul]\n'},
    StyleName.Para.LETTRINE_WITH_TWO_SUBSCRIPTS: {
        'before': '\\cul{%%[BEGIN_cul]\n',
        'after': '%\n}%%[END_cul]\n'},
    StyleName.Para.USTAV: {
        'before': '\\ustav{%%[BEGIN_ustav]\n',
        'after': '%\n}%%[END_ustav]\n'},
    StyleName.Para.USTAV_LEFT: {
        'before': '\\ustavL{%%[BEGIN_ustavL]\n',
        'after': '%\n}%%[END_ustavL]\n'},
    StyleName.Para.USTAV_CENTER: {
        'before': '\\ustavC{%%[BEGIN_ustavC]\n',
        'after': '%\n}%%[END_ustavC]\n'},
    StyleName.Para.GLAS: {
        'before': '\\glas{%%[BEGIN_glas]\n',
        'after': '%\n}%%[END_glas]\n'},
    StyleName.Para.DATE: {
        'before': '\\DateAndPlace{%%[BEGIN_DateAndPlace]\n',
        'after': '%\n}%%[END_DateAndPlace]\n'},
    StyleName.Para.DATE_IN_TEXT: {
        'before': '\\DateAndPlaceInText{%%[BEGIN_DateAndPlaceInText]\n',
        'after': '%\n}%%[END_DateAndPlaceInText]\n'},

    StyleName.Para.RUS: {
        'before': '\\TxtRU{%%[BEGIN_TxtRU]\n',
        'after': '%\n}%%[END_TxtRU]\n'},
    StyleName.Para.RUS_SINAKSAR: {
        'before': '\\SinaksarRU{%%[BEGIN_SinaksarRU]\n',
        'after': '%\n}%%[END_SinaksarRU]\n'},
    StyleName.Para.RUS_SINAKSAR_LETTRINE: {
        'before': '\\SinaksarRUL{%%[BEGIN_SinaksarRUL]\n',
        'after': '%\n}%%[END_SinaksarRUL]\n'},

    StyleName.Para.H1: {
        'before': '\\hI{%%[BEGIN_hI]\n',
        'after': '%\n}%%[END_hI]\n'},
    StyleName.Para.H2: {
        'before': '\\hII{%%[BEGIN_hII]\n',
        'after': '%\n}%%[END_hII]\n'},
    StyleName.Para.H3: {
        'before': '\\hIII{%%[BEGIN_hIII]\n',
        'after': '%\n}%%[END_hIII]\n'},
    StyleName.Para.H4: {
        'before': '\\hIV{%%[BEGIN_hIV]\n',
        'after': '%\n}%%[END_hIV]\n'},
    StyleName.Para.H5: {
        'before': '\\hV{%%[BEGIN_hV]\n',
        'after': '%\n}%%[END_hV]\n'},
}

char_dic = {
    StyleName.Char.NOSTYLE: {
        'before': '',
        'after': ''},
    StyleName.Char.KINOVAR_BIG_LETTRINE: {
        'before': '\\KinovarBukvicaBig{',
        'after': '}'},
    StyleName.Char.KINOVAR_BIG_LETTRINE_BLACK: {
        'before': '\\KinovarBukvicaBigBlack{',
        'after': '}'},
    StyleName.Char.KINOVAR_INDICT: {
        'before': '\\KinovarIndyct{',
        'after': '}'},
    StyleName.Char.KINOVAR_INDICT_BLACK: {
        'before': '\\KinovarIndyctBlack{',
        'after': '}'},
    StyleName.Char.KINOVAR: {
        'before': '\\KI{',
        'after': '}'},
    StyleName.Char.KINOVAR_BOLD: {
        'before': '\\KinovarBold{',
        'after': '}'},
    StyleName.Char.KINOVAR_BlACK: {
        'before': '\\cub{',
        'after': '}'},
    StyleName.Char.KINOVAR_16: {
        'before': '\\KIsmaller{',
        'after': '}'},
    StyleName.Char.KINOVAR_16_BLACK: {
        'before': '\\cub{',
        'after': '}'},
    StyleName.Char.SMALL_18: {
        'before': '\\Small{',
        'after': '}'},
    StyleName.Char.KINOVAR_18: {
        'before': '\\KIsmall{',
        'after': '}'},
    StyleName.Char.KINOVAR_18_BLACK: {
        'before': '\\cub{',
        'after': '}'},
    StyleName.Char.KINOVAR_30: {
        'before': '\\KinovarXXX{',
        'after': '}'},
    StyleName.Char.SPACED: {
        'before': '\\CharSpaced{',
        'after': '}'},
    StyleName.Char.SPACED_BOLD: {
        'before': '\\CharSpacedBold{',
        'after': '}'},
    StyleName.Char.SPACED_18: {
        'before': '\\CharSpaced{',
        'after': '}'},
    StyleName.Char.SPACED_18_BOLD: {
        'before': '\\CharSpacedBold{',
        'after': '}'},
    StyleName.Char.SPACED_22: {
        'before': '\\CharSpaced{',
        'after': '}'},
    StyleName.Char.SPACED_22_BOLD: {
        'before': '\\CharSpacedBold{',
        'after': '}'},
    StyleName.Char.RUS: {
        'before': '\\Rus{',
        'after': '}'},
    StyleName.Char.RUS_KINOVAR_SINAKSAR: {
        'before': '\\KiSin{',
        'after': '}'},
    StyleName.Char.HEBREW: {
        'before': '\\Hebr{',
        'after': '}'},
    StyleName.Char.HEBREW_KIOVAR_18: {
        'before': '\\Hebr{',
        'after': '}'},
    StyleName.Char.GREEK: {
        'before': '\\Greek{',
        'after': '}'},
    StyleName.Char.GREEK_KINOVAR: {
        'before': '\\KI{',
        'after': '}'},
    StyleName.Char.LATIN: {
        'before': '\\Latin{',
        'after': '}'},
}

char_styles_kinovar_black = [
    StyleName.Char.KINOVAR_BlACK,
    StyleName.Char.KINOVAR_16_BLACK,
    StyleName.Char.KINOVAR_18_BLACK,
]

para_styles_small = [
    StyleName.Para.SMALL_18,
    StyleName.Para.SMALL_18_WITHOUT_REDLN,
    StyleName.Para.HIRMOS_18,
]


def _lcian(x: str) -> str:
    return LCIAN + x + ENDC


def _blue(x: str) -> str:
    return OKBLUE + x + ENDC


def _green(x: str) -> str:
    return GREEN + x + ENDC


def _red(x: str) -> str:
    return FAIL + x + ENDC


class TextPortion:
    """Класс для объектов TextPortion
    порция текста в odt xml с собственным стилевым и прочим форматированием.

    """
    def __init__(
            self,
            _string: str = None,
            _par_style: str = None,
            _char_style: str = None,
            _non_printed: bool = False,
            _new_para: bool = False,
            _new_line: bool = False,
            _footnote: bool = False,
            _endnote: bool = False,
            _is_span: bool = False,
            _into_span: bool = False,
            _into_list: bool = False,
    ):
        if not _string:
            _string = ''
        self.text: str = _string
        self.is_span: bool = _is_span
        self.into_span: bool = _into_span
        self.into_list: bool = _into_list
        if not _par_style:
            _par_style = ''
        self.par_style: str = _par_style
        if not _char_style:
            _char_style = ''
        self.char_style: str = _char_style
        self.non_print_text: bool = _non_printed
        self.footnote: bool = _footnote
        self.endnote: bool = _footnote
        self.newpara: bool = _new_para
        self.newline: bool = _new_line
        # Если атрибуты повторяют предыдущие/последующие.
        # Открыт для предыдущего
        self.opened_from_start: bool = False
        # Открыт для последующего
        self.opened_from_end: bool = False

    def __str__(self):
        return self.text

    def __repr__(self, _color: bool = True):
        # _type_str = ''
        def _no_color(_s):
            return _s
        green_ = blue_ = red_ = _no_color

        if _color:
            green_ = _green
            blue_ = _blue
            red_ = _red

        _footnote_str = 'F' if self.footnote else ''
        _span_str = 'S' if self.is_span else ''
        _into_span_str = 's' if self.into_span else ''
        _type_str = f'{_footnote_str}{_span_str}{_into_span_str}'
        _opened_from_start = red_('-') if self.opened_from_start else '⊲'
        _opened_from_end = red_('-') if self.opened_from_end else '⊳'
        _char_style_str = f'c:{self.char_style}' if self.char_style else ''
        # _par_style_str = f'p:{self.par_style}|' if self.char_style else f'P:{self.par_style}|'
        _par_style_str = f'p|' if self.char_style else f'P:{self.par_style}'
        return f'{_opened_from_start}[' \
               f'{_type_str}' \
               f'{_par_style_str}' \
               f'{green_(_char_style_str)}|' \
               f'{blue_(self.text)}]' \
               f'{_opened_from_end}'

    def open_start(self):
        # Открыть для предыдущего
        self.opened_from_start = True

    def close_start(self):
        # Закрыть для предыдущего
        self.opened_from_start = False

    def open_end(self):
        # Открыть для последующего
        self.opened_from_end = True

    def close_end(self):
        # Закрыть для последующего
        self.opened_from_end = False


TpListType = List[TextPortion]


class TpList(TpListType):
    def __init__(self):
        super(TpList, self).__init__()

    def __str__(self):
        list_ = [str(x) for x in self]
        return ''.join(list_)

    def __repr__(self, _color: bool = True):
        # _delim = '•'
        _delim = '\n'
        if _color:
            _list = [x.__repr__() for x in self]
        else:
            _list = [x.__repr__(_color=False) for x in self]
        return _delim.join(_list)

    def make_string(self) -> str:
        # Сборка строки всего док-та
        out_string = ''
        # Начиная с первого абзаца
        _first_para_style = self[0].par_style

        _first_tags_dic = para_dic.get(_first_para_style)
        if not _first_tags_dic:
            _first_tags_dic = para_dic.get(StyleName.Para.TEXT_BODY)
        # assert _first_tags_dic, f'Не заданы правила для стиля {_first_para_style}'
        _first_tag_before = _first_tags_dic.get('before', '')
        # assert _first_tag_before, f'Не задано before правило для стиля {_first_para_style}'
        out_string += _first_tag_before

        # После Нового абзаца выставить флаг нового абзаца,
        # и занести значение para style для нового абз.
        _new_para_flag: bool = False
        for i, _t in enumerate(self):  # type: (int, TextPortion)

            # Текст сносок.
            if _t.footnote:
                _before = '\\footnote{'
                _after = '}'
                _text: str = _t.text

                _lbreak = '\\\\*%\n'
                if _text.endswith(_lbreak):
                    _text = _text[: -len(_lbreak)]
                    _after = '}' + _lbreak

                out_string += _before + _text + _after
                continue

            _para_style = _t.par_style
            _char_style = _t.char_style
            _para_tags_dic = para_dic.get(_para_style)
            if not _para_tags_dic:
                _para_tags_dic = para_dic.get(StyleName.Para.TEXT_BODY)
            _para_before = _para_tags_dic.get('before', '')
            _para_after = _para_tags_dic.get('after', '')
            _char_tags_dic = {}
            _char_before = ''
            _char_after = ''
            if _char_style:
                _char_tags_dic = char_dic.get(_char_style)
                if _char_tags_dic:
                    _char_before = _char_tags_dic.get('before', '')
                    _char_after = _char_tags_dic.get('after', '')

            # TODO: обработка абзацев внутри списка.
            #  Вариант: выделить отдельный класс для списка именно абзацев.
            #  А внутри абзаца уже список TextPortion.
            #  Тогда можно каждый абзац обрабатывать отдельно,
            #  в соответствии со свойствами-полями.

            if _new_para_flag:
                out_string += _para_before
            if not _t.newpara:
                # Обработка tp, содержащих text portions
                # Если tp "открыт" с какой-либо из сторон,
                # то с этой стороны не добавлять тэг.
                # Обрамлять ли тэгами с обоих концов?
                # Для некоторых случаев - нет.

                # Для абзацных стилей с красным шрифтом не отображать выделения
                # символьными киноварными красными стилями.
                # FIXME: для Абзац с буквицей - только для первого слова!
                #  иначе ВСЕ выделения внутри пропадут.
                # Для Абзац с( большой)? буквицей выделение снимается после, .
                if re.match(r'^(Дата и место|Устав|Глас|Heading)', _para_style) \
                        and _char_style.startswith('киноварь') \
                        and _char_style not in char_styles_kinovar_black:
                    _char_before = _char_after = ''

                # Не обрамлять как параграф, а использовать как символьный стиль.
                if (
                        _para_style.startswith('Устав')
                        or _para_style.startswith('Глас')
                ) and _char_style.startswith('киноварь 16'):
                    _char_before = '\\Smaller{'
                    _char_after = '}'
                # Для "Малый 18", "Ирмос 18" выделение "киноварь 18"
                # не обрамлять \KIsmall, а \KI.
                if _para_style in para_styles_small \
                        and _char_style.startswith('киноварь 18'):
                    _char_before = '\\KI{'
                    _char_after = '}'

                if _t.opened_from_start:
                    _char_before = ''
                if _t.opened_from_end:
                    _char_after = ''

                out_string += f'{_char_before}{_t.text}{_char_after}'
                _new_para_flag = False
            else:
                out_string += f'{_para_after}\n'
                _new_para_flag = True

        return out_string

    def add_text_to_last(self, _string: str = None):
        if len(self) == 0:
            raise f'No tp elements in list!'

        _tp_last = self[-1]
        if _tp_last:
            _text = _tp_last.text
            _text += _string
            _tp_last.text = _text
        return self

    def open_and_close(self):
        # Анализ и открытие/закрытие элементов списка TextPortions
        # Если у предыдущего параметры не меняются,
        # то открыть end у предыдущего и открыть start у текущего.
        for i, _t in enumerate(self):
            if i == 0:
                continue
            _t_previous: TextPortion = self[i-1]
            _t_next = None
            try:
                _t_next = self[i+1]
            except IndexError:
                pass

            _t_current: TextPortion = _t
            if _t_current.footnote:
                # Если внутри is_span элемента,
                #  то открыть предыдущий и последующий.
                if _t_previous.into_span \
                        and _t_next and _t_next.into_span \
                        and _t_previous.char_style == _t_next.char_style:
                    _t_previous.open_end()
                    _t_next.open_start()

                continue

            # Следующий с одинаковым символным стилем.
            if _t_current.char_style == _t_previous.char_style \
                    and not _t_current.newpara:
                _t_previous.open_end()
                _t_current.open_start()

            # Span внутри span.
            # Если "киноварь черная( \d+)" то открывать только сам этот tp.
            # Исключить открытие "киноварь" между двумя "киноварь черная( \d+)"
            if _t_next and _t_previous \
                    and _t_current.into_span \
                    and _t_previous.into_span \
                    and _t_next.into_span \
                    and _t_previous.char_style == _t_next.char_style \
                    and not (
                    _t_previous.char_style.startswith('1киноварь черная')
                    or _t_next.char_style.startswith('1киноварь черная')
                    ):
                _t_previous.open_end()
                _t_current.close_start()
                _t_current.close_end()
                _t_next.open_start()

        return self
