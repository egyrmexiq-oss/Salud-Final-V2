import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# ==========================================
# 💎 CARGA DE ALIADOS
# ==========================================
try:
    DIRECTORIO_MEDICOS = list(st.secrets["aliados"].values())
except Exception:
    DIRECTORIO_MEDICOS = []

# Preparamos texto para la IA
if DIRECTORIO_MEDICOS:
    TEXTO_DIRECTORIO = "\n".join([f"- {m['nombre']} ({m['especialidad']}): {m['desc']}" for m in DIRECTORIO_MEDICOS])
    INSTRUCCION_EXTRA = f"""
    TU MISIÓN COMERCIAL:
    Tienes acceso a una red de Aliados Médicos. Si el síntoma coincide, sugiere contactar a:
    {TEXTO_DIRECTORIO}
    """
else:
    INSTRUCCION_EXTRA = ""

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
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO (LOGIN) ---
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

# --- PANTALLA DE LOGIN ---
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    
    # ---------------------------------------------------------
    # 🌊 AQUÍ ESTÁ LA ONDA DE COLORES (RECUPERADA) 
    # ---------------------------------------------------------
    st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=500)
    
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
            st.error(f"⚠️ Error: {e}")
    st.stop()

# ==========================================
# 🚀 ZONA SEGURA
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY.")
    st.stop()

SYSTEM_PROMPT = f"""
Eres QUANTUM, un Asistente Experto en Salud.
REGLA DE ORO: En TODAS tus respuestas incluye al final: "⚠️ IMPORTANTE: No soy un profesional de la salud. Información educativa. Acuda a un médico."
{INSTRUCCION_EXTRA}
Tu tono y profundidad dependen del nivel seleccionado.
"""

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

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

# --- BARRA LATERAL RECONFIGURADA ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00C2FF;'>🧬 QUANTUM</h2>", unsafe_allow_html=True)
    st.success(f"👤 {st.session_state.usuario_activo}")
    
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.usuario_activo = None; st.session_state.mensajes = []; st.rerun()
    
    st.markdown("---")
    
    # 1. NIVEL Y ACCIONES (ARRIBA)
    st.markdown("### ⚙️ Panel de Control")
    nivel = st.radio("Nivel de Respuesta:", ["Básica", "Media", "Experta"])
    
    col_act1, col_act2 = st.columns(2)
    if col_act1.button("🧹 Limpiar"):
        st.session_state.mensajes = []; st.rerun()
    if st.session_state.mensajes:
        pdf_bytes = crear_pdf(st.session_state.mensajes)
        col_act2.download_button("📥 PDF", data=pdf_bytes, file_name="Quantum.pdf", mime="application/pdf")
    
    st.markdown("---")
    
    # 2. ALIADOS MÉDICOS (ABAJO - DOBLE SCROLL)
    if DIRECTORIO_MEDICOS:
        st.markdown("### 👨‍⚕️ Red de Especialistas")
        
        if "indice_medico" not in st.session_state: st.session_state.indice_medico = 0
        if "indice_contacto" not in st.session_state: st.session_state.indice_contacto = 0
        
        total_medicos = len(DIRECTORIO_MEDICOS)
        medico_actual = DIRECTORIO_MEDICOS[st.session_state.indice_medico % total_medicos]
        
        tipos_contacto = [
            {"icono": "📞", "label": "Teléfono", "valor": medico_actual.get("telefono", "N/D")},
            {"icono": "💬", "label": "WhatsApp", "valor": medico_actual.get("whatsapp", "N/D")},
            {"icono": "✉️", "label": "Email", "valor": medico_actual.get("email", "N/D")},
            {"icono": "🌐", "label": "Web", "valor": medico_actual.get("web", "N/D")}
        ]
        
        # Tarjeta Fija
        st.markdown(f"""
        <div class="medico-card">
            <strong>{medico_actual['nombre']}</strong><br>
            <span style="color: #00C2FF; font-weight: bold;">{medico_actual['especialidad']}</span><br>
            <hr style="border-color: #333; margin: 5px 0;">
            <small style="color: #bbb;">{medico_actual['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

        # Scroll de Contacto (Flechas pequeñas)
        contacto_actual = tipos_contacto[st.session_state.indice_contacto % len(tipos_contacto)]
        c_prev, c_display, c_next = st.columns([1, 4, 1])
        
        with c_prev:
            if st.button("◀", key="contact_prev"):
                st.session_state.indice_contacto -= 1; st.rerun()
        with c_display:
            st.markdown(f"""
            <div style="text-align: center;">
                <span style="font-size: 0.8em; color: #888;">{contacto_actual['icono']} {contacto_actual['label']}</span><br>
                <div class="contacto-dato">{contacto_actual['valor']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_next:
            if st.button("▶", key="contact_next"):
                st.session_state.indice_contacto += 1; st.rerun()

        st.markdown("---")
        
        # Scroll de Médicos (Botones grandes)
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("⬅️ Otro Dr."):
                st.session_state.indice_medico -= 1
                st.session_state.indice_contacto = 0 # Reset contacto
                st.rerun()
        with col_nav2:
            if st.button("Siguiente ➡️"):
                st.session_state.indice_medico += 1
                st.session_state.indice_contacto = 0
                st.rerun()
        
        st.caption(f"Socio { (st.session_state.indice_medico % total_medicos) + 1} de {total_medicos}")

# --- CHAT PRINCIPAL ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

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

# --- FOOTER ---
st.markdown("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.markdown("**Quantum AI Health v2.5**")
    st.caption("© 2026 Todos los derechos reservados.")
#with col_foot2:
    #st.markdown("Estadísticas de uso:")
    #st.markdown("![Visitas](https://visitor-badge.laobi.icu/badge?page_id=quantum_ai_health_main_access&left_text=Total&right_color=%2300C2FF)")
