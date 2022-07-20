# _*_ coding: utf-8

import re
from odf import teletype, text
from odf.opendocument import load, OpenDocumentText
from odf.element import Text, Element
from odf.text import P, H, Span
from pathlib import Path
from OdtTextPortion import TextPortion, TpList
from Utils import MyErrorOperation

# XML namespaces.
_ns_text = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
_ns_style = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
_ns_officeooo = 'http://openoffice.org/2009/office'
_ns_fo = 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
_ns_meta = 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0'


class Family:
    PARAGRAPH = 'paragraph'
    TEXT = 'text'
    ALL = (PARAGRAPH, TEXT)


class TagName:
    TEXT = 'Text'

    P = 'text:p'
    H = 'text:h'
    Span = 'text:span'

    LINEBREAK = 'text:line-break'
    SPACE = 'text:s'
    TAB = 'text:tab'
    LIST = 'text:list'
    LIST_ITEM = 'text:list-item'

    NOTE = 'text:note'
    NOTEBODY = 'text:note-body'

    TEXTBOX = 'draw:text-box'
    FRAME = 'draw:frame'
    AUTOSTYLES = 'office:automatic-styles'


class Style(object):
    def __init__(self, _name=None):
        if _name is None:
            return
        self.name = _name
        self.family = None
        self.is_autostyle = False
        self.is_default_style = False
        self.rsid = None
        self.parent_style = None
        self.font_name = None
        self.font_family = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_parent_for_auto_style(self):
        if self.is_autostyle:
            return self.parent_style
        else:
            return None


class Para(object):
    def __init__(self, _element: Element):
        self.element: Element = _element
        self.text: str = ''
        self.style_name: str = ''
        self.font_name: str = ''
        self.empty: bool = False
        self.in_frame: bool = False  # Содержимое врезки

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'P:{self.style_name}:{self.text}'


class Paragraph(object):
    def __init__(self, _element: Element):
        self.element: Element = _element
        self.tp_list: TpList = TpList()
        self.text: str = ''
        self.para_style: Style = Style()
        self.para_style_name: str = ''
        self.char_style_name: str = ''
        self.para_font_name: str = ''
        self.char_font_name: str = ''
        self.before_str: str = ''
        self.after_str: str = ''
        self.is_empty: bool = False  # Пустой абзац.
        self.into_frame: bool = False  # Содержимое врезки.
        self.into_list: bool = False  # Элемент списка.
        self.into_span: bool = False  # Внутри SPAN элемента.
        self.into_table: bool = False  # Содержимое таблицы.

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'P:{self.para_style_name}:{self.text}'

    def make_tp_list(self):
        # Обработка self.element, результат -> self.tp_list
        pass

    def get_string(self):
        # self.tp_list.make_string() -> self.text
        return f'{self.before_str}{self.text}{self.after_str}'


class Odt(object):
    # TODO: коррекция meta данных.
    # https://github.com/eea/odfpy/issues/105
    # Удалить, если есть,
    # лишние текстовые элементы (\n\n\n\n\) из мета-данных.

    def __init__(self, _odt=None):
        self.url = _odt
        self.p_odt = Path(_odt)
        self.extension = None
        self.converter = None
        self.style_font = None
        self.doc = load(self.url)
        self.auto_styles = self.doc.automaticstyles
        self.styles = self.doc.styles
        self.para_list = self.doc.getElementsByType(P)
        self.headers_list = self.doc.getElementsByType(H)
        self.spans_list = self.doc.getElementsByType(Span)

        self.styles_list = []
        self.styles_map = {}
        self.styles_handle()
        self.autostyles_handle()
        try:
            self.styles_list = self.styles_get_fonts_from_parent_style()
        except Exception as er:
            raise MyErrorOperation from er
        self.autostyles_define_all_parent_styles()

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url

    def make_tp_list(self) -> TpList:
        def note_handle(
                _note_element: Element,
                _out_list: TpList = None,
                _para_style_name: str = None,
                _into_span: bool = False) -> TpList:
            """Сноски обычные и концевые.

            :param _note_element:
            :param _out_list:
            :param _para_style_name:
            :param _into_span:
            :return:
            """

            _note_class = _note_element.getAttribute('noteclass')
            if _note_class in ['footnote', 'endnote']:
                if _note_element.childNodes and \
                        _note_element.childNodes[-1].tagName == TagName.NOTEBODY:
                    _note_para = _note_element.childNodes[-1].firstChild
                    _note_string = _note_para.firstChild.data
                    _tp_note = None
                    if _note_class == 'footnote':
                        _tp_note = TextPortion(_string=_note_string, _into_span=_into_span, _footnote=True)
                    elif _note_class == 'endnote':
                        _tp_note = TextPortion(_string=_note_string, _into_span=_into_span, _endnote=True)
                    _out_list.append(_tp_note)
            return _out_list

        def tab_handle(
                _out_list: TpList = None,
                _para_style_name: str = None,
                _into_span: bool = False) -> TpList:
            _tab_spaces: int = 4
            _tab_string = ' ' * _tab_spaces
            if len(_out_list) > 0:
                # _out_list = tp_list_add_text_to_last(_out_list, _tab_string)
                _out_list = _out_list.add_text_to_last(_tab_string)
            else:
                _tp_lbreak = TextPortion(_string=_tab_string, _par_style=_para_style_name)
                _out_list.append(_tp_lbreak)

            return _out_list

        def linebreak_handle(
                _out_list: TpList = None,
                _para_style_name: str = None,
                _into_span: bool = False) -> TpList:
            _lb_tex_string = '\\\\*%\n'

            if len(_out_list) > 0:
                _out_list = _out_list.add_text_to_last(_lb_tex_string)
            else:
                _tp_lbreak = TextPortion(_string=_lb_tex_string, _par_style=_para_style_name)
                _out_list.append(_tp_lbreak)
            return _out_list

        def space_handle(
                _space_element: Element,
                _out_list: TpList = None,
                _into_span: bool = False) -> TpList:
            # В XML единичный пробел в тексте - обычный текст.
            # В LO каждый дополнительный пробел - через space
            _space_amount: int = 0
            try:
                _space_amount = int(_space_element.getAttribute('c'))
            except TypeError:
                _space_amount = 1

            # NOTE: в дальнейшей обработке все пробелы - в один, для TeX.
            #  Уточнить в каком месте кода!
            if len(_out_list) > 0:
                # _out_list = tp_list_add_text_to_last(_out_list, ' ' * _space_amount)
                _out_list = _out_list.add_text_to_last(' ' * _space_amount)
            else:
                _tp_space = TextPortion(_string=' ' * _space_amount, _par_style=para_style_name)
                _out_list.append(_tp_space)
            return _out_list

        def span_handle(
                _span_element: Element,
                _out_list: TpList = None,
                _para_style_name: str = None,
                _char_style_name: str = None,
                _into_span: bool = False) -> TpList:

            char_style_name_ = _span_element.getAttribute('stylename')
            char_style = self.get_style_by_name(char_style_name_)
            assert char_style, f'No style element for style_name{char_style_name_}'
            if _char_style_name and _into_span and not char_style.is_autostyle:
                char_style_name = char_style_name_
            else:
                char_style_name = _char_style_name

            if _span_element.hasChildNodes():
                for _span_child in _span_element.childNodes:  # type: [Element, Text]
                    if type(_span_child) is Text:
                        _out_list = text_handle(
                            _text_element=_span_child,
                            _out_list=_out_list,
                            _para_style_name=_para_style_name,
                            _char_style_name=char_style_name,
                            _into_span=True,
                        )
                    elif type(_span_child) is Element:
                        _out_list = element_handle(
                            _element=_span_child,
                            _out_list=_out_list,
                            _para_style_name=_para_style_name,
                            _char_style_name=char_style_name,
                            _into_span=True,
                        )
            else:
                # NOTE: как пример, случай пустого абзаца,
                #  с одним пустым элементом span - выставлен стиль "киноварь"
                # print(f'SHORT SPAN type={type(_span_element)}')
                return _out_list

            return _out_list

        def element_handle(
                _element: Element = None,
                _out_list: TpList = None,
                _para_style_name: str = None,
                _char_style_name: str = None,
                _into_span: bool = False) -> TpList:

            try:
                char_style_name_ = _element.getAttribute('stylename')
            except ValueError:
                char_style_name = _char_style_name
                pass
            else:
                # char_style_name_ = char_style_name_.replace('_20_', ' ')
                char_style = self.get_style_by_name(char_style_name_)
                assert char_style, f'No style element for style_name{char_style_name_}'
                if not _char_style_name and _into_span and not char_style.is_autostyle:
                    char_style_name = char_style_name_
                else:
                    char_style_name = _char_style_name

            # ОБщий код для обработки Element.
            _element_tagname = _element.tagName
            if _element_tagname == TagName.LINEBREAK:
                _out_list = linebreak_handle(_out_list=_out_list, _into_span=_into_span)
            elif _element_tagname == TagName.TAB:
                _out_list = tab_handle(_out_list=_out_list, _para_style_name=_para_style_name, _into_span=_into_span)
            elif _element_tagname == TagName.SPACE:
                _out_list = space_handle(_space_element=_element, _out_list=_out_list, _into_span=_into_span)
            elif _element_tagname == TagName.NOTE:
                _out_list = note_handle(_note_element=_element, _out_list=_out_list, _into_span=_into_span)
            elif _element_tagname == TagName.Span:
                _out_list = span_handle(
                        _span_element=_element,
                        _out_list=_out_list,
                        _para_style_name=_para_style_name,
                        _char_style_name=char_style_name,
                        _into_span=_into_span
                    )

            return _out_list

        def text_handle(
                _text_element: Text = None,
                _out_list: TpList = None,
                _para_style_name: str = None,
                _char_style_name: str = None,
                _into_span: bool = False) -> TpList:

            # Обработка Text элемента
            # Взять span_style_name из родительского parent_node
            _parent_span_node_style_name = None
            char_style_name_ = None
            if _into_span:
                _parent_span_node: Element = _text_element.parentNode
                if not _char_style_name:
                    try:
                        _parent_span_node_style_name = _parent_span_node.getAttribute('stylename')
                        # Проверка на auto-default-style
                        _parent_span_node_style = self.get_style_by_name(_parent_span_node_style_name)
                        if _parent_span_node_style and _parent_span_node_style.is_autostyle:
                            # FIXME: для вложенных span элементов
                            #  с auto-styles проблема - символьный стиль остается
                            #  "пустым". В этом случае необходимо найти
                            #  родительский не-авто стиль.
                            _parent_span_node_style_name = find_parent_style_for_non_styled_in_text(_parent_span_node)

                    except ValueError:
                        pass
                    else:
                        char_style_name_ = _parent_span_node_style_name
                else:
                    char_style_name_ = _char_style_name
            if char_style_name_:
                char_style_name_ = char_style_name_.replace('_20_', ' ')
            _text_element_str = _text_element.data
            _tp = TextPortion(
                _string=_text_element_str,
                _par_style=_para_style_name,
                _char_style=char_style_name_,
                _into_span=_into_span,
            )
            _out_list.append(_tp)

            return _out_list

        # def list_handle(
        #         _text_element: Text = None,
        #         _out_list: TpList = None,
        #         _para_style_name: str = None,
        #         _char_style_name: str = None,
        #         _into_span: bool = False) -> TpList:
        #     return _out_list

        def find_parent_style_for_non_styled_in_text(_span_element: Element = None):
            _founded_style_name: str = ''
            return _founded_style_name
            # _parent_node: Element = _span_element.parentNode
            # _parent_node_style_name = _parent_node.getAttribute('name')
            # _parent_style_family = _parent_node.getAttribute('family')
            # _parent_style_parent_style_name = _parent_node.getAttribute('stylename')
            # if _parent_node_style_name:
            #     return _parent_node_style_name
            # if _parent_style_parent_style_name:
            #     return _parent_style_parent_style_name

            # Рекурсия.
            # return find_parent_style_for_non_styled_in_text(_parent_node)

        # Проход по всем параграфам и всем его элементам.
        # Возвращает список TexPortion
        nodes_ = self.doc.body.childNodes[0].childNodes
        out_list: TpList = TpList()

        def para_handle(_para, _into_list: bool = False):
            if _para.hasChildNodes():
                for _para_child in _para.childNodes:  # type: [Element, Text]
                    _tagname = _para_child.tagName
                    into_span_ = True if _tagname == TagName.Span else False
                    _type = type(_para_child)
                    if _type is Text:
                        _out_list = text_handle(
                            _text_element=_para_child,
                            _out_list=out_list,
                            _para_style_name=para_style_name,
                            _into_span=into_span_,
                        )

                    elif _type is Element:
                        _out_list = element_handle(
                            _element=_para_child,
                            _out_list=out_list,
                            _para_style_name=para_style_name,
                            _into_span=into_span_
                        )

            else:
                pass
            _new_para_tp = TextPortion(_string='\n', _par_style=para_style_name, _new_para=True)
            out_list.append(_new_para_tp)

        def para_style_name_handler(_para_element):
            _para_style_name: str = ''
            _para_style_name = _para_element.getAttribute('stylename')
            _para_style: Style = self.get_style_by_name(_para_style_name)

            if _para_style is None:
                return

            if _para_style.is_autostyle:
                if _para_style.is_default_style:
                    _para_style_name = 'default-style'
                else:
                    _para_style = self.get_style_by_name(_para_style.parent_style)
                    _para_style_name = _para_style.name
                    assert _para_style, f"Can't get parent for autostyle!"

            _para_style_name = _para_style_name.replace('_20_', ' ')

            return _para_style_name
        
        for _para in nodes_:
            tag_name = _para.tagName
            if tag_name == TagName.LIST:
                for _list_item in _para.childNodes:
                    for _list_item_para in _list_item.childNodes:
                        para_style_name = \
                            para_style_name_handler(_para_element=_list_item_para)
                        para_handle(_list_item_para, _into_list=True)

                continue

            elif tag_name not in [TagName.P, TagName.H]:
                continue
            para_style_name = para_style_name_handler(_para_element=_para)
            # Колонтитулы и пр.
            if para_style_name in \
                    ['Header left', 'Header right', 'Содержимое врезки ПервоеСловоСледСтр']:
                continue

            para_handle(_para)

        return out_list

    def set_converter(self, _converter):
        self.converter = _converter

    def set_style_font(self, _style_font):
        self.style_font = _style_font

    def set_extension(self, _extension):
        self.extension = f'.{_extension}'

    def find_parent_style_for_non_styled(self, _style: Element = None):
        _founded_style_name: str = ''
        _parent_style_obj: Element = _style.parentNode
        if _parent_style_obj.tagName == TagName.AUTOSTYLES:
            # Выход из рекурсии.
            _founded_style_name = 'default-style'
            return _founded_style_name
        else:
            _parent_style_name = _parent_style_obj.getAttribute('name')
            _parent_style_family = _parent_style_obj.getAttribute('family')
            _parent_style_parent_style_name = _parent_style_obj.getAttribute('parentstylename')
            if _parent_style_name:
                return _parent_style_name
            if _parent_style_parent_style_name:
                return _parent_style_parent_style_name

            # Рекурсия.
            return self.find_parent_style_for_non_styled(_parent_style_obj)

    def autostyles_define_all_parent_styles(self):
        # NOTE: не подходит для autostyles.
        #  У них у всех родитель _parent_style_obj.tagName == TagName.AUTOSTYLES
        for _style in self.auto_styles.childNodes:  # type: Element
            try:
                _name = _style.getAttribute('name')
            except AttributeError as er:
                continue
            _family = _style.attributes.get((_ns_style, 'family'))
            parent_style_name = _style.attributes.get((_ns_style, 'parent-style-name'))
            if not parent_style_name:
                parent_style_name = self.find_parent_style_for_non_styled(_style)
            assert parent_style_name, f'No parent style for autostyle: {_name}'
            style: Style = self.get_style_by_name(_name)
            assert style, f'No style(Style) for style: {_name}'
            style.parent_style = parent_style_name
            if parent_style_name == 'default-style':
                style.is_default_style = True

    def autostyles_handle(self):

        for _style in self.auto_styles.childNodes:  # type: Element
            try:
                _name = _style.getAttribute('name')
            except AttributeError as er:
                continue
            _family = _style.attributes.get((_ns_style, 'family'))
            _parent_style = _style.attributes.get((_ns_style, 'parent-style-name'))

            _rsid = None
            _font_name = None
            for _prop_node in _style.childNodes:
                if _family == Family.PARAGRAPH:
                    _rsid = _prop_node.attributes.get((_ns_officeooo, 'paragraph-rsid'))
                elif _family == Family.TEXT:
                    _rsid = _prop_node.attributes.get((_ns_officeooo, 'rsid'))
                try:
                    _font_name = _prop_node.attributes.get((_ns_style, 'font-name'))
                except AttributeError as er:
                    continue

            if _font_name:
                _font_name = re.sub(r'.*(Ponomar Unicode).*', r'\1', _font_name)
            # if _font_family:
            #     _font_family = re.sub(r'.*(Ponomar Unicode).*', r'\1', _font_family)

            style = Style(_name)
            style.is_autostyle = True
            style.family = _family
            style.parent_style = _parent_style
            style.rsid = _rsid
            style.font_name = _font_name
            self.styles_list.append(style)

    def styles_handle(self):
        # print('STYLES============')
        for _st in self.styles.childNodes:
            try:
                _style_name = _st.attributes.get((_ns_style, 'name'))
            except AttributeError as er:
                continue
            _style_family = _st.attributes.get((_ns_style, 'family'))
            _parent_style_name = _st.attributes.get((_ns_style, 'parent-style-name'))
            _font_name = None
            _font_family = None
            if _style_family in (Family.PARAGRAPH, Family.TEXT):
                if _style_family == Family.PARAGRAPH \
                        and not _style_name \
                        and _st.qname[1] == 'default-style':
                    _style_name = 'default-style'
                if _style_name == 'Standard':
                    _parent_style_name = 'default-style'

                for _elem in _st.childNodes:
                    try:
                        qname_ = _elem.qname[1]
                    except AttributeError as er:
                        continue
                    if qname_ == 'text-properties':
                        _font_name = _elem.attributes.get((_ns_style, 'font-name'))
                        _font_family = _elem.attributes.get((_ns_fo, 'font-family'))

                if _font_name:
                    _font_name = re.sub(r'.*(Ponomar Unicode).*', r'\1', _font_name)
                if _font_family:
                    _font_family = re.sub(r'.*(Ponomar Unicode).*', r'\1', _font_family)
                    # print(f'_font_name={_font_name}')

                style = Style(_style_name)
                style.family = _style_family
                style.parent_style = _parent_style_name
                style.font_name = _font_name
                style.font_family = _font_family
                self.styles_list.append(style)

    def get_style_by_name(self, _style_name):
        for _style_obj in self.styles_list:
            if _style_name == _style_obj.name:
                return _style_obj
        return None

    def styles_get_fonts_from_parent_style(self):
        _out_styles_list = []

        def walk_on_parent_styles(_style: Style = None):
            if _style.font_name:
                return _style.font_name
            try:
                if _style.parent_style:
                    _parent_style_name = _style.parent_style
                    _parent_style = self.get_style_by_name(_parent_style_name)
                    assert _parent_style, f'Can\'t get_parent style for style={_style}!'

                    if _parent_style.font_name:
                        return _parent_style.font_name
                    else:
                        _parent_font_name = walk_on_parent_styles(_parent_style)
                        if _parent_font_name:
                            return _parent_font_name
                        else:
                            return None
                else:
                    return None
            except AttributeError as err:
                raise MyErrorOperation from err

        for _style in self.styles_list:  # type: Style
            if _style.font_name is None \
                    and _style.family in (Family.PARAGRAPH, Family.TEXT):

                try:
                    _font_name = walk_on_parent_styles(_style)
                except Exception as er:
                    raise MyErrorOperation from er
                if _font_name:
                    _style.font_name = _font_name

            _out_styles_list.append(_style)
        return _out_styles_list

    def txt_handle(self, _element, _font):
        if type(_element) is Text:
            _txt = _element.data
            _txt_cnv = self.converter(_txt, _font_name=_font)
            _element.data = _txt_cnv
            # print(f'{_font}:{_txt_cnv}')
        return None

    def element_handle(self, _element):
        """Общий обработчик элементов (абзац, заголовок, span)

        :param _element:
        :return:
        """
        element_type = _element.tagName
        element_font = None
        element_style_name = _element.getAttribute('stylename')
        element_style = self.get_style_by_name(element_style_name)
        if element_style:
            element_font = element_style.font_name

        if element_type in (TagName.P, TagName.H):
            for _para_part in _element.childNodes:
                # Элементы непосредственно абзаца, вне span.
                self.txt_handle(_para_part, element_font)

        elif element_type == TagName.Span:
            _parent_node = _element.parentNode
            _parent_style_name = _parent_node.getAttribute('stylename')
            _parent_style = self.get_style_by_name(_parent_style_name)
            parent_node_font = None
            if _parent_style:
                parent_node_font = _parent_style.font_name

            for span_node in _element.childNodes:
                span_font = None
                if span_node.hasChildNodes():
                    # span_style_name = span_node.getAttribute('stylename')
                    span_style_name = span_node.attributes.get((_ns_style, 'stylename'))
                    span_style = self.get_style_by_name(span_style_name)
                    if span_style:
                        span_font = span_style.font_name

                    # Для текстовых стилей, у кот-х не указан шрифт.
                    if span_style and span_style.family == Family.TEXT and not span_font:
                        # Взять шрифт стиля parentNode.
                        span_font = parent_node_font
                else:
                    span_font = element_font
                    # Для текстовых стилей, у кот-х не указан шрифт.
                    if not span_font:
                        span_font = parent_node_font

                self.txt_handle(span_node, span_font)

    def spans_handle(self):
        """Обработчик элементов span.

        """
        for _span in self.spans_list:
            self.element_handle(_span)

    def paragraphs_handle(self):
        for _para in self.para_list:
            self.element_handle(_para)

    def headers_handle(self):
        for _header in self.headers_list:
            self.element_handle(_header)

    def set_font_for_all_styles(self):
        def set_font_to_style(_doc_style):
            if _doc_style and _doc_style.hasChildNodes():
                _text_prop = None
                for _elem in _doc_style.childNodes:
                    if _elem.qname[1] == 'text-properties':
                        _text_prop = _elem
                        # Атрибуты задаются без дефисов!!!
                        _text_prop.setAttribute('fontname', self.style_font)
                        _text_prop.setAttribute('fontfamily', self.style_font)
            # else:
            #     # Для стилей у которых не задано ничего.
            #     # TODO: добавить text-properties?
            #     # print(f'empty')
            #     # _name = _doc_style.attributes.get((_ns_style, 'name'))
            #     # style_obj = get_style_by_name(_name)

        for _style in self.styles_list:
            _doc_style = None
            if _style.font_name:
                if _style.name == 'default-style':
                    for _style_elem in self.styles.childNodes:
                        _style_family = _style_elem.attributes.get((_ns_style, 'family'))
                        _qname = _style_elem.qname[1]
                        if _qname == 'default-style' \
                                and _style_family == Family.PARAGRAPH:
                            _doc_style = _style_elem
                            break
                else:
                    _doc_style = self.doc.getStyleByName(_style.name)
                set_font_to_style(_doc_style)

    def convert_with_saving_format(self):
        """Конвертация текста в файле ODT.

        Абзацы, Заголовки, Span-элементы. Форматирование сохраняется.
        Результат записывается в файл *.cnv.odt
        :return: None
        """
        self.paragraphs_handle()
        self.headers_handle()
        self.spans_handle()

        # Замена шрифта в стилях.
        if self.style_font:
            self.set_font_for_all_styles()

        _suffix = '.cnv.odt'
        if self.extension:
            _suffix = self.extension

        new_odt = self.p_odt.with_suffix(_suffix)
        self.doc.save(new_odt.as_posix())

    def convert_text_only(self):
        """Конвертация текста в файле ODT.

        Конвертируется все содерржимое <body>.
        Результат записывается в файл *.cnv.odt
        :return: None
        """

        body = self.doc.body
        new_doc = OpenDocumentText()
        for _body_elem in body.childNodes:
            for _elem in _body_elem.childNodes:
                body_text = teletype.extractText(_elem)
                body_text = self.converter(body_text)
                para = text.P()
                teletype.addTextToElement(para, body_text)
                new_doc.text.addElement(para)
                # print(body_text)

        # Замена шрифта в стилях.
        if self.style_font:
            self.set_font_for_all_styles()

        _suffix = '.all.odt'
        if self.extension:
            _suffix = self.extension

        new_odt = self.p_odt.with_suffix(_suffix)
        new_doc.save(new_odt.as_posix())

    def get_text(self):
        out_text = ''
        body = self.doc.body
        for _body_elem in body.childNodes:
            for _elem in _body_elem.childNodes:
                body_text = teletype.extractText(_elem)
                out_text += f'{body_text}\n'
        return out_text

    def get_property_title(self):
        """Возвращает значение свойства документа title (DocumentProperties.Title)

        """
        _meta: Element = self.doc.meta
        _title_string = ''
        for _node in _meta.childNodes:
            if _node.tagName == 'dc:title':
                _title_string = _node.firstChild.data
                break
        return _title_string

    def get_meta_user_defiled_field(self, _meta_field_name: str = None):
        """Возвращает значение odt meta user-defined field (UserDefinedProperties).

        """
        _meta: Element = self.doc.meta
        _meta_string = ''
        for _node in _meta.childNodes:
            if _node.tagName == 'meta:user-defined':
                _attr_dic = _node.attributes
                _attr_name = _attr_dic.get((_ns_meta, 'name'))
                if _attr_name == f'{_meta_field_name}':
                    try:
                        _meta_string = _node.firstChild.data
                    except AttributeError as er:
                        pass
                    break
        return _meta_string

    def get_meta_running_header(self):
        # Колонтитул.
        return self.get_meta_user_defiled_field('RunningHeader')

    def get_meta_title_in_text(self):
        # Заголовок в тексте.
        return self.get_meta_user_defiled_field('TitleInText')


if __name__ == "__main__":
    odt = 'АкафистБогородице.odt'
    try:
        odt_obj = Odt(odt)
    except Exception as e:
        raise e

    print(odt_obj.get_meta_running_header())
    print(odt_obj.get_meta_title_in_text())
    print(odt_obj.get_property_title())
    # tp_list: TpList = odt_obj.make_tp_list()
    # tp_list = tp_list.open_and_close()
    # all_string = tp_list.make_string()
    # print(tp_list.__repr__())
    # all_string = replace_in_string_as_one_string(all_string)
    # print(all_string)
