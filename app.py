import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# --- 🔐 CONTRASEÑA MAESTRA ---
# Cambia esta palabra por la contraseña que tú quieras vender
PASSWORD_CORRECTO = "QUANTUM2026"

# --- GESTIÓN DE ESTADO (LOGIN) ---
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.logueado:
    st.markdown("## 🔒 Acceso Restringido - QUANTUM AI")
    st.info("Este es un sistema privado para profesionales de la salud y pacientes autorizados.")
# --- CONTADOR HITS (NUEVO) ---
    # Este enlace genera un botón visual automático.
    # El parámetro 'url' es el identificador único de tu app.
    st.markdown("[![Visitas](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fquantum-health-app&count_bg=%2300C2FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=VISITAS&edge_flat=false)](https://hits.seeyoufarm.com)")
    
    st.caption("Profesionales conectados globalmente")
    
    #st.info("Introduce tu Código de Acceso Personal para iniciar sesión.") #egyr
    password_input = st.text_input("Introduce tu Clave de Acceso:", type="password")
    
    if st.button("Ingresar"):
        if password_input == PASSWORD_CORRECTO:
            st.session_state.logueado = True
            st.rerun()  # Recarga la página para entrar
        else:
            st.error("🚫 Clave incorrecta. Contacta al administrador.")
    
    # Detenemos el código aquí si no está logueado
    st.stop()

# ==========================================
# 🚀 ZONA SEGURA: AQUÍ COMIENZA LA APP REAL
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

# --- GESTIÓN DE MEMORIA CHAT ---
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
        try:
            texto_limpio = m['content'].encode('latin-1', 'replace').decode('latin-1')
        except:
            texto_limpio = m['content']
            
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, txt=f"{rol}:", ln=1)
        
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, txt=texto_limpio)
        pdf.ln(3)
        
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🧬 QUANTUM")
    st.caption("Sistema Privado v2.0")
    st.markdown("---")
    
    # Botón para Cerrar Sesión
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.logueado = False
        st.session_state.mensajes = []
        st.rerun()
    
    st.markdown("---")
    
    # 1. AVISO LEGAL
    st.markdown("### 1. Validación")
    acepta_terminos = st.checkbox("Acepto los términos de uso médico.")
    
    if acepta_terminos:
        # 2. SELECTOR DE NIVEL
        st.markdown("### 2. Configuración")
        nivel = st.radio(
            "Nivel de detalle:",
            ["Básica (Sencilla)", "Media (Detallada)", "Experta (Técnica)"]
        )
        
        # 3. HISTORIAL
        st.markdown("---")
        st.markdown("### 📜 Historial")
        if not st.session_state.mensajes:
            st.caption("Esperando consultas...")
        else:
            for m in st.session_state.mensajes:
                if m["role"] == "user":
                    st.text(f"• {m['content'][:25]}...")

        # 4. BOTONES ACCIÓN
        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("Limpiar"):
            st.session_state.mensajes = []
            st.rerun()
        
        if st.session_state.mensajes:
            pdf_bytes = crear_pdf(st.session_state.mensajes)
            c2.download_button("Descargar", data=pdf_bytes, file_name="Quantum.pdf", mime="application/pdf")

# --- ÁREA PRINCIPAL ---
st.markdown("""
    <style>
        /* Importamos la fuente futurista de Google */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

        /* Creamos una clase personalizada para el título */
        .titulo-quantum {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 3em !important;  /* Tamaño grande */
            color: #00C2FF !important; /* Color azul cian tipo láser */
            text-align: center !important;
            text-transform: uppercase;
            /* Efecto de brillo de neón opcional */
            text-shadow: 0 0 10px #00C2FF, 0 0 20px #004e92;
            margin-bottom: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)
# 2. Usamos HTML en lugar de st.title para aplicar la clase que creamos arriba
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

if not acepta_terminos:
    st.info("👋 Bienvenido, Usuario Autorizado. Por favor acepta los términos en la barra lateral.")
    # Imagen de respaldo de internet (la que te gustó)
    st.image("https://cdn.pixabay.com/photo/2018/05/08/08/44/artificial-intelligence-3382507_1280.jpg", use_container_width=True)

else:
    # CHAT ACTIVO
    st.success(f"🟢 Conectado | Modo: **{nivel}**")

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input(f"Consultar a Quantum ({nivel})...")
    
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
            with st.spinner("Procesando..."):
                response = model.generate_content(prompt_completo)
                texto_ia = response.text
            
            st.session_state.mensajes.append({"role": "assistant", "content": texto_ia})
            st.rerun()
                
        except Exception as e:
            st.error(f"Error: {e}")

# --- PIE DE PÁGINA (FOOTER) ---
    st.markdown("---")
    col_foot1, col_foot2 = st.columns(2)
    
    with col_foot1:
        st.markdown("**Quantum AI Health v2.0**")
        st.caption("© 2026 Todos los derechos reservados.")
    
    with col_foot2:
        st.markdown("Popularidad del sistema:")
        # Usamos el mismo enlace, pero como imagen simple para que sume al mismo contador
        st.image("https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fquantum-health-app&count_bg=%2300C2FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=TOTAL&edge_flat=false")
        st.markdown("![Popularidad](https://visit-counter.vercel.app/counter.png?page=QuantumAI_Health_Login&s=14&c=555555&t=EEEEEE)")
