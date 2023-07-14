#!/usr/bin/env python
import os
import re
import shutil
import subprocess
import tkinter
from tkinter import (
    HORIZONTAL, VERTICAL, DISABLED, NORMAL, NONE, N, S, E, W, CHAR

)
from pathlib import Path
import argparse
from shutil import copy
from CslOdt2Tex import csl_odt2tex
from utils.breezypythongui import EasyFrame, TextArea
from Utils import *


"""
Скрипт для быстрого конвертирования ODT->TEX
с возможностью компиляции в PDF (XeLaTeX).

Использование: csl2tex.py [-b] [-p] [-d] odt-filename [odt-filename]  
  
  -g      - gui make PDF dialog.
  -G      - только для запуска диалога из LibreOffice.
  -p      - make PDF.
  -b      - black color PDF.
  -T      - Не удалять TeX-каталог сборки pdf.
  -I      - Из ODT получать только .init.tex    
  -d DIR  - каталог с TeX стилями (churchslavichymn.sty etc) и прочими вспомогательными файлами 
            (как правило, каталог, в котором находится этот скрипт). 
"""

dots = '.' * 5


class MyEasyFrame(EasyFrame):
    """Небольшие изменения"""

    def addTextArea(self, text, row, column, rowspan=1, columnspan=1,
                    width=80, height=5, wrap=NONE, no_x_scrollbar=False):
        # ADD - без скроллбара по горизонтали.
        """Creates and inserts a multiline text area at the row and column,
        and returns the text area.  Vertical and horizontal scrollbars are
        provided."""

        Tkinter = tkinter
        frame = Tkinter.Frame(self)
        frame.grid(row=row, column=column,
                   columnspan=columnspan, rowspan=rowspan,
                   sticky=N+S+E+W)
        self.columnconfigure(column, weight=1)
        self.rowconfigure(row, weight=1)
        xScroll = Tkinter.Scrollbar(frame, orient=HORIZONTAL)
        if not no_x_scrollbar:
            xScroll.grid(row=1, column=0, sticky=E+W)
        yScroll = Tkinter.Scrollbar(frame, orient=VERTICAL)
        yScroll.grid(row=0, column=1, sticky=N+S)
        area = TextArea(frame, text, width, height,
                        xScroll.set, yScroll.set, wrap)
        area.grid(row=0, column=0,
                  padx=5, pady=5, sticky=N+S+E+W)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        xScroll["command"] = area.xview
        yScroll["command"] = area.yview
        return area


def create_parser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        '-d', '--data_dir',
        nargs=1,
        action="append",
        metavar="DATA DIR",
        help='Каталог с TeX стилями (churchslavichymn.sty etc) '
             'и прочими вспомогательными файлами '
             '(как правило, каталог, в котором находится этот скрипт).'
    )
    _parser.add_argument(
        dest='filenames',
        metavar='filename',
        nargs='+'
    )
    _parser.add_argument(
        '-g', '--gui',
        action='store_true',
        help='Run make pdf simple dialog',
        default=False,
    )
    _parser.add_argument(
        '-G', '--from_office',
        action='store_true',
        help='Run from LibreOffice',
        default=False,
    )
    _parser.add_argument(
        '-b', '--black',
        action='store_true',
        help='Bold black color PDF',
        default=False,
    )
    _parser.add_argument(
        '-p', '--pdf',
        action='store_true',
        help='Make PDF',
        default=False,
    )
    _parser.add_argument(
        '-T', '--tex_dir',
        action='store_true',
        help="Don't delete TeX dir",
        default=False,
    )
    _parser.add_argument(
        '-I', '--init_only',
        action='store_true',
        help="Only create init.tex file. No compile.",
        default=False,
    )
    # _parser.add_argument(
    #     '-v', '--version',
    #     help='Версия',
    #     action="store_true",
    # )
    # _parser.add_argument(
    #     '-D', '--debug',
    #     nargs='?',
    #     action="append",
    #     metavar="PARAMS",
    #     help="Some debug [with debug PARAMs]"
    # )
    return _parser


def main(_odt_from_office: str = None):
    class Params:
        # Default values.
        def __init__(self, _odt_file):
            if Path(_odt_file).is_absolute():
                self.parent: str = Path(_odt_file).parent.as_posix()
                self.odt_path = Path(_odt_file)
            else:
                self.parent: str = os.getcwd()
                self.odt_path = Path(self.parent).joinpath(_odt_file)
            self.odt: str = _odt_file
            self.tmp_dir_name: str = f'{self.odt_path.name}.tex'
            _tex_name: Path = self.odt_path.with_suffix('.tex')
            self.tex_file: str = \
                _tex_name.parent.joinpath(self.tmp_dir_name).joinpath(_tex_name.name).as_posix()
            _pdf_name: Path = self.odt_path.with_suffix('.pdf')
            self.pdf_file: str = _pdf_name.name  # .as_posix()
            self.pwidth = '210mm'
            self.pheight = '297mm'
            self.toppmarg = '1.7cm'
            self.toppmarg_num: float = 1.7  # cm
            self.botpmarg = '2.0cm'
            self.botpmarg_num: float = 2.0  # cm
            self.outpmarg = '2.0cm'
            self.outpmarg_num: float = 2.0  # cm
            self.innpmarg = '2.0cm'
            self.innpmarg_num: float = 2.0  # cm
            self.cover = '0mm'
            self.cover_num: float = 0  # mm
            self.fontsize = '20pt'
            self.fontfamily = 'ponomar'
            self.nodigraphkinovar = 'true'
            self.kinovarcolor = 'red'
            if _black:
                self.kinovarcolor = 'boldblack'
            self.engine = 'xelatex'
            self.underscore: bool = False
            if self.odt.find('_') != -1:
                self.underscore = True
            self.tex_dir_keep: bool = _tex_dir_keep
            self.init_only: bool = _init_only

    class SingleString:
        def __init__(self, _params):
            # self.underscore = _underscore
            self.underscore_str = ''
            if _params.underscore:
                self.underscore_str = "\\catcode`\\_=12\\relax"
            _single_string = rf"""\documentclass[
pwidth={_params.pwidth},%A4=210x297; A5=148x210
pheight={_params.pheight},%A4=210x297; A5=148x210
toppmarg={_params.toppmarg},
botpmarg={_params.botpmarg},
outpmarg={_params.outpmarg},
innpmarg={_params.innpmarg},
cover={_params.cover},% припуск под корешок
]{{churchslavichymnsbook}}
\usepackage[
fontsize={_params.fontsize},
nodigraphkinovar={_params.nodigraphkinovar},
single=true,
kinovarcolor={_params.kinovarcolor},%red,boldblack,grey
fontfamily={_params.fontfamily},%ponomar,triodion,pochaevsk,acaphist,fedorovsk,vilnius
]{{churchslavichymn}}
{self.underscore_str}

\hfuzz=5pt
\begin{{document}}
\input{{hyphens.tex}}
% compile single only
\input{{{_params.tex_file}}}
\end{{document}}"""
            self.text = _single_string

        def get_text(self):
            return self.text

    class MsgTk(EasyFrame):
        """messageBox, но с закрытием родительского окна."""
        def __init__(self, _title='Csl_odt2TeX', _string=None, _w=40):
            super().__init__(self)
            root = self.master
            # Закрывает родительский фрейм.
            root.withdraw()
            self.messageBox(title=_title, message=_string, width=_w)
            root.destroy()

    class MakePdfDialog(MyEasyFrame):
        def __init__(self, _title='Csl_odt2TeX', _params: Params = None):
            from tkinter import END
            from tkinter.font import Font

            def row_inc():
                # Для автоматического увеличения номера ряда.
                nonlocal row
                row += 1

            super().__init__(
                # width=MAIN_WINDOW_WIDTH,
                # resizable=False
            )
            self.params = _params
            font = Font(family="Verdana", size=12)

            # Main window parameters.
            # self.setResizable(False)
            self.setTitle('Csl_odt2tex - Make PDF')
            root = self.master
            _crossblack_img = _data_dir_p.joinpath("crossblack.png")
            try:
                self.tk.call('wm', 'iconphoto', root, tkinter.PhotoImage(file=f'{_crossblack_img}'))
            except tkinter.TclError:
                pass

            # Widgets:
            # tex_file.
            row = 0
            self.addLabel(text='TeX File:', row=row, column=0, font=font)

            row_inc()
            tex_file_path = Path(self.params.parent).joinpath(self.params.tex_file).as_posix()
            self.ta_tex_file_path = self.addTextArea(
                text=f'{tex_file_path}',
                row=row, column=0, columnspan=2,
                height=3,  # 3 строки.
                wrap=CHAR,
                no_x_scrollbar=True,
            )

            # fontsize.
            row_inc()
            self.addLabel(text='Fontsize:', row=row, column=0, font=font)
            self.tf_fontsize = self.addTextField(
                text=self.params.fontsize, row=row, column=1, width=10)
            self.tf_fontsize.configure(justify='right')

            # kinovarcolor.
            row_inc()
            self.addLabel(text='Kinovarcolor:', row=row, column=0, font=font)
            self.cb_kinovarcolors = self.addCombobox(
                text="",
                values=("red", "boldblack", "gray"),
                row=row, column=1,
            )
            self.cb_kinovarcolors.setText(self.params.kinovarcolor)

            # Margins.
            # Top pmargin.
            row_inc()
            self.addLabel(text='Top margin (cm):', row=row, column=0, font=font)
            self.tf_topmargin = self.addFloatField(
                value=self.params.toppmarg_num, row=row, column=1)
            self.tf_topmargin.configure(justify='right')

            # Bot pmargin.
            row_inc()
            self.addLabel(text='Bottom margin (cm):', row=row, column=0, font=font)
            self.tf_botmargin = self.addFloatField(
                value=self.params.botpmarg_num, row=row, column=1)
            self.tf_botmargin.configure(justify='right')

            # Out pmargin.
            row_inc()
            self.addLabel(text='Outer margin (cm):', row=row, column=0, font=font)
            self.tf_outmargin = self.addFloatField(
                value=self.params.outpmarg_num, row=row, column=1)
            self.tf_outmargin.configure(justify='right')

            # Inner pmargin.
            row_inc()
            self.addLabel(text='Inner margin (cm):', row=row, column=0, font=font)
            self.tf_innmargin = self.addFloatField(
                value=self.params.innpmarg_num, row=row, column=1)
            self.tf_innmargin.configure(justify='right')

            # Cover pmargin.
            row_inc()
            self.addLabel(text='Cover (mm):', row=row, column=0, font=font)
            self.tf_cover = self.addFloatField(
                value=self.params.cover_num, row=row, column=1)
            self.tf_cover.configure(justify='right')

            # fontfamily
            row_inc()
            self.addLabel(text='Font family:', row=row, column=0, font=font)
            self.cb_fontfamily = self.addCombobox(
                text="",
                values=("ponomar", "triodion", "pochaevsk", 'acaphist', 'fedorovsk', 'vilnius'),
                row=row, column=1,
            )
            self.cb_fontfamily.setText(self.params.fontfamily)

            # Page format a4 a5, own
            row_inc()
            self.addLabel(text='Page format:', row=row, column=0, font=font)
            self.rb_group = self.addRadiobuttonGroup(
                row=row, column=1,
                orient=HORIZONTAL,
            )
            self.rb_a4 = self.rb_group.addRadiobutton(
                "A4", command=self.rb_a5_selected_handler)
            self.rb_a5 = self.rb_group.addRadiobutton(
                "A5", command=self.rb_a5_selected_handler)
            self.rb_other = self.rb_group.addRadiobutton(
                "Другой", command=self.rb_other_selected_handler)
            # Select one of the buttons in the group
            self.rb_group.setSelectedButton(self.rb_a4)
            self.rb_selected = self.rb_a4
            self.rb_selected_init()

            # pwidth.
            row_inc()
            self.addLabel(text='Page width:', row=row, column=0, font=font)
            # TODO: addFloatField()
            self.tf_pwidth = self.addTextField(
                text=self.params.pwidth, row=row, column=1, state=DISABLED)
            self.tf_pwidth.configure(justify='right')

            # pheight.
            row_inc()
            self.addLabel(text='Page height:', row=row, column=0, font=font)
            # TODO: addFloatField()
            self.tf_pheight = self.addTextField(
                text=self.params.pheight, row=row, column=1, state=DISABLED)
            self.tf_pheight.configure(justify='right')

            # nodigraphkinovar.
            row_inc()
            self.addLabel(text='Nodigraphkinovar:', row=row, column=0, font=font)
            self.chb_nodigraphkinovar = self.addCheckbutton(text='', row=row, column=1, )
            if self.params.nodigraphkinovar == 'true':
                self.chb_nodigraphkinovar.select()

            # Keep TeX dir.
            row_inc()
            self.addLabel(text='Keep TeX dir:', row=row, column=0, font=font)
            self.chb_tex_dir_keep = self.addCheckbutton(text='', row=row, column=1, )
            if self.params.tex_dir_keep:
                self.chb_tex_dir_keep.select()

            # Make init only.
            row_inc()
            self.addLabel(text='Make Init TeX file only', row=row, column=0, font=font)
            self.chb_init_only = self.addCheckbutton(text='', row=row, column=1, )
            if self.params.init_only:
                self.chb_init_only.select()

            # Engine
            row_inc()
            self.addLabel(text='TeX Engine:', row=row, column=0, font=font)
            self.cb_engine = self.addCombobox(
                text="",
                values=("xelatex", "lualatex"),
                row=row, column=1,
            )
            self.cb_engine.setText(self.params.engine)

            # Alternate PDF name
            row_inc()
            self.addLabel(text='PDF name:', row=row, column=0, font=font)
            row_inc()
            self.ta_pdf_name = self.addTextArea(
                text=self.params.pdf_file,
                row=row, column=0, columnspan=2,
                height=2,  # 2 строки.
                wrap=CHAR,
                no_x_scrollbar=True,
            )

            # Buttons.
            row_inc()
            self.btn_make_pdf = \
                self.addButton(text="Make PDF", row=row, column=0, command=self.make_pdf)
            self.btn_close = \
                self.addButton(text="Close", row=row, column=1, command=self.close)

            # Список виджетов, для которых нужно установить шрифт.
            # TODO: для всей формы одной строкой?
            _widgets_4font_list = [
                self.ta_tex_file_path,
                self.tf_fontsize,
                self.cb_kinovarcolors,
                self.tf_topmargin,
                self.tf_botmargin,
                self.tf_outmargin,
                self.tf_innmargin,
                self.tf_cover,
                self.cb_fontfamily,
                self.rb_a4,
                self.rb_a5,
                self.rb_other,
                self.tf_pwidth,
                self.tf_pheight,
                self.ta_pdf_name,
                self.cb_engine,
                self.btn_make_pdf,
                self.btn_close,

            ]
            for _widget in _widgets_4font_list:
                _widget['font'] = font

        def rb_selected_init(self):
            self.rb_selected = self.rb_group.getSelectedButton()

        def rb_a4_selected_handler(self):
            self.tf_page_geometry_turner(True)

        def rb_a5_selected_handler(self):
            self.tf_page_geometry_turner(True)

        def rb_other_selected_handler(self):
            self.tf_page_geometry_turner(False)

        def tf_page_geometry_turner(self, _state: bool = True):
            # По умолчанию - отключены.
            _state_str = DISABLED if _state else NORMAL
            self.tf_pwidth.config(state=_state_str)
            self.tf_pheight.config(state=_state_str)

        def apply_params_changes(self):
            def msg_wrong_format(_parameter, _string):
                self.messageBox(message=f'Неверный формат!\n{_string}: {_parameter}')

            _fontsize = self.tf_fontsize.getText()
            # validation.
            if re.match(r'\d+(\.\d+)?pt', _fontsize):
                self.params.fontsize = _fontsize
            else:
                msg_wrong_format(_fontsize, 'fontsize')
                return False

            self.params.kinovarcolor = self.cb_kinovarcolors.getText()

            self.params.toppmarg = f'{self.tf_topmargin.getValue()}cm'
            self.params.botpmarg = f'{self.tf_botmargin.getValue()}cm'
            self.params.outpmarg = f'{self.tf_outmargin.getValue()}cm'
            self.params.innpmarg = f'{self.tf_innmargin.getValue()}cm'
            self.params.cover = f'{self.tf_cover.getValue()}mm'

            self.params.fontfamily = self.cb_fontfamily.getText()

            self.rb_selected_init()
            if self.rb_selected == self.rb_a4:
                self.params.pwidth = '210mm'
                self.params.pheight = '297mm'
            elif self.rb_selected == self.rb_a5:
                self.params.pwidth = '148mm'
                self.params.pheight = '210mm'
            elif self.rb_selected == self.rb_other:
                _pwidth = self.tf_pwidth.getText()
                if re.match(r'\d+(\.\d+)?(cm|mm)', _pwidth):
                    self.params.pwidth = _pwidth
                else:
                    msg_wrong_format(_pwidth, 'pwidth')
                    return False

                _pheight = self.tf_pheight.getText()
                if re.match(r'\d+(\.\d+)?(cm|mm)', _pheight):
                    self.params.pheight = _pheight
                else:
                    msg_wrong_format(_pheight, 'pheight')
                    return False

            _nodigraphkinovar = self.chb_nodigraphkinovar.isChecked()
            self.params.nodigraphkinovar = 'true' if _nodigraphkinovar else 'false'

            tex_dir_keep_ = self.chb_tex_dir_keep.isChecked()
            self.params.tex_dir_keep = True if tex_dir_keep_ else False

            init_only_ = self.chb_init_only.isChecked()
            self.params.init_only = True if init_only_ else False

            self.params.engine = self.cb_engine.getText()

            _pdf_name = self.ta_pdf_name.getText().strip()
            if _pdf_name:
                if _pdf_name.endswith('.pdf'):
                    self.params.pdf_file = _pdf_name
                else:
                    msg_wrong_format(_pdf_name, 'pdf_name')
                    return False

            return True

        def make_pdf(self):
            _result_is_ok = self.apply_params_changes()
            if not _result_is_ok:
                return

            make_single_tex(_params=self.params)
            try:
                _result_flag = make_pdf(_params=self.params)
            except MyError as er_:
                # print(f'Error making pdf:\n  {er_}')
                raise MyErrorOperation(f'Error making pdf:\n  {er_}')
            else:
                if _result_flag:
                    MsgTk(_string=f'OK!\n'
                                  f'File: {_result_flag}\n'
                                  f'compiled ({self.params.kinovarcolor})!')
                else:
                    MsgTk(_string=f'ERROR Pdf compling!')

        def close(self):
            self.master.destroy()

    # Default location - directory of this script.
    data_dir = Path(os.path.realpath(__file__)).parent.as_posix()
    tex_files = [
        'churchslavichymnsbook.cls',
        'churchslavichymn.sty',
        'crossblack.png',
        'cross.png',
        'hyphens.tex',
    ]

    parser = create_parser()
    args = parser.parse_args()
    _black = args.black
    _pdf = args.pdf
    _gui = args.gui
    _from_office = args.from_office
    _files_list = args.filenames
    _tex_dir_keep = args.tex_dir
    _init_only = args.init_only
    if _init_only:
        _tex_dir_keep = True
    if _odt_from_office is not None:
        _files_list = [_odt_from_office]
    # List of data tex files creation.
    data_files = []
    if args.data_dir:
        _data_dir = args.data_dir
    else:
        _data_dir = data_dir

    _data_dir_p = Path(_data_dir)
    if _data_dir.startswith("~/"):
        _data_dir_p = Path.expanduser(_data_dir_p)

    if not _data_dir_p.exists():
        print(f'No {_data_dir} directory exists!')
        return
    for _data_file in tex_files:
        _data_file_p = _data_dir_p.joinpath(_data_file)
        if not _data_file_p.exists():
            print(f'ERROR! No data file {_data_file} exists!')
            return
        else:
            data_files.append(_data_file_p)

    cwd = os.getcwd()

    def make_tex_init(_odt: str, _params: Params = None):
        _odt_path = Path(cwd).joinpath(_odt)
        if not _odt_path.exists():
            _err_string = f'No file exists: {_odt_path}'
            if _gui:
                MsgTk(_title='Csl_odt2TeX', _string=f'ERROR!\n{_err_string}')
            print(f'ERROR! {_err_string}')
            return None
        print(f'Convert {_odt_path}')
        csl_odt2tex(
            odt_path=_odt_path,
            color=True,
            copy_from_init=True,
        )
        return _odt_path.with_suffix('.init.tex')

    def make_pdf_gui(_params: Params):
        _window = MakePdfDialog(_params=_params)
        _window.mainloop()

    def make_single_tex(_params: Params = None):
        _odt_file = _params.odt
        if _black:
            _params.kinovarcolor = 'boldblack'

        single_string = SingleString(_params=_params).get_text()
        _single_tex = Path(_params.parent).joinpath('single.tex')
        try:
            with open(_single_tex, 'wt') as f:
                f.write(single_string)
        except OSError as e:
            print(f"ERROR! Cant't write single.tex.\n{e}")
            return None
        else:
            return _single_tex.as_posix()

    def make_pdf(_params: Params = None, _black: bool = False):
        """Make PDF in tmp dir, and copy pdf file to workdir. """

        _odt_file: str = _params.odt
        _engine = _params.engine
        _single_tex = 'single.tex'
        _parent_path = Path(_params.parent)
        _single_tex_path = _parent_path.joinpath(_single_tex)
        _src_tex = _parent_path.joinpath(_odt_file).with_suffix('.tex')
        _src_init_tex = _parent_path.joinpath(_odt_file).with_suffix('.init.tex')
        _tmp_dir_parent = _parent_path
        _tmp_dir_path = Path(_tmp_dir_parent).joinpath(_params.tmp_dir_name)
        if not (_params.init_only and _tmp_dir_path.exists()):
            #     # Оставить возможность работать с уже отредактированным .tex файлом
            #     # (чтобы сохранить изменения сделанные ранее вручную).
            print(f'Create tmp dir {dots} ', end='')
            try:
                _tmp_dir_path.mkdir(exist_ok=True)
            except Exception as _err:
                print('NO')
                raise MyErrorOperation(f'Error creating tmp dir:\n  {_err}')
            else:
                print('OK')

        for _data in data_files:
            try:
                copy(_data, _tmp_dir_path)
            except Exception as _err:
                raise MyErrorOperation(f'Error copy {_data} file:\n  {_err}')

        try:
            copy(_single_tex_path, _tmp_dir_path)
        except FileNotFoundError as _err:
            err_str_ = f'Error copy _single_tex_path file:\n  {_err}'
            raise MyErrorOperation(err_str_)

        init_only = _params.init_only
        src_in_tmp = _tmp_dir_path.joinpath(_src_tex.name)
        if (
                not init_only
                or (init_only and not src_in_tmp.exists())
        ) and _tmp_dir_path.is_dir():
            # Оставить возможность работать с уже отредактированным .tex файлом
            # (чтобы сохранить изменения сделанные ранее вручную).
            print(f'Copy {_src_tex.name} to tmp_dir {dots} ', end='')
            try:
                copy(_src_tex, _tmp_dir_path)
            except Exception as _err:
                print('NO')
                raise MyErrorOperation(f'Error copy file:\n  {_err}')
            else:
                print('OK')

        # Работать с init-файлом только в _tmp_dir_path
        try:
            copy(_src_init_tex, _tmp_dir_path)
        except Exception as _err:
            raise MyErrorOperation(f'Error copy file:\n  {_err}')
        else:
            try:
                _src_init_tex.unlink()
            except Exception as _err:
                raise MyErrorOperation(f'Error deleting _src_init_tex:\n  {_err}')

        _single_pdf_file = 'single.pdf'
        command_tex = [
            _engine,
            '-synctex=1',
            '-interaction=nonstopmode',
            _single_tex
        ]
        # Конвертация.
        _color_str = f'({_params.kinovarcolor})'
        print(f'Make PDF {_color_str} {dots} ', end='')

        try:
            os.chdir(_tmp_dir_path)
        except (FileNotFoundError, NotADirectoryError) as _e:
            raise MyErrorOperation(f'Error chdir:\n  {_e}')

        try:
            subprocess.run(command_tex, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as err:
            print(f'NO')
            raise MyErrorOperation(f'Error runing tex compliation:\n  {err}')
        else:
            print(f'OK')
            # Копирование pdf в рабочий каталог.
            _compiled_pdf = _parent_path.joinpath(_params.pdf_file)
            print(f'{_compiled_pdf}')

            try:
                copy(_single_pdf_file, _params.pdf_file)
            except FileNotFoundError as e:
                raise MyErrorOperation(f'Error copy _single_pdf to _main_pdf:\n  {e}')

            try:
                copy(_single_pdf_file, _compiled_pdf)
            except FileNotFoundError as e:
                raise MyErrorOperation(f'Error copy pdf to work dir:\n  {e}')

            # Удаление временного 'single_tex'
            try:
                _parent_path.joinpath(_single_tex).unlink()
            except FileNotFoundError as err:
                raise MyErrorOperation(f'Error delete file:\n  {err}')

            if not (_params.tex_dir_keep or _params.init_only):
                print(f'Delete tmp dir {dots} ', end='')
                try:
                    shutil.rmtree(_tmp_dir_path)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation(f'Error delete dir:\n  {err}')
                else:
                    print('OK')

            return _compiled_pdf

    def main_handler():
        for _file in _files_list:
            params = Params(_odt_file=_file)
            _init_tex = make_tex_init(_file, params)
            if not _init_tex:
                continue

            if not _gui:
                _pdf_path = Path(params.pdf_file)
                if _pdf_path.exists():
                    _pdf_path.unlink()

            if _gui:
                make_pdf_gui(_params=params)
                break

            if _pdf:
                single_tex = make_single_tex(_params=params)
                if not single_tex:
                    continue

                try:
                    _result_flag = make_pdf(_params=params)
                except MyError as er_:
                    raise MyErrorOperation(f'{er_}')
                else:
                    if _from_office:
                        if _result_flag:
                            MsgTk(_string=f'OK!\n'
                                          f'File: {_result_flag}\n'
                                          f'compiled ({params.kinovarcolor})!')
                        else:
                            MsgTk(_string=f'ERROR Pdf compling!')

    try:
        main_handler()
    except MyError as error_:
        _err_str = f'{error_}'
        print(_err_str)
        if _gui:
            MsgTk(_err_str)


if __name__ == '__main__':
    main()
