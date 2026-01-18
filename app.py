import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="Logo_quantum.png", layout="wide")

# ==========================================
# 🔐 1. LOGIN (EL PORTERO VA PRIMERO)
# ==========================================
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    try: st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=400)
    except: pass
    
    # Música de fondo (Opcional)
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", loop=True)
    
    c = st.text_input("Clave de Acceso:", type="password")
    if st.button("Entrar"):
        if c.strip() in st.secrets["access_keys"]:
            st.session_state.usuario_activo = st.secrets["access_keys"][c.strip()]
            st.rerun()
        else: st.error("Acceso Denegado")
    st.stop() # 🛑 AQUÍ SE DETIENE TODO SI NO HAY LOGIN

# ==========================================
# 💎 2. VARIABLES Y CONEXIÓN (SOLO SI YA ENTRÓ)
# ==========================================

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1sLchuJZ-P3CrCStgYq__q3dTqFUBig-WaDquCAcG4xUmbVtbBywII7tv5URMQC9gUb1foG5kyeIi/pub?gid=1579037376&single=true&output=csv"
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSdvLcp8q9kbJ2VAkqdSHFBreD3yCqimuXRt-OuOykJCoMj2Tg/viewform?usp=publish-editor"

@st.cache_data(ttl=60)
def cargar_medicos():
    try:
        df = pd.read_csv(URL_GOOGLE_SHEET)
        df.columns = [c.strip().lower() for c in df.columns]
        
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

# --- PREPARACIÓN DE CONTEXTO E IA ---
if TODOS_LOS_MEDICOS:
    ciudades = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades.insert(0, "Todas las Ubicaciones")
    
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        ficha = f"ID: {m.get('nombre')} | Especialidad: {m.get('especialidad')} | Ubicación: {m.get('ciudad')} | Experiencia: {m.get('descripcion')}"
        info_medicos.append(ficha)
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    
    # CEREBRO HÍBRIDO (El bueno)
    INSTRUCCION_EXTRA = f"""
    ERES "QUANTUM HEALTH AI", UN CONSULTOR EXPERTO EN SALUD.
    
    TIENES 2 MODOS DE OPERACIÓN (DETECTA CUÁL USAR):

    MODO 1: CURIOSIDAD Y EDUCACIÓN 🧠
    Si el usuario hace preguntas generales (ej: "¿Qué es el colesterol?", "¿Por qué el cielo es azul?"), responde con calidad educativa. NO recomiendes doctores a menos que sea pertinente.

    MODO 2: TRIAGE Y SÍNTOMAS 🚑
    Si el usuario describe un DOLOR o SÍNTOMA (ej: "Me duele la cabeza"), ACTIVA EL PROTOCOLO:
    1. Analiza qué especialista necesita.
    2. Busca EXCLUSIVAMENTE en esta lista:
    {TEXTO_DIRECTORIO}
    3. SI HAY COINCIDENCIA: Recomienda al doctor diciendo: "Te recomiendo al Dr. [Nombre]...".
    4. SI NO HAY COINCIDENCIA: Sugiere Médico General.
    """
else:
    ciudades = ["Mundo"]
    INSTRUCCION_EXTRA = "Actúa como asistente médico general. No tienes médicos en tu red por ahora."

# ==========================================
# 🖥️ 3. INTERFAZ GRÁFICA (APP)
# ==========================================

try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except: st.error("Falta API Key")

if "mensajes" not in st.session_state: 
    st.session_state.mensajes = [{"role": "assistant", "content": f"Hola {st.session_state.usuario_activo}. ¿En qué te ayudo hoy?"}]

# --- BARRA LATERAL ÚNICA Y ORDENADA ---
with st.sidebar:
    # Logo
    try: st.image("Logo_quantum.png", use_container_width=True)
    except: st.header("QUANTUM HEALTH")
    
    st.success(f"Usuario: {st.session_state.usuario_activo}")
    st.markdown("---")

    # 1. Configuración de IA
    st.markdown("### 🧠 Configuración")
    nivel = st.radio("Nivel de Respuesta:", ["Básica", "Media", "Experta"])
    
    # 2. Directorio Médico
    st.markdown("---")
    st.markdown("### 👨‍⚕️ Directorio")
    if TODOS_LOS_MEDICOS:
        filtro = st.selectbox("📍 Filtrar Ciudad:", ciudades)
        lista = TODOS_LOS_MEDICOS if filtro == "Todas las Ubicaciones" else [m for m in TODOS_LOS_MEDICOS if str(m.get('ciudad')).title() == filtro]
        
        if lista:
            if "idx" not in st.session_state: st.session_state.idx = 0
            m = lista[st.session_state.idx % len(lista)]
            
            # Tarjeta del Médico
            st.markdown(f"""
            <div style="background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #444;">
                <h4 style="margin:0; color:white;">{m.get('nombre','Dr.')}</h4>
                <div style="color:#00C2FF; font-weight:bold;">{m.get('especial
