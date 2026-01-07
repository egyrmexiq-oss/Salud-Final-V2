import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# --- GESTIÓN DE ESTADO (LOGIN) ---
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

# --- PANTALLA DE LOGIN (TIPO CAJERO AUTOMÁTICO) ---
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    st.info("Introduce tu Código de Acceso Personal para iniciar sesión.")
    
    # Campo de entrada
    input_code = st.text_input("Código de Tarjeta / Clave:", type="password")
    
    if st.button("Validar Acceso"):
        # Accedemos a la lista de claves en los Secrets
        try:
            claves_validas = st.secrets["access_keys"]
            
            # Verificamos si lo que escribió el usuario está en nuestra lista
            if input_code in claves_validas:
                # ¡BINGO! Es una clave válida
                nombre_cliente = claves_validas[input_code]
                st.session_state.usuario_activo = nombre_cliente
                st.toast(f"✅ Bienvenido, {nombre_cliente}", icon="🎉")
                st.rerun()
            else:
                st.error("🚫 Código inválido o expirado.")
        except:
            st.error("⚠️ Error de configuración de claves.")
    
    st.stop() # Frena el código aquí si no entró

# ==========================================
# 🚀 ZONA SEGURA (SOLO ENTRAN SI EL CÓDIGO EXISTE)
# ==========================================

# --- CONEXIÓN API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY.")
    st.stop()

# --- SYSTEM PROMPT ---
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
    st.title("🧬 QUANTUM")
    # Mostramos quién está conectado
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
st.title("Quantum AI Health")

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
