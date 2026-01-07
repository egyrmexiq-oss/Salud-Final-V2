import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="HealthExpert AI", page_icon="🩺", layout="centered")

# --- CONEXIÓN SEGURA ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY en los Secrets.")
    st.stop()

# --- CEREBRO: SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Eres un Asistente Experto en Contexto de Salud.
REGLA DE ORO: En TODAS tus respuestas incluye al final: "⚠️ IMPORTANTE: No soy un profesional de la salud. Información educativa. Acuda a un médico."

Tu tono y profundidad dependen del nivel seleccionado:
- Nivel Básica: Explicación sencilla, analogías, para público general.
- Nivel Media: Lenguaje formal, cita fuentes generales.
- Nivel Experto: Terminología médica, patologías, protocolos, NOMs y efectos secundarios.

Si el usuario pregunta algo ajeno a salud, responde amablemente que solo puedes hablar de temas médicos.
"""

# --- GESTIÓN DE MEMORIA ---
if "nivel" not in st.session_state:
    st.session_state.nivel = None
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Función para resetear
def nueva_consulta():
    st.session_state.nivel = None
    st.session_state.mensajes = []
    st.rerun()

# --- INTERFAZ ---
st.title("🩺 HealthExpert AI")

# ESCENA 1: SELECCIÓN DE NIVEL
if st.session_state.nivel is None:
    st.markdown("### Bienvenido. Selecciona el nivel de profundidad para tu consulta:")
    
    col1, col2, col3 = st.columns(3)
    if col1.button("🟢 BÁSICO\n(Sencillo)", use_container_width=True):
        st.session_state.nivel = "Básica"
        st.rerun()
    if col2.button("🟡 MEDIO\n(Detallado)", use_container_width=True):
        st.session_state.nivel = "Media"
        st.rerun()
    if col3.button("🔴 EXPERTO\n(Técnico)", use_container_width=True):
        st.session_state.nivel = "Experto"
        st.rerun()

# ESCENA 2: CHAT ACTIVO
else:
    # Barra superior con estado y botón de salir
    c1, c2 = st.columns([3, 1])
    with c1:
        st.info(f"Modo Activo: **Nivel {st.session_state.nivel}**")
    with c2:
        if st.button("🔄 Nueva Consulta"):
            nueva_consulta()

    # Mostrar historial
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Caja de entrada
    prompt = st.chat_input("Escribe tu consulta médica aquí...")
    
    if prompt:
        # 1. Mostrar mensaje usuario
        st.chat_message("user").markdown(prompt)
        st.session_state.mensajes.append({"role": "user", "content": prompt})

        try:
            # 2. Preparar el "Sándwich" de contexto para la IA
            prompt_completo = f"""
            {SYSTEM_PROMPT}
            ----------------
            CONTEXTO: El usuario eligió NIVEL {st.session_state.nivel}.
            Pregunta del usuario: "{prompt}"
            """
            
            # 3. LLAMADA AL MODELO (Usamos el que encontramos en tu lista)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with st.spinner("Analizando consulta..."):
                response = model.generate_content(prompt_completo)
                respuesta_ia = response.text

            # 4. Mostrar respuesta IA
            with st.chat_message("assistant"):
                st.markdown(respuesta_ia)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")
