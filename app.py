import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="Logo_quantum.png", layout="wide")

# ==========================================
# 💎 CONEXIÓN ROBUSTA A GOOGLE SHEETS
# ==========================================
# ✅ AQUÍ YA PUSE TU ENLACE CSV REAL:
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQGCfqt20Ny7i1f-Tk_RSApdEXk0-bDDK_a3vyRcUCcfPIGXHxe2J3MPInrdwJbeBfnLcQoer16uU9y/pub?output=csv"

# ⚠️ IMPORTANTE: PEGA AQUÍ EL LINK DE TU GOOGLE FORM (Para reclutar médicos)
URL_FORMULARIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQGCfqt20Ny7i1f-Tk_RSApdEXk0-bDDK_a3vyRcUCcfPIGXHxe2J3MPInrdwJbeBfnLcQoer16uU9y/pub?output=csv" 

@st.cache_data(ttl=60)
def cargar_medicos():
    try:
        df = pd.read_csv(URL_GOOGLE_SHEET)
        
        # 1. Normalizar nombres de columnas (todo minúsculas)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # 2. Mapeo Inteligente (Para que reconozca "Cedula profesional" como "cedula")
        mapa_columnas = {}
        for col in df.columns:
            if "nombre" in col: mapa_columnas[col] = "nombre"
            elif "especialidad" in col: mapa_columnas[col] = "especialidad"
            elif "descripci" in col: mapa_columnas[col] = "descripcion"
            elif "tel" in col: mapa_columnas[col] = "telefono"
            elif "whats" in col: mapa_columnas[col] = "whatsapp"
            elif "mail" in col or "correo" in col: mapa_columnas[col] = "email"
            elif "web" in col: mapa_columnas[col] = "web"
            elif "ciudad" in col: mapa_columnas[col] = "ciudad"
            elif "colonia" in col: mapa_columnas[col] = "colonia"
            elif "remoto" in col: mapa_columnas[col] = "remoto"
            elif "cedula" in col or "cédula" in col: mapa_columnas[col] = "cedula"
            elif "aprobado" in col: mapa_columnas[col] = "aprobado"
            
        df = df.rename(columns=mapa_columnas)
        
        # 3. Filtrar solo APROBADOS (Busca "SI" en la columna aprobado)
        if 'aprobado' in df.columns:
            medicos_activos = df[df['aprobado'].astype(str).str.upper().str.contains('SI')].to_dict(orient='records')
            return medicos_activos
        else:
            return [] 
            
    except Exception as e:
        # Si falla, no mostramos error feo, solo lista vacía
        return []

TODOS_LOS_MEDICOS = cargar_medicos()

# --- PREPARACIÓN DE CONTEXTO ---
if TODOS_LOS_MEDICOS:
    # Obtenemos ciudades únicas
    ciudades_disponibles = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades_disponibles.insert(0, "Todas las Ubicaciones")
    
    # Creamos texto para la IA
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        remoto_txt = "Atiende Online" if str(m.get('remoto', '')).lower() in ['si', 'sí', 'yes', 'true'] else "Solo Presencial"
        info_medicos.append(f"- {m.get('nombre','Dr.')} ({m.get('especialidad','General')}) en {m.get('ciudad','Mx')}. {remoto_txt}. Cédula: {m.get('cedula','En trámite')}. Perfil: {m.get('descripcion','')}")
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    INSTRUCCION_EXTRA = f"Recomienda especialistas de esta lista si aplica: {TEXTO_DIRECTORIO}"
else:
    ciudades_disponibles = ["Mundo"]
    INSTRUCCION_EXTRA = ""

# ==========================================
# 🎨 ESTILOS (CSS)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .titulo-quantum {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 2.5em !important;
            color: #00C2FF !important;
            text-align: center !important;
            text-shadow: 0 0 10px #00C2FF;
        }
        .medico-card {
            background-color: #111;
            border: 1px solid #00C2FF;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
        }
        .cedula-badge {
            background-color: #222; color: #ccc;
            padding: 2px 8px; border-radius: 4px;
            font-size: 0.8em; border: 1px solid #555;
            display: inline-block; margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    try:
        st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=400)
    except:
        st.info("Sistema Cuántico Iniciando...")
        
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", format="audio/mp3", loop=True)
    
    code = st.text_input("Código de Acceso:", type="password")
    if st.button("Entrar"):
        keys = st.secrets["access_keys"]
        if code.strip() in keys:
            st.session_state.usuario_activo = keys[code.strip()]
            st.rerun()
        else:
            st.error("Acceso Denegado")
    st.stop()

# --- APP PRINCIPAL ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("Falta API Key.")

if "mensajes" not in st.session_state: 
    st.session_state.mensajes = []
    st.session_state.mensajes.append({"role": "assistant", "content": f"Hola {st.session_state.usuario_activo}, soy Quantum. ¿En qué puedo ayudarte hoy?"})

# --- BARRA LATERAL (MENU LIMPIO) ---
with st.sidebar:
    try: st.image("Logo_quantum.png", use_container_width=True)
    except: st.header("QUANTUM")
    
    st.success(f"Hola, {st.session_state.usuario_activo}")
    
    # 1. DIRECTORIO
    st.markdown("---")
    st.markdown("### 👨‍⚕️ Directorio")
    
    if TODOS_LOS_MEDICOS:
        ciud = st.selectbox("📍 Ciudad:", ciudades_disponibles)
        if ciud == "Todas las Ubicaciones": filtrados = TODOS_LOS_MEDICOS
        else: filtrados = [m for m in TODOS_LOS_MEDICOS if str(m.get('ciudad')).title() == ciud]
        
        if filtrados:
            if "idx" not in st.session_state: st.session_state.idx = 0
            m = filtrados[st.session_state.idx % len(filtrados)]
            
            st.markdown(f"""
            <div class="medico-card">
                <h3 style="margin:0; color:white;">{m.get('nombre','Dr.')}</h3>
                <div style="color:#00C2FF; font-weight:bold;">{m.get('especialidad','Especialista')}</div>
                <div class="cedula-badge">Cédula: {m.get('cedula','--')}</div>
                <p style="font-size:0.9em; color:#aaa; margin-top:5px;">{m.get('descripcion','Sin descripción')}</p>
                <div style="margin-top:10px; border-top:1px dashed #333; padding-top:5px;">
                    📞 {m.get('telefono','--')}<br>
                    💬 {m.get('whatsapp','--')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("⬅️", use_container_width=True): st.session_state.idx -= 1; st.rerun()
            if c2.button("➡️", use_container_width=True): st.session_state.idx += 1; st.rerun()
            st.caption(f"{len(filtrados)} encontrados.")
        else:
            st.info("No hay médicos aquí.")
    else:
        st.warning("Directorio vacío (Revisa Excel 'aprobado').")

    # 2. SECCIÓN ÚNETE
    st.markdown("---")
    st.markdown("### 💼 ¿Eres Médico?")
    st.link_button("📝 Regístrate Aquí", URL_FORMULARIO) 

    # 3. CONTROLES
    st.markdown("---")
    if st.button("Limpiar Chat"): st.session_state.mensajes = []; st.rerun()
    if st.button("Salir"): st.session_state.usuario_activo = None; st.rerun()

# --- CHAT CENTRAL ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Consulta aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    try:
        full_promt = f"Eres un asistente médico experto. {INSTRUCCION_EXTRA} Responde a: {prompt}. Termina con: ⚠️ Info educativa, acuda al médico."
        model = genai.GenerativeModel('gemini-2.5-flash')
        res = model.generate_content(full_promt)
        st.session_state.mensajes.append({"role": "assistant", "content": res.text})
        st.rerun()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
