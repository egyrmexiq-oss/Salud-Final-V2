import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# --- CONEXIÓN ---
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

# --- GESTIÓN DE MEMORIA ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- FUNCIÓN: GENERAR PDF ---
def crear_pdf(mensajes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Resumen de Consulta - QUANTUM AI", ln=1, align='C')
    pdf.ln(10)
    
    for m in mensajes:
        rol = "USUARIO" if m["role"] == "user" else "QUANTUM"
        texto = f"{rol}: {m['content']}\n"
        # Limpieza básica de caracteres para PDF simple
        texto = texto.encode('latin-1', 'replace').decode('latin-1') 
        pdf.multi_cell(0, 10, txt=texto)
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🧬 QUANTUM")
    st.caption("Sistema Experto de Salud")
    st.markdown("---")
    
    # 1. AVISO LEGAL (Candado)
    st.markdown("### 🔒 Acceso")
    acepta_terminos = st.checkbox("Declaro que entiendo que esta IA NO sustituye a un médico.")
    
    if acepta_terminos:
        st.markdown("---")
        # 2. SELECTOR DE NIVEL
        st.markdown("### 🎚️ Nivel de Respuesta")
        nivel = st.radio(
            "Selecciona profundidad:",
            ["Básica (Sencilla)", "Media (Detallada)", "Experta (Técnica)"]
        )
        
        # 3. BOTONES DE ACCIÓN
        st.markdown("---")
        col_side1, col_side2 = st.columns(2)
        if col_side1.button("🗑️ Limpiar"):
            st.session_state.mensajes = []
            st.rerun()
            
        # Botón de descarga (Solo si hay mensajes)
        if st.session_state.mensajes:
            pdf_bytes = crear_pdf(st.session_state.mensajes)
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_bytes,
                file_name="consulta_quantum.pdf",
                mime="application/pdf"
            )

# --- ÁREA PRINCIPAL ---
st.title("Quantum AI Health")

if not acepta_terminos:
    st.warning("⚠️ Para iniciar el sistema, por favor acepta los términos en la barra lateral izquierda.")
    st.image("https://img.freepik.com/free-vector/futuristic-medical-background_23-2148496587.jpg?w=826", caption="Quantum Interface", width=400)

else:
    # Mostrar Nivel Activo
    st.success(f"Sistema Activo | Nivel: **{nivel}**")

    # Mostrar Chat
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input Usuario
    prompt = st.chat_input(f"Escribe tu consulta ({nivel})...")
    
    if prompt:
        # Guardar y mostrar usuario
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        try:
            # Lógica
            prompt_completo = f"""
            {SYSTEM_PROMPT}
            CONTEXTO: El usuario eligió {nivel}.
            Pregunta: "{prompt}"
            """
            
            # Llamada IA
            model = genai.GenerativeModel('gemini-2.5-flash')
            with st.spinner("Quantum procesando..."):
                response = model.generate_content(prompt_completo)
                texto_ia = response.text
            
            # Guardar y mostrar IA
            st.session_state.mensajes.append({"role": "assistant", "content": texto_ia})
            with st.chat_message("assistant"):
                st.markdown(texto_ia)
                
        except Exception as e:
            st.error(f"Error en Quantum: {e}")
