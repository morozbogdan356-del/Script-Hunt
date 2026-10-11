# Script Hunt AI — Search Edition for Render Web Service.
# Single-file bot.py with embedded source modules; uses Telegram webhook rather than polling.
import base64
import io
import os
from pathlib import Path
import runpy
import sys
import tempfile
import zipfile
import zlib

PAYLOAD = (
    'c-nP&Wl$W9lI`H`8r)rjy9W*K?(XjH5FCON+}$O(yW0>LT!X{l?04U*_jdQz?&%*bRi~@}^{H-Uc_?UX0000FxX_h1a9%c<JHZ72YQ+Em*ng^~',
    'PVOwuKDBy&ZiHjWp9KY`36;y2x**InmO6aggH-zo)o1bos+~^6K?mkwh>itQyv-<?NYixtu^3g=gQuD%wFJ@ygAuUOWkSjbWi8wT4z7`y5$Fx0',
    'uG`9T2axq-tkyp}`*?qUzrQBb92Xad_Zq?xv%aw&w?5%^@%*Ek$tUB2)^7=%Dt!^U<M!_HXlc*7`*8oQ>8D^$AOK97$@I**A)8MlFyAHg&Lw!m',
    'o)efUsL+-==57Ym{|C;aSR&Dx#E#wpV_H9}7uGfU41zdady>2EB_0?-XIcmG&x35&WA-5AsJbPy+fk`Nt|P;OJ`3r04U%YK7mzrfn<*T*7IFP(',
    'U|LEuaS&H5O%acNJfvR@fBtPTtlta*ZK!Ej9=$t9R081*nff22hcPoCp?>@YAU{=Wgtq7hg3@c>$k05A%ZY8b<J_gu^H?SvA&Td$8*yUa0FQ4k',
    'F|y)_%7NeEYWoF9PSA!d&Xw$m7%fT=6y~-~l`zX&hlw@4+C8d@0ECj~i~*9P)$s+8Wbd#4$V~!@1!;J|_SVeDcy}};`6=??vg8Hr-vet<kjxW!',
    'TW!i`jhZTSIB*R`yiPB=%WJX?p9OToZ04U2?40uafc)T1sgurA@8n*`hC<Q?k0bAA>7~FuJ`NDp+NGO;Srd6~hhm8x%8c=BQf-bRuk*KgQ+wwA',
    ')??}TNC#%NCur{JbOV3^TmU~YbYM~rq?<Um=ODT|27a2H&Ev)VY2TTjgjGrR8-W+_Y__v~E|&)v7AsS%jD?IwdAvUaCMw2(dHsF7b9C2hJfs|k',
    '+@{(|!f0Wj^|uN#BKhkW`B}zU;N$(onxYZe7aQ8w0O6Px+@%YI=}sr<gezvFJ6IY8FRn}CXQ>lEx-_ql;l&9Ia7A;26X#XxaR%$+^|6qb1m(>E',
    '-ZvSUg!Ki*(S<5f-o6r(7M2FKWyOJgLF1g~v9^|o2ncCeIJ5WczoT18O-Cw3-q#k9E=p)EvwiFGefBKBmxV$V_HH9o$O_mDf>12rroKRQv$=_J',
    'g2-G6TlTBiQj&#Wr($x)HH!5kzF9*&MnjxgaSp>gYW9tA+()a&RfmcutZ=jux~?2DFziK#$Su}aEWWCu$IT`OMfi1C<~=Ax)XR-f)w*{^y#$03',
    '|7Eycry>b|<QACh&(y(B^zhXsZKR~5eB$}4Do1~_6=vpVAhJo9q-V-FYVUaHG2wLP^hzRwTZ+IPX;+8kb9XGA48+(cBcLa1<kWhK#QEll9mW3?',
    '+en1*vWJshUnhpwGMNNh?_47Ec}tn`MhKmlcOX3cBkvS$2}~Y-f**(<kz78pbXt3WFk~DqX7xg7y(v#Z4UFWr;x%oy?5THbKBzX28W0t+oR6+A',
    '?j5+z?7JpblIBwE47P~WfE-J!&8SPhEnG$OmN`0sm&d`&HgVTw<<6O@`wGRy(?Z;&%|@D;hg7)Vb?mjS3dZT^>4o*Y8dLGj+ltcp`_=g2<{q`-',
    'H;NfqvxWn2Jk#SYk{CeF+{u?V)jNifKzIvY3~~)>o`Dv$%c#(vC8pq$i*`Rh-b(l39R0eKm}(%3MhZYnJZ=!s(m3OrDf9hVhG^H3BN%MuqESHe',
    'ntjWz=uN%+`XSnheSLrqijX?b7Ux`2DzWsROWHr^K1JzhMKXo`1DJ(E38U^}b#mwP-)#zfXCjMV^O3~MUXY<J6&8IB$VF^;1e{#Lcg-1Ry!P)i',
    '7sYV0#A*i+W5h*Z9+|is1kRBwF21kaOAI?87GQjzDBdt?g&H_LoH{4Io_<_x==O29gRKYLiVi%6>^N`-6nqbYS=)hH1S;lJ`AK>+12_QQ!!Rqs',
    'z_5Ecj;?2oQ*ThtgruPBDVZB*y81l~SJ*1-5R9$yKHsmF22tmf-ItIR9sHMj^ywk7dFX32ddPc3;9z|%BqO@ksa%~aw!OJ8O+}#)yKF=}pOTEf',
    'Mah9z*e`l*6FpP8JB_uFc|X~fP_+d6_V*N%etaft9O$@I&ImM%AUO748}=H|_5GvS#NOAnc2=wgzESU-;h!o;w=UVuDn8nXgvL_etAASx02;ri',
    '80>%nPExqy8syZz;q{b9fF<VXAHix8<i2W(8f_m~u<kG4)nE}fN*Gf4hR9zU3Q=^w27hTCu93O8{-yE=#g_awi3E;8kZXIyq*DN>Ohk~ZC!>@x',
    'mFa2VqR`^DW&Gr@wcH_P1!75aGb3>=S7{~(aJN<i+73Vj&=wv1o8blH@NfC(2Wz9hhT$h8A&xgQ(i-t(J1QuvDKbLPV2tZj*fzGlN){W_V%HLz',
    'D3N*hzn@eMb7f=0Qnt{@@}-JEQk-N*DA+59Vf*UjpTzb_Y1yME<rJ~}GFKJ?pm+6~LzR<$fuy$9m5YTWE!yypPTN(6nQUnuw(!WDyJhHC3Q%?<',
    'RthD23wIP`P{1S{w${lxM6RMV8-t2Qa>)tq@8p^1IaJpT<w!zBXh}cTfqB-Hg=ct_r=M1@gS4c>n%EJ@#9YT=*g=l?Ihl}|>S{5_MTa@muk++G',
    'f2<?!f=H6%fU(IX6B3C^+7BhP<K@Ow?iI~s+NSwsNOmac8>^(D`*Yg0Ha@0Y25b60?S%)NYd(n-3eA!pjAABACCYlFLZM+~D;(Z3(lx<W65H=2',
    'S@#ipi1r!(OXZmyS7dp4!I~WiX-W>>M&#j(uU`Y<6FHV~d2IId;y~;J5tKI>gh1;mEE4U-Pa-=<E_FvMq7&Y)BH_#@DFT0TH|VQpGnm~_`Aii2',
    '?`?Ew?Gf_E(YWOT9q_yBG$bJRK5R|!?dcw}b~&xx)5UkqqTETEF9b^4nNpgHIvM*4vb(s)IAb4cRBXPR(nm^hRCdwG_rlghP`3y4=LW+=U_oyA',
    'a=xSArHuiCa5SL-ZA!d>z+8^Hh7W~I?U3e%WN2MBmjQ_F@eOth4Gsl2likHrFpEi+X^4#&@^6p7QBIfJCKEh1^o{x=lD8uMZm(dbXQ$wWc6doU',
    '&SR@^E>Z=jR6+PwtQNRvrn6-EYr-2aGdWw=EAhA`>vR76W#BFJFt~G?kt|)pKcE0H-7o%9!btRz0?!-32VIKW4LBiHa-tker&hcz)AcXqEj;~x',
    'qMbW`-~1NdI~+y-zDRbru1KONlCwR`zJ#z#5h#5zj#!-yg&xYM;6(XzNuUfLZ9=5bojwn$MR3$m^ve;TsA?AAlfnTq<PPIN)g+)wQ)cR;uU1}n',
    '#!xQ^iBhk@uq6`&)a|zLxaOhHAn4Pb*S`o$`d?g(?318nim0QeMQ#^i+fDyo@1lsy^u0hX`C|GPDUF6X1Y!O!GC_%?_{s(BIaemkALSAL_4Xv$',
    'WepjRD1s$&VBRtVzlVn=@zN}J{PIsO9V8*+9FVSjkw`I+7dd&Gi2{Q+TO~8)lz`%O_}RROK4TV@r`6uExieJiV}|8T$aJEBjgpEH!ft_Ki$a7M',
    'J8(bAoOEEPo$1-DDdO+xaS|oc!=HRHqMFnB;ZMk*&q8-cSfP0b+4?x~_o#tkqBw%?{Q8;mNEI)oHDx}C_yf=gffqTZn}Mf8W%h4<VrAv|Z$3-I',
    'u3ZrtdP`rTf!YIHe?ye-)#reBt+~pfMK*rqt067NMq6fMezdl2){^8u^GJB{r4v}eiu#W%ew!HXXEf0GeuEFwhWygq%_iid8)OH#XEub3Q|;T!',
    'bb(!jtC{L`23$M7eCOFh_yUG1naiB=X|oNQ3D}DR8zm#3`elZU6$dOU3c>&|n2E9YLLn$lgHVl;Hl<lg7`pa#U+BK;B++X=OZ@&9!<d8%-@8Xs',
    'z{cxtj?xEHD53AJ!S0n54${`$eLy7pmk-Z=q6T9MpOleIT;OmhvrTMc#4=lxKLqj)6Lv^a%|*@*FIyXDC!kUY9dcnVGki;Y8H|2Y&C;XfA|>80',
    '_a42fCk<J<r<tZtKu*$AZ%$bvV=F#m%GCJ2xJbbG&5D}Y$&7W?5voEtp}r?vvZyD4!vDjLMb|6<eE<SbuO-!>;<?OFZ8MQRd9lgtD$)DK)>E>Y',
    'y20czb#4=eoH;Fzno%z>mt}QZpsw>FD*5*lLJN8Ky?35Q6j2}=%X3)xLPA~eBr*>jZep`s2V2c?s;x;$U?-O`^($(v-a+707mkjcwOd*o(O!t0',
    '<h5uQq<(_#0z-1|dBhDgn3X)jje`@b?!_+S?=6|_K8s{6t&CQu8pgMuEw+(j*2g<^9ao*U;kt`YdaGi58yqw^V|R62J*MQmub)WjEz1rM&<W+-',
    '2mH0^mK+9O&a~zuERvTBt1)AqZp`5L9l}SoJNvSrM(G!o$a@nWENuNDFW(UaA_-9OqJazSgdA_(TakZ<J7R~I{M&<$``A_;k0>iLCo&N0Cxns(',
    ';N1<`Ig=9$F@$NJ0$y?CcGnS)>|T>X+mER4VOG#P_>ZRvR>%xg5<_+p#mW&G_MS6rQLQQ`;#Vq3F3ChBo=>1`gTe(MYzc#*gS(+@!3YvN%+6|F',
    '7Ijrb*x!cA?=*YU_IGa)YxI+2C8s`gwQJ0hOcz&ya$&#MjTx_7A$O#AUr*wm->JRTsbAehg)|2Ri;+d5ba&unRyXh44m=B@%wUZ#v;~Xr$U;*o',
    'FRZ?`C-IRYZc=)EE4=1Hc*7{sI#soNxD-a_hW3QzwCrjV66mj;JTCaNypE(0<!JAdRm+LOWGVQ0fn{r8(?p%|r%DA8m3K*8C8-pkUHMDZgwkBf',
    'g9dutU6C0{^ZU6yWWAn2lNiY2ygYWVeCO*e_6`=LU-ktQMNt+a=w6^r7HfO)%;6xZQGv;VJrkzUYJ$09qcEN>G`_UE5)N@B4DM-oOB*%;HXhQ;',
    'c_AIXIa>{Tg6Yut2KA}JIXathwrcvANo(#IooynaqE?Vn>kYd<JCrucJYqP3OIS&+HX05c1>3xRFrocW;(A}(O}M$^oKYXA0_9d$?S+r2T$~r1',
    '#fs^QX_(3DY4a|G)e=x}oEm<bm%HR2xUct}551}mu$1d}@JMjmfIfkB2X#+20>$p;B^a0EhbI-HTmDBtr<MihyGuMop30;vW+mA5eoxaJT2#v0',
    'y3qHYH{WZZR?Y2VXz(R}Y3&EKOa0OXiO8yb?4OcZv2OnZpPQeqPtt@J+F|d%7hp)&vYIvK#}&KMojj&qTPplGf1IJ#Zn9c)tRa*l!&Yt|iFBA+',
    '3PRu<cQ$$JhBBvts8=YGdqwg)1SxiTki5ceOLxWoBFgh|od%iopxr^}b|gx3SsA3z>blsQJK~4&CFQPc*Awf~tMMa@SIAZT@_wG9yWW?z#Sir@',
    'E#3;N13J`|>uy+Nj9@OeL9EsoWq6|Su$xOJ{AKX5ThSO&Vg)^>>*VH@)yHO~ZR}R*O(xNGO#Qw3xnc?JD&^_JyUL)4f2OusDy70BBZbl=MDF*d',
    'aS3xoD==%+iVDI~jU&k?FWz@`hs(Lf<($uRjF2;2IL&$q>Hmrd6sas-evEwHgW{!p%kZJx)EDx2OOjHBRrm524^S7=gOuXG)I81II7;T$<Lg10',
    'Zr88L`@L*`P|??~8E6>|6*MWGWMkFg|H2-gko`AUk1O=`Tz&l}vbXLxrH{p6dgFR?eF!2@Xlt2O@DuA%u|G;sW{x+>5Gj+f&C;dy!X3;4v}Hqb',
    'Uxo}%+CE1&B%>z<!*c66vFEk@TobUps;x%#N0d%r5dAqH#(jSM;cG+NC8np>K}zgwjqHN}1A=R@i~O9E9#ABJ=yv!`^e0@Uv|7^u*@vk``Ah)9',
    '#;Y3N=9NYNv=m*h-0)5V30`aEL~Ss;Lgux!RZv@vArPz~;wi<fWgEK{twm(xJ~<{{%OI<tMn^v@d&$o%9+1U~k&5NUa6s#=iJlToq*|I%#r7jd',
    '8{KiGjE-U_v!IM^TAg7-#xOc5?EuWi4$j+_wd*j|9K{uXG-#7m+noIA?}Vu$lUq)j6=nQQ{zDmY%a1vOc;0$^2Tze}Jwoj&2I+}DFqoldOvuQP',
    '?LC^Gll%;yVh-Kf2aU0@0xxkmju@5={1zwjenmp{*dH?Z`K4stY>$m0Z)Pi!M9CuL!?U+V7G58lhjh|cECBasGdh0-C5+DUfX~BfJ@koE@6cV5',
    '=|$qnPGWhV#*C8GAFlQ`(^rjE!E4Ydm?@9p5NqYfah}g<mddTIjjLE}gqRD!E`xX{c1%#Tq2dTgmwPda#;1Zo$$^(iQp9>vYnO;#a+J`GNgxdg',
    'X^pqf`Q(<ci|181EFOd+A8T`plKi~uDytE4x>rJ4n6ag-k&l~~)*sBAAd3YBi^AYts6zknOe}vnVc?aO6Z2P=+*ozcygkAX0xjGjZLD+;D;xXN',
    'v~F76P^FgF%7ym{X&L(LM+ARsVmMj}EwigX6|mG}IQ18*gSnc=!IIO&`_@!!m_632hh66Z6zVmPj_lWGC}Ny-$6YL`HL3I7=n#iS`FaK-Z3nR?',
    '(yKjRibIk8tnDoK)3hnm_9b1u)e91thf7+?Tcl(InWDpXXjF>ZF~3-@O7u(=Bwcs?-^xKHFur7e88`T%`}(ktWe@|&B-(@K5`gwN#tMFo-z0+x',
    '@w!o5j1`9)YDcgv%8@UP?s0>I8j<Xr;!uD-5<xE(I?1}KRt)o0BdQgqs-%s>(m(miCN5AsbBX;bFB@*`(W=~ukYAptK(zBMjNzx3U;otI?0J9V',
    'luWX&y&=hyZ~k@86;;2|&%D_tQ4~a(I$1`VGBX+W`a_)hd${ES71;AIhqN>MF?BQeUh8{AhTGA3@X8t(RcNQBsa`93-ZyirxG4%(dZ@HuAA?o!',
    'N8(ABP+H?4#hm$`k63XJU^g*c$j2x?pHv*=t#D#)6fV`Y*;75@{1Tq$FHPh)o@WiLPNNBY3yqeo@D)FC6<(N09}EE#qzMT8IM$9G-#9=vXV~t1',
    'CIAbHl3*9O`cX9h8fA&pjUb9lfGe8Qx{*}Dq}i$8k<h2JCw<D7;=1yNv{73g1j{TzHRF-B9){q4^&bFH_<;v=XavwUltICE&&NyUv-u*QksfCU',
    'BTKkjrgq*hcKx(<eIeB(`^})>H*1_;t#`J`l#YDj+r9H&7Ph*F*dL1w0J9}9q$%Ru$X;~;<SIzhtd}bO9;wt{N^Z*Oe!1sKCu^A(m9o=JBF6R`',
    'oz@P_Kvu_;(02bM9*G~q!v(zNqh%e-RU21PG($G=o4wr~>bIlWv*m?iD0vH4BTTYxwfV|0_?RVr3%M_t65T+oY+XLc)cnq>R22N(sw<-fo6`YG',
    'Ch1_`c`);Y0IxMjiK(VM_(PjQ1Q|$yVKffRso>L3fzG4~wx}=Uh#ffHm8bN80)f6sy=(1TgX(=O-skREw?9w21IL%}RK~c;v^TW)+|<zyM@`lT',
    'g<S7b@YEh#uS@ON&>oJu!l?6*_Jr!18^~CC?NRsQXf-cUj0U!$ksL+m1hf7m14uI?{n&8w5{lzS2Zqx!9AW(r!ZA8dreCBA_+jtGUTEC>*lfsd',
    'xZl2f!7+|7T+?+}W2#n<RNq6#(Pxu=Sk--)5zbwNAyM>43ujJvPgm?lpaq7G3{@o)m_Xj$nt|Y|y>QdrGFl^voD@kH3YVKH+}J1H-YQ9%bJnXT',
    'eVV;yjXJ_f>`M_yalW}2b_BqOL$lw<IMmuK2H_6|YZ88np+G5FE<kus6`9FpM7&t)-2O^Y?v40_QvPqZ@P7gTB;fzzUsX2?S5F%=3pZ9HBO6B>',
    'cOxSfXCElQf9H6w@OA{j0RWR&007>9<v4iQyW6-~n7Eo*|LdTxZR14Q{^g_2XrPOZcPU*uHtbieE^`B+J$iADsfk}4Ae2IxBW?Jfoh+L`y>cBi',
    'H)MuNyzLl**uW*x3w}TQ2Y%EjYf96xw2EyWHY2Snt+Rae;S(!ZYf%Wvv6=eKa^qY&Bn+0wD%tSQ!=;BX3tNB%b1f|`sK(l~w(zX5=?Ggx9#1{)',
    'xl-MFu?n9R|As}|bFrpa8yShcl|(d=fVTrBNSWFxRVFB9s5@=Osi?~{E$Wh>YcPZvTK1Ohc4!dYGp@J@$a;Q~VR>}ZmaU^N;K^C3?7&C#x)9un',
    'n;u|PC6tG5`v$~x(y426Uytha+Yvjl`24thpMw~NI5`yVClU+y+lLrzouF!;d7sm-A{i&CM^XQE`?cfq_%CgA-aLjqBNZ_w|Dr#0{NZMwx~^d3',
    '8>qmgjq8J6Yq4qT#p=r5;K{1@*vCObv{f!0B9~c%I2gr>e}^;8jh92XI-RaFsIFSIF|;gf;1`Io3CbZ=ySM#xxVp5nww0=xScg2tGn$&nqRfyc',
    'dp6Ky?emM#r^Cl+GR2cs4eGegEV5B$lguI~hX%cU3T7h(_0I_wYNv@ALD#LXIZhq2BzBV5N%z_!gX&@=K|f!HPy|5u(_itv$trC-qmihRZ|ZM#',
    '!}Y`23RwgiQ}3~ex0jHpm2Xi$!5Q53vMc=l?upT%QOAXL(vv4%8{o=u|FQ?l_Ft+Zy>x<)LO*cf&M#1o_4F|<rNbRhfew;TtzgFbsylj?pJe;Y',
    '$h26J8m6d(1CX&aK4hj<!=Iy0E)1UtrMk2&j!$ROhZUanE$4A>2U?`{*ht<y$xG&ytFU)ZfC5#>yKLNHcaD3S4t8p4p5bcK14nSg_LcK68STFy',
    '!t70Gb&$sls9Yzhh)>X$F5oZhm%AKPh-!DN#cYw6S$%zzm)$ORH}x^Hw-ifx{@Iu%NF|*BZ%MzBa1QNboYiJYdqJ}i6}%y^(_M89({=Nn<(sao',
    '`{vc+!Jp%Qw{}Bx+8&wX{ADGPYZj+SyC56w?*`=B@Ai#@BLOAEl>JdgrLb-9A9cKC5p|TBp?DqOeCR=^w_qMxA;Znp7Ud@QW0rJ7&{dE7@6+O>',
    'zO0gSk_AK-d|V{*2m>a}p(%|y{<69rW}qLoG+RTQ|4_>jBZmi57qat-&gm1GtmWPQ9SXYhR(99#iriv;Xxe$$UBlZ5aG`}AE8bvyZB)2U^>?Lj',
    'l900jvuyl)P1*$x<gPi;TlO;!;(z$Q&+QuhEHloKlHJ;GL?&i6@i!I_VvXLPu&Sx*V8T>7N<(2uP!IgBWrW$AQR^i)#BI}v&ecffHCXz+r5vxu',
    'Z6fBU0uTO^&e(bD9vv>y8h8H)K6DThZ?KgfhsQ9>%BJXm1zU{wwp+mR^&#SXMlqVw{(MS+5hBlA_|h=L)a0qr;=X^^^@g*ivqRb3JqPB&%O3(s',
    'ea$G@{W0B5ulC}rCc>1S8;RXhh0H}fb=&<|yF;3BGwEmzzul_TT9juf-z9HBzEnoVu&gA;^!eBRvW$zEm=tCeyH9gAIAQ-mo*$!v<azlE@ufc&',
    ')e0-zW};uNZ?L4Puxl|EVXzt_xavqz(+e!Dt!1&B4?g34>aHv{_G|_{71k5F5~(ivbF)-us#6Lr%j$SpNB0|FbHIeAu0+_qT&OuJf^qDaN+R;f',
    ')f6pCSF-abCGUv!3ce%|mmAIil-J6I_%;L6@KZ)hC~PTym<Lu16?_(&VwE6Ck`b%u8wJuFmIqhPM!v6B-`O;KIvf<thGhJrHe&B6kb^(4BdcwJ',
    'IPz;25;_Q25T+CqFE2|j;Q@pAhjw#PTx7kJD>};By)cUr1EoM*g4YMeva!2H0%nOk{dy(Tv4t<{_6+64>5p&`&O$l<0>X7Zuu0b0FgpbuZC{!x',
    '2$`b5flg%l6m7hn-F;VQ6G^{ziwMjhhsAAh8VONn$;`JRPcxMz8fuqos0yxxv+Y5Z+g*Xn<+{%F9bwZx>#7U=hXk~cFocFff;<<4!Pc2j=cS2a',
    '08C_b)ALpRBcBxFuas=gs>}IjRV-5yt8_Toy7*4zV`_PQ;u}w0<DPEUi`2xcU7jN^s>EpQeMO4%6K?3c5&A+=OdS+nlMdBXk&wJF4?{(#US0Yt',
    'g%?2rWn(r_l}1z9#j~a9t~v{P)g0~K-MtKJ2o*%%F9O&^vJLXLDU0R#;Oqmgaq#1tarP3@EySA_#$oLHK#@JUkvllHF+OP;f;UejbAIHgeU(Vq',
    'n>oqitNCKxTaF<)yM<C`Gd))R`>yhz?5~G^-)4Z8jY1alq(y|nMrwG5M%J^4!=KcrCif9Y-CC2+q_SWjLgeoxe_Ps#Zl(5FANi*`{x@Rt_(4Cz',
    'RT$by3yNI*^GrpWgG>t=g^kbOi%;k=#fa-vf95!bwprPS3~_{Be5muhkO@<JR@*n*=4rf^tk!x<sDd8Nvvr%{zW^ZLzZb=TRq@X~+cW(KMSZ5s',
    'XH(ykdaTA%VFgfLg&4HDkHsRNL0-!85RlkV|NGbb{~;Ix@c)0{|IYb$b?~1YWW4`bEBt$hf7c5C*+CTVe^n03@-Y8rLa2YN`yYQ#@~`Ya0QRwA',
    '*8',
)

def main():
    root = Path(tempfile.mkdtemp(prefix='script_hunt_')).resolve()
    packed = zlib.decompress(base64.b85decode(''.join(PAYLOAD)))
    with zipfile.ZipFile(io.BytesIO(packed)) as z:
        for name in z.namelist():
            destination = (root / name).resolve()
            if not destination.is_relative_to(root):
                raise ValueError('Unsafe path in package')
        z.extractall(root)
    sys.path.insert(0, str(root))
    runpy.run_path(str(root / 'bot.py'), run_name='__main__')

if __name__ == '__main__':
    main()
