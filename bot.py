# Script Hunt AI — SEARCH ONLY — one file for GitHub
# Build: pip install "aiogram>=3.13,<4" "aiohttp>=3.10,<4" "python-dotenv>=1,<2"
# Start: python bot.py
import base64, io, runpy, sys, tempfile, zipfile, zlib
from pathlib import Path
_DATA=(
    'c-nQDWl$V!ldcDMg1fuB4n9b53uJJ23GRctdx8XlySuyV;2I=Aa18{9eZO<+oZbCu_wFD4JY98n_0Oxi)s^7j@c;k-G60~fWaudT^<4=c0EiL;01*GFnmM_1',
    'IQvxV`?-;hCcjhuFiR+3ywKZ8N#m#?BG^y07}s2DfTTbUSdd$r0f;+tv4%F3G{iC5zC+QPnne#q4WAMy=M0DM)h-fJhLe0Xj7_icZxLoFcRT#7{-OjaLzpyH',
    'b8^m)kB>)d{Se*U+zvZ~d1F?~S7TS_7S8UPk=T6F&lp7ZPRDsYXD-{`Se~g`4zB|s>}v`}@lJhzMj4bY81=^|EztA?M|&d#FY2$S_Z1p4MN5&ge{XIYOcN)(',
    'P?>qQ{q`U?{>kxC8f@74X0qcA=W!Z&!m@M1;u_Jl{NaWARQR>$)I9^@oNJuWzH(rFR@ONMH^+!+aAcNnMzvqDcd(kM>Dsc#`EgGEHX>Wf<b(F8d4QJnC2&_>',
    'y{a)a{EOAL3oS)h#j{JGP*eBT;~3_Sm=732t4Dg>^iE6>@i#~syx}3@c|R{PDymc2xR875{o>!Ve0`qh#g;&`&Dxq<AF6a+mcTX<yaT+r_v!O1?baa6aW|l6',
    '$f))TFUD!{`)Y%eC{1DD(jm$hSx+iV-5Pq)aDooe&Bwj2`#jlQO4^KOy)AJ~Z9f2;38(6~Uf)Q_X15%-?pMnB{plftKOg)S{n?ttUHs`HbAeK?bX)9$*a|u4',
    'JQ!p79<F7AjPu=YU9HO+5wgE-SYxj&5JtNa?Ot6&Jaycty@2931JH|$C)xB17_wQFi|=QwGp#uzI|3dpL{nXbZsKL&Hss?*<i+&mX(=|EN2=bpUEbvcU)->6',
    'I#w{2N{IR_m)*&6g(@3LD(58y!=Yi~Zj`P49BUug1@8BKQjuRjS%-q%ogJO9LP2A1E>RuD9Y26Bw?A<Y<>l7rzI;ohsqW|VgLk`FPu}xG19#=3EEpz;AO&DQ',
    'QJ@}}Q*j5n_lcdbosmvIA03DP;d{}YHC&JveGJFONuh0NDs*W&Lz>~VC91|?yKOeV0)ANaeQU<3{(S0^=FYWPyZU7cgV~;9I2g&;ipc9$(*Ctl?0s_hv2`6O',
    'Nx`6p3w58g<g_;L%tV;hgwTp33Xx3aOQ@#-fgDd=q=|4cZo6IDBovvwkAhqBHLjzrf9piAOS)FRxs45ZUq{TglNxNuQAmSHR7Phgo4!RDqT`<MqO>{4Z(nW2',
    '0?}n*uq~bxTfC$_Gto~TWw@qk5?qr)9GM#ME?d}m3L=*z?tf2C)>Mo>G$LECeCqcN-W1j6DRE=HR0{a?4!xIbU{a~$HgL-s%a)Lc+QcM6nv;i#E^Z%Msp4uV',
    '6k6;DqaQ>;2``}#4~&jH?Fc^aaN6@b@Q;T5ZE9}^`b4TP4)IQLwbICQ+%H_Hw4ABm_BO`RBKna-XC4HhO{t<v0vL`X&O^V$u6ue0Q)*M$5#e4lq-c9$o)9O^',
    '-v+!y$(Mu<V80T7Mj`vuqSqle5vjMmN1a(n%ci|)6ESDk)!x>&`q?V)cSMUc0orf4MmK7AgS!`kY^PqhRxr5l;#ElTGW8=@r6XdMIOR4%i=ZjGMN0+7bMi0;',
    'gc?~g`Yi6!3Ww80b}-VOT7Jh4pmzW-3W+=x;EiHV{F6&T(oQf;iFs`U;ao$!b%yiy77zWIS;3RJ;85|wrlKxlW8B=E5PWCZP{~ZW7xoR*eR`j!1fzxtW2Dnm',
    '!z{!5rffIzDT0h~JF&LE&=HIG2+^6shKOy>-zPM7mz40XvJ_z2HA>qt7v~FPzJpm`abf9OH_z*&Kk5n5y?{+@jb@k^;xxO{mSH1M%!r)ReiRE8Qn&~2Wk+q`',
    'iPL7Kd~ED=KnhuiB?Rm5WS&0;_`U9o;2FW}2Zx-)_GUXka^eFK?$uz99T_-N$Z5K8f`|d4ze4Q#&W(IaiO*junnbUrEodm(-IIi~6j`1^vZU;Dc43$5uldv~',
    'mXK9>3?%A+Xwp9@LVSdfvjA_@vOz|spB|bmO%Q&u{2bR#2x(THh39W#WGGMKK17MGjZ1r}!R13>bx>5crSKw0?k1FB6*?I6%yuG1jO!1Pld2O^`1GLu_X8Fj',
    '0U;@VKWkmR84?BLbiEvnP~1!cW0!KmphwkBfQ3`Z6s{@*YFE38Dd~`Ev2rKYr=J|It}P#Jv|AY^+~<zwM!Ta0j@nB5lwSQF0+Ul?J0VG(t!2r>C@e#{+$yEy',
    '%T*YWfgeq7#5WNDU`R3c*%jxO8ecYo4acTpX@`o5H1wwpyH`#W><$f#41naO&z=Sm{PxF65b`7RmRK5QJ3NW|zLFV)=AnBb5$@s;2cKd~1vnxr#^qH}I@dVL',
    '6Z<8H#R3~x%!nV<0l!HQQtvRN`A|JUbL%*N;X{x%6KfPV3l&VcK=vtVypOb0AvL;VLx}wH`QHwrYrNSz%tC`U@jPJYLr-9Wpa=}7!av8bn4}goHSr#>rhiKp',
    'p+~Z)m*miMWQRSn)xy3kBJr<W)3x=h9gTzz(A7)DeQnlNtp)OUZicpDwW1(@_Y?CsR4t|!f;&!<B=yPFPI5{M%QNdu8_+snF^S+werfDx4mQlcQPJ=&KZ_D(',
    '1~V9h(r}}H52r*j%%#U0-Dy51$TtkeE4#d+=z?DR3y!)zg^kfz*{5-T=R>!>1?|gzQ$tA%r_Q%{)D#XF*m9#fJXT*c;px`i30q5A4{{vCJ8{(UbC${hT=rw2',
    'ETCn|fTswYH>M6Tm%5lo>zamMpU9p0ctUX}C8s#3_MWeV{2jmKF!XREQQ#T~;W)L`$Cm(q1=GLI<`2hrOq|Dwk$?OhS%+ZgTA9NuV!5=|U^zq07?+$V&VCxk',
    'o{#(3uQy(MXTH+RkQCI`Ye0lZs_0)Lgh66htp2bro-@k#ta{8IRa9kjF>zU1QZvmJUm#|$rI)G`V>+i?Q8S+61h6+9cO>LuqyqJY0a|n8oy>A?$aZQ6VgP-f',
    'D5FkUyd(I_KTvR4oe2a|B+(c+g!+(#MM|pdVr-Y~2vs4jFq3%vB?#QN%gvNM{?6a%w@ZqLTwk%q->=Sdwj1{Y0dm_6Sk-gijj@*@qCL_#REw%m3aW;(k28b(',
    'zb-dGCbzeKNz<w~Y0!%=H?TwZ;Zv+s>C%wbDAaV3xLj#t$qO1nZ**b!VuB68(T~JSs)2NR)teGMNV!n{HT#jycj&{Pm$06JZ_KarRDV{LbK@i^w+FZvP<Cko',
    ')Xv6GE3@FRLWJWkslM%XmJody@6B^(&Vg$Z9W|09{tYOom;v~t@a`B1gr;JCCZS7HXA7jNR9|(b(E1S^sa1t-M<oiV*$oqP&cT{SF<?67covs|oSh91Vt&Zj',
    '24kj0Y~|tEk9Dth(8Xr>p4}D^o1LSjF|Y@tK+kVaiex}bXTa0NOoX56!+NW&NeappNhg^6CDH==<=RaQOS&G)BH3J;;AIQ;+aQ$?dyMF}I8T2G8Q?;c%#IDB',
    'sbYy^)EVw!YIKPXaASM1p<U$=mEciu<LW++K5!r|sS3VIw$eHFg-`wA&OgN;F>t$nUt)|vVANPLfo;*t4b`Qt#2@z^?d7#}zMc72vX#DD0QK&NFRdGs-I;HX',
    'KrQJ=k#$GJ1d0hA66fbOwB(G_27BqHvxAeMkPv~1NQSQq>{aVos%oMms5Q3tVFjhWTi>e>!f^0ZHqh!Zi@M)#s6{q~c}!#F@LboTb3<MBuRw=mvX=#=<dUUd',
    'Ktc5%4Q9`ZJ?g~B3CzA@fWGAC3Q%{8{t1@5UNCHoC~}>ycvSt`ShLohzlR^Lpt2xye9JhI3<3&eH$D8ATx3LL@sZ?DCEa;5vb0RAzILj&Gq*dCaqSp;&hrR_',
    'L>UpjUK0R6MNw!Sc+-3t?Nt@v^p$`-ul<m9mgekYf9WnW3-+ThwkAs5bwZnhL1Rc^)Qz*P^I%&|DIp@2$Dp13)^}A6!bTpS=y{BXGnY<9OInAc#(FJM7-N_5',
    '|A5_lGVqKCrh~6qjJN6bpo21fksU9_{?&h|C;*BnVpwDw!P(%%sP3_7`Z|9j@YigbAqe&0VM0lsZsL?_;IQ|gfPWbYn+$LT<OqpxD3sGxQL53hTKSSpdUNo+',
    'OW&M3WmT?kq;_i2XJO=82l?qUBAWVMFmZ!{-TaPPLp1PAo39dt*Mi095beLpSmq7I5TV9QX;y1wD%t$%X!*mlMHtLrd8Xew_WIR>wIK~^#Y8APB$ghv6YP%A',
    'Musa}Df3iMI6}MG8-_PC4OMPCtJP_l3@wZ9#KIMm>X@jG;aV@!{)7$^c@F6JpVgvWOnKUF#GDw<<trD;^{U>bN9$jEH_j_4{!$_6EZR)HV#mhLQNk+yirP^}',
    '<qCAyroong*r=7pLy1`LTV4BvWS^LaR_c3{<2n1fdrczM2X_%&M1WT2F@fJU>Z*yr$=+G#e=pwzN7nBk@c6uI>bv|tOs+`5GprE|H{5&!hw#0ZUDC{C`U4P0',
    'Ld~m@s<56s5?JuzcinE1BG!|+Kb_o1T2iv2+nUq6eEgXWz@<U*eQPF4f93O8XGTd!xFmqHm*ly)=}{-fmy_Tr?ex$An+MnBiEpl=21dc@teVL-YsM(C9_X6N',
    '>%RIGje@5RC_P_yo~a;|5Z>Ni_}U7KK*X|9#SH7TU2EghC%`z#=~l$%#UJM>Kpc6jwL683vun`nlno)zp}&;h{tOddk6f@s&@GGMMAg>M@cySh)x;6yl@@cP',
    'Htol!Kl&top~uj8cDA}=S-4o@T8Z~Ky>A3-qLUOV>Zq7P3m}c8Vt`J0o~9|Sg>0%aa@}#99zj*svL2F=;JQU<-{goI{_yiQ_YIyJN^rNbCk*zSGJ^9Hxqc~%',
    'lTE6l#gBSrHcRddgnH|7_Oj#rIHr)e;?7KTycnbpSMizk=wui~2p2mAtk_okg-j{B6K}uBuQYbC_`%<`GpBWHa@}yb#=n+TchP`faQd=B7@sY|hZ6Y3)fB6v',
    'kgzcDELw*!1rL;*U2I$g8rx1;4e-k_Zh-l>jmE0s&P)cXx?8qUx))dc)^NsCfSxf%l)X;j(#NNDuPj$8Ekl?R;rp@kr2|vy6vp33M^Z6JW>y#81cLW7v9Qgm',
    'on8%khAdgXh{S+}X$N$gmj_3~)nmv(F;`H~-I0grWr%+1Z)jxromgol>7QS^_VxY`&|d|sDt711lOJ;lYtsfLbgUy!&M4yr9@>`UszZD|=c`}J47W;Ue-_$m',
    'dD$!lNTs%`GFd{E?gZZZ@p<>K%Y<grhZk@h^5Hql38LL!cgGH}Q3C6)WXe91P%PHer7h6B;*LDiQRam|dkgGVDcyir6XK`t%(;+K8rPqjrCBW%8DT6*e<?-A',
    'RWzY0X1t@rN>CKb(a2S}r#;W5dgd~Isy-8%96-5Q9eldmm>=1tjz}D<H>CHg?g)7}hTrVri*Lle)#lFR5i#&kBE}i^YR7+TS<jHH8I!vo)w2|l_E!{XVLAbp',
    'S4w#@StNoFj7(x0_Rh5JVLnsiAMg0^0D&LX>QE@9;KXdfW&7#5TbZI*Itr$&OwC!*-KIScurtWLmYC6h1v7yGV?buoEcY~!zm|)Bh#c_g^YQn!<6s8;^<Ipr',
    '7PG3t?q;1?jlfX$*D0*X_q1Lr-dV1v2a2#{6n(f>M&t{pPo|@%&mDi0_tQ~YN6cn>U|AfzoI`uB-qcn<!d(8L61$Z2Wv8lLEg4>FSjg#e*yv}2YM^0(Dr%+6',
    'g5mvFkJlWU``y>=j2z4T+ggAx%-?|(fS;fb>urOFmBog~Ku5RTE%&~B?tOZhAWCQrb3GL$w!ST&gW#QO5w2W%jh+YhKK2}F?Gm|YC*ExFyu-Ql+rT;9T~@W8',
    'WLt&YJ&IQW&H2}5S0|P7ho5@^XE7Z$i+JtKwL<epLy6&f+9_>JV9lx2&1RA?0Ix9(1LJS4G3~2ODmpyjMa2VcQ<By?q0Nkpny5{4&xrvp`*I5gA8JrY%J%G#',
    's5eBg`Y=Y9m=t-tbq%OuOKberEh|GEO%Z5!5lYPdD9s#o$*1F~Q^-*}OJ3RNHY$!S=*-L^i7&pJ%juL6AW5Ew#gCEfhP>Yus;#>iYyImZ1tQn|)1<`fB_`ct',
    'U+@G1k9YmxP`?(iv>ipvXu|9@2a=fzZDVp5Pi_t!CpMe`9YGWDEHsd;myCJ|P$X}}a>?<{0~O!5N#8&7_u}!dZm!2v>*&7sNtdbV0<|aDE3%>bjhg(0`%CjO',
    'p?GMaW*?T>L?-Y*_yqN7Ot%^d9mG?*7SPC9ad3&L8$<P1D5y-P$^Gdq65!#FI7V!*4#@^NFXW@c-w?mzeOk1qK^r<qseoM=R*;ZpZ!cjH#{lvN!|0P`G9aRp',
    'XkCE{HA!wozKW)aT=A&k>ZgPHio(V{;qDPA&^DM7mBN|$nCFKL#>=}3^jv0s<z0O%Ls=w^^|Vt%F_u>|+<%Z4P&$n&1(B~WmMD(DUXHzrPN9Z7kS}|f=kLS)',
    'y%N;*;dz83CtY>eA(dT`Jr$1(cC1m6&|hu539-0z-1DV5kl1_NDtA8~nl$KK(g8NDZl#`t&PMHjqghCjnd~K6jUA(;WLYi(nOL#e%+1|_*i#6O>YHjU>^a}w',
    'G{4g_KjfnSd=wLLXtWICo^D5>f!!2ZsfitQqls{wB4-w{bbc>r1-!WZgZ26jTQek2Z(vJVJNcY)$y7Y0{1^rQAy>+uzcUyb1y@ZykE#`r5=;Hmi}y^Rkso0s',
    'LP`v&mDLE3uHiWo4rQg`qnA-Hp~U=X9Y!t>6Yy=a`rh)lmlm39x3~?uK2g0!Wfjp-wyb^e+82EJnx0oPGs&my640dZU1{*rkDGJ99@})|TCDs#uJ(`gSnLT;',
    'e<VitjJ$a$=R6uY&BJAL$A=n2<$PcUC|Uh(dWgiFKs(;5M;72P*@pG5%3<fH5b{@fGWW5ZFB|1)%mFVUQ3_?gpd(lD`RU?;-Fp-!FJF?`dc5Suapp0tm$%=f',
    'o9_T0b;!hdqH-w729X`U>yZdWl(_L6E`nkP#Oo%&thz3ptBD%3(h!!?zHanIz7)6m(Un1z$K{h(TSPd8=mGZ0T6E!AWLXDfeX*<}p)x7Q&B3m52IhA{iE_cm',
    'L$`_j9-1kaR;re6<mf?WOGV;U$)$DdSPkLpWD4$y$r3>vedOgaFT*KUNgXQ7tIq`F*3E1{cN1ME`^l71%(MoC`qEfgF1vRm_5ZeR{pSII1^i$AtLkRy>S=3k',
    '>BebnZ2QI5-PoAJ*#{2r-#y+-LT!Oa0Kfz;06_R(J&qm@?zV20rmp5T|JvE=*gDa+62H|L_jfP}Eu?>p3C*k4W3MB1z$(l(GxduFgwUw-rVUxhBq$`%FI@%B',
    '4w_?<Z+!_yt>c&Oxqm(RM}G7eD{50QjH)djw!_UD%`?KxVdG1<E0HM4F&PGpievn`6f9Qg8d=DXL&XOObDMxU3osZAS6`jh5|$Y{6>euF=&3I-TdY?rRpzq<',
    'shhVum1>Bwm6!gtl=wly|7BkdR=#>tlMPNC?vD=ZWaPyOn7%0R>K?}YL)NC<R!AVzBLPTa#|ApVvN*DC$JN&B|KO}vvhO2#m4Dw(knV3>A(n$>_p*WGq+8SC',
    'z8cx?w=H#K`TlnCItw!db95lyM<x~Kw+A!OJWkg-{W@z<K`};Ai=mZw!_)SDc+MD=1I2b=r6b1y&O_Ma4%U0M^hE1lc7C|D@V_yG=NmSktS=o5AFO*0eH^tV',
    'n-$YxzO!qS2VqzPxB1fCgm}d()0x@>YbrJCLrOyX^LAJp;2cwRdRmW%DvR5zo9P<Kb*WQ4qv**jON<z@W&%uC-ieLh9p6ThX&$VrFvoOf(2dI*<mdT#wV54K',
    'aO!F3zm0RyJB?3^x^D7hJGCiL*vnic-RejTXh~57etR0k5ZNJ`;vtk%P}_3;K%q&!Zm`*j)Q4mzW*J~Y|BD0ET14@wbd&x8$?#7Pw{o|NCw7~54gZIut{hOc',
    'zbo(U)32Q@$U+6>g%ffl*1n5C?ho}CPam^lCW5gP_&{mRGIm@Zy^)jLB)dmew)vveP*pX2fV`E-0XyR-qFMUn{IKy5x(mC)xO6rHMDZElQbG6D4a>AHTbb(z',
    'C7GO34erkIod6B$4qJD`?Zd8y{q3r%N2KcXfMI;8J@p(MRtI8KgkR&}HtOhpjjJRL&^UAP9MRlfsmp$uq)yvP^d@zQHP4HZ!d9ufnUAr9l~l^(xB5&`x{nFS',
    'R?JHYr|>=|nJrd~XAEnRL2Dx0ofTII9oMg!zUk_EFJ4U^z--8$m20x&)`)Cp;-y6X8T<mBA6XyH*I-w=Ti5n~i>RTd?2WLhg>HGr*9et_*U)|rA#A(Pg&%Nw',
    '2@+%!Gg@D6Qg3iS<VZK#x$JW9J}yk^%`7^lm_y|tB0!@KH)O*ZoYbBLmeh2yZ}{PT<f@B>3^x5{<@I3eKzBaUJ$|54u==z22LsD_GpnP!?0X>)o)L<;YjhKS',
    'pKoc;NjMN!9T}!usiGz)13TkC!vz#>(D~s=?V1h0=`igG`YEh3yKDTd#N?~2!scE*Iyt8)#6(1lGiq<#x~ig$4M**F8U{y#R)7lF7^mlJwU^?cfNeb%e?67g',
    'K(R_wDPfh{c=R`AL81rU(bMK%Oay2v0)4|o@PTYXLDu@b9zz^U>yrJJT+!ZJZvKl`2dL1mg&)-Rpeg>wsDiU$3qvfE6UWB$dytN+HRsRHjwQ3Vyg2($KS^W^',
    'K1V9-jq0s?wH97BkfwB9OYa^lXUr37+3m&HA25uWe~i-h+pS2g#(0GDUGNqaPGwaM%}ioVhd%d}d_9YfPGQ%uf4AU55{C>3#*c_n=j6`C701ti$}e-9j(WPf',
    '#{Ec#SB*W7fLkBVUqgwR{=?G7MggyJ|2@v9=F)QQm+gS3@@hgyBHab>d#2`eWlFwPNsSQa$X@+(_C2YYD;Zu7KW4UuXe>95nuJnvB~6psr2_P*=oPhA*_Q(5',
    'V$B(V@mxL^*J5ZEcFbx8hbId}xZ||cAmU&s)CiQJ7`BeOR;JA6xO3&J7v`~6;riUw=BR8wDDM}!7W0P&J?ITDqS9^yUunfsS{DTu#*BvM>1n|w%zuFBz<ySi',
    'pQ?v;NmpH`2Vp+Ezj%Xy<oS-ZWb{ux3A=QTL9H6*=p3<@150UP`d_4QXR&OEh<J?;Vv<c3!uF507UD)4QntwZ04FK~niiq<&fd$D@ua-n0upoBA&@P8Jt^i4',
    'mBnVnafZ5dUG-uW-H%K0EQg))t&V`jQaxwpw$Le`Rn57+0}@791X80xQNgo;Ae#)h)8a%a01i5q+3B*uZ=V!$9$GGE&Bff43XVzXWhVSAJtC*l(N8(OptXmN',
    'F;BOvd3y5Y4$t8yP4W-iy#=b!aW|~pa09VOwl*5C3CBvh2v{M6yTO8EuMUHy{Ifujl2Kc@a^uOY!kOZ9SKT@NO5RrQ&K{N(lrl1vGk-3LEW_L_+Cn8^BnSU1',
    'e4@BU{9g&_mY~MDF$9O+ortdQ5!?87(LQO~qSp@;vwqZ=z2#_l>)FYm<y@)G%`d^(yZN#w(_Pk(Jy)f7?&pK^m+1|wdNE5VWdW(U@h3tfW1AV&p?CUY)7x;g',
    'PVmGdrNaFNN<?=O#Ex;iQ>}HzN9myk_(E<GH{fTqjKDZyN%P&{G((kPKf{tidF{P>{sAkx5OtOA=Pd8w7AN<h5x&@y4}FdoI%#Uxa_f2vl)-DkdZnj`F7U5K',
    'mR=(=F#z^er6BrVljzj5H3Kpr=`(3Dllq#}Wj&UPD1z}U#scm<l!|!V@lscUfyIOS-w&(*Pes9i|9@uvchA4m!GC(3@c(C4`1cO~&I<q8p%DLnB?omSg#R-k',
    '+&|IzPX?3!>-QhvT&8#',
)
def main():
    root=Path(tempfile.mkdtemp(prefix='scripthunt_search_'))
    archive_data=zlib.decompress(base64.b85decode(''.join(_DATA)))
    with zipfile.ZipFile(io.BytesIO(archive_data)) as z:
        for entry in z.infolist():
            target=(root/entry.filename).resolve()
            if not target.is_relative_to(root.resolve()):
                raise ValueError('Invalid embedded path')
            z.extract(entry,root)
    sys.path.insert(0,str(root))
    runpy.run_path(str(root/'bot.py'),run_name='__main__')
if __name__=='__main__':
    main()
