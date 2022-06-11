# csl_odt2tex

**Оформление документов с текстом на церковно-славянском языке.**

Исходный документ оформляется в `Libre Office` в соответствии с набором стилей, представленных в шаблоне `Гимнография 20 новый.ott`.  
В ч/б версии _киноварь_ заменена на **bold black** начертание.  
Далее документ можно конвертировать в TeX файл для дальнейшей компиляции либо в качестве отдельного самостоятельного документа, либо в составе сборника-книги.  

Промежуточный `.init.tex` файл позволяет сохранить изменения сделанные в итоговом `.tex` файле при повторной конвертации из `.odt.` Изменения отслеживать и вносить можно такими средствами как `meld, kdiff3` и т.п.

Для TeX-компилляции используются класс документа `churchslavichymnsbook.cls` и стилевой файл `churchslavichymn.sty`.  
В классе `churchslavichymnsbook.cls` загружается `KOMA-Script` класс `scrbook`. Также возможно задать некоторые параметры книги (размеры, поля и т.п.).   
При использовании стилевого файла `churchslavichymn.sty` отдельно, класс `scrbook` необходимо указать **явно.** 

Изначально данная система оформления использует базу данных, в которой в числе прочего для каждого документа указан `Заголовок` - для заголовка в тексте, колонтитула, и оглавления, и `ЗаголовокРусский` - для PDF-закладок (аргументы макроса `\section`). В данном примере в скрипте `convert.py` эти заголовки указаны в качестве параметров `title` и `title_ru` для функции `csl_odt2tex()`.  

Каждый документ предполагается в структуре книги как **\section-level.**  
Соответственно в стилевом файле определены команды рубрикации, аналогичные уровням **\subsection** и **\subsubsection,** `\hI` (соответствует ODT-стилю `Заголовок 1`) и `\hII` (соответствует ODT-стилю `Заголовок 2`).  
Кегль для этих заголовков (а также `\section`) опредяется относительно параметра `basefontsize` пакета `churchslavichymn` (по умолчанию `basefontsize=20pt.`). Для заголовков:  
- `\section: basefontsize + 6pt,`  
- `\subsection` и `\hI: basefontsize + 4pt,`  
- `\subsubsection` и `\hII: basefontsize + 2pt,`  

Кегль основного текста задается параметром `basefontsize` класса `churchslavichymnsbook.cls,` либо явно в параметре класса `scrbook`. (по умолчанию также `basefontsize=20pt.`)  

Для удобства (это, конечно, субъективно) добавлено сокращение для макроса установки киновари `\KI = \cuKinovar.`
Для отмены действия киновари, например если весь абзац оформлен киноварью, и только некотрый фрагмент нужно оформить без нее, то вместо оформления двух отдельных сегментов киноварью, внутри макроса киновари `\cuKinovar` можно использовать макрос `\cub.` Или `\cuB`, который также отменяет красный цвет внутри `\cuKinovar` но кроме первой буквы (используется `\cu@tokenizeletter`).   
Например (`\glas` - макрос для центрированного текста с киноварью) - два отрывка одинаковы по результату:  

**\glas{%**  
Стїхи̑ры ᲂу҆мили́тельны, гла́съ ѕ҃. \\*%  
Подо́бенъ: В\cub{сю̀ ѿложи́вше:}%  
**}**    

**\glas{%**  
Стїхи̑ры ᲂу҆мили́тельны, гла́съ ѕ҃. \\*%  
Подо́бенъ: \cuB{Всю̀ ѿложи́вше:}%  
**}**    

### Буквицы
В ODT-шаблоне определены две группы стилей для абзацев с буквицей. С обычной и большой буквицей.  
Для обычной: 
- Абзац с буквицей, 
- Абзац с буквицей и надстрочник
- Абзац с буквицей и два надстрочника

буквица на две строки. Гарнитура `Indiction Unicode` (символьный стиль `киноварь индикт`). Поскольку шрифт Unicode, работать с ним можно как с обычным текстом гарнитуры `Ponomar Unicode.`  
Для этой группы стилей определен один макрос `\cul.` 

Для "большой": 
- Абзац с большой буквицей 
- Абзац с большой буквицей и надстрочник 
- Абзац с большой буквицей и два надстрочника

буквица на пять строк. Гарнитура `Bukvica.ttf` - декоративный **не-Unicode** шрифт, соответственно работа с ним специфическая, особенно для случая с надстрочниками.  
Соответственно, для этого стиля определены макросы:
`\culB` - для буквицы без надстрочника и `\culs` - для буквицы с надстрочниками.

### Цвет киновари
Для стилевого файла `churchslavichymn.sty` тип цвета киновари определяется параметром `kinovarcolor`.  
Возможные значения: **red, grey, boldblack.**    
- **red** - обычный красный цвет, определенный макросом `\definecolor{kinovar}{rgb}{1,0,0}` (вариант красного цвета).  
- **grey** - соответствует параметру **[grey]** пакета `churchslavonic`.  
- **boldblack** - для случая ч/б печати, но когда серый цвет не подходит по каким-либо причинам. Тогда киноварь заменяется, как и в odt шаблоне на **bold black** начертание.    


### Последняя строка абзаца
`\ParFilling`  
Макрос для управления вида последней строки абзаца.
У макроса шесть параметров, в тексте он присутствует в таком виде:  
`\ParFilling{}{}{}{}{}{1}%{lsp}{lsm}{pis}{pie}{pif}{pih}`  
`{lsp}{lsm}{pis}{pie}{pif}{pih}` - подсказки, названия применяемых макросов.
- {lsp} - \looseness=+1 - увеличить по возможности абзац на одну строку.
- {lsm} - уменьшить по возможности абзац на одну строку.
- {pis} - последняя строка заполнена (по возможности) на 10%. 
- {pie} - последняя строка заполнена (по возможности) на 90%.
- {pif} - последняя строка заполнена (по возможности) на 100%.
- {pih} - последняя строка заполнена (по возможности) на 50%.

Флаги можно комбинировать. Заполнение - любым символом.

**Пример:** 

**\Txt{%%[BEGIN_Txt]**    
\KI{Бг҃оро́диченъ: І҆}и҃са моего̀ и҆~бг҃а носи́вшаѧ хрⷭ҇та̀ несказа́ннѡ, бцⷣе мр҃і́е, того̀ молѝ при́снѡ ѿ~бѣ́дъ сп҃сти́сѧ рабѡ́мъ твои̑мъ, и҆~пѣвцє́мъ твои̑мъ, неискꙋсомꙋ́жнаѧ дв҃о.%  
**\ParFilling{}{}{}{}{}{1}%{lsp}{lsm}{pis}{pie}{pif}{pih};**  
**}%%[END_Txt]**  

В данном случае последнее слово абзаца **дв҃о** оказывалось единственным на последней строке. Был задействован флаг `{pih}` (`\parfillskip=0pt plus .5\textwidth`)  
Можно использовать вариант **неискꙋсомꙋ́жнаѧ~дв҃о,** но такое решение не всегда доступно. 



## Стилевые макросы
В модуле `OdtTextPortion.py` в словарях `para_dic` и `char_dic` определены правила конвертации для отдельного стиля. Указаны строки **ДО** и **ПОСЛЕ** текста.
### Заголовки
- `\hI` - `Заголовок 1` (`H1`) 
- `\hII` - `Заголовок 2` (`H2`)
- `\hIII` - `Заголовок 3` (`H3`)
- `\hIV` - `Заголовок 4` (`H4`)
### Абзацы
- `\section` - `Заглавие` (`Title`)
- `\Txt` - соответствуют стили: 
  + `Основной текст` (`Text body`). Отдельный макрос определен для удобства контроля над версткой (см. ниже макрос `\ParFilling`).
  + `Без красной строки` 
  + `Длинная строка` 
  + `Обратный отступ`
  + `Основной текст с отступом`
  + `Отступы`
  + `Первая строка с отступом`
  + `Стих жирный`
  + `Заметки`  

- `\TxtC` - `По центру`
- `\sSubtitle` - `Подзаголовок`
- `\Small` 
  + `Малый 18` 
  + `Малый 18 без красной строки` 
  + `Ирмос 18`
- `\Smaller` 
  + `Малый 16`
  + `Ирмос 16`
- `\FrameNarrow` - `Вставка узкая`
- `\culB` - `Абзац с большой буквицей`
- `\culs`
  + `Абзац с большой буквицей и надстрочник`
  + `Абзац с большой буквицей и два надстрочника`
- `\cul` 
  + `Абзац с буквицей`
  + `Абзац с буквицей и надстрочник`
- `\TxtRU` - `Русский текст`  

**Киноварные стили**  
- `\ustav` - `Устав`
- `\ustavL` - `Устав влево`
- `\ustavC` - `Устав по центру`
- `\glas` - `Глас` (по центру, неотрывен от последующего абзаца)

### Символы
- `\KI` - `киноварь`
- `\KinovarBold` - `киноварь жирная`
- `\Small` - `Малый 18`
- `\KIsmall` - `киноварь 18`
- `\KIsmaller` - `киноварь 16`
- `\KinovarXXX` - `киноварь 30`
- `\CharSpaced` - `разрядка` 
- `\KinovarIndyct` - `киноварь индикт`
- `\KinovarBukvicaBig` - `Киноварь Буквица большая`
- `\Rus` - `Русский текст`

### ODT шаблоны
#### Пользовательские поля
В шаблоне определены специальные **User-field** поля, и в числе прочего - `RunningHeader` - содержимое этого поля автоматически вставляется в колонтитулы правой и левой страницы (первая - титульная, без колонтитулов). Поле доступно для редактирования через `Меню|Файл|Свойства|Свойства пользователя`. Остальные поля не используются.  

При необходимости иметь две версии - **цветную** и **черно-белую,** можно работать только с цветной версией, а ч/б получать автоматически, для этого есть как **oobacis-макросы,** так и **py-скрипты** (будт выложены позже). 


### Конвертация
После конвертации как правило TeX файл готов к компиляции (его нужно вставить в main-document, в данном случае файлы `single.tex` и `book.tex`). Может потребоваться небольшая правка, например, праметров макросов, вставка вертикальных шпаций и т.п. В частности в данном примере в файле `СлужбаГосподу.init.tex` у макроса \section такие параметры:  
`\section[tocentry={\TOCENTRY},head={\TITLE}]{%`  
Однако при данной геометрии в оглавлении строка заголовка, которая берется из `\TITLE`, выдает `badbox overfull`. Поэтому в окончательном варианте вместо `\TOCENTRY` используется такая строка (вставлен разрыв `\\*`):   
\section[tocentry={\texorpdfstring{\KI Слꙋ́жба со а҆ка́ѳїстомъ сладча́йшемꙋ гдⷭ҇ꙋ на́шемꙋ і҆и҃сꙋ\\\\*хрⷭ҇тꙋ}{\TITLERU}},head={\TITLE}]{%  

Также добавлена вертикальная (отрицательная) шпация (`СлужбаГосподу.tex:18`): 
`\VSPACE{-.7}{-.7}%`  
перед абзацем с большой буквицей, т.к. он сильно сдвинут вниз из-за буквицы с надстрочником.  
Два параметра у шпации `\VSPACE` - для случаев отдельного документа и книги (чтобы можно было использовать один текст для обоих случаев, без дублирования). 

## Шрифты
Основной шрифт: `Ponomar Unicode`.  
Шрифт для **русского (гражданского), греческого** и **латинского** текстов: `Noto Serif SemiBold`.  
Для **bold black** - `Noto Serif Black`.  
Для экзотического случая еврейского текста: `Arial` (необходима опция `hebrew=true` для стилевого файла `churchslavichymn.sty`). 

## Файлы:

### ODT
#### Файлы шаблонов для оформления ЦСЯ-текстов:
- `Гимнография 20 новый_BLACK.ott` 
- `Гимнография 20 новый.ott`  
#### Файлы примеров:  
- `СлужбаГосподу.odt`
- `АкафистБогородице.odt`

### Odt2TeX
**Конвертация Odt->TeX**  
Скрипт `convert.py`, функция `csl_odt2tex()`   
Odt файл `filename.odt` конвертируется в TeX файл `filename.init.tex`.  
Если указано через опцию `copy_from_init`,
`filename.init.tex` копируется в файл `filename.tex`.

### TeX 
- Класс документа `churchslavichymnsbook.cls`   
- Стилевой файл `churchslavichymn.sty`
- Для компиляции отдельным документом `single.tex`, `single_black.tex`  
- Для компиляции книги `book.tex`, `book_black.tex`  

**Конвертированные TeX файлы**
- `СлужбаГосподу.init.tex`
- `АкафистБогородице.init.tex`
- `СлужбаГосподу.tex`
- `АкафистБогородице.tex`

**Компилированные PDF файлы** 
- `book.pdf` - сборник
- `book_black.pdf`- сборник ч/б
- `single.pdf` - Акафист Богородице отдельно
- `single_black.pdf` - Акафист Богородице отдельно ч/б

 
**Скрипты для TeX-компиляции**  
- `make_single.sh`
- `make_book.sh`

**Шрифты**
- `Arial.ttf`
- `NotoSerif-SemiBold.ttf`
- `Bukvica.ttf`