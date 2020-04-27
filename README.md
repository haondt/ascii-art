# ascii-art
Generate ascii art from pictures

Generation is done with Noto Mono for Powerline for regular text and Symbola for
unicode braille symbols. Results may look slightly different when using a
different font. Does not work on pngs.

Usage: `python main.py -h`

Requirements: 'scikit-imag', 'numpy', 'Pillow'

## Description

The purpose of this project is to convert images to ascii art. The basic
strategy is to take an n\*m resolution image and break it into chunks matching a
target resolution. I then use a variety of methods to convert each one of these
chunks into a single character, giving an ascii image of the target resolution.

The described strategies will be exemplified on this image of Albert Einstein.

![](sample/einstein.jpg)

### Strategy 1: Blockify

This was my first strategy, meant to act as a quick test to verify the algorithm
for breaking the image into chunks was working correctly. This strategy is to
convert the image pixels to grayscale, using a 0.2125/0.7154/0.0721 multiplier
for each of the rgb values. From there we just average all the values in the
chunk and scale that to a gray value from the 256 available ones in the
terminal. Using ansi escape codes, we can then print it out.

![](sample/blockify.jpg)


### Strategy 2: Asciiify

Blockifying the image works quite well, but only works in terminals, and only
ones that support 256 colors. The next step was to use actual ascii characters.
Taking a naive approach, this strategy changes the image to grayscale the same
way as the first, then creates an image of each ascii character (A-Za-z and some
punctuation) that is the same size as each chunk. It then averages the
brightness of all the pixels in the character image and finds the one closest to
the average brightness of all the pixels in the chunk. This strategy works
fairly well, but lines and edges in the image can be made cleaner.

```

__~__~~~~~~__~_____~_~~~____~;_____~__~;~~__"""""""""""""""""""""+++++++^^+++"""""""+""""""++"""""""
__~~~~___________"_~__~~~~__~~~~;~___;;;;;~~____"_"_""""""""""""""""""++++++++""""""""""""_"""_""_""
____~_____"____________;;~;;;~~;;;;;;;;;;-;;;;;;~_____"__"_______""""""""+""""""""""""""""""""++^++"
_~________""____________~;;;;;;;;;;--;-------;;;;;~~_______________"""""""""""""""_""__""++^^++"""_~
~~________________~_______~~~;;;;;------:-:----;~__;~~~__~~~____________""________""+^=r=^++"""___;-
__"_"__""________~_________~~;;;;---:::::::::--~-;~;;;;;~~~;~~_~__________~~___"^^^=++++++""__~;;;--
""""__"___________________"_~~~_+^""~~;;;;;;;;~;_"+1(i]]z(r+"""_~_~~~~~~;_""""""""++++"""___~;-----:
"__"__"""____""________"_"____^=_"+"_~;;--;;_"r(}F]c??rrrczz]vvv((c|""""""_""__""""""""___;-------::
""""___"_""__"_""""""""""""""r=_~___;;;;;--;=1(fZz||1|]flii}vlu]((r?}z(+""___""__"_"__;;---::::::::.
""""""""____""""_"__""+=""""+|++""_~__~~;_+^"|yk]r(caFu}ivlv?(v|???i=^=r|"""~_""_____;---:::........
+"""""""""""""""""++++"==^++^r(r+r=^^r=++^c(i]alyaaVffyfyFFeZPhkVValfr+=+(^"_;;_~;;-----::........::
"+""""""""""""+"""+++^^+^=rr==rrr^=rr1(c(cizuukayeyf]fVkZZVVVeVVaFff}Fyf?"=+^_;;---::::........:..::
++"""+""""""""++"""+^=r+rr1|r||1|(v}lfyuu]fyaykyyy]uyyeaFfuakZZZaFFyylu]}u}1=+"~-::::............:::
^+""+"""""++"+^+"""++r|??||r|1(|1c]ykZkVFyuFFVeeeaeeeVVaeyufyuFeVkZZZkayu]z]c=++"-::.`..``.......:::
=++""""++"""++""""==rrrr1?(c?((cv}laVkeeVVkVZkkZkkZZZZZkZVeaayuyyuluFFaVaufuaaz=";..:..`````..:...::
=^^+""++++"""+""+"^"+^=rr|(ic(?c]uyFVVVkkZZZZhhhwhPPPPhhPhZkVVeaFuyuufyFeVFvify]+:-....`..```...::::
rr=+""++^++^+++="""""^+rvfav1ilFeekZZZZhZZZkZhhPwwwwPPPPhPhZZkkVVaaFyyuFekkZei?fz":-.......`.....:::
|r=+++^^r^+++++^^++""=cfVa1cyVZZhPwwwGGGwGGGdddgdggggdgOgGwwPhhZkVeaeaaFeVVVkZuifz;-.....`..`.:.::::
||r=+++++^+""""+=+^(ifuac|lFeZwwdgggOgdddgOOgdgOOOOO%%%gGPPwwGPkZZkeeeeFFaeekkVFiFv+-````````..:::::
|r|r++++^""__"+^^r(?zv]|1}yFkhwdgOOOOgOOOgOOggdgOOR%OOdddGddPZZZZZhZVVVaFFaVkZZkei]r=+-.`````.::::::
|||r^++++"""+=c}]lfz?((|vuyZPdgg%O%%OOOOOgOOOOO%RRRRR%OOOOGPhPhZZhhkZeVeeaaeZZZhZefr;_-_~.````.:.:::
1|r=++""""^rvF](rrr||?r1zakZhGO%ORRR%OOggOOOOOO%%O%%OOOOgddGdhZhPhhPkhZVVaVkwhZhkkfv^-..-"-```.::.::
r||r++"+""rf(=|r??|=iy"c]F?(|(]akGOOOOOgggOOgGwwVyyfyPPkZPGwGGwPZZZZwZZZVVZhZwZVaFai(r_:.:~;.``....:
rr=r+""""=}""||vyvr?uy+^u|"r?zeZZPOOOOOddgOOGwddhwZFz}uaVaZgdGwPPZZhPZkVVVZwGPZZeFuui^==~-~__.`.....
rrrr=++++ic++1}zf||}ea^rFykPPPPwwddO%%OOO%%RO%%RR%OO%%OOggOgOwhZhPhGwZhkkVZGgGZeayuf]v="";:.:;-:....
||r==rrr"r=_^iff]|1lVF^iVPdgwPPwPZhdOOR%RRRR%OgOgdgOOOO%%%OgdGZkZPPPwPPPPZZPdGZkkey}z]z1|+_:`..::...
r=^+^=+"""__+z}1cr1zFv"yZOwhFaFFVZZeaZO%RR%OgddGGhVaFuFFyhOOOwZaZhGGwGPGPwwGdOOgGwkeFz}]uuv+-:`..:::
^^""++"_;-;~"zi=1=|fyr"eZZuczeFfuaewy?VgOOgddhkZZa}vffFaauaGwwZeVhPwPwkPwPwwdddwhZPPeyful]vvi+:.....
=+""""";---;_lr=|r?eyr=aZF?F%u_++FVaerydgdwGZZkVyeGP=^~=}]VkwhwZkZwPhZZZhwGGGGddZZeeeeylFyuv^"+":..:
+""_""";---"+u==1rrei|iFkZfyVF(1FZFV]ikhwwPPkGwVaVkVr""iVFkZZPwPZZwPhZkZhwPPwhkZkVVeauyeyuzizr--";::
"_~;~__~;"+_"f=_=^"}^|]fyuFl}uaVZZZ}=fZwPhZhPZhVaeeayeyaaFVkeVPwhhhPPZZkZPwPhkaaeekkeeallyf(=cr-.;-.
_;-;-~"~;;_;(rr;~""="|ay}VZkZhhVZZu=1VPPZkhZZPGdGPZZhPPZhhVeZZhGwZZZZkVVkZkVaaVkF}cfaeaeylVu(rc";.~-
~;---;_;-~_r+_=;-_~;;cyhZZGddGwZdG?|aZhhZVVZhPGg%OOGOgdGwPhhhZZhwVVZkkeVekeeeuukhkfy|vfaVVaky]?z_;.;
-:::--;-;_^~~"_;"r-;-1kGOgdggddgh]cVhhPhZeaeZwdddOO%%%%OOOOOOOdwPZVVVVVau]fVu}hdPVFfl?lykhZhZyyy?_~;
::.:--;__"~;;;--_"~-;|PO%%OGGdGPFiZwgOOgGPVueewRROO%%%%%R%%R%OOghZakeeeF]caFhwGO%hwlawiekgdGwFeZZr^-
::..:-~~~;-:-;;;~~~-;+ZOOOdGGdgg(}wg%RRROGZVZkehO%RRRR%%O%R%%OOghZaFaeau]]eZOOg%RPG%GRG?V%R%OkekG]1:
::..:;~--;~-----;-;;;"kwGwPdOOgc?rlhdggdPZZZGdZFwgGRRRR%%O%OOOggwZeyeeFuulyedPO%wZkRNOOFVNR%%kafdl]~
::..:-;---~--;-;_"+;;=khZhd%%OPFv1"|yaaeeZVZkVVZddghdO%R%OgdgdGPGhaueeFyylkO%GwhkggwGgPkdWROOk}iP}1"
::..::-::::;""+=++~-;=kkahgOgPkZPZkkkhhZkhhhZPwwGwdGZZdgOgGGGdgdwZFueaaaalwO%GZeVZZgOwhZNNO%wa?aVi"+
:...::::::::::::;;;--+ZZyZZPZZhZwdwhwwwZwgdGhGddhZhkhPZdgdGwPdddwkyyeeaaukOGdZyyeaaFkZhdgP%Geeafr_;-
:...:..:::::::::-;-.._FhaVkaZZwZwGhZwgwdGGwwhPPwhGgPkZwZwdGGGddGhafuFVeF]V%Ohazr==ZPVZZV1cZu]_;:----
::..::::::::::::-:...:cZekkffuuekPeZkZZaZhZVkekaZZhhhwwPGwdwPGGwkaffekaul""(+-:::-;+?1r_;_?+-::--:--
-:..:::::::::........."aVyGPyz|=1+??(}c1?zv}uy]zlllyVkwwhdGwwwwPhe}ehZFf(_-.::::::::::::::-::--:----
-::.::::::::::........:lZfeOOGev?|uuuaauyFFeeeyl|_+zFVPVhdwhGGdGhFlwPkl^-....::::::::::::::::::::--;
:...::::::::::..`..`...~awyhOgGP+uVkeZeaVeVFZVyz|iaVPGkeGGhhdggdPuPGZ?-.....::::::::::::::::-::-:-_^
:....::::::::::......`.._aGyd%Od"lPPZZVkVVyePZv]yFkGOdPkdGZGgOgdVwdv~::::..:::::::.:::::::-:::::~^r?
::::::::::::::::.........-]dyO%O^^wwhhZaeFyZZ]vuukwGgOgPgGZOOOdkZ]~:::::::::::::::--:::::::-::~^+1cv
---;;;~;--::::::::.::..``.:]ha%O}~ZgGwkeaFyPyzfFhwGPOOOOOhGOOdu(;:::::::::::-:----------:---~+?|?viv
""+""""_;-::::::::::::..``.:uyPgk-vPdGaZeuVV]aZPGggO%%%%OPOOPr-::::::::-::::---;;---;-----;"||?c?vlz
rrr=^=+"_;-::::::::::::..`..:}(PGc:zPGkkakelePGgOO%RRRROP%Gi;::.::::::--::::----;--;-;;-;"r?i}vv?zcc
rrrrrr=+"~;::::::::::::::....."+aPi:zZVhZefZOOOOO%RRRROGa=-:-:::::::---::-;;;;;;;---;-;"?vflzvv}iv1|
|rrr|rrr+"_-:::::::::::::::.....-(Zf;+i}]aOO%OOOORRRRh?~::::::..:::::----;;;;;;;-----;r(cc}}(zivi?=^
||rrrr1|^^"_-:::::::::::::::......"feffed%%OO%%%RRgu^-::::::::::::--:----;;~;;;;--:;+(civzz1v}}i(|"_
r1rrrr|rr"~-::::::::::::::::::.....-ruVwwdGPPPGdyr;----:::::::::::::-;;;;;~;;;----"rri}lf}v}iv?1="_;
||rrrr";--:::::::::::::::::::::-..::..;"r1cvir+;::::--::::::::::::-;;;;;;;~;;;--"r(c]zl}fvv}}v1+""~_
r|r+~--::-::::::::::::::::...-~""-VOkz"."iy?~:::::::::::::::::::---;;;;;;;;;;;"1cvz]}}]zii?z?1r+";""
r";------::::::-:::::::::...-_"=+eZlc^r=F_::::::::::::::::::::-----;;;;;;;;;;"1?z](]l}virc|1c|+";""r
;----------:::::::::::::...:_+="V="=r="-::::::-::::::::::::::-:---;;;;;;--;"rcl}]zi]}cz??ccrr+";_"^c
------------:::::::::::..-_+rr+1+r|+;-:::::::::::::::::::::-----;;;;;;-;-"^(v}z]]i]]vcczvicr++~~"^c1
-::----------:::::::::.-;"^|r+:_r";:::::::::::::::::::::::::-----;;;;;-_rr|zz]}}?zzcv|izc(r^^";"=|_-
:::----------:::::::::-"=|(r+:-;::::::..:..::::::::::::::::-------;;-;+(((zlvz]1vi]vv?cc1=++";""_;--
:::::---------::::::-;+=rrr"-::::::.........::::-:::::::::::-------;_rrccizzzzivi}vi(c1|+""";;~~__~;
-::::::----::::--::;"=r1r"-:::::...........::.::::::.:.:::::.:::::;+|?ic((zcvccccc1=r1="_+";~;-;;~~;
-:::.:::::::-::-:-_=rr=~::-::....``..`````........::......``````._rr11|r(1(|r^rrr1=^++"~~1r=+"r=r1|_
```
