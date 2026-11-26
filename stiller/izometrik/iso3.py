# İzometrik şehir v3 — mevsim/hava + sevimli karakterler
import random, sys, math
mode, season = sys.argv[1], sys.argv[2]   # v|h , kis|yagmur|bahar|sonbahar
random.seed(23)
if mode=="v": W,H,SX,CX,CY=540,960,34,270,318
else:         W,H,SX,CX,CY=960,540,40,480,150
SY=SX*0.5774; K=SX/34.0; N=7
def P(i,j): return (CX+(i-j)*SX, CY+(i+j)*SY)
def f(x): return f"{x:.1f}"
def pts(L): return " ".join(f"{f(x)},{f(y)}" for x,y in L)
def up(p,h): return (p[0],p[1]-h)
def lerp(a,b,u): return (a[0]+u*(b[0]-a[0]), a[1]+u*(b[1]-a[1]))
def hull(ps):
    ps=sorted(set((round(x,2),round(y,2)) for x,y in ps))
    cr=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];hi=[]
    for p in ps:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(ps):
        while len(hi)>=2 and cr(hi[-2],hi[-1],p)<=0: hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]
S=season
SNOW = S=="kis"; RAIN = S=="yagmur"
CFG={
 "kis":     dict(ground="#EEF2F8",edge="#B9C3D6",road="#646A7E",grass="#F4F7FB",shadow="#5A6A9A",tops="#FFFFFF",roof=["#FFFFFF"],trees="pine"),
 "yagmur":  dict(ground="#C9CFD6",edge="#8F98A8",road="#4E5566",grass="#8FB38A",shadow="#3B4660",tops=None,roof=["#9C5A4E","#5F5A7A","#3F6672"],trees="round",tree=("#4F8A55","#6FA56E")),
 "bahar":   dict(ground="#F2E8DC",edge="#C8B4BE",road="#6A6378",grass="#BFE3A0",shadow="#5B3B6E",tops=None,roof=["#D9707F","#8A6FB5","#5E9AA0"],trees="round",tree=("#F4A9C0","#FBD1DE")),
 "sonbahar":dict(ground="#EEDCC6",edge="#C3A68A",road="#6A5F6E",grass="#D8C27A",shadow="#5B3B30",tops=None,roof=["#B5523B","#7B4F6B","#3F6672"],trees="round",tree=("#E07A2F","#F2B544")),
}[S]
pals=[("#FFF4E8","#F4BBA6","#D98A79"),("#F0FFF8","#ABDDC9","#71B49E"),("#F7F2FF","#C9BBF0","#9280CC"),("#FFF9E6","#F4D68C","#D0A752"),("#F3F8FF","#B8CDEB","#7F9CC8"),("#FFF0F3","#F2B8C6","#CF8299")]
if RAIN: pals=[("#E9ECEF","#B9C1CC","#8C96A6"),("#E6EEF0","#9DB9BD","#6F8F95"),("#ECE8EF","#B8AFC4","#8A7F9C"),("#EFE9E1","#C9B8A2","#9C8A75"),("#E3E9F2","#A8B8CF","#7A8CA8")]
if S=="sonbahar": pals=[("#FFF1E2","#F0B48E","#CF8660"),("#FFF6E0","#EAC27A","#C29445"),("#F7EFF2","#D3A9B4","#A57885"),("#F1F3EA","#BFC79F","#8F9970"),("#FBEDE6","#E4A08A","#B8705C")]
ROAD_I=3; ROAD_J=3; HERO=(5,4)
types={}
for i in range(N):
    for j in range(N):
        if i==ROAD_I or j==ROAD_J: types[(i,j)]="road"; continue
        d=math.hypot(i-3,j-3)
        if (i,j) in [(1,4),(2,4)]: types[(i,j)]="plaza"
        elif (i,j) in [(6,4),(1,5),(0,1),(5,6),(0,4)]: types[(i,j)]="park"
        elif (i,j) in [(2,5),(0,5)]: types[(i,j)]="house"
        elif (i,j)==HERO: types[(i,j)]="hero"
        elif d>3.6 or (i,j) in [(6,5),(6,6)]: types[(i,j)]="house"
        elif random.random()<0.3: types[(i,j)]="shop"
        else: types[(i,j)]="tower"
ground=[]; shadows=[]; items=[]; wins=[]; kf=[]; cars=[]; pools=[]; refl=[]; walkers_back=[]; walkers_front=[]
nb=[0]
def rise(delay):
    nb[0]+=1; n=nb[0]
    kf.append(f".b{n}{{animation-name:r{n}}}@keyframes r{n}{{0%,{delay*10:.1f}%{{transform:scaleY(0)}}{delay*10+3.5:.1f}%{{transform:scaleY(1.07)}}{delay*10+5:.1f}%{{transform:scaleY(.98)}}{delay*10+6:.1f}%,100%{{transform:scaleY(1)}}}}")
    return f"b b{n}"
G=[P(0,0),P(N,0),P(N,N),P(0,N)]
ground.append(f'<polygon points="{pts([(x,y+10*K) for x,y in G])}" fill="{CFG["edge"]}"></polygon>')
ground.append(f'<polygon points="{pts(G)}" fill="{CFG["ground"]}"></polygon>')
rc=CFG["road"]
r1=[P(ROAD_I+.08,0),P(ROAD_I+.92,0),P(ROAD_I+.92,N),P(ROAD_I+.08,N)]
r2=[P(0,ROAD_J+.08),P(N,ROAD_J+.08),P(N,ROAD_J+.92),P(0,ROAD_J+.92)]
ground.append(f'<polygon points="{pts(r1)}" fill="{rc}"></polygon><polygon points="{pts(r2)}" fill="{rc}"></polygon>')
if SNOW:
    for (a,b) in [((ROAD_I+.08,0),(ROAD_I+.08,N)),((ROAD_I+.92,0),(ROAD_I+.92,N)),((0,ROAD_J+.08),(N,ROAD_J+.08)),((0,ROAD_J+.92),(N,ROAD_J+.92))]:
        x0,y0=P(*a); x1,y1=P(*b)
        ground.append(f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}" stroke="#FFFFFF" stroke-width="{4*K:.1f}" stroke-linecap="round" stroke-opacity=".9"></line>')
for t in range(N):
    if t!=ROAD_J:
        a=P(ROAD_I+.5,t+.2); b=P(ROAD_I+.5,t+.6)
        ground.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="#F6EEDF" stroke-opacity=".8" stroke-width="{1.6*K:.1f}" stroke-linecap="round"></line>')
    if t!=ROAD_I:
        a=P(t+.2,ROAD_J+.5); b=P(t+.6,ROAD_J+.5)
        ground.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="#F6EEDF" stroke-opacity=".8" stroke-width="{1.6*K:.1f}" stroke-linecap="round"></line>')
for s_ in range(5):
    u=.18+s_*.15
    q=[P(ROAD_I+u,ROAD_J-.02),P(ROAD_I+u+.08,ROAD_J-.02),P(ROAD_I+u+.08,ROAD_J-.3),P(ROAD_I+u,ROAD_J-.3)]
    ground.append(f'<polygon points="{pts(q)}" fill="#F6EEDF" fill-opacity=".85"></polygon>')
    q=[P(ROAD_I+1.02,ROAD_J+u),P(ROAD_I+1.3,ROAD_J+u),P(ROAD_I+1.3,ROAD_J+u+.08),P(ROAD_I+1.02,ROAD_J+u+.08)]
    ground.append(f'<polygon points="{pts(q)}" fill="#F6EEDF" fill-opacity=".85"></polygon>')
if RAIN:
    random.seed(77)
    for _ in range(14):
        i0=random.uniform(.3,6.7); j0=random.choice([random.uniform(ROAD_J+.15,ROAD_J+.85), random.uniform(.3,6.7)])
        x,y=P(i0,j0); rx=random.uniform(7,14)*K
        ground.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(rx*.45)}" fill="#9FB4C8" fill-opacity=".55"></ellipse><ellipse class="ripple" cx="{f(x)}" cy="{f(y)}" rx="{f(rx*.5)}" ry="{f(rx*.22)}" fill="none" stroke="#E3ECF5" stroke-width=".8" style="animation-delay:{-random.random()*1.2:.2f}s"></ellipse>')
    random.seed(23)
ground.append(f'<polygon class="ns" points="{pts(G)}"></polygon>')

def box(i0,j0,i1,j1,h,pal,z=0,snowcap=False):
    A,B,C,D=[up(p,z) for p in (P(i0,j0),P(i1,j0),P(i1,j1),P(i0,j1))]
    top,l,r=pal
    if CFG["tops"]: top=CFG["tops"]
    s=f'<polygon points="{pts([D,C,up(C,h),up(D,h)])}" fill="{l}"></polygon>'
    if z==0: s+=f'<polygon points="{pts([D,C,up(C,h),up(D,h)])}" fill="url(#ao)"></polygon>'
    s+=f'<polygon points="{pts([C,B,up(B,h),up(C,h)])}" fill="{r}"></polygon>'
    if z==0: s+=f'<polygon points="{pts([C,B,up(B,h),up(C,h)])}" fill="url(#ao)"></polygon>'
    s+=f'<polygon points="{pts([up(A,h),up(B,h),up(C,h),up(D,h)])}" fill="{top}"></polygon>'
    if SNOW and snowcap:
        # snow drip on edges
        s+=f'<polyline points="{pts([up(D,h-1.5*K),up(lerp(D,C,.3),h-3.5*K),up(lerp(D,C,.55),h-2*K),up(C,h-3*K),up(lerp(C,B,.4),h-1.5*K),up(lerp(C,B,.7),h-3.2*K),up(B,h-1.5*K)])}" fill="none" stroke="#FFFFFF" stroke-width="{2.6*K:.1f}" stroke-linejoin="round" stroke-linecap="round"></polyline>'
    s+=f'<polyline points="{pts([up(D,h),up(C,h),up(B,h)])}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".8"></polyline>'
    s+=f'<polygon class="ns" points="{pts([D,C,B,up(B,h),up(A,h),up(D,h)])}"></polygon>'
    return s,(A,B,C,D)
def shadow(i0,j0,i1,j1,h):
    fp=[P(i0,j0),P(i1,j0),P(i1,j1),P(i0,j1)]
    sh=[(x+0.8*h,y-0.42*h) for x,y in fp]
    shadows.append(f'<polygon points="{pts(hull(fp+sh))}"></polygon>')
def windows(D,C,B,h,z,rows_from=10,step=16,cols=(0.16,0.58),wcol=0.26):
    out=[];lit=[]
    for (p0,p1) in ((D,C),(C,B)):
        nr=int((h-rows_from-4)//(step*K))
        for rr in range(nr):
            v0=z+rows_from*K+rr*step*K; v1=v0+8*K
            for u0 in cols:
                u1=u0+wcol
                q=lambda u,v:(p0[0]+u*(p1[0]-p0[0]), p0[1]+u*(p1[1]-p0[1])-v)
                poly=[q(u0,v0),q(u1,v0),q(u1,v1),q(u0,v1)]
                out.append(f'<polygon class="wd" points="{pts(poly)}"></polygon>')
                if SNOW and random.random()<.5:
                    out.append(f'<line x1="{f(poly[0][0])}" y1="{f(poly[0][1]+.6)}" x2="{f(poly[1][0])}" y2="{f(poly[1][1]+.6)}" stroke="#fff" stroke-width="{1.4*K:.1f}" stroke-linecap="round"></line>')
                if random.random()<0.12: continue
                t0=3.6+random.random()*2.6
                dur=random.choice([4.5,5.2,6,6,6])
                cls="w tv" if random.random()<.08 else "w"
                col=random.choice(["#FFD27A","#FFC56B","#FFE2A0","#FFB45E"])
                lit.append(f'<polygon class="{cls} wl{int(dur*10)}" fill="{col}" points="{pts(poly)}" style="animation-delay:{t0-10:.2f}s"></polygon>')
    return "".join(out)+"".join(lit)
def tree(cx,cy,s=1.0):
    s*=K; dl=-random.random()*3
    base=f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(9*s)}" ry="{f(4.5*s)}" fill="#2E3A4A" fill-opacity=".2"></ellipse>'
    if CFG["trees"]=="pine":
        g=(f'<rect x="{f(cx-1.4*s)}" y="{f(cy-8*s)}" width="{f(2.8*s)}" height="{f(8*s)}" fill="#7A5A4A"></rect>'
           f'<polygon points="{f(cx-11*s)},{f(cy-7*s)} {f(cx)},{f(cy-24*s)} {f(cx+11*s)},{f(cy-7*s)}" fill="#3E7A63"></polygon>'
           f'<polygon points="{f(cx-8.5*s)},{f(cy-17*s)} {f(cx)},{f(cy-33*s)} {f(cx+8.5*s)},{f(cy-17*s)}" fill="#4C8E72"></polygon>'
           f'<path d="M {f(cx-8.5*s)} {f(cy-17*s)} Q {f(cx-3*s)} {f(cy-20*s)} {f(cx)} {f(cy-18*s)} Q {f(cx+4*s)} {f(cy-21*s)} {f(cx+8.5*s)} {f(cy-17*s)} L {f(cx)} {f(cy-33*s)} Z" fill="#FFFFFF"></path>'
           f'<path d="M {f(cx-11*s)} {f(cy-7*s)} Q {f(cx-5*s)} {f(cy-10*s)} {f(cx)} {f(cy-8*s)} Q {f(cx+5*s)} {f(cy-11*s)} {f(cx+11*s)} {f(cy-7*s)} L {f(cx+5*s)} {f(cy-14*s)} L {f(cx-5*s)} {f(cy-14*s)} Z" fill="#FFFFFF" fill-opacity=".9"></path>'
           f'<polygon class="ns" points="{f(cx-11*s)},{f(cy)} {f(cx-11*s)},{f(cy-7*s)} {f(cx)},{f(cy-33*s)} {f(cx+11*s)},{f(cy-7*s)} {f(cx+11*s)},{f(cy)}"></polygon>')
    else:
        c1,c2=CFG["tree"]
        if S=="sonbahar": c1,c2=random.choice([("#E07A2F","#F2B544"),("#C9483A","#E9844F"),("#D9A12B","#F4D06A")])
        g=(f'<rect x="{f(cx-1.4*s)}" y="{f(cy-12*s)}" width="{f(2.8*s)}" height="{f(12*s)}" fill="#8A6A55"></rect>'
           f'<circle cx="{f(cx)}" cy="{f(cy-19*s)}" r="{f(10*s)}" fill="{c1}"></circle>'
           f'<circle cx="{f(cx+4*s)}" cy="{f(cy-16*s)}" r="{f(6*s)}" fill="{c1}"></circle>'
           f'<circle cx="{f(cx-3*s)}" cy="{f(cy-22*s)}" r="{f(5.5*s)}" fill="{c2}"></circle>')
        if S=="bahar":
            g+="".join(f'<circle cx="{f(cx+dx*s)}" cy="{f(cy+dy*s)}" r="{f(1.3*s)}" fill="#FFFFFF" fill-opacity=".9"></circle>' for dx,dy in [(-5,-24),(3,-25),(6,-18),(-7,-16),(1,-13)])
        g+=f'<circle class="ns" cx="{f(cx)}" cy="{f(cy-18*s)}" r="{f(11*s)}"></circle>'
        if S=="sonbahar":
            base+="".join(f'<ellipse cx="{f(cx+dx*s)}" cy="{f(cy+dy*s)}" rx="{f(2.2*s)}" ry="{f(1.1*s)}" fill="{random.choice([c1,c2])}"></ellipse>' for dx,dy in [(-7,2),(6,1),(10,-1),(-11,-1),(2,3)])
    return base+f'<g class="tr" style="animation-delay:{dl:.2f}s">{g}</g>'
def snowman(cx,cy,s=1.0):
    s*=K
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(9*s)}" ry="{f(4*s)}" fill="#5A6A9A" fill-opacity=".2"></ellipse>'
            f'<circle cx="{f(cx)}" cy="{f(cy-7*s)}" r="{f(8*s)}" fill="#FFFFFF"></circle><circle cx="{f(cx)}" cy="{f(cy-19*s)}" r="{f(5.8*s)}" fill="#FFFFFF"></circle>'
            f'<circle cx="{f(cx-2*s)}" cy="{f(cy-20*s)}" r="{f(.8*s)}" fill="#2B1B2A"></circle><circle cx="{f(cx+2*s)}" cy="{f(cy-20*s)}" r="{f(.8*s)}" fill="#2B1B2A"></circle>'
            f'<polygon points="{f(cx)},{f(cy-18.5*s)} {f(cx+5*s)},{f(cy-17.6*s)} {f(cx)},{f(cy-17.2*s)}" fill="#F08A3C"></polygon>'
            f'<rect x="{f(cx-5.5*s)}" y="{f(cy-15*s)}" width="{f(11*s)}" height="{f(2.4*s)}" rx="{f(1.2*s)}" fill="#E2574C"></rect>'
            f'<rect x="{f(cx+2*s)}" y="{f(cy-15*s)}" width="{f(2.4*s)}" height="{f(6*s)}" rx="{f(1*s)}" fill="#E2574C"></rect>'
            f'<rect x="{f(cx-4.5*s)}" y="{f(cy-29*s)}" width="{f(9*s)}" height="{f(6*s)}" fill="#2B1B2A"></rect><rect x="{f(cx-6.5*s)}" y="{f(cy-23.5*s)}" width="{f(13*s)}" height="{f(1.6*s)}" fill="#2B1B2A"></rect>'
            f'<circle cx="{f(cx-2.6*s)}" cy="{f(cy-18*s)}" r="{f(1.2*s)}" fill="#F6A6B2" fill-opacity=".8"></circle><circle cx="{f(cx+2.6*s)}" cy="{f(cy-18*s)}" r="{f(1.2*s)}" fill="#F6A6B2" fill-opacity=".8"></circle>'
            f'<line x1="{f(cx-7*s)}" y1="{f(cy-9*s)}" x2="{f(cx-13*s)}" y2="{f(cy-14*s)}" stroke="#7A5A4A" stroke-width="{f(1*s)}"></line><line x1="{f(cx+7*s)}" y1="{f(cy-9*s)}" x2="{f(cx+12*s)}" y2="{f(cy-15*s)}" stroke="#7A5A4A" stroke-width="{f(1*s)}"></line>'
            f'<circle class="ns" cx="{f(cx)}" cy="{f(cy-13*s)}" r="{f(12*s)}"></circle>')
order=sorted([(i,j) for i in range(N) for j in range(N)], key=lambda c:(c[1],c[0]))
heroinfo={}
for (i,j) in order:
    t=types[(i,j)]; key=(j,i)
    dl=0.15+(i+j)*0.1+random.random()*0.12
    if t=="road": continue
    if t=="plaza":
        q=[P(i+.04,j+.04),P(i+.96,j+.04),P(i+.96,j+.96),P(i+.04,j+.96)]
        pav="#FFFFFF" if SNOW else "#E8DCCB"
        s=f'<polygon points="{pts(q)}" fill="{pav}"></polygon>'
        for u_ in (.28,.52,.76):
            a_,b_=P(i+u_,j+.04),P(i+u_,j+.96); s+=f'<line x1="{f(a_[0])}" y1="{f(a_[1])}" x2="{f(b_[0])}" y2="{f(b_[1])}" stroke="#C9B9A6" stroke-opacity=".5" stroke-width=".7"></line>'
            a_,b_=P(i+.04,j+u_),P(i+.96,j+u_); s+=f'<line x1="{f(a_[0])}" y1="{f(a_[1])}" x2="{f(b_[0])}" y2="{f(b_[1])}" stroke="#C9B9A6" stroke-opacity=".5" stroke-width=".7"></line>'
        s+=f'<polygon class="ns" points="{pts(q)}"></polygon>'
        if (i,j)==(2,4):
            cx_,cy_=P(i+.5,j+.5)
            s+=(f'<ellipse cx="{f(cx_)}" cy="{f(cy_)}" rx="{f(16*K)}" ry="{f(8*K)}" fill="#B9A58E"></ellipse><ellipse cx="{f(cx_)}" cy="{f(cy_-3*K)}" rx="{f(16*K)}" ry="{f(8*K)}" fill="#D8C8B4"></ellipse>'
                f'<ellipse cx="{f(cx_)}" cy="{f(cy_-3*K)}" rx="{f(13*K)}" ry="{f(6.2*K)}" fill="{"#E9F1FA" if SNOW else "#7EC4D8"}"></ellipse>'
                f'<rect x="{f(cx_-1.6*K)}" y="{f(cy_-12*K)}" width="{f(3.2*K)}" height="{f(9*K)}" fill="#D8C8B4"></rect>'
                +("" if SNOW else f'<g class="fount"><path d="M {f(cx_)} {f(cy_-12*K)} q {f(-6*K)} {f(-6*K)} {f(-9*K)} {f(6*K)} M {f(cx_)} {f(cy_-12*K)} q {f(6*K)} {f(-6*K)} {f(9*K)} {f(6*K)}" fill="none" stroke="#CFEAF4" stroke-width="{f(1.2*K)}" stroke-linecap="round"></path></g>')
                +f'<ellipse class="ns" cx="{f(cx_)}" cy="{f(cy_-3*K)}" rx="{f(16*K)}" ry="{f(8*K)}"></ellipse>')
        else:
            # bench + flower pots
            b0=P(i+.3,j+.62); b1=P(i+.75,j+.62)
            s+=f'<polygon points="{pts([up(b0,4*K),up(b1,4*K),up(b1,6*K),up(b0,6*K)])}" fill="#A06A4C"></polygon><polygon points="{pts([up(b0,6*K),up(b1,6*K),up(b1,10*K),up(b0,10*K)])}" fill="#8A5A40"></polygon>'
            s+=f'<line x1="{f(b0[0])}" y1="{f(b0[1])}" x2="{f(b0[0])}" y2="{f(b0[1]-4*K)}" stroke="#4A3A55"></line><line x1="{f(b1[0])}" y1="{f(b1[1])}" x2="{f(b1[0])}" y2="{f(b1[1]-4*K)}" stroke="#4A3A55"></line>'
            if SNOW: s+=f'<line x1="{f(b0[0])}" y1="{f(b0[1]-6.4*K)}" x2="{f(b1[0])}" y2="{f(b1[1]-6.4*K)}" stroke="#fff" stroke-width="{f(1.6*K)}" stroke-linecap="round"></line>'
            for (a_,b_) in ((.18,.25),(.82,.3)):
                x_,y_=P(i+a_,j+b_)
                fl={"kis":"#FFFFFF","yagmur":"#6FA56E","bahar":"#F28AAE","sonbahar":"#E07A2F"}[S]
                s+=f'<rect x="{f(x_-3*K)}" y="{f(y_-5*K)}" width="{f(6*K)}" height="{f(5*K)}" fill="#C96B4E"></rect><circle cx="{f(x_)}" cy="{f(y_-7*K)}" r="{f(3.6*K)}" fill="{fl}"></circle><circle cx="{f(x_+1.5*K)}" cy="{f(y_-8.5*K)}" r="{f(1.6*K)}" fill="#F7D44A"></circle>'
            s+=f'<polygon class="ns" points="{pts([up(b0,0),up(b1,0),up(b1,10*K),up(b0,10*K)])}"></polygon>'
        items.append((key,f'<g class="{rise(dl)}">{s}</g>')); continue
    if t=="park":
        q=[P(i+.06,j+.06),P(i+.94,j+.06),P(i+.94,j+.94),P(i+.06,j+.94)]
        s=f'<polygon points="{pts(q)}" fill="{CFG["grass"]}"></polygon>'
        if S=="bahar":
            s+="".join(f'<circle cx="{f(P(i+a,j+b)[0])}" cy="{f(P(i+a,j+b)[1])}" r="{1.2*K:.1f}" fill="{c}"></circle>' for a,b,c in [(.2,.6,"#F7D44A"),(.5,.3,"#F28AAE"),(.8,.4,"#FFFFFF"),(.6,.85,"#F7D44A"),(.3,.2,"#B48AF0"),(.85,.8,"#F28AAE")])
        s+=f'<polygon class="ns" points="{pts(q)}"></polygon>'
        spots=[(.32,.35,1),(.7,.62,1.25),(.35,.75,.85)]
        if SNOW and (i,j)==(6,4): spots=[(.3,.3,1),(.75,.4,.9)]
        for (a,b,sc) in spots:
            x,y=P(i+a,j+b); s+=tree(x,y,sc)
        if SNOW and (i,j)==(6,4):
            x,y=P(i+.5,j+.75); s+=snowman(x,y,1.0)
        items.append((key,f'<g class="{rise(dl)}">{s}</g>')); continue
    pal=random.choice(pals); m=.14
    if t=="house":
        h=random.choice([22,26,30])*K
        s,(A,B,C,D)=box(i+m,j+m,i+1-m,j+1-m,h,pal)
        ap=up(P(i+.5,j+.5),h+16*K)
        roof=random.choice(CFG["roof"])
        s+=f'<polygon points="{pts([up(D,h),up(C,h),ap])}" fill="{roof}"></polygon>'
        s+=f'<polygon points="{pts([up(C,h),up(B,h),ap])}" fill="{roof if not SNOW else "#E3E9F4"}" fill-opacity="{1 if SNOW else .8}"></polygon>'
        if not SNOW: s+=f'<polygon points="{pts([up(C,h),up(B,h),ap])}" fill="#000" fill-opacity=".12"></polygon>'
        # chimney
        chx,chy=up(lerp(C,B,.55),h+7*K)
        s+=f'<rect x="{f(chx-2.5*K)}" y="{f(chy-8*K)}" width="{f(5*K)}" height="{f(9*K)}" fill="#8C5E52"></rect>'
        if SNOW: s+=f'<ellipse cx="{f(chx)}" cy="{f(chy-8*K)}" rx="{f(3.4*K)}" ry="{f(1.6*K)}" fill="#FFFFFF"></ellipse>'
        if SNOW or S=="sonbahar":
            for k_ in range(3):
                s+=f'<circle class="smoke" cx="{f(chx)}" cy="{f(chy-11*K)}" r="{f(3*K)}" fill="#F3F1F6" style="animation-delay:{-k_*1.1-random.random()*.4:.2f}s"></circle>'
        s+=f'<polygon class="ns" points="{pts([up(D,h),up(C,h),up(B,h),ap])}"></polygon>'
        s+=windows(D,C,B,h,0,rows_from=7,step=30,cols=(0.3,),wcol=.36)
        q=lambda p0,p1,u,v:(p0[0]+u*(p1[0]-p0[0]), p0[1]+u*(p1[1]-p0[1])-v)
        s+=f'<polygon points="{pts([q(D,C,.68,0),q(D,C,.86,0),q(D,C,.86,10*K),q(D,C,.68,10*K)])}" fill="#5A3E4E"></polygon>'
        shadow(i+m,j+m,i+1-m,j+1-m,h+8*K)
        items.append((key,f'<g class="{rise(dl)}">{s}</g>')); continue
    if t=="shop":
        h=random.choice([40,48,56])*K
        s,(A,B,C,D)=box(i+m,j+m,i+1-m,j+1-m,h,pal,snowcap=True)
        q=lambda p0,p1,u,v:(p0[0]+u*(p1[0]-p0[0]), p0[1]+u*(p1[1]-p0[1])-v)
        aw=random.choice(["#E2574C","#2F7D6D","#E8A33B","#4F5BB8"])
        for (p0,p1) in ((D,C),(C,B)):
            a0,a1=q(p0,p1,0,14*K),q(p0,p1,1,14*K)
            s+=f'<polygon points="{pts([a0,a1,(a1[0]+3*K,a1[1]+5*K),(a0[0]+3*K,a0[1]+5*K)])}" fill="{aw}"></polygon>'
            s+="".join(f'<polygon points="{pts([lerp(a0,a1,u_),lerp(a0,a1,u_+.1),(lerp(a0,a1,u_+.1)[0]+3*K,lerp(a0,a1,u_+.1)[1]+5*K),(lerp(a0,a1,u_)[0]+3*K,lerp(a0,a1,u_)[1]+5*K)])}" fill="#FFFFFF" fill-opacity=".75"></polygon>' for u_ in (.1,.3,.5,.7))
            if SNOW: s+=f'<line x1="{f(a0[0])}" y1="{f(a0[1])}" x2="{f(a1[0])}" y2="{f(a1[1])}" stroke="#fff" stroke-width="{2*K:.1f}" stroke-linecap="round"></line>'
            s+=f'<polygon class="shopw" points="{pts([q(p0,p1,.12,2*K),q(p0,p1,.88,2*K),q(p0,p1,.88,11*K),q(p0,p1,.12,11*K)])}"></polygon>'
        s+=windows(D,C,B,h,0,rows_from=22,step=15)
        shadow(i+m,j+m,i+1-m,j+1-m,h)
        items.append((key,f'<g class="{rise(dl)}">{s}</g>')); continue
    if t=="hero": h1=150*K; h2=0
    else:
        dist=math.hypot(i-3,j-3)
        h1=max(50,random.choice([70,90,110,130,160])-dist*12)*K
        h2=random.choice([0,0,30,45])*K
    s,(A,B,C,D)=box(i+m,j+m,i+1-m,j+1-m,h1,pal,snowcap=not h2)
    s+=windows(D,C,B,h1,0,rows_from=10,step=15)
    top_h=h1
    if h2:
        m2=.28
        s2,(A2,B2,C2,D2)=box(i+m2,j+m2,i+1-m2,j+1-m2,h2,pal,z=h1,snowcap=True)
        s+=s2; s+=windows(D2,C2,B2,h2,h1,rows_from=8,step=15,cols=(0.3,),wcol=.4); top_h=h1+h2
    shadow(i+m,j+m,i+1-m,j+1-m,top_h)
    rt=random.random(); tp=up(P(i+.5,j+.5),top_h)
    if t=="hero" or rt<0.35:
        s+=f'<line x1="{f(tp[0])}" y1="{f(tp[1])}" x2="{f(tp[0])}" y2="{f(tp[1]-24*K)}" stroke="#4A3A55" stroke-width="1.4"></line>'
        s+=f'<circle class="beacon" cx="{f(tp[0])}" cy="{f(tp[1]-24*K)}" r="{f(2.2*K)}" fill="#FF3B3B" style="animation-delay:{-random.random()*1.6:.2f}s"></circle>'
    elif rt<0.65:
        x,y=tp
        s+=f'<rect x="{f(x-6*K)}" y="{f(y-14*K)}" width="{f(12*K)}" height="{f(10*K)}" class="tank"></rect><ellipse cx="{f(x)}" cy="{f(y-4*K)}" rx="{f(6*K)}" ry="{f(2.6*K)}" class="tank"></ellipse><ellipse cx="{f(x)}" cy="{f(y-14*K)}" rx="{f(6*K)}" ry="{f(2.6*K)}" class="{"snowtop" if SNOW else "tank2"}"></ellipse>'
    if t=="hero":
        p0,p1=C,B; u0,u1=.2,.8; v0=h1-48*K; vh=18*K
        ux=(p1[0]-p0[0],p1[1]-p0[1]); L=math.hypot(*ux); ux=(ux[0]/L,ux[1]/L)
        ox=p0[0]+u0*(p1[0]-p0[0]); oy=p0[1]+u0*(p1[1]-p0[1])-v0-vh
        wpx=(u1-u0)*L
        heroinfo=dict(m=f"matrix({ux[0]:.4f},{ux[1]:.4f},0,1,{ox:.2f},{oy:.2f})",w=wpx,h=vh,cx=ox+ux[0]*wpx/2,cy=oy+ux[1]*wpx/2+vh/2)
    items.append((key,f'<g class="{rise(dl)}">{s}</g>'))
# lamps
for t in [0.5,1.5,5.5,6.5]:
    for (ii,jj) in [(ROAD_I-0.02,t),(t,ROAD_J+1.02)]:
        x,y=P(ii,jj); hl=20*K
        g=(f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x)}" y2="{f(y-hl)}" stroke="#4A3A55" stroke-width="1.3"></line>'
           f'<circle class="lg" cx="{f(x)}" cy="{f(y-hl)}" r="{f(9*K)}" fill="url(#halo)"></circle><circle class="lampc" cx="{f(x)}" cy="{f(y-hl)}" r="{f(2.2*K)}"></circle>')
        if SNOW: g+=f'<ellipse cx="{f(x)}" cy="{f(y-hl-2.2*K)}" rx="{f(2.6*K)}" ry="{f(1.2*K)}" fill="#fff"></ellipse>'
        items.append(((jj,ii),f'<g>{g}</g>'))
        pools.append(f'<ellipse cx="{f(x+4*K)}" cy="{f(y+2*K)}" rx="{f(16*K)}" ry="{f(8*K)}" fill="url(#pool)"></ellipse>')
        if RAIN: refl.append(f'<rect x="{f(x+2*K)}" y="{f(y+1*K)}" width="{f(3*K)}" height="{f(20*K)}" rx="{f(1.5*K)}" fill="url(#streak)"></rect>')
# ---------- cute characters ----------
SKIN=["#F7D5BD","#EDBE9C","#D49A73","#A8704E","#7A4C33"]
HAIR=["#3A2230","#5B3A2A","#1F1A2E","#B5643C","#E8C07A","#6B4A8A"]
COAT={"kis":["#E2574C","#4F5BB8","#2F7D6D","#E8A33B","#9A5FB5","#F2F0EA"],"yagmur":["#F2C14E","#E2574C","#4FA3B8","#7A9A5A","#3A4A78"],"bahar":["#F28AAE","#7FC8A9","#F7D44A","#8FB8F2","#FFFFFF","#C9A0F0"],"sonbahar":["#C9563A","#E8A33B","#6B7F3A","#7B4F6B","#3F6672"]}[S]
UMB=["#E2574C","#F2C14E","#4FA3B8","#9A5FB5","#2F7D6D","#F28AAE"]
def chibi(s,front=True,kind="adult"):
    # local origin = feet center; returns svg (normal) and parts for night overlay
    s*=K; sk=random.choice(SKIN); hr=random.choice(HAIR); ct=random.choice(COAT)
    kid = kind=="kid"; sc=0.8 if kid else 1.0; s*=sc
    parts=[]
    parts.append(f'<rect class="legL" x="{f(-2.4*s)}" y="{f(-4*s)}" width="{f(2*s)}" height="{f(4.2*s)}" rx="{f(1*s)}" fill="#3A3048"></rect>')
    parts.append(f'<rect class="legR" x="{f(.4*s)}" y="{f(-4*s)}" width="{f(2*s)}" height="{f(4.2*s)}" rx="{f(1*s)}" fill="#3A3048"></rect>')
    parts.append(f'<path d="M {f(-4.2*s)} {f(-3.2*s)} Q {f(-4.6*s)} {f(-10.5*s)} 0 {f(-11*s)} Q {f(4.6*s)} {f(-10.5*s)} {f(4.2*s)} {f(-3.2*s)} Z" fill="{ct}"></path>')
    if SNOW: parts.append(f'<rect x="{f(-3.6*s)}" y="{f(-11.2*s)}" width="{f(7.2*s)}" height="{f(2.2*s)}" rx="{f(1.1*s)}" fill="{random.choice(["#F2F0EA","#E2574C","#F2C14E","#7FC8A9"])}"></rect>')
    if kind=="adult" and random.random()<.4:
        parts.append(f'<rect x="{f(3.4*s)}" y="{f(-8*s)}" width="{f(2.6*s)}" height="{f(3.4*s)}" rx="{f(.8*s)}" fill="#8C5E52"></rect>')
    hy=-15.8*s; hrr=5.4*s
    parts.append(f'<circle cx="0" cy="{f(hy)}" r="{f(hrr)}" fill="{sk}"></circle>')
    if front:
        parts.append(f'<path d="M {f(-5.6*s)} {f(hy+.2*s)} Q {f(-5.8*s)} {f(hy-6.6*s)} 0 {f(hy-6*s)} Q {f(5.8*s)} {f(hy-6.6*s)} {f(5.6*s)} {f(hy+.2*s)} Q {f(3*s)} {f(hy-3.6*s)} {f(-1*s)} {f(hy-2.8*s)} Q {f(-4*s)} {f(hy-2.4*s)} {f(-5.6*s)} {f(hy+.2*s)} Z" fill="{hr}"></path>')
        parts.append(f'<circle cx="{f(-1.9*s)}" cy="{f(hy+.6*s)}" r="{f(.75*s)}" fill="#2B1B2A"></circle><circle cx="{f(1.9*s)}" cy="{f(hy+.6*s)}" r="{f(.75*s)}" fill="#2B1B2A"></circle>')
        parts.append(f'<circle cx="{f(-1.6*s)}" cy="{f(hy+.3*s)}" r="{f(.25*s)}" fill="#FFFFFF"></circle><circle cx="{f(2.2*s)}" cy="{f(hy+.3*s)}" r="{f(.25*s)}" fill="#FFFFFF"></circle>')
        parts.append(f'<ellipse cx="{f(-3.3*s)}" cy="{f(hy+2.1*s)}" rx="{f(1.1*s)}" ry="{f(.7*s)}" fill="#F48FA0" fill-opacity=".7"></ellipse><ellipse cx="{f(3.3*s)}" cy="{f(hy+2.1*s)}" rx="{f(1.1*s)}" ry="{f(.7*s)}" fill="#F48FA0" fill-opacity=".7"></ellipse>')
        parts.append(f'<path d="M {f(-.8*s)} {f(hy+2.3*s)} Q 0 {f(hy+3.1*s)} {f(.8*s)} {f(hy+2.3*s)}" fill="none" stroke="#2B1B2A" stroke-width="{f(.4*s)}" stroke-linecap="round"></path>')
    else:
        parts.append(f'<circle cx="0" cy="{f(hy-.4*s)}" r="{f(hrr+.3*s)}" fill="{hr}"></circle>')
    if SNOW:
        bc=random.choice(["#E2574C","#4F5BB8","#F2C14E","#7FC8A9","#F28AAE"])
        parts.append(f'<path d="M {f(-5.7*s)} {f(hy-1*s)} Q {f(-5.4*s)} {f(hy-7.4*s)} 0 {f(hy-7.2*s)} Q {f(5.4*s)} {f(hy-7.4*s)} {f(5.7*s)} {f(hy-1*s)} Z" fill="{bc}"></path><rect x="{f(-5.9*s)}" y="{f(hy-2.2*s)}" width="{f(11.8*s)}" height="{f(2*s)}" rx="{f(1*s)}" fill="#FFFFFF"></rect><circle cx="0" cy="{f(hy-7.6*s)}" r="{f(1.6*s)}" fill="#FFFFFF"></circle>')
    elif S=="bahar" and random.random()<.35:
        parts.append(f'<circle cx="{f(3.6*s)}" cy="{f(hy-4.4*s)}" r="{f(1.3*s)}" fill="#F7D44A"></circle><circle cx="{f(3.6*s)}" cy="{f(hy-4.4*s)}" r="{f(.6*s)}" fill="#F28AAE"></circle>')
    extra=""
    if RAIN:
        uc=random.choice(UMB)
        extra=(f'<line x1="{f(2.6*s)}" y1="{f(-7*s)}" x2="{f(2.6*s)}" y2="{f(-27*s)}" stroke="#4A3A55" stroke-width="{f(.6*s)}"></line>'
               f'<path d="M {f(-9.4*s)} {f(-25*s)} Q {f(2.6*s)} {f(-39*s)} {f(14.6*s)} {f(-25*s)} Q {f(11.6*s)} {f(-26.8*s)} {f(8.6*s)} {f(-25*s)} Q {f(5.6*s)} {f(-26.8*s)} {f(2.6*s)} {f(-25*s)} Q {f(-.4*s)} {f(-26.8*s)} {f(-3.4*s)} {f(-25*s)} Q {f(-6.4*s)} {f(-26.8*s)} {f(-9.4*s)} {f(-25*s)} Z" fill="{uc}"></path>'
               f'<path d="M {f(2.6*s)} {f(-32*s)} Q {f(5.6*s)} {f(-31*s)} {f(8.6*s)} {f(-25*s)}" fill="none" stroke="#FFFFFF" stroke-opacity=".5" stroke-width="{f(.6*s)}"></path>')
    if kind=="kid" and S=="bahar":
        bc=random.choice(["#E2574C","#F7D44A","#8FB8F2"])
        extra+=(f'<path d="M {f(3*s)} {f(-8*s)} Q {f(6*s)} {f(-20*s)} {f(4*s)} {f(-30*s)}" fill="none" stroke="#4A3A55" stroke-width="{f(.4*s)}"></path>'
                f'<ellipse class="balloon" cx="{f(4*s)}" cy="{f(-34*s)}" rx="{f(3.6*s)}" ry="{f(4.4*s)}" fill="{bc}"></ellipse><ellipse cx="{f(2.8*s)}" cy="{f(-35.5*s)}" rx="{f(.9*s)}" ry="{f(1.4*s)}" fill="#FFFFFF" fill-opacity=".6"></ellipse>')
    body="".join(parts)
    night=f'<g class="nsc">{extra}{body}</g>'
    shadowc=f'<ellipse cx="0" cy="0" rx="{f(5*s)}" ry="{f(1.8*s)}" fill="#2B1B2A" fill-opacity=".22"></ellipse>'
    return shadowc+f'<g class="bob" style="animation-delay:{-random.random()*.5:.2f}s">'+extra+body+night+'</g>'
def dog(s=1.0):
    s*=K; c=random.choice(["#E8B57A","#F2F0EA","#5B3A2A"])
    return (f'<ellipse cx="0" cy="0" rx="{f(4*s)}" ry="{f(1.4*s)}" fill="#2B1B2A" fill-opacity=".2"></ellipse><g class="bob" style="animation-duration:.25s">'
            f'<rect x="{f(-3.6*s)}" y="{f(-3*s)}" width="{f(1.4*s)}" height="{f(3*s)}" fill="{c}"></rect><rect x="{f(2*s)}" y="{f(-3*s)}" width="{f(1.4*s)}" height="{f(3*s)}" fill="{c}"></rect>'
            f'<ellipse cx="0" cy="{f(-4.2*s)}" rx="{f(4.4*s)}" ry="{f(2.6*s)}" fill="{c}"></ellipse>'
            f'<circle cx="{f(3.8*s)}" cy="{f(-7*s)}" r="{f(2.8*s)}" fill="{c}"></circle><ellipse cx="{f(2.4*s)}" cy="{f(-8.6*s)}" rx="{f(1*s)}" ry="{f(1.8*s)}" fill="#5B3A2A"></ellipse>'
            f'<circle cx="{f(4.6*s)}" cy="{f(-7.3*s)}" r="{f(.55*s)}" fill="#2B1B2A"></circle><circle cx="{f(6.4*s)}" cy="{f(-6.4*s)}" r="{f(.6*s)}" fill="#2B1B2A"></circle>'
            f'<path class="wag" d="M {f(-4*s)} {f(-5*s)} q {f(-2*s)} {f(-2*s)} {f(-1.6*s)} {f(-4*s)}" fill="none" stroke="{c}" stroke-width="{f(1.2*s)}" stroke-linecap="round"></path>'
            '</g>')
wid=[0]
def walker(j, i_from, i_to, svg, dur, delay):
    wid[0]+=1; n=wid[0]
    x0,y0=P(i_from,j); x1,y1=P(i_to,j)
    kf.append(f".wk{n}{{animation:wk{n} {dur:.3f}s linear infinite;animation-delay:{delay:.2f}s}}@keyframes wk{n}{{0%{{transform:translate({f(x0)}px,{f(y0)}px)}}100%{{transform:translate({f(x1)}px,{f(y1)}px)}}}}")
    return f'<g class="wk{n}">{svg}</g>'
random.seed(91)
for lane_j,group in ((ROAD_J-.05,walkers_back),(ROAD_J+1.07,walkers_front)):
    for k in range(4):
        fwd=random.random()<.65
        kind="kid" if (k==1 and S=="bahar") else "adult"
        dur=random.choice([10,10,20/1.0])
        dl=-random.random()*dur
        if fwd: svg=chibi(1.3,True,kind); a,b=-.6,N+.6
        else: svg=chibi(1.3,False,kind); a,b=N+.6,-.6
        group.append(walker(lane_j,a,b,svg,dur,dl))
        if k==2 and not RAIN:
            group.append(walker(lane_j,a+(-.32 if fwd else .32),b+(-.32 if fwd else .32),dog(1.3),dur,dl))
random.seed(23)
# cars
def carbox(i0,j0,di,col,rev=False):
    if di: bi0,bj0,bi1,bj1=i0,j0-.09,i0+.36,j0+.09
    else:  bi0,bj0,bi1,bj1=i0-.09,j0,i0+.09,j0+.36
    s,_=box(bi0,bj0,bi1,bj1,6*K,("#FFFFFF",col,col))
    cab,_=box(bi0+(.08 if di else .02),bj0+(.02 if di else .08),bi1-(.08 if di else .02),bj1-(.02 if di else .08),4*K,("#DDE8F5","#8FA6C9","#6F87AE"),z=6*K)
    if SNOW: s+=""; cab=cab.replace('fill="#FFFFFF"','fill="#FFFFFF"')
    front=P(bi1,(bj0+bj1)/2) if di else P((bi0+bi1)/2,bj1)
    back=P(bi0,(bj0+bj1)/2) if di else P((bi0+bi1)/2,bj0)
    sg=1
    if rev: front,back=back,front; sg=-1
    hd=f'<ellipse class="hl" cx="{f(front[0]+sg*(9 if di else -9)*K)}" cy="{f(front[1]+sg*5*K)}" rx="{f(12*K)}" ry="{f(5*K)}" fill="url(#beam)"></ellipse>'
    tl=f'<circle class="tl" cx="{f(back[0])}" cy="{f(back[1]-3*K)}" r="{f(1.6*K)}" fill="#FF4A4A"></circle>'
    rf=f'<rect class="hl" x="{f(front[0]-1.5*K)}" y="{f(front[1])}" width="{f(3*K)}" height="{f(16*K)}" rx="{f(1.5*K)}" fill="url(#streak)"></rect>' if RAIN else ""
    return rf+s+cab+hd+tl
carcols=["#E2574C","#F4D68C","#4F5BB8","#2F7D6D","#F4F1EA","#E8A33B","#9280CC"]
cid=0
for (di,jj,rev) in [(1,ROAD_J+.3,False),(1,ROAD_J+.7,True),(0,ROAD_I+.3,True),(0,ROAD_I+.7,False)]:
    for k in range(2):
        cid+=1; col=random.choice(carcols)
        g=carbox(-1.0,jj,1,col,rev) if di else carbox(jj,-1.0,0,col,rev)
        dur=random.choice([5,10/3,10/3,5])*(1.4 if SNOW else 1)
        dur=10/round(10/dur)
        dx=(N+1.4)*SX*(1 if di else -1); dy=(N+1.4)*SY
        a,b="translate(0px,0px)",f"translate({dx:.1f}px,{dy:.1f}px)"
        if rev: a,b=b,a
        kf.append(f".car{cid}{{animation:car{cid} {dur:.3f}s linear infinite;animation-delay:{-random.random()*dur:.2f}s}}@keyframes car{cid}{{0%{{transform:{a}}}100%{{transform:{b}}}}}")
        cars.append(f'<g class="car{cid}">{g}</g>')
# insert walkers into depth order (key by j)
items.append(((ROAD_J-.05,99),"".join(walkers_back)))
items.append(((ROAD_J+.5,99),"".join(walkers_front)))
items.sort(key=lambda x:x[0])
# hero interior (cute)
hi=heroinfo; w=hi["w"]; hh=hi["h"]
def X(u): return f(w*u)
def Y(v): return f(hh*v)
interior=f'''<g transform="{hi['m']}">
<rect x="0" y="0" width="{X(1)}" height="{Y(1)}" fill="url(#room)"></rect>
<rect x="{X(.06)}" y="{Y(.1)}" width="{X(.22)}" height="{Y(.64)}" rx="{Y(.02)}" fill="#9C5B3F" fill-opacity=".55"></rect>
<g><rect x="{X(.08)}" y="{Y(.18)}" width="{X(.03)}" height="{Y(.16)}" fill="#E2574C"></rect><rect x="{X(.115)}" y="{Y(.16)}" width="{X(.025)}" height="{Y(.18)}" fill="#4F5BB8"></rect><rect x="{X(.145)}" y="{Y(.2)}" width="{X(.035)}" height="{Y(.14)}" fill="#F2C14E"></rect><rect x="{X(.185)}" y="{Y(.17)}" width="{X(.025)}" height="{Y(.17)}" fill="#2F7D6D"></rect>
<rect x="{X(.08)}" y="{Y(.34)}" width="{X(.18)}" height="{Y(.025)}" fill="#6B3B2A"></rect>
<circle cx="{X(.13)}" cy="{Y(.5)}" r="{Y(.06)}" fill="#7FC8A9"></circle><rect x="{X(.115)}" y="{Y(.54)}" width="{X(.03)}" height="{Y(.08)}" fill="#C96B4E"></rect><rect x="{X(.17)}" y="{Y(.46)}" width="{X(.05)}" height="{Y(.16)}" rx="{Y(.02)}" fill="#F7F1E6"></rect><rect x="{X(.08)}" y="{Y(.62)}" width="{X(.18)}" height="{Y(.025)}" fill="#6B3B2A"></rect></g>
<circle class="lampp" cx="{X(.7)}" cy="{Y(.45)}" r="{Y(.5)}" fill="url(#lampglow)"></circle>
<path d="M {X(.74)} {Y(.78)} L {X(.74)} {Y(.44)} L {X(.68)} {Y(.34)}" fill="none" stroke="#3A2230" stroke-width="{Y(.025)}" stroke-linecap="round"></path>
<path d="M {X(.62)} {Y(.30)} L {X(.72)} {Y(.27)} L {X(.73)} {Y(.37)} L {X(.66)} {Y(.40)} Z" fill="#F2C14E"></path>
<rect x="{X(.28)}" y="{Y(.78)}" width="{X(.64)}" height="{Y(.05)}" rx="{Y(.02)}" fill="#7B4A36"></rect>
<g class="reader">
<path d="M {X(.34)} {Y(.80)} C {X(.34)} {Y(.60)}, {X(.39)} {Y(.54)}, {X(.46)} {Y(.54)} C {X(.53)} {Y(.54)}, {X(.58)} {Y(.60)}, {X(.58)} {Y(.80)} Z" fill="#7FC8A9"></path>
<path d="M {X(.40)} {Y(.57)} Q {X(.46)} {Y(.64)} {X(.52)} {Y(.57)}" fill="none" stroke="#F7F1E6" stroke-width="{Y(.02)}"></path>
<circle cx="{X(.46)}" cy="{Y(.38)}" r="{Y(.16)}" fill="#F7D5BD"></circle>
<path d="M {X(.375)} {Y(.40)} Q {X(.37)} {Y(.18)} {X(.46)} {Y(.19)} Q {X(.55)} {Y(.18)} {X(.545)} {Y(.40)} Q {X(.52)} {Y(.28)} {X(.47)} {Y(.29)} Q {X(.41)} {Y(.29)} {X(.375)} {Y(.40)} Z" fill="#3A2230"></path>
<circle cx="{X(.46)}" cy="{Y(.15)}" r="{Y(.06)}" fill="#3A2230"></circle>
<g class="blinkE"><circle cx="{X(.43)}" cy="{Y(.41)}" r="{Y(.017)}" fill="#2B1B2A"></circle><circle cx="{X(.49)}" cy="{Y(.41)}" r="{Y(.017)}" fill="#2B1B2A"></circle></g>
<ellipse cx="{X(.41)}" cy="{Y(.46)}" rx="{Y(.03)}" ry="{Y(.018)}" fill="#F48FA0" fill-opacity=".8"></ellipse><ellipse cx="{X(.51)}" cy="{Y(.46)}" rx="{Y(.03)}" ry="{Y(.018)}" fill="#F48FA0" fill-opacity=".8"></ellipse>
<path d="M {X(.45)} {Y(.47)} Q {X(.46)} {Y(.49)} {X(.47)} {Y(.47)}" fill="none" stroke="#2B1B2A" stroke-width="{Y(.008)}" stroke-linecap="round"></path>
<g class="book"><path d="M {X(.44)} {Y(.66)} L {X(.52)} {Y(.60)} L {X(.60)} {Y(.66)} L {X(.60)} {Y(.74)} L {X(.52)} {Y(.69)} L {X(.44)} {Y(.74)} Z" fill="#E2574C"></path><path d="M {X(.45)} {Y(.665)} L {X(.52)} {Y(.615)} L {X(.59)} {Y(.665)} L {X(.59)} {Y(.72)} L {X(.52)} {Y(.675)} L {X(.45)} {Y(.72)} Z" fill="#FFF8EC"></path></g>
<circle cx="{X(.44)}" cy="{Y(.70)}" r="{Y(.03)}" fill="#F7D5BD"></circle><circle cx="{X(.60)}" cy="{Y(.70)}" r="{Y(.03)}" fill="#F7D5BD"></circle>
</g>
<g class="steam" fill="none" stroke="#FFF8EC" stroke-opacity=".8" stroke-width="{Y(.012)}" stroke-linecap="round"><path d="M {X(.85)} {Y(.70)} q {X(.012)} {Y(-.05)} 0 {Y(-.1)} q {X(-.012)} {Y(-.05)} 0 {Y(-.1)}"></path></g>
<rect x="{X(.825)}" y="{Y(.70)}" width="{X(.05)}" height="{Y(.08)}" rx="{Y(.015)}" fill="#F7F1E6"></rect><path d="M {X(.875)} {Y(.72)} q {X(.02)} 0 0 {Y(.04)}" fill="none" stroke="#F7F1E6" stroke-width="{Y(.01)}"></path>
<g class="cat">
<path class="tail" d="M {X(.115)} {Y(.92)} q {X(-.05)} {Y(-.02)} {X(-.035)} {Y(-.16)}" fill="none" stroke="#F2A65A" stroke-width="{Y(.03)}" stroke-linecap="round"></path>
<ellipse cx="{X(.18)}" cy="{Y(.92)}" rx="{X(.07)}" ry="{Y(.06)}" fill="#F2A65A"></ellipse>
<circle cx="{X(.24)}" cy="{Y(.85)}" r="{Y(.065)}" fill="#F2A65A"></circle>
<path d="M {X(.212)} {Y(.81)} l {X(.006)} {Y(-.06)} l {X(.015)} {Y(.04)} Z M {X(.252)} {Y(.80)} l {X(.012)} {Y(-.055)} l {X(.01)} {Y(.055)} Z" fill="#F2A65A"></path>
<path d="M {X(.225)} {Y(.85)} q {X(.006)} {Y(.012)} {X(.012)} 0 M {X(.245)} {Y(.85)} q {X(.006)} {Y(.012)} {X(.012)} 0" fill="none" stroke="#2B1B2A" stroke-width="{Y(.008)}" stroke-linecap="round"></path>
<ellipse cx="{X(.222)}" cy="{Y(.875)}" rx="{Y(.012)}" ry="{Y(.008)}" fill="#F48FA0"></ellipse><ellipse cx="{X(.262)}" cy="{Y(.875)}" rx="{Y(.012)}" ry="{Y(.008)}" fill="#F48FA0"></ellipse>
</g>
<rect x="0" y="0" width="{X(.12)}" height="{Y(1)}" fill="#E07A5F" fill-opacity=".85"></rect><rect x="{X(.88)}" y="0" width="{X(.12)}" height="{Y(1)}" fill="#E07A5F" fill-opacity=".85"></rect>
<g fill="#FFF4E8" fill-opacity=".35"><circle cx="{X(.03)}" cy="{Y(.2)}" r="{Y(.012)}"></circle><circle cx="{X(.08)}" cy="{Y(.45)}" r="{Y(.012)}"></circle><circle cx="{X(.04)}" cy="{Y(.7)}" r="{Y(.012)}"></circle><circle cx="{X(.93)}" cy="{Y(.3)}" r="{Y(.012)}"></circle><circle cx="{X(.97)}" cy="{Y(.6)}" r="{Y(.012)}"></circle></g>
<rect x="0" y="0" width="{X(1)}" height="{Y(1)}" fill="none" stroke="#FFF4E8" stroke-width="{Y(.04)}"></rect>
<line x1="{X(.5)}" y1="0" x2="{X(.5)}" y2="{Y(1)}" stroke="#FFF4E8" stroke-width="{Y(.02)}" stroke-opacity=".6"></line>
{"<path d='M 0 0 Q %s %s %s 0 Z' fill='#E3ECF5' fill-opacity='.7'></path>"%(X(.5),Y(.12),X(1)) if SNOW else ""}
{"".join("<line class='drip' x1='%s' y1='%s' x2='%s' y2='%s' stroke='#DCE8F4' stroke-opacity='.55' stroke-width='%s' style='animation-delay:-%.2fs'></line>"%(X(u),Y(.05),X(u),Y(.2),Y(.012),random.random()*2) for u in (.32,.58,.71,.9)) if RAIN else ""}
<rect x="{X(-.04)}" y="{Y(.98)}" width="{X(1.08)}" height="{Y(.07)}" fill="{"#FFFFFF" if SNOW else "#FFF4E8"}"></rect>
</g>'''
kz=13.0 if mode=="v" else 9.0
tx=W/2-kz*hi["cx"]; ty=(H*0.42 if mode=="v" else H*0.46)-kz*hi["cy"]
cam_end=f"translate({tx:.1f}px,{ty:.1f}px) scale({kz})"
def camAt(sc,fx,fy,sx,sy): return f"translate({sx-sc*fx:.1f}px,{sy-sc*fy:.1f}px) scale({sc})"
dcx,dcy=CX,CY+N*SY
if mode=="v": c0=camAt(.78,dcx,dcy,W/2,dcy+150); stz=2.7
else: c0=camAt(.82,dcx,dcy,W/2,dcy+90); stz=2.2
c1=camAt(1,dcx,dcy,dcx,dcy)
fx,fy=P(1.7,ROAD_J+.55)
sa=camAt(stz,fx,fy,W*0.5,H*(0.5 if mode=="v" else 0.55)); sb=camAt(stz*1.1,fx+26*K,fy+12*K,W*0.5,H*(0.5 if mode=="v" else 0.55))
camkf=("@keyframes cam{0%{transform:"+c0+";animation-timing-function:cubic-bezier(.3,0,.2,1)}22%{transform:"+c1+";animation-timing-function:cubic-bezier(.6,0,.3,1)}32%{transform:"+sa+";animation-timing-function:linear}63%{transform:"+sb+";animation-timing-function:cubic-bezier(.7,0,.2,1)}95%,100%{transform:"+cam_end+"}}")
# weather particles (screen space)
random.seed(5); wx=[]
if SNOW:
    for _ in range(150 if mode=="v" else 170):
        x=random.uniform(0,W); r=random.choice([1,1.3,1.6,2.2,2.8]); d=random.uniform(5,10); dl=-random.random()*d
        wx.append(f'<g class="fall" style="animation-duration:{10/round(10/d):.3f}s;animation-delay:{dl:.2f}s"><circle class="drift" cx="{x:.0f}" cy="-10" r="{r}" fill="#FFFFFF" fill-opacity="{.6+r/8:.2f}" style="animation-delay:{-random.random()*3:.2f}s"></circle></g>')
elif RAIN:
    for _ in range(170 if mode=="v" else 200):
        x=random.uniform(-60,W+40); L_=random.uniform(14,26); d=random.choice([.5,.625,.8333,1.0]); dl=-random.random()*d
        wx.append(f'<line class="rain" x1="{x:.0f}" y1="-30" x2="{x-L_*.25:.0f}" y2="{-30+L_:.0f}" stroke="#DCE8F4" stroke-opacity="{random.uniform(.35,.7):.2f}" stroke-width="1" style="animation-duration:{d}s;animation-delay:{dl:.2f}s"></line>')
else:
    cols=["#F7B6C8","#FBD3DF","#FFFFFF"] if S=="bahar" else ["#E07A2F","#F2B544","#C9483A","#D9A12B"]
    for _ in range(46 if mode=="v" else 56):
        x=random.uniform(-40,W); d=random.choice([5,10/3,10]); dl=-random.random()*d; c=random.choice(cols)
        shape=(f'<ellipse cx="0" cy="0" rx="3.2" ry="1.8" fill="{c}"></ellipse>' if S=="bahar" else f'<path d="M -4 0 Q 0 -3 4 0 Q 0 3 -4 0 Z" fill="{c}"></path><line x1="-4" y1="0" x2="4" y2="0" stroke="#8A4A2A" stroke-width=".4"></line>')
        wx.append(f'<g class="fall2" style="animation-duration:{d:.3f}s;animation-delay:{dl:.2f}s"><g transform="translate({x:.0f} -20)"><g class="spin" style="animation-delay:{-random.random()*2:.2f}s">{shape}</g></g></g>')
tpl=open(sys.argv[3]).read()
rep={"%GROUND%":"\n".join(ground),"%SHADOWS%":"\n".join(shadows),"%ITEMS%":"\n".join(x for _,x in items),
"%CARS%":"\n".join(cars),"%LAMPGLOW%":"\n".join(pools),"%REFL%":"\n".join(refl),"%HERO%":interior,"%KF%":"\n".join(kf),"%CAMEND%":cam_end,
"%W%":str(W),"%H%":str(H),"%GROUNDCLIP%":pts(G),"%WX%":"\n".join(wx),"%SHCOL%":CFG["shadow"]}
for k,v in rep.items(): tpl=tpl.replace(k,v)
import re as _re
tpl=_re.sub(r"@keyframes cam\{.*?\}\}",camkf,tpl,count=1,flags=_re.S)
print(tpl)
