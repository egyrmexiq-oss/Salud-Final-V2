import streamlit as st
import google.generativeai as genai

# --- VERIFICACIÓN DE VERSIÓN ---
st.set_page_config(page_title="HealthExpert AI", page_icon="🩺")
st.title("✅ VERSIÓN FINAL - CONECTADA")

# --- API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Faltan los Secretos. Configura la GEMINI_API_KEY en Streamlit.")
    st.stop()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Eres un Asistente Experto en Contexto de Salud.
REGLA: Si el usuario eligió un nivel, responde ESTRICTAMENTE en ese nivel.
- Nivel Básico: Explicación sencilla, como a un niño de 12 años.
- Nivel Medio: Explicación formal, citando fuentes generales.
- Nivel Experto: Terminología médica, patologías, protocolos y NOMs.
"""

# --- INICIALIZAR ESTADO ---
if "nivel" not in st.session_state:
    st.session_state.nivel = None
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- PANTALLA 1: SELECCIÓN DE NIVEL ---
if st.session_state.nivel is None:
    st.info("👋 Hola. Para empezar, selecciona tu nivel de profundidad:")
    c1, c2, c3 = st.columns(3)
    if c1.button("BÁSICO (Sencillo)"):
        st.session_state.nivel = "Básica"
        st.rerun()
    if c2.button("MEDIO (Detallado)"):
        st.session_state.nivel = "Media"
        st.rerun()
    if c3.button("EXPERTO (Técnico)"):
        st.session_state.nivel = "Experto"
        st.rerun()

# --- PANTALLA 2: CHAT ---
else:
    st.success(f"Modo Activo: {st.session_state.nivel}")
    if st.button("Cambiar Nivel"):
        st.session_state.nivel = None
        st.session_state.mensajes = []
        st.rerun()

    # Historial
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input
    prompt = st.chat_input("Escribe tu consulta médica...")
    
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.mensajes.append({"role": "user", "content": prompt})

        try:
            # Lógica del Prompt Oculto
            full_prompt = f"""
            {SYSTEM_PROMPT}
            CONTEXTO: El usuario eligió NIVEL {st.session_state.nivel}.
            Pregunta del usuario: {prompt}
            """
            
            # Usamos el modelo Flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(full_prompt)
            
            text = response.text
            with st.chat_message("assistant"):
                st.markdown(text)
            st.session_state.mensajes.append({"role": "assistant", "content": text})
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")
