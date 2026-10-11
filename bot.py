# Script Hunt AI — Search + Random cards / Render webhook
# Self-contained: extracts bundled modules into a temporary folder on boot.
import base64
import io
import runpy
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

PAYLOAD = (
    'c-nQEV{j%;kjCHGwr$(lm~U*`wr$(CZES4Y8)w6fy}|wOu8wv0^oN=5si$i`{-&lCWx>GF0RR9rU_nP#kE^_qD2NaMc-8>`ApfZvJGe4BdbRQYao-+G`+h=K',
    'Iei4g(nvL@*o)>|Yey0MC68}O@7;F6#(*LhhQ)whcx^1D=A~-NSrc%|o28U<>6Tu;%Aft({KXru$M>bEALI+sKk$t5>^}nlLoUs1ofe~H!JgUaa_PSzz~^x`',
    'twZw~7R!|l5z7^1%J2J3!uI3i#TLNsXY;0J472;OgVInwN2;H&M=0>mNgw3Pji&MA!P)NF<QZY>F5x$7zNbNKL&9~ueFEWP-1b@$nIvZKAagA0!AOtrINa)q',
    'IqU7J!;h<%pM?#K!<wJbx=(a>kefFXFx>}+MOa~AxMR4yN>>shyMi752dnE<VLhcuH$HaPrSC%9^P)_ZM@Zd+dOi9LP=0C+94|5#kOVKmDXyFr2p$v&De(N`',
    'a9k;-6F(1%iFm+Poj8COhZIbN_mOT+?F+LPUjBy?O&4Fr+}H!g>!?)0r^jk{QKlYe=ATTRPFIh5XBV&j+vm2Qq8Ac9Zcc)?KL`9qf7wOIujt98ki$>aVdYxV',
    '5v-wz@t}Oj`v`D3_nd|pW#>NmhEZzTIjWiVoVwcCA8rS})##7M)d^ov>0j|GS*W-{c3y4B?sysr`^?oc)EfAn%-9se<TyO(S+l7#)o-uZu3+j5_WNJoSL-dx',
    '_M5DPf#fOlyB>VlJileE6`tl}k^h#LdmNIwf@WGEnti`>Q9nlXt2oLIPeiy|ctKsR#N#-48i_v{)oVavX#0fdL>v-ZXpMsaDVPXqi<TXb6soZ(rjBi;fM&u3',
    'V~P)&0TGhERo{;KITvHJ@bF%Kqwn@v-tF?$)`DdN_lu;Km<me>4cYW~FnoCE87o)*P|xka;|dfA7i-mXBxG>C&nNr?A~^AL8QV(M?T5$jM_CI-l=#@?ym&rf',
    'Y&df+Np05=xjr_%9zr)Jy$72e(We(aWMt|z^T^?OAD*H`IsrAWe1U;>$vG3`SH1ArB3C#IxrHrG#j+_|Y%iA;t_hgX8BWbDH}hTo*G6Ac<ANK?^5Q`6#cP#L',
    'N~e1YJM8{+^m026PF(>{i~}Q6U!xOx(8!;d6e&TYw*$^Y#CA3iN23#d%VW?fg2H&Z8FD`hKyHd>RD*dJXxswmJ_=x^LH!i&s?Ps`?J<%(hK@fF@<MAIiiWI5',
    'S6Ji<j#&CV4fv>^pnRPhs$(DMv$i!U{TfXUESA|rNbFOHGQqR<v^|6>`biTHV`z?20hW@_`S+0e5c*5bdQ)n1e=7vcVw_){3BH3`-FmqwZJnaast*$~P-}$p',
    '7W=wOdRXU&VEDpw7+hr%^kLnmv&SE9r(||cVRiW9*afVHL_ayOZeoow_BU{`v1NrljFJGbQCEjYjI&aoBby@+A%U#QE%2&JsuHTB7l{N2T3%JlBLm^(kj3G}',
    'KiMoMyr3<{ee?Fwixwq5pp@@6lyW-+rCb|?a2Tmkrn$l(+weW$!8Cge%fyGG)i>QNO(o;GQ&<vpYt|o@US3|JO+ngt_lQpPjYzd~P^)+9$n7JCV+#BCb$0uI',
    'ndO=<7d0BI|AGqnvG+k3?uGLpZ%A8bLSaGOhCxCa9}m8&$KRo<vitSofkEy@2Uhn^#08K7C0C#;2i$thb(gi#eYr<9j$R~R23flxnfbFpu7S!`;p_$%lC7#6',
    '!+%ToZt1TtQWk@XOk=SeM$M_NXp=yb@zMERTCJ#UtUiKDV;#Un_}{%hICr{{EFrf56J%g%6wwWZ-x42Jc)xW{2ZlU1<<5pGS6jrZkYYa(86kvvz>ap0ochDm',
    '2m!G-i<#VGxR)0l3&u?-!}hto6#W+P@*AI{ue@8KQ_m$V6tU_S%Td@%T)P`qL8k7QK6pOk&lLl(kmSf4AOk)+v3n>-1_MuAhT^+~0)zsEK^<g<V9W`+gdEO!',
    '_U>jYoR4}|5X3oA;-IMKfi9+L@J|q|A#2?O2-PM>Uf5PfK|r;jzfigsB^PWahDc1NAt;jI%XIe5y4&E2LJdo4J168@v*)prqW-AP=*H%L#9vbp$$M_BK0$Cf',
    'OXaQlj{=H6FLz)?c$_|d!?oegkQ7URG<8bFm{q=loCThojDa7fH8uSa1M$rn>w0=xA4M{GC30dUs^D0sBut-xY$+~Y-E`+?USSy0qk<pUm9b@4!;yWA><Qt7',
    'YP2`9Gv!`Q>oA-wn_3GH3zP4+nq(H~tBe}Wbrb#@nGdGA6o$d!sTS()*{Gfl)`;wPs^we!kaF{r9X;GoX)^AbHwvtFW;%}?6ATNJD?R;wu~wd2(>XlfR@<1B',
    'owAGc`wB;6U?VvNuQ2uCVuSTVOlbcl5$JCM5Q~-2Vsh3qF*xLwD($i)t*o6E3J*52Ph{QPZg3(CL36Q*d4oYla{m!c+b5AOVivkXE;)CX0Eyx{t47ILDGmGc',
    'DzN9!;W`?@);VPjf(}Ot2_8DduDO0)+S--^TY?jvMzGb~4TEO2NI6x@!YV^;)7PEZ=(P$-xgJaE2=Yf$!82UU2xLBkL(9+W<C%@S#6g^2n40_c3mh-U%DC`2',
    'h7rhH3r6ZPeM%z1OP{E4Dp56tY^hL-Hw1#Hw-~5<=)oBy@tjm|Q>N?0GS(cr;+YZzTprZw2TkYrM!FDKm8V^Lo`nSAeUQ%X5#i!FbxQ3A<w%zZnRzq0j8*5X',
    'wXtgk*7J$Z+_N(Fsmb9lU6mFS)6GgqX(Mr^6BZ-WgxuP8%4#C-D^sMXh_5OGiAxTAAmC8W4Fm@q6N0~AG^JAHxowYhx`$cMYpnpX&jlJAL9QwGWH$mJJ)wc~',
    'B)`4Kk_5D0zfh2u3%ML`!wYz+iNftoWs5v~z546%r?!fgXtDe^g1rmditf5mDR}CRQKd!4n8k#%J%-XZWQQy}$bmjpH`^GZflW<XnUHuge&tfM*?MnwuN%3j',
    'Hra}kV>-qPjnpQo&6CG5EFnZOA|r*GMeO_F5+D@k+QyGi%(u+po`7)1%p$|c;J6n@UxK_6NkbPpFpSzhFlR!09k$<QNhxG#CPAE>s3LIAVI%{1*|)?R_OLdL',
    '{AB7Sj(A5L#@JmN0v>quk?5V9=j2sKF+n-pBgn(8e|+vJZ?$|h0C=$ZZSp<b06u#b0$3`U_F>CuZOwjHFT2kf+2^hpn@fCe8kwmbmzb>!Uh5l2l{MnDHjGXf',
    '{hLnV%52k&-0#@Wu=tyiCeOSKClCPF19lawsSxyLJC<jZ9hmH2fw=lZ*U0#iv|sa47(UvOu!zi6Nt}6wmpx}glG2BdRzigu6-eQF$zn~M+=+axB~jM<+!9H-',
    'UOLVyxaGow*7wv}d{XYmz{$g5YVbg`$<+9<1sP*3Un3ZZcwt1h4TnZwD0WI>wn3{2ynXY@c}6`ED63#}jbtNO`~+~v<3K4+qq%NSMeRvoFNZskNd=T9xwpuW',
    'L_yKi@BnoYtZ5E}i62|65^1(5TtLz<wUI!Ku8`YmIP%>Gcc6)n&o(P1@TdsGgHx|{Gh2BI4_&!<5yV2gc#Kaprub*1f_rkl&$Z{`#k|~GH#b7hdE2sB_Opty',
    'MQ9Sc`<9SaE76rmTi%A9d=p<RzjNpg^rzF?tIF~^JM0D-MiEHKP>#)b5mF)R6pcg(a-vBQXl(aD1jG5oc1b?d0-=YB=9h518BASo!%dOxP@;X674!_^P`S>i',
    'boXcOe9f4e*r4xz1i|>Yj>OM$gaS86KhzRwqwH{Tza&=%CLt<3M(eg=fTu)lNOH*|^bWYgA#En>WI0yMbcQ}eS3JFo$m=d(CT_zAZEZtTiyiz&6CL-0VOj^U',
    'sAE-gurNd3nP*hZuGKuY3q(^sryc!oS5Qd=>0*6ib7XeQS~@!-OQjz1ny!Mhkq9rX1I4I#ZG)1n79h1dr7}|!!9AM~evtXd67L}lFCVIsfQWiDeuq)BAdlQ0',
    'HDs>&&sj+^o=+M5P}r^9{7YWhX`Pu7=z6f*5y-B5B>&GwTuNEGHD?5Rt7x~*J7)Mt?%I*8Zlze?#F^o<J=APyNVq`a8+s6vk-iCMPbWVQ>e-IT0co5?HRQ_5',
    'h#N@10UnuAs~7nwtn`dOC)LQatyx<}8ES-3+A?4|*o15e4~1>nt8SAm%uA&muO^zQF}lcH2wAtRGN5$9Np3bpzS|c@I~c+fH&SFm?gKT=;yU~BOLMcv_{!O>',
    '99ia+Ua1{eZLO;JZbeDYp<V)`vvr`dH-Q66Q#=TTt2pU}IgVKmJ!-qIHFvqmN@;~^xTx^xd%WPe#`NG~hj+zdAO1xh-JSTJQVM2vanX`o<x!STiMW>VIeAKf',
    'D(2NqXdm0Zk``4lS-t7i-pyO(yQa=b3KpSq%K;rBr1$vk0R`&c9@EK)rj^$3kzQw0`(k5m@GdIQ1d!!}>8pnHc@~INpU6D>RHG{i$*;IUsgTpnxl}qo_}ZKv',
    'Q}YjVG3s$Xh3EAQ5%*!fTmbrOPm3D+UPg!KLZs(`tm5+o8q>wxqCB1I(R5}oYQBKD8gs1zvwVg>NpVk*saK!VrybXkDSuQ-m<Dco;?K!%F?m3WGqQ4ZtqWMG',
    'dzXF<9^)lLjH^0EBK4P&d`0ph(s{G@MZJaGaWp~wddYZ>OntV34<7W`VjQx>RS5VV|Mml1|2}13^eaw}D1j2^O1<ZCF!2e|HDz^}*k5ku<%s@5Zk8H4^}v=-',
    'Q4#Ary%|dM@R~o7H_Sp{`rbW@Dtaw|JQ`Ru5d1#lGJd2A1b1Zf&j6VQfkcMTC!O=G2$E^h`-1gRB0Zm1jdLOH0JW4s&DvypzK`1sAPcm6BN{m;WCa)@ZtwOd',
    'OdRH~od5n2BT#PD$v(v!)Bc;SsRD&u;As)cxFL5V@A;$OU-<6>j*;{>yk^9{ctD(n1Go=w$pYm1^9gUqR^v!DF4l61gpX`Hrw$HuU9}7jnp{M=@TEEl{6@UZ',
    'QBI)wR${{eQpYh06?XPnh~3I5J_fhZ<Mv&{IMF_5dMC)(<%BXJUI~I+^gUN6=#-+1R650zN9E>ZQ__sA*zX}cZDwEx?%gnFc<M$v+Q>F`_%?jXLTNw_yO17=',
    'x{7}XE)#!$uaZT|fJA2w<QM@wtod8dbD(=k*Xmqbiz?9K3@!@2g<srKHGdq=yU0q4O}t(JA-5*}^yr@ELu2ZF1yL`Z#;AbEx<e81wgX2+CRHR6Jce1bJ{NtQ',
    '3OG9Dm4x(z0;MX7NS?Lis&m^A@&`=(91Xf7FWsFg@uNKB;vd-kHob@Ga!-m$*I{{H0N-#fHC@U1K+#H_DzP%~wzy_<1vc)A1C<|BBD4bPfle@*7l%$oap=%B',
    'IvN}WHrHQKsn<v?h89C6D?|b@2v&@@)#&027x2t5DXfaeKK}_5DO0r8oQkTub(^UE$lwch<{?!43;UO7A{Jww|DUoLtg8$K1MU`ycT_aiL)+9~g?La?4%p#3',
    'xzlP{lm<8}@ZFToKsDUOdTt2;<@uZFWn&K4<Y?%6r*1sNCf%g>_kF)8HDni0x3w5PbkqPEa4d*`-rHc$*-HmX7Bwon?n7H>335#mIC{uG?zlJRYIfOOT~UIx',
    'ZY)ZXGCr(N%!DBbnCf&}*uqV{^~U_YaeYRDu3o2Si}%k0e&04M?;b0yojCo31`Wu+A(qWqXU5811RG9Vdng0RW`XXOIW2*PdiO9238_J46kHFJ7K6h{-mIAY',
    'By1PIDjWi;V!8Cl_{r9C2N%Z4SJb$ieGg0!NV8UQ&z+9YNC$kp5M{WXjckc9n+H27`>aOU8>><b^lUj2PBWK+vBmey;zV&N!=OxkOQ@5Xzv3s0rbhhrY8{m@',
    'G=7t4;t_vpYjs)gX4tn60C%b3_sX?9d_z*PRy|PZgM2V68m9Bw^~&}RDbpJ;o|K^y4}zL22DL}EjMouZmDe4JufRcvn2fSwDbdl=R_YLQv3jzG>Y&|`fhVoW',
    'oTLgdYYtvlnAHJ$F)1`9_bFO-CO<+18XPVifc#abPn8}|`z@bI(Qf--ov<J2D5N4>7z*+TBN~3UEWdZFhqB-+HU(?0bP1(b21qlAFL`-rQt)D+rvG?H#f4MA',
    'hA8;c4fJ<IeZT{M_*)E}djj4O)TZRzGm`!grH+m~-7yGL=sU=M-v0wtt<$Haq<iJ8jhB^1*G(WXZn`fP$5&GY!EX-)c27Kl5qP_u|BwlLVu<Auk-3w@3Z+MD',
    'YFTmI5rD;Et~Ib3-6wB$0W5uzODm_iu}5#+18qIGvu0Gy^(Qgen)e9R(ZghS6_7G(j3Ry24j9<o96Xf?nj+yut2zWFL~dqv5*xeUH31X#C}^!xM(Lvupj%!^',
    'tf%fVWE*&HZVsJ)&nl=l5pfpAR*J?TIFs5tw0hN)eWQnyfqcICV(&)kMu}lWXfEob$nGo2B#)sPRDQFaA>}JMdeID7`qeP${1J|SAF^nod2nM&aADHi+L(!1',
    'VeuF7J((eba)*F<W}|YM4A*rhd`6G#7cHZuFIb357)0EUHLORP?S|IEc|dp1QNrMYPiV?CgwfZh4X9-Pvyx3<P~V`Q81;CEXMyGGIKF|RO(13~+kOuGN)85{',
    'Q06i04za<Y7E)LZy?_dFKdl0T;V|w3CypN~dovsL0mR`OaAADKhky?pbb}h)d2~*g*D~Z2<yrL)oZL?Z9I;!WC15V{B)h3A^}tg7)dV<}mG>`R6cm*r6|6tq',
    'jYW9Lns9$HX%)WR7a=RO;U}#JZ!mQ;2~2XBMjR)Af2{T?4LKi81eAqy0yC$%iaaY#1j&DE=5~D<{EFz0Fn*M*RipIxRm4ye_QdU+ed3AmgAOn#9{o;4?EgeW',
    'o{n|)nc5%da6$SqxP2*z?yiW1(j_0?7ApPn^Qau@t17@9Hgz2pSQg?OSa7*!vg`4u!tbPI-&3rZg!NBx=AqQ3;?+@g)k2>8ZR=m{8dmW21sAKWiVr*{lQ@Jw',
    '!&g+r@AD*Mj=xBX$z{_S=QJ0GMvNH)!bV&3=Y%g4cnYIrt*|4c={KMzOkK>xml0sHVf&><fZu}#u#VpEi_U2+E6tH;q~3JUtlUDc{vxRE@1M>%GKjY~L4FDO',
    'HspxD{}Qyp6f_VnFBuqOc<q6@3M~6TrSt+8k~}j<i>E3dB{H8i?tu+(!H%OjYHn)$Sds|R+X{>&sszsR+bDSvso^<^gUS{h#*Y~CyP<A5G$-SZiY7bTu-|AO',
    'hBrx>ip=t35y9JHKc#8gQ1E$j6qZV>U}x>;(0L9-zZ<ak02JyAaY)lgVrtjWi8!WAwNcAx4@*VK%)D^YqX5#QCCUdgEwQn8&h7<~%_~taQEU|wW3)=_?+&ck',
    '4NX>e7Kw+3A-<!bkxq28U0pHkaK9SSaBc2|64XW--N(ER4IgZ!nVTxNc1)#{dw}Utb%~rIjMC|ZG6AN;QZ&KaN>SQjOVc2j%b_Ug(0{uo#Z?bp?Nd{Y(Xx>z',
    '-Mct~Vi8CuXnIX`eand7ERs=_r9b~(g(S~gF!0`$$)0#lOTgVbR2*5><XphyDo}{?NY=WCzhhV$MJ-oSpL8z#J-!n?5!kxPJnJday76+?cq5@C%q|`qFT^2?',
    'Ig&bX44Q+OdfY-^C7#FZP~H&_wrU?s>=My?yO()RGlyJ$C{o2lT5O_W$)2$=o(S>{&G}K(*`_%tb``|kx08t>O`Qmd_nnPj3)D=V5Tzh@MTHrnS3pr9OQGpu',
    'd*cL8W((83|MOvsM*>Lbts+aS<k$mac}fC`(1DEd{KDZga2BHpS1^ADS1&C>@b_zy&xcN#`cl6*lyqwXHK4oogYQfDlwx8DkyPun4*wBo1}0o*+w~kP551;q',
    '!nBcLp$Ud#b7L|I{_{AHgoif2!493a<@6pFxm)|daFiML?>^X=*I*Ry$ZF7}H$Xn)_snzqAH%1VyT>EEa8LEj1vz?#s5CQ~aDmTPFl#+6%ox&sHDPow&C>Dw',
    '>rmmE=F0(bHG0(~Y$jiC2^%ECUwg!a;F`|?l@cGfvck!Sc&xkmv4{hi#c9p6Pk2p|aJvoi7qd0fo^&x&^#2fieob!ul%?1}6FS#wxX2y5fFO%XMo{6PafE@=',
    '@i}M9YV3sE9L>WyA8;a_L~QB=i+Ls-2*;~;`hg4?NDT}3@#SxxKLZ0>L;$uOG@`voC}dL@*n{EJOhXh*G@fAr79*LZrD|k-t8eCOtuKYcQ_5Ijd&6$x)2EBY',
    'i`2jT2?wucA;LDVKZ&fUN1>pN=f)5uQXe)81>M@g5B&Y}D|!WOcCoBi?s`tDJEH|FWC{kGmcA(K@yuyP)G(-?1KP-Bc;GU#O}uYidzahG*DI?gyqZmSYf&w^',
    '_f;0=!^F+0modLaY073ysnz@IJ^jAUI9p<gkfEfyJZ-*&gNDm=ilWvQ2)Ra+l#Iwit*`d3D+MvBB-_=B%oYtp63|sFLZX6nQQ0!G%=$S$<D;RmKrcwBz5<9P',
    '%utqv)@6clC+4s5EkxVKQKTfPBu!#h3N8`+qy|RdnB1PB5t!BXSI4(_uSAtBv(5#ttc|iMQIQ)gTTv^5<R8)bDoj?ik*#lLLu!d*7Q^B*kdc5Sx25MMaThfw',
    'Lu1^X_!iDinO%%?qpY&}N%xL-GM(^L-8J%8Y_(x-P>li^_68|?%TTjhT=E}hz8&Ts8szM%EB~(aQu;gZ@^7KjJv<E9&W$#1!%e%{Jz9*y=4%N_%1%NX|Jh+A',
    '>PM<BA+@;EhdAuRgQ+3q2v=*QUY=f&VdD>RdlBH8LcB)PYst#d$l~2RU*IP)#u!t=Lk{stsF)d`A!_Z3->`yCnFHRms<PaKd&i)_Ig^8QhZ3qn#=UsRjMrSc',
    '?t>v|Not;<^kA65yEZl`e_d)frdbWdm20ip&!}$J%h`w5#?XnuC<JZ)qPE_ON75(@j*_|0meXdwCCBlTYNte961HMOsz`<D`fHr|jt`lhN{Zx77YXm}78a+f',
    'HpDH-B|R^Frj5}2?ySX1VYgj^wQrbaXkVqwp00HSIhKr<#t8ctujLndQ2taXS1}n%E~>y{bl=UZI_B4j+Uj!`vqM69YlCEr!$P4dq1`OVjM$riy2q&lLFM#b',
    'hWh2<(uKkssQ*0@aacjOFf~)Cmny;3DL3R_99xDT1H_C=qoV$3#t4BbYNrK?U7VZWUD9_#w|ME5q&J+8o}?y!xt<m%wf6CMdg+cJT4dQ)d03++s%d90JTEP5',
    'A6*8?=H<eo8u|LwXBD`wtN;9I)%_wnQ2?5c-^@DCTT@i2^CR$Qh%?qOUdc><;M~y?Fs0^&`aUSpCoA$Nq>E6+kz(J4LN~?IvFY(4QcsOM_$|6m;=um%*!g{d',
    'WEE7`1!mESBT@h6TLrEaqvB{cAs+^##NEYJsm>kta-Di1CxZ=e(x(H-nT)^K;$VwlY?ztyWFv~LO}&=a^N|MfI+C^Ss@-@Wd^){mkwjWxwXb;92j{-_p=z>m',
    'xZuPtht#VvHHOm2K5CArU-eusw5s<>4#u%NoNMmlhjBgzxBW1rM>d5FgKE<}c%iFEn(MAEt#aIeGiqbrAO1W?o{1_AVnUeJS9OM2_$?tpe`}{~<C(sWiZv(`',
    '$<J)?bv|>^6@z8aq@mD|*L0V8!<laH`m2cOx|pEgu*LA0xyQ^R&die0J?7?%KEWK=>ulwOh8~Uqi2^ceF;o{R`iLF8E=s}ePcl*#zLc=9_VdKWSSf^E-jqCL',
    'gOf-q#s_eCs|R>C#1ashAs;u_Urp=}UrqJMfsBK;S&?63kJD0<(|+%<=C1~!MtY$+Pt$?O=Cvi356qB!7r|s|s`&_{aU-qCO=D3#FyFRw2tU9iXc`AxDU&M1',
    'GEMPuTcIP`J+cM*+qUN%N11AcD>ja{kexaM(C-Brko;Y-=A%{R0#nv0Cj!{yx`|(=9~*|}D{A@tv3oXkB%u(wshb<TlbDhtyoDKoI-QbCZ)uI1%?)u58?y$U',
    'y}yfUT%y$0dAy$_#7OF0Eo~ZH%x=TaB8NQJ&OhSW<3KDsp=4RkIfU*t4;PYi?Zxf)hH(SfPW`V{AObgM^>wzdf{749xDFc96F>_Wdfqs5Ft%x<NQPg_FJA|e',
    'FEGMVB6gjmGmcp-wWL*OiH%6M17}4YWM-K|-NI-FLiFq8?B|k|G9G5nh6!W@s2t~FR@N0hEw{PDYouG&ne??KVZt34HPy#Oob<5OBZ54cQ={ZeHjBR(UPGF)',
    'Uy+nEBOIKBqpY@5`#S7Oxwg|`d@1|FzQGj#^OL$!M^^8j4FDAI@A}uOi<z^#m5G@PlYxPiy_Kth0i&ZA7~p?;JXg6p1E2taDKr28>%V*K+-zN~T+ED|O)USh',
    ')oEHekaggE)f)_UQ*$q;Nk)eh)@d^|;@KjX<QN<I!~lXx71>fpOvU1*<0)2e1LlWK5D9kegJ2suMEhPoFaD7a1;V<*Of;2zyPMT$n^M~x4^8OgD%yGkOj2~F',
    'Zi~zWhZZ5NIlNLf^xH_;3B=+KV9``VLj$a-F10;0D`Y0jTA#~ZhjYG6yFs|pYt^@L$@)^bIoe7}^l&u+>4)FPu>z=6-Lx`2m?GGNCf#(z^@RpSX~69ZhzU~m',
    'j`ePE0QDQD$d7%?g(=#Vu`O%n&VIjFM}_iZFQMC_moCgSKZ9z4JY?&SZBz%X`gYfih%TQ!;WM-Euj|iwkP(ox6Tty|;ZUC=kfF9o@{ZZhdEIKl3Bm>h)xvw$',
    '&hOJdRFQcLD7JLu1gN}Az6`M^Tm7oq{7oPG1y1c8Uo;v^%{%WFH@14O7Ja8)c4|UxGHD>W3~B^{2o}71?5Qr?Y=Sju)LjAfHOfuF<spNG`*h7<b}5>D9p@u8',
    'WnFb`<ShhRB+2fP6!>Q4`jpvo{zmKHI0oN#Ut>w6uNJk46Iyfd235^cOYCfFG`7j8O{5eVlZ+G&le7HJJFGblozjFhVz-Hpnm>kAg$V;P-iHzR_OWMJu_UAw',
    'b{&xjl}WaAcY2@(psWSV{0%7%8AUou2~{d~C|;rT9{N~-Kjqv}I@Rhqkj{GZMC$yU*&g2y_p^PMtBI~1pd*lvojCIg6r<g}jLWDoCz8PfM3pNU&{(y{F7gwt',
    '-{|O<N>f7Q6)*r&=7uK>R4Ul>6iG#)lfmTI)+MoN^tzCObKVtPt{vNEsl8TWcdxQyc@;`5J(K(XN+jJ@u8@1Dz0JpawY6_hb!q;i7{W)2d8l-@IIs|hlNy~Q',
    'QG-giiAo}qG-Zp}i$@hs$CW~wo$FCMB;^*YAF|TB6|Tl!2DawH$!{4=S^VUZ@zCZptMQlMUWQri=2Tadn-PJVe0x3Bw-DWTpIP2%irOC@t!}(Iz7Okn_~#wr',
    'IgU812^@16#hL}#NPjj#*MD|w9{=W3fK5Icqf-dk^^B|ME)T0GQxC@Ke8~qNa`*`3q7u;GT5DBoc0FZG)8D`8b^Uo>lGvYBdP%ql%ZQB$M-rw-k2*Z9HqTpL',
    '-^;M=gD%P37~?zK`kRi;jlLV+@l5Odl~~&R;phPY*>NYk`)6ft2`@O+0_1`Ieb`HpnGF-xP;6a9s8)@ff`l08oZlQXFHf^(fgOo+4)~7ktewa&9=Z7ggN$;+',
    'baCmOqb7I)CL>=%J^`l4qe+X}>P~u8h2N<NjPa`eavBDxed%=`GQ*r!O~@Qg#2!Osa;+6uwJwuU89*-VSFQ2OwnJ)6xOL8fQEc!4dhS3A9X7WS#?>vMK{Mtk',
    '&s`V4mD>~8h4d06g`<UJKLc2<`OxJN+UcotgQX+i?%PdAbw|7M`A0U?<M&^<V!G-P(nsUkTOJ)HH_dp-y?3Gq=fKP*ELH2HXqywt2@}akHJ^j(lsberFz;ng',
    'ex4LM`H-wcy0nGA1Lf&gQBlbZN;co7%us^9LtJrV{3Ln#i?L;KODaW`F0+yEw|8ig<mh!MOAu&HVI1{Dh-n38mX^}!Eyv%nUiCL-n}=3I?!b-s?ga8{-rOwZ',
    '*_z}c^YVIbrm>@@zd0{>#?JWYeH@56O8hY_s0u%1lWIs?6>g*#&PqRF8-U(~AlI9Y0EE9)i?Qu`#-ZnQ=3waJybw=JW=hzMlqE_5VuYg>k#|6%9L6VS_9h-y',
    '3pr->-cCE9$*`19#AfsZDSY4;dU%cXHiqoFnWz>F8i+9|>HGV#Q>fn%_KD5BI0tbb*{YVJW*@{-*kIW<Chp%Sy7KXdCR_&5JlzHb#PLNORa@GMlC)>2Fh_wL',
    'Up~QlFUUm8Y>2&r&UTy@Qat*I7k>w0UD9^$uAcszi^;^ogJN70&=C<Uj3zw9IbzeD@bgSX(Z;%!TJnM$!ED?8s@-n?l?rV~n$D0JuMOqJffHORPzXHzVScWw',
    'p+L(_u*<RpVE`&Tvhn4b?r*PT0#-6+N9C3Li)zMc(KTv}Y;A0ZigA^^ev!@B?g@97+a(HuwQl#(cVz-3mi}V-g-I9WgD_oz2>MP^k14wv@^DaYh^OJ=bB}J_',
    ')uO8azVdM^uquP;?2@^%G-s_vof@_d&z?Tob(l(gxhp^BAK7~OyJRJ@JW#fNw;0&5Ef|OKX=WlVixUvG{rlm)x#4>l)=^%mYW#Pvg!4Wmi2YS?=vz5SB5V1=',
    'Jv;V6IR{1J7qh(<zDLfo-z<Mm{(Q`Cn>PuVEf5vs2^y$i=^I$i!H#@WoEtrc!S!fNy%9;jY{P{AO!T#;n(R^NnDdf-t>^t9FpVAZ(O-k0nldBJ)xFG=r##Ly',
    'qXce#|6F=Sjw*rOApbSbHoVKkGOUjw@a{#C=K+tG(!18N)xJRKv23y4S4tl6Y?`gz0*wOz{gf+?dQrx{bnnRY9TM`IHl0iPOzgFoNP*--_$xrG(Q_&s{<iO-',
    'C<_9L4)*_#qy2|Ug8=_Ioc7;6{}&znm#2*I|7L~%-Qj<;!hdzxB>aELK~Was-);!@PxSn=#!>!j_Ahs+2_*',
)

def main():
    root = Path(tempfile.mkdtemp(prefix='script_hunt_random_')).resolve()
    data = zlib.decompress(base64.b85decode(''.join(PAYLOAD)))
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.namelist():
            path = (root / member).resolve()
            if not path.is_relative_to(root):
                raise ValueError('Unsafe archive member')
        archive.extractall(root)
    sys.path.insert(0, str(root))
    runpy.run_path(str(root / 'bot.py'), run_name='__main__')

if __name__ == '__main__':
    main()
