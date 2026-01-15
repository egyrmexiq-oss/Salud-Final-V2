import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import pandas as pd # Nuevo cerebro de datos

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="Logo_quantum.png", layout="wide")

# ==========================================
# 💎 CONEXIÓN A GOOGLE SHEETS (AUTOMATIZACIÓN)
# ==========================================

# ⚠️ PEGA AQUÍ EL ENLACE QUE OBTUVISTE AL "PUBLICAR COMO CSV":
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQGCfqt20Ny7i1f-Tk_RSApdEXk0-bDDK_a3vyRcUCcfPIGXHxe2J3MPInrdwJbeBfnLcQoer16uU9y/pub?output=csv"

@st.cache_data(ttl=60) # Actualiza datos cada 60 segundos
def cargar_medicos():
    try:
        # Leemos el Excel de internet
        df = pd.read_csv(URL_GOOGLE_SHEET)
        
        # Limpiamos nombres de columnas (quitar espacios extra y minúsculas)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Filtramos: Solo los que tengan "SI" en la columna 'aprobado'
        # Usamos .astype(str) para evitar errores si está vacía
        medicos_activos = df[df['aprobado'].astype(str).str.upper() == 'SI'].to_dict(orient='records')
        return medicos_activos
    except Exception as e:
        # Si falla (ej. internet), devolvemos lista vacía pero no rompemos la app
        return []

# Cargamos la lista real
TODOS_LOS_MEDICOS = cargar_medicos()

# --- LÓGICA DE FILTRADO ---
if TODOS_LOS_MEDICOS:
    # Obtenemos ciudades únicas de la lista cargada
    ciudades_disponibles = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades_disponibles.insert(0, "Todas las Ubicaciones")
else:
    ciudades_disponibles = ["Todas las Ubicaciones"]

# ==========================================
# 🎨 ESTILOS CSS
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .titulo-quantum {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 3em !important;
            color: #00C2FF !important;
            text-align: center !important;
            text-transform: uppercase;
            text-shadow: 0 0 10px #00C2FF, 0 0 20px #004e92;
            margin-bottom: 20px !important;
        }
        .medico-card {
            background-color: #0e1117;
            border: 1px solid #00C2FF;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
            box-shadow: 0 0 5px rgba(0, 194, 255, 0.2);
            text-align: center;
        }
        .contacto-dato {
            font-size: 1.1em;
            color: #ffffff;
            background: rgba(0, 194, 255, 0.1);
            padding: 8px;
            border-radius: 5px;
            margin-top: 10px;
            border: 1px dashed #00C2FF;
        }
        .cedula-badge {
            font-size: 0.7em;
            color: #aaa;
            border: 1px solid #444;
            padding: 2px 5px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None
if "saludo_inicial" not in st.session_state: st.session_state.saludo_inicial = False

# ==========================================
# 🔐 PANTALLA DE LOGIN ZEN
# ==========================================
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    # Usa tu enlace de Spline si lo tienes, aquí dejo uno genérico de ejemplo
    st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=500)
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", format="audio/mp3", loop=True)
    st.caption("🎵 Modo Zen: Activado.")
    
    input_code = st.text_input("Código de Acceso:", type="password")
    
    if st.button("Validar Acceso"):
        try:
            # Mantenemos las claves de acceso en secrets (más seguro)
            claves_validas = st.secrets["access_keys"]
            if input_code.strip() in claves_validas:
                st.session_state.usuario_activo = claves_validas[input_code.strip()]
                st.rerun()
            else:
                st.error("Código no válido.")
        except:
            st.error("Error de configuración.")
    st.stop()

# ==========================================
# 🚀 ZONA SEGURA (APP PRINCIPAL)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Falta API Key.")
    st.stop()

# --- PREPARACIÓN DE CONTEXTO IA ---
if TODOS_LOS_MEDICOS:
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        # Construimos la ficha para la IA
        remoto_txt = "Atiende Online" if str(m.get('remoto', '')).lower() in ['si', 'sí', 'yes', 'true'] else "Solo Presencial"
        info_medicos.append(f"- {m['nombre']} ({m['especialidad']}) en {m['ciudad']}. {remoto_txt}. Cédula: {m.get('cedula','N/A')}. Perfil: {m['descripcion']}")
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    INSTRUCCION_EXTRA = f"""
    TU MISIÓN COMERCIAL:
    Recomienda a estos especialistas de nuestra red si coinciden con el problema:
    {TEXTO_DIRECTORIO}
    Prioriza por ciudad si el usuario la menciona.
    """
else:
    INSTRUCCION_EXTRA = ""

DISCLAIMER_TEXTO = "\n\n⚠️ *AVISO LEGAL: Quantum AI Health proporciona información educativa. Consulta a un especialista.*"
SYSTEM_PROMPT = f"Eres QUANTUM, Asistente de Salud. {INSTRUCCION_EXTRA} Al final incluye el aviso legal."

if "mensajes" not in st.session_state: st.session_state.mensajes = []

# Saludo
if not st.session_state.saludo_inicial:
    st.session_state.mensajes.append({"role": "assistant", "content": f"Hola {st.session_state.usuario_activo}. ¿Cómo te sientes hoy? 🌿"})
    st.session_state.saludo_inicial = True

def crear_pdf(mensajes):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt="Resumen Quantum AI", ln=1, align='C'); pdf.ln(5)
    for m in mensajes:
        txt = m['content'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, txt=f"{m['role'].upper()}: {txt}"); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL ---
with st.sidebar:
    # Tu Logo
    try: st.image("Logo_quantum.png", use_container_width=True)
    except: st.markdown("## QUANTUM")
    
    st.success(f"👤 {st.session_state.usuario_activo}")
    if st.button("Cerrar Sesión"):
        st.session_state.usuario_activo = None; st.session_state.mensajes = []; st.rerun()

    st.markdown("---")
    # RECLUTAMIENTO (Botón Nuevo)
    st.markdown("### 💼 Únete al Equipo")
    st.caption("¿Eres médico? Recibe pacientes.")
    # CAMBIA ESTE LINK POR TU FORMULARIO REAL:
    st.link_button("📝 Registro de Especialistas", "https://forms.gle/TU_LINK_AQUI")
    
    st.markdown("---")
    st.markdown("### ⚙️ Panel")
    nivel = st.radio("Nivel:", ["Básica", "Experta"])
    c1, c2 = st.columns(2)
    if c1.button("Limpiar"): st.session_state.mensajes = []; st.rerun()
    if st.session_state.mensajes:
        c2.download_button("PDF", data=crear_pdf(st.session_state.mensajes), file_name="Quantum.pdf", mime="application/pdf")

    st.markdown("---")
    
    # DIRECTORIO DESDE GOOGLE SHEETS
    if TODOS_LOS_MEDICOS:
        st.markdown("### 👨‍⚕️ Red de Especialistas")
        
        filtro_ciudad = st.selectbox("📍 Ubicación:", ciudades_disponibles)
        
        if filtro_ciudad == "Todas las Ubicaciones": medicos_filtrados = TODOS_LOS_MEDICOS
        else: medicos_filtrados = [m for m in TODOS_LOS_MEDICOS if str(m.get('ciudad')).title() == filtro_ciudad]
        
        if medicos_filtrados:
            if "idx_med" not in st.session_state: st.session_state.idx_med = 0
            if "idx_con" not in st.session_state: st.session_state.idx_con = 0
            
            # Navegación circular
            m_actual = medicos_filtrados[st.session_state.idx_med % len(medicos_filtrados)]
            
            st.markdown(f"""
            <div class="medico-card">
                <strong>{m_actual['nombre']}</strong><br>
                <span style="color: #00C2FF;">{m_actual['especialidad']}</span><br>
                <small>📍 {m_actual['ciudad']}, {m_actual['colonia']}</small><br>
                <div class="cedula-badge">Cédula: {m_actual.get('cedula', 'Verificada')}</div>
                <hr style="border-color: #333; margin: 5px 0;">
                <small style="color: #bbb;">{m_actual['descripcion']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Contactos
            contactos = [
                {"i": "📞", "t": "Teléfono", "v": m_actual['telefono']},
                {"i": "💬", "t": "WhatsApp", "v": m_actual['whatsapp']},
                {"i": "✉️", "t": "Email", "v": m_actual['email']},
                {"i": "🌐", "t": "Web", "v": m_actual['web']}
            ]
            # Filtramos contactos vacíos
            contactos = [c for c in contactos if pd.notna(c['v']) and str(c['v']) != 'nan']
            
            if contactos:
                c_act = contactos[st.session_state.idx_con % len(contactos)]
                col_L, col_C, col_R = st.columns([1,4,1])
                with col_L: 
                    if st.button("◀", key="cp"): st.session_state.idx_con -= 1; st.rerun()
                with col_C:
                    st.markdown(f"<div style='text-align:center'><small>{c_act['i']} {c_act['t']}</small><div class='contacto-dato'>{c_act['v']}</div></div>", unsafe_allow_html=True)
                with col_R:
                    if st.button("▶", key="cn"): st.session_state.idx_con += 1; st.rerun()
            
            st.markdown("---")
            nav1, nav2 = st.columns(2)
            if nav1.button("⬅️ Anterior"): st.session_state.idx_med -= 1; st.session_state.idx_con = 0; st.rerun()
            if nav2.button("Siguiente ➡️"): st.session_state.idx_med += 1; st.session_state.idx_con = 0; st.rerun()
            
            st.caption(f"Socio {(st.session_state.idx_med % len(medicos_filtrados)) + 1} de {len(medicos_filtrados)}")
        else:
            st.info("No hay médicos en esta zona.")

# --- CHAT ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    try:
        full_prompt = f"{SYSTEM_PROMPT}\nNivel: {nivel}. Pregunta: {prompt}"
        model = genai.GenerativeModel('gemini-2.5-flash')
        with st.spinner("Procesando..."):
            res = model.generate_content(full_prompt)
            st.session_state.mensajes.append({"role": "assistant", "content": res.text + DISCLAIMER_TEXTO})
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("**Quantum AI Health v4.0** | © 2026")
