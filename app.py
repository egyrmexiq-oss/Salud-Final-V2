import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="Logo_quantum.png", layout="wide")

# ==========================================
# 💎 VARIABLES DE CONEXIÓN
# ==========================================

# 1. ESTE ES EL ENLACE DE DATOS (EL CSV) - NO LO TOQUES, YA ESTÁ BIEN:
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1sLchuJZ-P3CrCStgYq__q3dTqFUBig-WaDquCAcG4xUmbVtbBywII7tv5URMQC9gUb1foG5kyeIi/pub?gid=1579037376&single=true&output=csv"

# 2. ⚠️ AQUÍ PEGA EL ENLACE DEL FORMULARIO (El que sacas del botón "Enviar" 🔗):
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSdvLcp8q9kbJ2VAkqdSHFBreD3yCqimuXRt-OuOykJCoMj2Tg/viewform?usp=publish-editor" 
# ^^^ REEMPLAZA ESTO CON TU LINK DE FORMS (ej: https://forms.gle/xyz...) ^^^

@st.cache_data(ttl=60)
def cargar_medicos():
    try:
        df = pd.read_csv(URL_GOOGLE_SHEET)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Mapeo para corregir nombres de columnas
        mapa = {}
        for col in df.columns:
            if "nombre" in col: mapa[col] = "nombre"
            elif "especialidad" in col: mapa[col] = "especialidad"
            elif "descripci" in col: mapa[col] = "descripcion"
            elif "tel" in col: mapa[col] = "telefono"
            elif "whats" in col: mapa[col] = "whatsapp"
            elif "mail" in col or "correo" in col: mapa[col] = "email"
            elif "web" in col: mapa[col] = "web"
            elif "ciudad" in col: mapa[col] = "ciudad"
            elif "colonia" in col: mapa[col] = "colonia"
            elif "remoto" in col: mapa[col] = "remoto"
            elif "cedula" in col or "cédula" in col: mapa[col] = "cedula"
            elif "aprobado" in col: mapa[col] = "aprobado"
            
        df = df.rename(columns=mapa)
        
        if 'aprobado' in df.columns:
            return df[df['aprobado'].astype(str).str.upper().str.contains('SI')].to_dict(orient='records')
        return []
    except: return []

TODOS_LOS_MEDICOS = cargar_medicos()

# --- PREPARACIÓN IA ---
if TODOS_LOS_MEDICOS:
    ciudades = sorted(list(set(str(m.get('ciudad', 'Gral')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades.insert(0, "Todas las Ubicaciones")
    info_medicos = [f"- {m.get('nombre')} ({m.get('especialidad')}) en {m.get('ciudad')}. Cédula: {m.get('cedula')}. {m.get('descripcion')}" for m in TODOS_LOS_MEDICOS]
    INSTRUCCION_EXTRA = f"Recomienda doctores de esta lista: {str(info_medicos)}"
else:
    ciudades = ["Mundo"]
    INSTRUCCION_EXTRA = ""

# --- ESTILOS CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .titulo-quantum { font-family: 'Orbitron', sans-serif !important; color: #00C2FF !important; text-align: center; font-size: 2.5em; }
        .medico-card { background-color: #111; border: 1px solid #00C2FF; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
        .cedula-badge { background: #222; color: #aaa; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; border: 1px solid #555; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    try: st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=400)
    except: pass
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", loop=True)
    c = st.text_input("Clave:", type="password")
    if st.button("Entrar"):
        if c.strip() in st.secrets["access_keys"]:
            st.session_state.usuario_activo = st.secrets["access_keys"][c.strip()]
            st.rerun()
        else: st.error("Incorrecto")
    st.stop()

# --- APP ---
try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except: st.error("Falta API Key")

if "mensajes" not in st.session_state: 
    st.session_state.mensajes = [{"role": "assistant", "content": f"Hola {st.session_state.usuario_activo}. ¿En qué te ayudo?"}]

# --- BARRA LATERAL (CORREGIDA) ---
with st.sidebar:
    try: st.image("Logo_quantum.png", use_container_width=True)
    except: st.header("QUANTUM")
    st.success(f"Hola, {st.session_state.usuario_activo}")

    # 1. CONFIGURACIÓN (Aquí volvió el Nivel) ✅
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    nivel = st.radio("Nivel de Respuesta:", ["Básica", "Media", "Experta"]) # RESTAURADO
    
    if st.button("🗑️ Limpiar Chat"): st.session_state.mensajes = []; st.rerun()
    if st.button("🔒 Salir"): st.session_state.usuario_activo = None; st.rerun()
  # --- CONTADOR COMPACTO (En una sola línea) ---
    st.markdown("---")
    
    # Usamos HTML para poner el texto y la imagen lado a lado (Flexbox)
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="color: white; font-weight: bold; font-size: 1.1em;">📊 Visitas:</span>
        <img src="https://api.visitorbadge.io/api/visitors?path=quantum-health-ai.com&label=&countColor=%2300C2FF&style=flat&labelStyle=none" style="height: 25px; border-radius: 3px;" />
    </div>
    """, unsafe_allow_html=True)
    # 2. DIRECTORIO
    st.markdown("---")
    st.markdown("### 👨‍⚕️ Especialistas")
    # --- PREPARACIÓN DE CONTEXTO (Modo Triaje Inteligente) ---
if TODOS_LOS_MEDICOS:
    ciudades_disponibles = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades_disponibles.insert(0, "Todas las Ubicaciones")
    
    # Formateamos la lista para que la IA entienda quién es quién
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        # Creamos una ficha técnica clara para la IA
        ficha = f"ID: {m.get('nombre')} | Especialidad: {m.get('especialidad')} | Ubicación: {m.get('ciudad')} | Experiencia: {m.get('descripcion')}"
        info_medicos.append(ficha)
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    
    # 🧠 AQUÍ ESTÁ EL CEREBRO DEL TRIAGE
    INSTRUCCION_EXTRA = f"""
    ACTÚA COMO UN ASISTENTE DE TRIAGE MÉDICO EXPERTO.
    Tu misión es escuchar los síntomas del usuario y conectarlo con el especialista MÁS ADECUADO de esta lista exclusiva:
    
    {TEXTO_DIRECTORIO}
    
    REGLAS DE OPERACIÓN:
    1. ANALIZA los síntomas (ej: "dolor de pecho" -> Cardiología).
    2. BUSCA en la lista de arriba si tenemos un especialista que cubra esa necesidad.
    3. SI LO ENCUENTRAS: Recomiéndalo con entusiasmo diciendo: "Basado en tus síntomas, la mejor opción en nuestra red es el Dr. [Nombre]...".
    4. SI NO LO ENCUENTRAS: Di "Para ese síntoma necesitas un [Especialidad], pero por ahora no tenemos uno en nuestra red. Te sugiero acudir a un Médico General para valoración inicial".
    5. SIEMPRE prioriza la seguridad del paciente.
    """
else:
    ciudades_disponibles = ["Mundo"]
    INSTRUCCION_EXTRA = "Actúa como asistente médico general. No tienes médicos en tu red por ahora."
    
    # Formateamos la lista para que la IA entienda quién es quién
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        # Creamos una ficha técnica clara para la IA
        ficha = f"ID: {m.get('nombre')} | Especialidad: {m.get('especialidad')} | Ubicación: {m.get('ciudad')} | Experiencia: {m.get('descripcion')}"
        info_medicos.append(ficha)
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    
    # 🧠 AQUÍ ESTÁ EL CEREBRO DEL TRIAGE
    INSTRUCCION_EXTRA = f"""
    ACTÚA COMO UN ASISTENTE DE TRIAGE MÉDICO EXPERTO.
    Tu misión es escuchar los síntomas del usuario y conectarlo con el especialista MÁS ADECUADO de esta lista exclusiva:
    
    {TEXTO_DIRECTORIO}
    
    REGLAS DE OPERACIÓN:
    1. ANALIZA los síntomas (ej: "dolor de pecho" -> Cardiología).
    2. BUSCA en la lista de arriba si tenemos un especialista que cubra esa necesidad.
    3. SI LO ENCUENTRAS: Recomiéndalo con entusiasmo diciendo: "Basado en tus síntomas, la mejor opción en nuestra red es el Dr. [Nombre]...".
    4. SI NO LO ENCUENTRAS: Di "Para ese síntoma necesitas un [Especialidad], pero por ahora no tenemos uno en nuestra red. Te sugiero acudir a un Médico General para valoración inicial".
    5. SIEMPRE prioriza la seguridad del paciente.
    """
else:
    ciudades_disponibles = ["Mundo"]
    INSTRUCCION_EXTRA = "Actúa como asistente médico general. No tienes médicos en tu red por ahora."
        
        if lista:
            if "idx" not in st.session_state: st.session_state.idx = 0
            m = lista[st.session_state.idx % len(lista)]
            
            st.markdown(f"""
            <div class="medico-card">
                <h4 style="margin:0; color:white;">{m.get('nombre','Dr.')}</h4>
                <div style="color:#00C2FF;">{m.get('especialidad')}</div>
                <div class="cedula-badge">Cédula: {m.get('cedula','--')}</div>
                <small style="display:block; margin-top:5px; color:#bbb;">{m.get('descripcion')}</small>
                <div style="margin-top:10px; border-top:1px dashed #333; padding-top:5px;">
                    📞 {m.get('telefono','--')}<br>💬 {m.get('whatsapp','--')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("⬅️"): st.session_state.idx -= 1; st.rerun()
            if c2.button("➡️"): st.session_state.idx += 1; st.rerun()
        else: st.info("Sin resultados.")
    else: st.warning("Directorio vacío.")

    # 3. RECLUTAMIENTO
    st.markdown("---")
    st.markdown("### 💼 ¿Eres Médico?")
    st.link_button("📝 Regístrate Aquí", URL_FORMULARIO) # AHORA SÍ ABRIRÁ EL FORM

# --- CHAT ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    try:
        full = f"Eres Quantum (Nivel: {nivel}). {INSTRUCCION_EXTRA}. Usuario: {prompt}. FIN: ⚠️ Info educativa."
        res = genai.GenerativeModel('gemini-2.5-flash').generate_content(full)
        st.session_state.mensajes.append({"role": "assistant", "content": res.text})
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

