import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import time  # <--- IMPORTANTE: Necesitamos esto para el truco anti-caché

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

# --- PANTALLA DE LOGIN ---
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    
    # --- CONTADOR ANTI-CACHÉ ---
    # Usamos time.time() para crear un número único cada vez. 
    # Esto obliga al navegador a actualizar la imagen.
    ts = int(time.time())
    st.markdown(f"[![Visitas](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fquantum-health-app-v2&count_bg=%2300C2FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=VISITAS&edge_flat=false&dummy={ts})](https://hits.seeyoufarm.com)")
    
    st.caption("Profesionales conectados globalmente")
    
    st.info("Introduce tu Código de Acceso Personal para iniciar sesión.")
    
    input_code = st.text_input("Código de Tarjeta / Clave:", type="password")
    
    if st.button("Validar Acceso"):
        try:
            codigo_usuario = input_code.strip()
            claves_validas = st.secrets["access_keys"]
            
            if codigo_usuario in claves_validas:
                nombre_cliente = claves_validas[codigo_usuario]
                st.session_state.usuario_activo = nombre_cliente
                st.toast(f"✅ Bienvenido, {nombre_cliente}", icon="🎉")
                time.sleep(1) # Pequeña pausa para ver el mensaje
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
# Título con estilo futurista
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
    # Truco anti-caché también en el footer
    ts_foot = int(time.time())
    st.markdown(f"![Total](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fquantum-health-app-v2&count_bg=%2300C2FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=TOTAL&edge_flat=false&dummy={ts_foot})")
