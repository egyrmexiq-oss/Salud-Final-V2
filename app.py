import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# --- ESTILOS CSS (TIPOGRAFÍA FUTURISTA) ---
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
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO (LOGIN) ---
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

# --- PANTALLA DE LOGIN (VERSIÓN CINEMÁTICA) ---
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    
    # ---------------------------------------------------------
    # 🎥 VIDEO DE FONDO (CEREBRO DIGITAL)
    # ---------------------------------------------------------
    
    # Usamos HTML para mostrar un video en bucle (loop), mudo y auto-reproducible.
    # Este video es una red neuronal azul que combina con tu marca.
    video_html = """
    <style>
        .video-container {
            display: flex;
            justify_content: center;
            margin-bottom: 20px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 0 20px #00C2FF; /* Resplandor Azul Quantum */
        }
        video {
            width: 100%;
            max-width: 700px;
            border-radius: 15px;
        }
    </style>
    <div class="video-container">
        <video autoplay loop muted playsinline>
            <source src="https://cdn.pixabay.com/video/2019/04/20/22908-331569022_large.mp4" type="video/mp4">
            Tu navegador no soporta video.
        </video>
    </div>
    """
    st.markdown(video_html, unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    
    st.caption("Sistema de Inteligencia Artificial Avanzada")
    st.info("Introduce tu Código de Acceso Personal.")
    
    input_code = st.text_input("Código de Tarjeta / Clave:", type="password")
    
    if st.button("Validar Acceso"):
        try:
            codigo_usuario = input_code.strip()
            claves_validas = st.secrets["access_keys"]
            
            if codigo_usuario in claves_validas:
                nombre_cliente = claves_validas[codigo_usuario]
                st.session_state.usuario_activo = nombre_cliente
                st.toast(f"✅ Bienvenido, {nombre_cliente}", icon="🎉")
                st.rerun()
            else:
                st.error(f"🚫 El código '{codigo_usuario}' no es válido.")
        except Exception as e:
            st.error(f"⚠️ Error verificando claves: {e}")
            st.info("Asegúrate de configurar [access_keys] en los Secrets.")
    
    st.stop()

# ==========================================
# 🚀 ZONA SEGURA - QUANTUM APP
# ==========================================

# --- CONEXIÓN API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY.")
    st.stop()

SYSTEM_PROMPT = """
Eres QUANTUM, un Asistente Experto en Salud.
REGLA DE ORO: En TODAS tus respuestas incluye al final: "⚠️ IMPORTANTE: No soy un profesional de la salud. Información educativa. Acuda a un médico."
Tu tono y profundidad dependen del nivel seleccionado.
"""

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- FUNCIÓN PDF ---
def crear_pdf(mensajes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt="Resumen de Consulta - QUANTUM AI", ln=1, align='C')
    pdf.ln(5)
    for m in mensajes:
        rol = "USUARIO" if m["role"] == "user" else "QUANTUM"
        try: texto_limpio = m['content'].encode('latin-1', 'replace').decode('latin-1')
        except: texto_limpio = m['content']
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, txt=f"{rol}:", ln=1)
        pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 6, txt=texto_limpio); pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00C2FF;'>🧬 QUANTUM</h2>", unsafe_allow_html=True)
    st.success(f"👤 {st.session_state.usuario_activo}")
    
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.usuario_activo = None
        st.session_state.mensajes = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 1. Validación")
    acepta_terminos = st.checkbox("Acepto los términos de uso médico.")
    
    if acepta_terminos:
        st.markdown("### 2. Configuración")
        nivel = st.radio("Nivel:", ["Básica", "Media", "Experta"])
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("Limpiar"):
            st.session_state.mensajes = []; st.rerun()
        if st.session_state.mensajes:
            pdf_bytes = crear_pdf(st.session_state.mensajes)
            c2.download_button("PDF", data=pdf_bytes, file_name="Quantum.pdf", mime="application/pdf")

# --- APP PRINCIPAL ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

if not acepta_terminos:
    st.info(f"Hola {st.session_state.usuario_activo}. Valida el aviso legal para comenzar.")
    try: st.image("image_143480.png", use_container_width=True)
    except: st.image("https://cdn.pixabay.com/photo/2018/05/08/08/44/artificial-intelligence-3382507_1280.jpg", use_container_width=True)
else:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input(f"Consultar ({nivel})...")
    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)
        try:
            prompt_completo = f"{SYSTEM_PROMPT}\nCONTEXTO: Nivel {nivel}. Pregunta: {prompt}"
            model = genai.GenerativeModel('gemini-2.5-flash')
            with st.spinner("Procesando..."):
                response = model.generate_content(prompt_completo)
                texto_ia = response.text
            st.session_state.mensajes.append({"role": "assistant", "content": texto_ia})
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# --- PIE DE PÁGINA (FOOTER) ---
st.markdown("---")
col_foot1, col_foot2 = st.columns(2)

with col_foot1:
    st.markdown("**Quantum AI Health v2.0**")
    st.caption("© 2026 Todos los derechos reservados.")

with col_foot2:
    st.markdown("Estadísticas de uso:")
    # Usamos el mismo identificador (page_id) para que sume al mismo contador
    st.markdown("![Visitas](https://visitor-badge.laobi.icu/badge?page_id=quantum_ai_health_main_access&left_text=Total&right_color=%2300C2FF)")
