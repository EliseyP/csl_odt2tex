#!/usr/bin/env python

from pathlib import Path
from CslOdt2Tex import csl_odt2tex

if __name__ == '__main__':
    _odt = Path('АкафистБогородице.odt')
    csl_odt2tex(
        odt_path=_odt,
        # copy_from_init=True,
        title='А҆ка́ѳїстъ Бл҃говѣ́щенїю Прест҃о́й Бцы',
        title_ru='Акафист Благовещению Богородицы',
        color=True,
    )
    _odt = Path('СлужбаГосподу.odt')
    csl_odt2tex(
        odt_path=_odt,
        # copy_from_init=True,
        title='Слꙋ́жба со а҆ка́ѳїстомъ сладча́йшемꙋ гдⷭ҇ꙋ на́шемꙋ і҆и҃сꙋ хрⷭ҇тꙋ',
        title_ru='Служба со акафистом сладчайшему господу нашему иисусу христу',
        color=True,
    )
    _odt = Path('Полунощница.odt')
    csl_odt2tex(
        odt_path=_odt,
        copy_from_init=True,
        # title='Полꙋ́нощница',  # берется из odt-файла.
        # title_ru='Полунощница',  # берется из odt-файла.
        color=True,
    )
