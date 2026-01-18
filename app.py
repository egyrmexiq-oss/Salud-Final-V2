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
# --- PREPARACIÓN DE CONTEXTO (LÓGICA CORREGIDA) ---
if TODOS_LOS_MEDICOS:
    ciudades = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades.insert(0, "Todas las Ubicaciones")
    
    # Creamos la ficha técnica
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        ficha = f"ID: {m.get('nombre')} | Especialidad: {m.get('especialidad')} | Ubicación: {m.get('ciudad')} | Experiencia: {m.get('descripcion')}"
        info_medicos.append(ficha)
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    
    # CEREBRO HÍBRIDO (El que definimos hace un momento)
    INSTRUCCION_EXTRA = f"""
    ERES "QUANTUM HEALTH AI", UN CONSULTOR EXPERTO EN SALUD.
    
    TIENES 2 MODOS DE OPERACIÓN (DETECTA CUÁL USAR):

    MODO 1: CURIOSIDAD Y EDUCACIÓN 🧠
    Si el usuario hace preguntas generales (ej: "¿Qué es el colesterol?", "¿Por qué el cielo es azul?"), responde con calidad educativa. NO recomiendes doctores a menos que sea pertinente.

    MODO 2: TRIAGE Y SÍNTOMAS 🚑
    Si el usuario describe un DOLOR o SÍNTOMA (ej: "Me duele la cabeza"), ACTIVA EL PROTOCOLO:
    1. Analiza qué especialidad necesita.
    2. Busca EXCLUSIVAMENTE en esta lista:
    {TEXTO_DIRECTORIO}
    3. SI HAY COINCIDENCIA: Recomienda al doctor diciendo: "Te recomiendo al Dr. [Nombre]...".
    4. SI NO HAY COINCIDENCIA: Sugiere Médico General.
    """
else:
    ciudades = ["Mundo"]
    INSTRUCCION_EXTRA = "Actúa como asistente médico general. No tienes médicos en tu red por ahora."

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=100)
    st.title("Quantum Health")
    st.markdown("---")
    
    # 1. NAVEGACIÓN
    menu = st.radio("Navegación", ["🏠 Inicio", "👨‍⚕️ Directorio", "🤖 Asistente IA"])
    
    # 2. FILTROS
    st.markdown("---")
    st.subheader("📍 Ubicación")
    ciudad_filtro = st.selectbox("Selecciona tu ciudad:", ciudades)
    
    # BOTÓN DE REGISTRO
    st.markdown("---")
    st.markdown("### ¿Eres Especialista?")
    st.link_button("📝 Regístrate Aquí", URL_FORMULARIO)

    # 3. CONTROLES Y CONTADOR
    st.markdown("---")
    if st.button("Limpiar Chat"): st.session_state.mensajes = []; st.rerun()
    
    # CONTADOR DE VISITAS (Aquí estaba el error, ahora está protegido)
    st.markdown("### 📊 Métricas")
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="color: white; font-weight: bold; font-size: 1.1em;">Visitas:</span>
        <img src="https://api.visitorbadge.io/api/visitors?path=quantum-health-ai.com&label=&countColor=%2300C2FF&style=flat&labelStyle=none" style="height: 25px; border-radius: 3px;" />
    </div>
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
   # --- CONTADOR DE VISITAS (Corregido) ---
    st.markdown("---")
    
    # Fíjate que todo el HTML está dentro de las triples comillas """
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="color: white; font-weight: bold; font-size: 1.1em;">📊 Visitas:</span>
        <img src="https://api.visitorbadge.io/api/visitors?path=quantum-health-ai.com&label=&countColor=%2300C2FF&style=flat&labelStyle=none" style="height: 25px; border-radius: 3px;" />
    </div>
    """, unsafe_allow_html=True)
    
    # 2. DIRECTORIO
    st.markdown("---")
    st.markdown("### 👨‍⚕️ Especialistas")
    if TODOS_LOS_MEDICOS:
        filtro = st.selectbox("📍 Ciudad:", ciudades)
        lista = TODOS_LOS_MEDICOS if filtro == "Todas las Ubicaciones" else [m for m in TODOS_LOS_MEDICOS if str(m.get('ciudad')).title() == filtro]
        
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
