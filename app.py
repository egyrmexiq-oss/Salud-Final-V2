import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

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
    pdf.set_font("Arial", size=10)
    
    pdf.cell(0, 10, txt="Resumen de Consulta - QUANTUM AI", ln=1, align='C')
    pdf.ln(5)
    
    for m in mensajes:
        rol = "USUARIO" if m["role"] == "user" else "QUANTUM"
        # Limpieza básica
        texto_limpio = m['content'].encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, txt=f"{rol}:", ln=1)
        
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, txt=texto_limpio)
        pdf.ln(3)
        
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🧬 QUANTUM")
    st.caption("Sistema Experto de Salud")
    st.markdown("---")
    
    # 1. AVISO LEGAL
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
        
        # 3. HISTORIAL
        st.markdown("---")
        st.markdown("### 📜 Historial Reciente")
        if not st.session_state.mensajes:
            st.caption("No hay preguntas aún.")
        else:
            for m in st.session_state.mensajes:
                if m["role"] == "user":
                    st.text(f"• {m['content'][:30]}...")

        # 4. BOTONES
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.session_state.mensajes = []
                st.rerun()
        
        with col2:
            if st.session_state.mensajes:
                pdf_bytes = crear_pdf(st.session_state.mensajes)
                st.download_button(
                    label="📥 PDF",
                    data=pdf_bytes,
                    file_name="Quantum_Consulta.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# --- ÁREA PRINCIPAL ---
st.title("Quantum AI Health")

if not acepta_terminos:
    st.info("👋 Bienvenido a QUANTUM. Para iniciar, por favor valida el aviso legal en el menú de la izquierda.")
    
    # INTENTO DE CARGAR IMAGEN LOCAL
    try:
        st.image("portada.png", use_container_width=True)
    except:
        # Si falla (porque no se subió bien), usa una de internet de respaldo
        st.warning("⚠️ No se encontró la imagen local. Usando respaldo.")
        st.image("https://cdn.pixabay.com/photo/2018/05/08/08/44/artificial-intelligence-3382507_1280.jpg", use_container_width=True)

else:
    st.success(f"Sistema Activo | Nivel: **{nivel}**")

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input(f"Escribe tu consulta ({nivel})...")
    
    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        try:
            prompt_completo = f"""
            {SYSTEM_PROMPT}
            CONTEXTO: El usuario eligió {nivel}.
            Pregunta: "{prompt}"
            """
            model = genai.GenerativeModel('gemini-2.5-flash')
            with st.spinner("Quantum procesando..."):
                response = model.generate_content(prompt_completo)
                texto_ia = response.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_ia})
            st.rerun()
                
        except Exception as e:
            st.error(f"Error en Quantum: {e}")
