import random, sys
mode=sys.argv[1]; season=sys.argv[2]
random.seed(4)

SE={
 "kis":dict(name="KIŞ",sub="ilk kar",dawn="linear-gradient(180deg,#C9CFE6 0%,#E9E6F0 55%,#F4F2F6 100%)",day="linear-gradient(180deg,#BFD6EC 0%,#E6EEF5 60%,#F5F7FA 100%)",dusk="linear-gradient(180deg,#5D5A93 0%,#C98AA8 55%,#F2C6B8 100%)",night="linear-gradient(180deg,#0C1233 0%,#1E2660 55%,#3D3C78 100%)",
   caps=["İlk kar düştüğünde","şehir sessizleşir,","pencereler ısınır."],cloud=("#FFFFFF","#E9C9D6","#3A3F78"),flash="0",sun=""),
 "yagmur":dict(name="YAĞMUR",sub="ıslak bir salı",dawn="linear-gradient(180deg,#8E9AAE 0%,#B8C1CE 55%,#CDD3DA 100%)",day="linear-gradient(180deg,#93A3B5 0%,#C3CCD6 60%,#D6DCE2 100%)",dusk="linear-gradient(180deg,#3E4664 0%,#7C7690 55%,#A99BA6 100%)",night="linear-gradient(180deg,#0A0F24 0%,#18203F 55%,#2C3150 100%)",
   caps=["Yağmur yağarken","herkes bir yere koşar,","biri pencerede bekler."],cloud=("#7D8799","#5D6278","#20253F"),flash=".38",sun="display:none"),
 "bahar":dict(name="BAHAR",sub="erik çiçekleri",dawn="linear-gradient(180deg,#F9C9D4 0%,#FCE6E4 55%,#F8F0E8 100%)",day="linear-gradient(180deg,#A6DDF0 0%,#E4F4F1 60%,#F7F4EA 100%)",dusk="linear-gradient(180deg,#7A5AA0 0%,#F08FA0 55%,#FBC99A 100%)",night="linear-gradient(180deg,#0E1236 0%,#252A66 55%,#4A3C7C 100%)",
   caps=["Bahar gelince","sokaklar çiçek açar,","kalpler de."],cloud=("#FFFFFF","#FFC7C7","#3A3F78"),flash="0",sun=""),
 "ramazan":dict(name="RAMAZAN",sub="iftar vakti",dawn="linear-gradient(180deg,#F4B98C 0%,#F9DDBE 55%,#F6EADC 100%)",day="linear-gradient(180deg,#E7906F 0%,#F6C08F 55%,#F8E2C4 100%)",dusk="linear-gradient(180deg,#3E2F6B 0%,#B65F7C 55%,#F09A6E 100%)",night="linear-gradient(180deg,#0B1A33 0%,#173A5A 55%,#2B4F6E 100%)",
   caps=["Güneş batarken","sofralar kurulur,","şehir aynı anda oruç açar."],cloud=("#FFE3CC","#F0A08A","#2A3E63"),flash="0",sun="",clk=["17:20","18:05","18:52","20:30"],eve=True),
 "yaz":dict(name="YAZ GECESİ",sub="pencereler açık",dawn="linear-gradient(180deg,#F7B48A 0%,#FBD9B5 55%,#F8EBD8 100%)",day="linear-gradient(180deg,#F08A6A 0%,#F7B98C 55%,#F9DDB8 100%)",dusk="linear-gradient(180deg,#2E2A6E 0%,#9B4F8C 55%,#F2836A 100%)",night="linear-gradient(180deg,#070B26 0%,#141F52 55%,#2C2C6A 100%)",
   caps=["Yaz geceleri","şehir uyumaz,","pencereler açık kalır."],cloud=("#FFE3CC","#F59A8A","#262A60"),flash="0",sun="",clk=["19:40","20:35","21:30","23:10"],eve=True),
 "sonbahar":dict(name="SONBAHAR",sub="yaprak dökümü",dawn="linear-gradient(180deg,#F3B88E 0%,#F9DCC0 55%,#F6EADC 100%)",day="linear-gradient(180deg,#B9D6E2 0%,#EFE9DA 60%,#F4EEE2 100%)",dusk="linear-gradient(180deg,#5A3F6E 0%,#E07A4F 55%,#F6B86A 100%)",night="linear-gradient(180deg,#120F2A 0%,#2A2250 55%,#4A3460 100%)",
   caps=["Yapraklar düşerken","şehir altına bürünür,","akşam erken çöker."],cloud=("#FFF6EC","#FFB98A","#3A3360"),flash="0",sun=""),
}[season]
CLK=SE.get('clk',['06:40','12:10','18:25','21:15'])
tpl=open('iso3_tpl.html').read()

def camS(s,cx,cy,dy=0,dx=0): return f"translate({cx*(1-s)+dx:.1f}px,{cy*(1-s)+dy:.1f}px) scale({s})"
if mode=="v":
    W,H=540,960; cx,cy=270,455
    c0=camS(.78,cx,cy,dy=150); c1=camS(1,cx,cy); c2=camS(1.07,cx,cy,dy=-6,dx=-6)
    sun=(130,220); moon=(410,170); birdx=520
    ui='''  <div class="hud hudc" style="position: absolute; top: 34px; left: 36px; right: 36px; display: flex; justify-content: space-between; align-items: center; font: 600 11px/1 Unbounded, sans-serif; letter-spacing: .2em">
    <span>İZOMETRİK · v3</span>
    <span style="display: flex; align-items: center; gap: 10px"><span style="position: relative; width: 74px; height: 3px; background: rgba(128,110,140,.3); border-radius: 2px; overflow: hidden"><span class="bar" style="position: absolute; inset: 0; background: currentColor"></span></span><span class="clk" style="position: relative; display: inline-block; width: 52px; height: 12px"><span class="k1">'''+CLK[0]+'''</span><span class="k2">'''+CLK[1]+'''</span><span class="k3">'''+CLK[2]+'''</span><span class="k4">'''+CLK[3]+'''</span></span></span>
  </div>
  <div class="t1" style="position: absolute; top: 96px; left: 0; right: 0; text-align: center">
    <div style="font: 600 13px/1 Unbounded, sans-serif; letter-spacing: .4em; color: rgba(60,40,70,.7); margin-bottom: 10px">MAHALLE</div><div style="font: 800 50px/1 Unbounded, sans-serif; letter-spacing: -.01em; color: #3C2846">'''+SE['name']+'''</div>
    <div style="margin-top: 8px; font: italic 400 24px/1 'Instrument Serif', serif; color: rgba(60,40,70,.75)">'''+SE['sub']+'''</div>
  </div>
  <div class="end" style="text-shadow: 0 2px 10px rgba(8,8,30,.9), 0 0 24px rgba(8,8,30,.7); position: absolute; top: 690px; left: 0; right: 0; text-align: center">
    <div style="font: 600 20px/1 Unbounded, sans-serif; letter-spacing: .14em; color: {{accent}}">KAT 14 · DAİRE 3</div>
    <div style="margin-top: 10px; font: italic 400 22px/1 'Instrument Serif', serif; color: rgba(255,240,220,.8)">her pencerede bir hikâye</div>
  </div>
  <div style="position: absolute; left: 30px; right: 30px; top: 792px; height: 84px">
    <div class="ph ph1"><span class="cap" style="font: 700 29px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][0]+'''</span><span class="lit">'''+SE['caps'][0]+'''</span></span></div>
    <div class="ph ph2"><span class="cap" style="font: 700 29px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][1]+'''</span><span class="lit">'''+SE['caps'][1]+'''</span></span></div>
    <div class="ph ph3"><span class="cap" style="font: 700 29px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][2]+'''</span><span class="lit" style="color: {{accent}}">'''+SE['caps'][2]+'''</span></span></div>
  </div>'''
    title="İzometrik Şehir v2 — Dikey"
else:
    W,H=960,540; cx,cy=480,312
    c0=camS(.82,cx,cy,dy=90); c1=camS(1,cx,cy); c2=camS(1.06,cx,cy,dy=-4,dx=-8)
    sun=(170,130); moon=(790,100); birdx=900
    ui='''  <div class="hud hudc" style="position: absolute; top: 28px; left: 40px; right: 40px; display: flex; justify-content: space-between; align-items: center; font: 600 11px/1 Unbounded, sans-serif; letter-spacing: .2em">
    <span>İZOMETRİK · v3 · 16:9</span>
    <span style="display: flex; align-items: center; gap: 10px"><span style="position: relative; width: 90px; height: 3px; background: rgba(128,110,140,.3); border-radius: 2px; overflow: hidden"><span class="bar" style="position: absolute; inset: 0; background: currentColor"></span></span><span class="clk" style="position: relative; display: inline-block; width: 52px; height: 12px"><span class="k1">'''+CLK[0]+'''</span><span class="k2">'''+CLK[1]+'''</span><span class="k3">'''+CLK[2]+'''</span><span class="k4">'''+CLK[3]+'''</span></span></span>
  </div>
  <div class="t1" style="position: absolute; top: 74px; left: 48px">
    <div style="font: 600 13px/1 Unbounded, sans-serif; letter-spacing: .4em; color: rgba(60,40,70,.7); margin-bottom: 10px">MAHALLE</div><div style="font: 800 46px/1 Unbounded, sans-serif; letter-spacing: -.01em; color: #3C2846">'''+SE['name']+'''</div>
    <div style="margin-top: 8px; font: italic 400 22px/1 'Instrument Serif', serif; color: rgba(60,40,70,.75)">'''+SE['sub']+'''</div>
  </div>
  <div class="end" style="text-shadow: 0 2px 10px rgba(8,8,30,.9), 0 0 24px rgba(8,8,30,.7); position: absolute; top: 74px; right: 48px; text-align: right">
    <div style="font: 600 18px/1 Unbounded, sans-serif; letter-spacing: .14em; color: {{accent}}">KAT 14 · DAİRE 3</div>
    <div style="margin-top: 10px; font: italic 400 20px/1 'Instrument Serif', serif; color: rgba(255,240,220,.8)">her pencerede bir hikâye</div>
  </div>
  <div style="position: absolute; left: 40px; right: 40px; top: 452px; height: 56px">
    <div class="ph ph1"><span class="cap" style="font: 700 25px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][0]+'''</span><span class="lit">'''+SE['caps'][0]+'''</span></span></div>
    <div class="ph ph2"><span class="cap" style="font: 700 25px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][1]+'''</span><span class="lit">'''+SE['caps'][1]+'''</span></span></div>
    <div class="ph ph3"><span class="cap" style="font: 700 25px/1.25 Manrope, sans-serif"><span class="dim">'''+SE['caps'][2]+'''</span><span class="lit" style="color: {{accent}}">'''+SE['caps'][2]+'''</span></span></div>
  </div>'''
    title="İzometrik Şehir v2 — Yatay"
stars="".join(f'<circle class="tw" cx="{random.uniform(10,W-10):.0f}" cy="{random.uniform(10,H*0.38):.0f}" r="{random.choice([.7,.9,1.1,1.4])}" style="animation-delay:{-random.random()*2.4:.2f}s"></circle>' for _ in range(40))
clouds=""
for (x,y,s) in ([(70,300,1),(380,250,.8),(250,140,.6)] if mode=="v" else [(120,200,1),(640,170,.9),(420,90,.6)]):
    clouds+=f'<g class="cloudc" transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="0" rx="44" ry="14"></ellipse><ellipse cx="-14" cy="-10" rx="20" ry="14"></ellipse><ellipse cx="12" cy="-14" rx="24" ry="17"></ellipse></g>'
birds="".join(f'<path class="flap" style="animation-delay:{-random.random():.2f}s" d="M {x} {y} q 5 -5 10 0 q 5 -5 10 0"></path>' for (x,y) in [(60,330),(82,318),(96,338),(44,346),(112,326)])
title=title.replace("v2","v3 · "+SE["name"].capitalize()); c1_,c2_,c3_=SE["cloud"]
sunkf=("@keyframes sun{0%{transform:translate(-20px,40px)}30%{transform:translate(70px,230px);opacity:1}34%,100%{transform:translate(80px,260px);opacity:0}}" if SE.get("eve") else "@keyframes sun{0%{transform:translate(-60px,140px)}20%{transform:translate(0,-10px)}40%,100%{transform:translate(120px,260px)}}")
skyx=""
if season=="ramazan":
    sx_,sy_=moon[0]+44,moon[1]-20
    skyx=f'<g class="moon"><path d="M {sx_} {sy_-7} l 2 5 l 5.5 .3 l -4.3 3.4 l 1.5 5.4 l -4.7 -3.1 l -4.7 3.1 l 1.5 -5.4 l -4.3 -3.4 l 5.5 -.3 Z" fill="#FFE7A8"></path></g>'
hgl={"ramazan":"#F2B36A","yaz":"#F08A9A"}.get(season,"#F2A36A")
rep={"%SUNKF%":sunkf,"%SKYEXTRA%":skyx,"%HGLOW%":hgl,"%HX%":str(W//2),"%HY%":str(int(H*(0.6 if mode=="v" else 0.75))),"%HRX%":str(int(W*0.8)),"%HRY%":str(int(H*(0.22 if mode=="v" else 0.35))),"%WG%":str(W+60),"%HG%":str(H+60),"%DAWN%":SE["dawn"],"%DAY%":SE["day"],"%DUSK%":SE["dusk"],"%NIGHT%":SE["night"],"%FLASH%":SE["flash"],"%SUNDISP%":SE["sun"],"%WXSTYLE%":"","%RY%":str(H+60),"%RX%":str(int((H+60)*.25)),"%CLOUDKF%":"@keyframes cloudc{0%%,26%%{fill:%s;opacity:.85}36%%{fill:%s;opacity:.8}48%%,100%%{fill:%s;opacity:.55}}"%(c1_,c2_,c3_),"%TITLE%":title,"%UI%":ui,"%CAM0%":c0,"%CAM1%":c1,"%CAM2%":c2,"%SUNX%":str(sun[0]),"%SUNY%":str(sun[1]),"%MOONX%":str(moon[0]),"%MOONY%":str(moon[1]),"%MOONX2%":str(moon[0]+10),"%MOONY2%":str(moon[1]-7),"%STARS%":stars,"%CLOUDS%":clouds,"%BIRDS%":birds,"%BIRDX%":str(birdx)}
for k,v in rep.items(): tpl=tpl.replace(k,v)
open(f'iso3_{mode}_{season}.html','w').write(tpl)
