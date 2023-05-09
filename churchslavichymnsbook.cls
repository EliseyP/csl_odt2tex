\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{churchslavichymnsbook}[2023/05/09 v.0.3]
% Класс для сборника (книги) гимнографических текстов
% на ЦСЯ с использованием шрифтов семейства Ponomar (Unicode). 

% Опции: 
% - основной размер шрифта
% - размеры (формат) книги
% - dtp

\RequirePackage{xifthen}
\RequirePackage{kvoptions}
\SetupKeyvalOptions{
  family=BookPROP,
  prefix=BookPROP@
}
\newlength{\pwidth}\newlength{\pheight}% paper size
\newlength{\toppmarg}\newlength{\botpmarg}
\newlength{\outpmarg}\newlength{\innpmarg}
\newlength{\Cover}
\newboolean{DTP}% предпечатная подготовка
\newlength{\TrimMm}% привязка к \Mediabox = \paper[height|weight]
\newlength{\BleedMm}% привязка к \TrimMm

\DeclareStringOption[0 mm]{trimbox}
\DeclareStringOption[0 mm]{bleedbox}
\DeclareStringOption[210 mm]{pwidth}%def A4
\DeclareStringOption[297 mm]{pheight}%def A4
\DeclareStringOption[2.0 cm]{toppmarg}
\DeclareStringOption[2.0 cm]{botpmarg}
\DeclareStringOption[2.0 cm]{outpmarg}
\DeclareStringOption[2.0 cm]{innpmarg}
\DeclareStringOption[0 mm]{cover}% на переплет

\DeclareBoolOption{dtp}% DTP

\ExecuteOptions{%
  trimbox,% dtp only
  bleedbox,% dtp only
  cover,% dtp only
  dtp,
  pwidth,
  pheight,
  toppmarg,
  botpmarg,
  outpmarg,
  innpmarg,
}
% !!! проверять на \setboolean
\ProcessKeyvalOptions*
\ifBookPROP@dtp
  \setboolean{DTP}{true}\fi
\pwidth=\BookPROP@pwidth
\pheight=\BookPROP@pheight
\toppmarg=\BookPROP@toppmarg % 1.5+0.5
\botpmarg=\BookPROP@botpmarg % 1.5+0.5
\outpmarg=\BookPROP@outpmarg % 1.5+0.5 Внешнее %3.7 % 2.5
\innpmarg=\BookPROP@innpmarg % 2.5 внутреннее

% TODO: DTP part.
\Cover=\BookPROP@cover
\TrimMm=\BookPROP@trimbox
\BleedMm=\BookPROP@bleedbox

\LoadClass[%
%%hyperref,usenames,dvipsnames,svgnames,table,
%final=true,
version=last,
twoside,openright,headings=optiontoheadandtoc,
%onelinechapter,
%footlines=1.25
%footheight=20pt
]{scrbook}
\KOMAoptions{%
pagesize,
headsepline=yes,
%parskip=half
%  toc=nonumberline
}

\usepackage[%
includehead=true,
includefoot=true,%
headsep=1.2ex,% между head и text
%a4paper%
%showframe,
papersize={\pwidth,\pheight}%{210mm,297mm}%A4
]{geometry} %showframe, includefoot=false,
\geometry{left=\innpmarg,right=\outpmarg,top=\toppmarg,bottom=\botpmarg}
% устраняет слишком большой \footskip (только c KOMA)
\addtolength{\footskip}{-2\baselineskip}
\addtolength{\textheight}{2\baselineskip}
