import math, random
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(page_title='Ubicación de equipos · Motor de localización', page_icon='🟢', layout='wide', initial_sidebar_state='expanded')

# ================= CSS =================
st.markdown('''<style>
:root{--verde-oscuro:#0d4a33;--verde:#1a8a5a;--verde-claro:#d9f1e5;--texto:#1d2b25;--texto-suave:#5b6b63;--fondo:#eef3f0;--borde:#dbe7e0;--rojo:#d7263d;--gris:#9aa7a1}
.stApp{background:#eef3f0;color:#1d2b25}.block-container{padding:1.3rem 1.5rem 2rem;max-width:none}
[data-testid="stSidebar"]{background:#0d4a33}.side-title{color:white;font-weight:800;font-size:1.15rem}.side-sub{color:#bfe8d3;font-size:.72rem}
[data-testid="stSidebar"] .stRadio label{color:#d7ece2}.stButton>button{border-radius:8px;border:1px solid #9fd9bb;font-weight:600}
.card{background:#fff;border:1px solid #dbe7e0;border-radius:14px;padding:1rem}.chip{background:#fff;border:1px solid #dbe7e0;border-radius:12px;padding:.75rem .9rem}.chipv{font-size:1.35rem;font-weight:800;color:#0d4a33}.chipt{font-size:.78rem;color:#5b6b63}
.kpi{background:#fff;border:1px solid #dbe7e0;border-radius:14px;padding:1rem}.kpiv{font-size:1.6rem;font-weight:800;color:#0d4a33}.kpit{font-size:.82rem;color:#5b6b63}
.alert{background:#fff5f6;border:1px solid #f5c2ca;border-radius:12px;padding:.7rem .9rem}.okalert{background:#f1faf5;border-color:#bfe3cf}.small{font-size:.8rem;color:#5b6b63}.title{font-size:1.5rem;color:#0d4a33;font-weight:700}.section-title{font-size:1rem;color:#0d4a33;font-weight:700;margin-bottom:.7rem}
.badge{display:inline-block;border-radius:999px;padding:.25rem .6rem;font-size:.78rem;font-weight:700}.bar{height:14px;background:#e9f2ed;border-radius:6px;overflow:hidden}.fill{height:100%;background:#1a8a5a;border-radius:6px}
.log{font-size:.78rem;border-top:1px solid #dbe7e0;padding-top:.6rem}.logrow{padding:.2rem 0;border-bottom:1px dashed #e6eee9}
</style>''', unsafe_allow_html=True)

# ================= DATA =================
ROOMS={
'UCI Adultos':[{'id':'H1','x':20,'y':20,'w':170,'h':180},{'id':'H2','x':210,'y':20,'w':170,'h':180},{'id':'H3','x':400,'y':20,'w':220,'h':180},{'id':'H4','x':20,'y':220,'w':170,'h':180},{'id':'EST','x':210,'y':220,'w':170,'h':180},{'id':'H5','x':400,'y':220,'w':220,'h':180}],
'Urgencias':[{'id':'TR1','x':20,'y':20,'w':200,'h':180},{'id':'TR2','x':240,'y':20,'w':200,'h':180},{'id':'TR3','x':460,'y':20,'w':160,'h':180},{'id':'SAL','x':20,'y':220,'w':300,'h':180},{'id':'ESP','x':340,'y':220,'w':280,'h':180}],
'Hospitalización 5A':[{'id':'501','x':20,'y':20,'w':150,'h':180},{'id':'502','x':190,'y':20,'w':150,'h':180},{'id':'503','x':360,'y':20,'w':150,'h':180},{'id':'504','x':530,'y':20,'w':90,'h':180},{'id':'ENF','x':20,'y':220,'w':250,'h':180},{'id':'MED','x':290,'y':220,'w':330,'h':180}],
'UCI Pediátrica':[{'id':'P1','x':20,'y':20,'w':200,'h':180},{'id':'P2','x':240,'y':20,'w':200,'h':180},{'id':'P3','x':460,'y':20,'w':160,'h':180},{'id':'CUA','x':20,'y':220,'w':300,'h':180},{'id':'PEST','x':340,'y':220,'w':280,'h':180}]}
ROOM={}; READERS={}
for service, rooms in ROOMS.items():
    for r in rooms:
        d={**r,'servicio':service,'cx':r['x']+r['w']/2,'cy':r['y']+14}; ROOM[r['id']]=d; READERS[r['id']]=d

BASE=[
('MON-0721','Monitor de signos vitales','Monitoreo','UCI Adultos','H3',True,'2026-11-18'),('VEN-0113','Ventilador mecánico','Soporte vital','UCI Adultos','H1',False,'2026-11-20'),('BOM-0345','Bomba de infusión','Infusión','UCI Adultos','H2',True,'2026-11-15'),('MON-0788','Monitor de signos vitales','Monitoreo','UCI Adultos','H5',True,'2026-11-23'),('VEN-0240','Ventilador mecánico','Soporte vital','UCI Adultos','EST',False,'2026-11-25'),('DES-0048','Desfibrilador','Emergencia','Urgencias','TR1',True,'2026-11-10'),('DES-0052','Desfibrilador','Emergencia','Urgencias','TR3',True,'2026-11-10'),('MON-0605','Monitor de signos vitales','Monitoreo','Urgencias','TR2',True,'2026-11-19'),('ECG-0210','Electrocardiógrafo','Diagnóstico','Urgencias','ESP',True,'2026-11-12'),('BOM-0391','Bomba de infusión','Infusión','Hospitalización 5A','501',True,'2026-11-16'),('BOM-0402','Bomba de infusión','Infusión','Hospitalización 5A','503',True,'2026-11-17'),('MON-0690','Monitor de signos vitales','Monitoreo','Hospitalización 5A','502',True,'2026-11-21'),('ASP-0077','Aspirador de secreciones','Soporte','Hospitalización 5A','MED',True,'2026-11-08'),('VEN-0310','Ventilador mecánico','Soporte vital','UCI Pediátrica','P1',False,'2026-11-14'),('MON-0415','Monitor de signos vitales','Monitoreo','UCI Pediátrica','P2',True,'2026-11-13'),('INC-0088','Incubadora de transporte','Neonatal','UCI Pediátrica','CUA',True,'2026-11-25')]
DES={'BOM-0345':'H4','DES-0052':'TR1','MON-0788':'EST','ASP-0077':'TALLER'}

def randpos(r): return {'x':r['x']+20+random.random()*(r['w']-40),'y':r['y']+45+random.random()*(r['h']-65)}

def init():
    if 'equipos' not in st.session_state:
        st.session_state.equipos=[]
        for c,n,t,s,sala,m,p in BASE:
            real=DES.get(c,sala); pos=randpos(ROOM[real]) if real!='TALLER' else None
            st.session_state.equipos.append(dict(codigo=c,nombre=n,tipo=t,servicio=s,sala=sala,real=real,movil=m,proximo=datetime.fromisoformat(p+'T12:00:00'),tag='TAG-'+c,pos=pos,reads=[],ultima=0,det=None))
        st.session_state.log=[]; st.session_state.pausado=False; st.session_state.selected=None
        st.session_state.ots=make_ots()

def make_ots():
    engineers=['Ing. Laura Gómez','Ing. Andrés Ruiz','Tec. Camila Torres','Ing. Felipe Mora']; out=[]; hoy=datetime(2026,11,6,12)
    for mes in [9,10]:
        for k in range(150):
            e=BASE[k%len(BASE)]; fecha=datetime(2026,mes,1+(k%28),12); cierre=None
            if fecha<hoy and k%10!=9: cierre=min(fecha+timedelta(days=(k%5)-1),hoy)
            elif fecha>=hoy and k%25==0: cierre=hoy
            out.append(dict(id=f'OT-{mes+1}-{k+1:03d}',codigo=e[0],fechaProg=fecha,ingeniero=engineers[k%4],cierre=cierre))
    return out

init()

def generate_reads(t):
    if st.session_state.pausado:return
    for e in st.session_state.equipos:
        if not e['pos'] or e['real'] not in ROOM: continue
        for rd in ROOMS[e['servicio']]:
            d=math.hypot(e['pos']['x']-rd['cx'],e['pos']['y']-rd['cy'])
            if d>240 or random.random()>.85: continue
            rssi=-40-22*math.log10(max(d,8)/25)+(random.random()+random.random()+random.random()-1.5)*2*2.5
            e['reads'].append({'reader':rd['id'],'rssi':rssi,'t':t})
        e['reads']=[r for r in e['reads'] if t-r['t']<60000]

def detect(e,t):
    win=[r for r in e['reads'] if t-r['t']<=20000]
    if not win:
        if not e['ultima'] or t-e['ultima']>40000: update(e,{'sala':None,'status':'sin','conf':0,'pos':e['det']['pos'] if e['det'] else None,'lecturas':0})
        return
    e['ultima']=max(e['ultima'],*[r['t'] for r in win])
    groups={}
    for r in win: groups.setdefault(r['reader'],[]).append(r['rssi'])
    ranking=sorted([(k,sum(v)/len(v)) for k,v in groups.items()],key=lambda z:z[1],reverse=True)
    best=ranking[0]; second=ranking[1] if len(ranking)>1 else None; sala=best[0]; conf=best[1]-second[1] if second else 20
    weights=[(k,10**(avg/20)) for k,avg in ranking[:3]]; ws=sum(w for _,w in weights); x=sum(w*READERS[k]['cx'] for k,w in weights)/ws; y=sum(w*READERS[k]['cy'] for k,w in weights)/ws
    R=ROOM[sala]; pos={'x':max(R['x']+10,min(x,R['x']+R['w']-10)),'y':max(R['y']+10,min(y,R['y']+R['h']-10))}
    update(e,{'sala':sala,'status':'ok' if sala==e['sala'] else 'verificar','conf':conf,'pos':pos,'lecturas':len(win)})

def update(e,new):
    old=e['det']; changed=not old or old.get('sala')!=new.get('sala') or old.get('status')!=new.get('status'); e['det']=new
    if changed:
        if new['status']=='sin': txt=f"{e['codigo']}: sin lectura reciente"; typ='gris'
        elif new['status']=='ok': txt=f"{e['codigo']} en {new['sala']}: coincide con el inventario"; typ='ok'
        else: txt=f"{e['codigo']} detectado en {new['sala']} (inventario: {e['sala']})"; typ='mal'
        st.session_state.log.insert(0,(datetime.now().strftime('%H:%M:%S'),txt,typ)); st.session_state.log=st.session_state.log[:25]

def tick():
    t=int(datetime.now().timestamp()*1000); generate_reads(t)
    if not st.session_state.pausado and random.random()<.01: move_random(False)
    for e in st.session_state.equipos: detect(e,t)

def move_random(forced=True):
    cand=[e for e in st.session_state.equipos if e['real']!='TALLER' and (forced or e['movil'])]
    if not cand:return
    e=random.choice(cand); salas=[r['id'] for r in ROOMS[e['servicio']]]; e['real']=random.choice([s for s in salas if s!=e['real']]); e['pos']=randpos(ROOM[e['real']])

def workshop():
    cand=[e for e in st.session_state.equipos if e['real']!='TALLER']
    e=random.choice(cand); e['real']='TALLER'; e['pos']=None

def status(e):return e['det']['status'] if e.get('det') else 'sin'
COL={'ok':'#1a8a5a','verificar':'#d7263d','sin':'#9aa7a1'}
LABEL={'ok':'Coincide con el inventario','verificar':'Ubicación distinta: corregir','sin':'Sin lectura reciente'}

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div style="display:flex;gap:10px;align-items:center;padding:8px 5px 20px"><div style="width:34px;height:34px;border-radius:50%;background:#2b8a62"></div><div><div class="side-title">FVL</div><div class="side-sub">Ingeniería Biomédica</div></div></div>',unsafe_allow_html=True)
    view=st.radio('', ['Inicio','Inventario','Ubicación en mapa','Mantenimiento','Reportes'], index=['Inicio','Inventario','Ubicación en mapa','Mantenimiento','Reportes'].index(st.session_state.get('view','Ubicación en mapa')))
    st.session_state.view=view

if not st.session_state.pausado: tick()

# ================= COMMON =================
def badge(s):
    return f'<span class="badge" style="background:{COL[s]}22;color:{COL[s]}">● {LABEL[s]}</span>'

def map_svg(service, equipment):
    parts=['<svg viewBox="0 0 640 420" width="100%" style="background:#fbfcfb;border:1px solid #dbe7e0;border-radius:10px">']
    for r in ROOMS[service]: parts.append(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" rx="4" fill="#fff" stroke="#b5c2bb" stroke-width="2"/><text x="{r["x"]+8}" y="{r["y"]+30}" font-size="11" fill="#7c8a83">{r["id"]}</text>')
    for r in ROOMS[service]: parts.append(f'<rect x="{r["cx"]-8}" y="{r["cy"]-7}" width="16" height="14" rx="3" fill="#0d4a33"/><text x="{r["cx"]}" y="{r["cy"]+3}" text-anchor="middle" font-size="8" fill="white" font-weight="700">R</text>')
    for e in equipment:
        d=e.get('det')
        if not d or not d.get('pos'):continue
        x,y=d['pos']['x'],d['pos']['y']; c=COL[d['status']]
        parts.append(f'<g transform="translate({x},{y})"><path d="M0,0 C-12,-12 -16,-20 -16,-30 A16,16 0 1,1 16,-30 C16,-20 12,-12 0,0 Z" fill="{c}" stroke="white" stroke-width="2"/><circle cx="0" cy="-30" r="5" fill="white"/><text x="0" y="-44" text-anchor="middle" font-size="10" fill="#1d2b25" font-weight="700">{e["codigo"]}</text></g>')
    parts.append('</svg>'); return ''.join(parts)

# ================= VIEWS =================
if view=='Ubicación en mapa':
    st.markdown('<div class="title">Ubicación de equipos</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,2]); service=c1.selectbox('Sede', ['Principal']); service=c2.selectbox('Servicio',list(ROOMS),index=list(ROOMS).index(st.session_state.get('service','UCI Adultos'))); st.session_state.service=service; q=c3.text_input('Buscar código o equipo…')
    all_eq=[e for e in st.session_state.equipos if e['servicio']==service]; eq=[e for e in all_eq if not q or q.lower() in (e['codigo']+' '+e['nombre']).lower()]
    total=len(st.session_state.equipos); ok=sum(status(e)=='ok' for e in st.session_state.equipos); dist=sum(status(e)=='verificar' for e in st.session_state.equipos); sin=total-ok-dist; readers=len(ROOMS[service])
    cols=st.columns(5)
    for col,val,lab in zip(cols,[total,round(ok/total*100),dist,sin,readers],['Equipos con etiqueta','Ubicación confirmada','Ubicación distinta','Sin lectura reciente','Lectores en el servicio']): col.markdown(f'<div class="chip"><div class="chipv">{val}{" %" if lab=="Ubicación confirmada" else ""}</div><div class="chipt">{lab}</div></div>',unsafe_allow_html=True)
    a,b,c=st.columns([1.2,1.7,1.3])
    with a:
        if st.button('⏸ Pausar lectores' if not st.session_state.pausado else '▶ Reanudar lectores',use_container_width=True): st.session_state.pausado=not st.session_state.pausado; st.rerun()
    with b:
        if st.button('Trasladar un equipo (simulado)',use_container_width=True): move_random(True); st.rerun()
    with c:
        if st.button('Sacar un equipo de cobertura',use_container_width=True): workshop(); st.rerun()
    limite=datetime(2026,11,6)+timedelta(days=7); critical=[e for e in st.session_state.equipos if e['proximo']<=limite and status(e)!='ok']
    if critical:
        items=''.join(f'<li><b>{e["codigo"]}</b> · preventivo en {(e["proximo"]-datetime(2026,11,6)).days} día(s) · {"sin lectura reciente" if status(e)=="sin" else "detectado en "+e["det"]["sala"]+", inventario "+e["sala"]}</li>' for e in critical)
        st.markdown(f'<div class="alert"><b style="color:#d7263d">Preventivo en 7 días sin ubicación confirmada ({len(critical)})</b><ul>{items}</ul></div>',unsafe_allow_html=True)
    else: st.markdown('<div class="alert okalert"><b style="color:#0d4a33">Sin alertas de preventivo.</b> Todos los equipos están localizados.</div>',unsafe_allow_html=True)
    left,right=st.columns([3,1.25])
    with left:
        st.markdown(f'<div class="card"><div class="section-title">{service} · Sede Principal</div>{map_svg(service,eq)}<div class="small" style="margin-top:8px">🟢 Coincide con inventario &nbsp; 🔴 Ubicación distinta &nbsp; ⚪ Sin lectura reciente &nbsp; ▪ Lector fijo</div></div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="section-title">Equipos del servicio</div></div>',unsafe_allow_html=True)
        options=['Selecciona un equipo']+[e['codigo'] for e in eq]; selected=st.selectbox('',options,key='mapselect'); st.session_state.selected=None if selected==options[0] else selected
        e=next((x for x in eq if x['codigo']==st.session_state.selected),None)
        if e:
            d=e.get('det') or {'status':'sin'}; st.markdown(f'<div class="card"><b style="font-size:1.05rem;color:#0d4a33">{e["codigo"]}</b><div class="small">{e["nombre"]} · {e["tipo"]}</div><br>{badge(d["status"])}<br><br><b>Tag</b> {e["tag"]}<br><b>Inventario</b> {e["sala"]}<br><b>Detectado en</b> {d.get("sala") or "—"}<br><b>Confianza</b> {d.get("conf",0):.1f} dB<br><b>Lecturas (20 s)</b> {d.get("lecturas",0)}<br><b>Próx. preventivo</b> {e["proximo"].strftime("%d %b %Y")}</div>',unsafe_allow_html=True)
            if d.get('status')=='verificar' and st.button('Actualizar inventario',type='primary'): e['sala']=d['sala']; st.rerun()
        st.markdown('<div class="card"><div class="section-title">Registro de eventos</div>'+''.join(f'<div class="logrow"><span class="small">{h}</span> {t}</div>' for h,t,_ in st.session_state.log[:12])+'</div>',unsafe_allow_html=True)
    with st.expander('Importar lecturas de lectores reales'):
        st.write('Formato: TAG,LECTOR,RSSI,FECHA. Ejemplo: TAG-BOM-0345,H4,-42,2026-11-06T10:15:00')
        txt=st.text_area('Lecturas',placeholder='TAG-BOM-0345,H4,-42')
        if st.button('Cargar ejemplo'): st.session_state.example='TAG-BOM-0345,H4,-41\nTAG-BOM-0345,H4,-43\nTAG-MON-0721,H3,-45\nTAG-DES-0052,TR3,-44'; st.rerun()
        if st.session_state.get('example'): st.code(st.session_state.example)
        if st.button('Procesar lecturas',type='primary') and txt:
            now=int(datetime.now().timestamp()*1000); good=bad=0
            for line in txt.splitlines():
                p=[x.strip() for x in line.replace(';',',').split(',')]
                try:
                    e=next(x for x in st.session_state.equipos if x['tag']==p[0]); rd=READERS[p[1]]; rssi=float(p[2]); tt=int(datetime.fromisoformat(p[3]).timestamp()*1000) if len(p)>3 else now; e['reads'].append({'reader':rd['id'],'rssi':rssi,'t':tt}); good+=1
                except Exception: bad+=1
            for e in st.session_state.equipos: detect(e,now)
            st.success(f'{good} lecturas procesadas'+(f', {bad} con formato no reconocido.' if bad else '.')); st.rerun()

elif view=='Inicio':
    st.markdown('<div class="title">Panel de control</div>',unsafe_allow_html=True)
    total=len(st.session_state.equipos); ok=sum(status(e)=='ok' for e in st.session_state.equipos); limite=datetime(2026,11,6)+timedelta(days=7); prox=[e for e in st.session_state.equipos if e['proximo']<=limite]; pct=round(sum(status(e)=='ok' for e in prox)/len(prox)*100) if prox else 100
    cs=st.columns(4)
    for col,v,t in zip(cs,[total,round(ok/total*100),pct,total-ok],['Equipos registrados','Con ubicación confirmada','Preventivos a 7 días con ubicación','Sin ubicación confirmada']): col.markdown(f'<div class="kpi"><div class="kpiv">{v} %</div><div class="kpit">{t}</div></div>',unsafe_allow_html=True) if '%' in t else col.markdown(f'<div class="kpi"><div class="kpiv">{v}</div><div class="kpit">{t}</div></div>',unsafe_allow_html=True)
    st.markdown('<br><div class="card"><div class="section-title">Ubicación confirmada por servicio</div>',unsafe_allow_html=True)
    for s in ROOMS:
        es=[e for e in st.session_state.equipos if e['servicio']==s]; p=round(sum(status(e)=='ok' for e in es)/len(es)*100); st.markdown(f'<div style="display:grid;grid-template-columns:170px 1fr 56px;gap:10px;align-items:center;margin-bottom:8px"><span>{s}</span><div class="bar"><div class="fill" style="width:{p}%"></div></div><b>{p}%</b></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="section-title">Próximos mantenimientos</div></div>',unsafe_allow_html=True)
    rows=sorted(st.session_state.equipos,key=lambda e:e['proximo'])[:6]
    import pandas as pd
    st.dataframe(pd.DataFrame([{'Código':e['codigo'],'Equipo':e['nombre'],'Servicio':e['servicio'],'Ubicación':LABEL[status(e)],'Preventivo':e['proximo'].strftime('%d %b %Y')} for e in rows]),use_container_width=True,hide_index=True)

elif view=='Inventario':
    st.markdown('<div class="title">Inventario de equipos</div>',unsafe_allow_html=True); q=st.text_input('Buscar código, equipo o servicio…'); rows=[e for e in st.session_state.equipos if not q or q.lower() in (e['codigo']+' '+e['nombre']+' '+e['servicio']+' '+e['sala']).lower()]
    import pandas as pd
    st.dataframe(pd.DataFrame([{'Código':e['codigo'],'Equipo':e['nombre'],'Servicio':e['servicio'],'Inventario':e['sala'],'Detectado':e.get('det',{}).get('sala','—'),'Estado':LABEL[status(e)],'Próx. preventivo':e['proximo'].strftime('%d %b %Y')} for e in rows]),use_container_width=True,hide_index=True)

elif view=='Mantenimiento':
    st.markdown('<div class="title">Mantenimiento preventivo</div>',unsafe_allow_html=True); month=st.selectbox('Mes',['Octubre 2026','Noviembre 2026'],index=1); m=9 if month.startswith('Oct') else 10; filt=st.radio('Mostrar',['Abiertas','Todas','Cerradas'],horizontal=True); ots=[o for o in st.session_state.ots if o['fechaProg'].month==m and (filt=='Todas' or (filt=='Abiertas' and not o['cierre']) or (filt=='Cerradas' and o['cierre']))]; ots.sort(key=lambda o:o['fechaProg'])
    import pandas as pd
    st.dataframe(pd.DataFrame([{'Orden':o['id'],'Fecha prog.':o['fechaProg'].strftime('%d %b %Y'),'Equipo':o['codigo'],'Ingeniero':o['ingeniero'],'Ubicación':LABEL[status(next(e for e in st.session_state.equipos if e['codigo']==o['codigo']))],'Estado':'Cerrada' if o['cierre'] else 'Abierta'} for o in ots[:80]]),use_container_width=True,hide_index=True)
    st.markdown('<div class="card"><div class="section-title">Desempeño por ingeniero</div></div>',unsafe_allow_html=True)
    engineers=['Ing. Laura Gómez','Ing. Andrés Ruiz','Tec. Camila Torres','Ing. Felipe Mora']; rows=[]
    for n in engineers:
        x=[o for o in st.session_state.ots if o['ingeniero']==n and o['cierre'] and o['cierre'].month==m]; rows.append({'Ingeniero':n,'Órdenes cerradas':len(x),'A tiempo':sum(o['cierre'].date()<=o['fechaProg'].date() for o in x),'Pendientes':sum(o['ingeniero']==n and not o['cierre'] and o['fechaProg'].month==m for o in st.session_state.ots),'Vencidas':sum(o['ingeniero']==n and not o['cierre'] and o['fechaProg']<datetime(2026,11,6) for o in st.session_state.ots)})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

elif view=='Reportes':
    st.markdown('<div class="title">Reportes</div>',unsafe_allow_html=True); total=len(st.session_state.equipos); ok=sum(status(e)=='ok' for e in st.session_state.equipos); dist=sum(status(e)=='verificar' for e in st.session_state.equipos); sin=sum(status(e)=='sin' for e in st.session_state.equipos)
    cs=st.columns(4)
    for col,v,t in zip(cs,[round(ok/total*100),total-ok,dist,sin],['Cumplimiento de ubicación','Equipos sin ubicación confirmada','Ubicación distinta al inventario','Sin lectura reciente']): col.markdown(f'<div class="kpi"><div class="kpiv">{v}{" %" if "Cumplimiento" in t else ""}</div><div class="kpit">{t}</div></div>',unsafe_allow_html=True)
    st.markdown('<br><div class="card"><div class="section-title">Cumplimiento por servicio</div>',unsafe_allow_html=True)
    for s in ROOMS:
        es=[e for e in st.session_state.equipos if e['servicio']==s]; p=round(sum(status(e)=='ok' for e in es)/len(es)*100); st.markdown(f'<div style="display:grid;grid-template-columns:170px 1fr 56px;gap:10px;align-items:center;margin-bottom:8px"><span>{s}</span><div class="bar"><div class="fill" style="width:{p}%"></div></div><b>{p}%</b></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    import pandas as pd
    bad=[e for e in st.session_state.equipos if status(e)!='ok']; st.dataframe(pd.DataFrame([{'Código':e['codigo'],'Equipo':e['nombre'],'Servicio':e['servicio'],'Inventario':e['sala'],'Detectado':e.get('det',{}).get('sala','—'),'Estado':LABEL[status(e)]} for e in bad]),use_container_width=True,hide_index=True)

# Note: Streamlit reruns preserve session state; use the pause button for deterministic simulation.
