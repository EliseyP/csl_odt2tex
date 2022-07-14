#!/usr/bin/env python
import os
import subprocess
from pathlib import Path
import argparse
import tempfile
from shutil import copy
from CslOdt2Tex import csl_odt2tex

"""
Скрипт для быстрого конвертирования ODT->TEX
с возможностью компиляции в PDF (XeLaTeX).

Использование: csl2tex.py [-b] [-p] [-d] odt-filename [odt-filename]  

  -p      - make PDF.
  -b      - black color PDF.
  -d DIR  - каталог с TeX стилями (churchslavichymn.sty etc) и прочими вспомогательными файлами (как правило, каталог, в котором находится этот скрипт). 
"""

dots = '.' * 5


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
        default=True,
    )
    _parser.add_argument(
        '-b', '--black',
        action='store_true',
        help='Bold black color PDF',
        default=True,
    )
    _parser.add_argument(
        '-p', '--pdf',
        action='store_true',
        help='Make PDF',
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


def main():
    class Params:
        # Default values.
        tex_file = ''
        pwidth = '210mm'
        pheight = '297mm'
        toppmarg = '1.7cm'
        botpmarg = '2.0cm'
        outpmarg = '2.0cm'
        innpmarg = '2.0cm'
        cover = '0mm'
        fontsize = '20pt'
        nodigraphkinovar = 'true'
        kinovarcolor = 'red'

    class SingleString:
        def __init__(self):
            _single_string = rf"""\documentclass[
pwidth={Params.pwidth},%A4
pheight={Params.pheight},%A4
toppmarg={Params.toppmarg},
botpmarg={Params.botpmarg},
outpmarg={Params.outpmarg},
innpmarg={Params.innpmarg},
cover={Params.cover},% припуск под корешок
]{{churchslavichymnsbook}}\
\usepackage[
fontsize={Params.fontsize},
nodigraphkinovar={Params.nodigraphkinovar},
single=true,
kinovarcolor={Params.kinovarcolor},
]{{churchslavichymn}}

\hfuzz=5pt
\begin{{document}}
\input{{hyphens.tex}}
% compile single only
\input{{{Params.tex_file}}}
\end{{document}}"""
            self.text = _single_string

        def get_text(self):
            return self.text
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

    def make_tex_init(_odt: str):
        _odt_path = Path(cwd).joinpath(_odt)
        if not _odt_path.exists():
            print(f'No file exists: {_odt_path}')
            return
        print(f'Convert {_odt_path}')
        csl_odt2tex(
            odt_path=_odt_path,
            color=True,
            copy_from_init=True,
        )

    def make_single_tex(_odt_file: str = None):
        _tex = Path(_odt_file).with_suffix('.tex')
        Params.tex_file = str(_tex)

        if _black:
            Params.kinovarcolor = 'boldblack'

        single_string = SingleString().get_text()

        try:
            with open(f'single.tex', 'wt') as f:
                f.write(single_string)
        except OSError as e:
            print(f"ERROR! Cant't write single.tex.\n{e}")
            exit(1)

    def gui_dialog():
        pass

    def make_pdf(
            _odt_file: str = None,
            _engine: str = 'xelatex',
            _black: bool = False
    ):
        """Make PDF in tmp dir, and copy pdf file to workdir.

        """
        _single_tex = 'single.tex'
        _src_tex = Path(cwd).joinpath(_odt_file).with_suffix('.tex')
        with tempfile.TemporaryDirectory() as tmpdirname:
            for _data in data_files:
                copy(_data, tmpdirname)
            copy(_single_tex, tmpdirname)
            copy(_src_tex, tmpdirname)
            _pdf_file = 'single.pdf'
            command_tex = [
                _engine,
                '-synctex=1',
                '-interaction=nonstopmode',
                _single_tex
            ]
            _black_str = ' (ч/б)' if _black else ''
            # КОНВЕРТАЦИЯ
            print(f'Make PDF{_black_str} {dots} ', end='')

            try:
                os.chdir(tmpdirname)
            except FileNotFoundError as _e:
                raise f'Chdir_tex_root: Error chdir! {_e}'

            try:
                subprocess.run(command_tex, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f'NO')
                raise f'ERROR make PDF! {e}'
            else:
                print(f'OK')
                # Копирование pdf в рабочий каталог.
                copy(_pdf_file, Path(cwd).joinpath(_odt_file).with_suffix('.pdf'))
                # Удаление временного 'single_tex'
                Path(cwd).joinpath(_single_tex).unlink()
                return _pdf_file

    for _file in args.filenames:
        make_tex_init(_file)
        if _pdf:
            if _gui:
                gui_dialog()
            make_single_tex(_file)
            make_pdf(_file)


if __name__ == '__main__':
    main()
