import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit.components.v1 as components
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quantum AI Health", page_icon="🧬", layout="wide")

# ==========================================
# 💎 CARGA DE ALIADOS & FILTROS
# ==========================================
try:
    TODOS_LOS_MEDICOS = list(st.secrets["aliados"].values())
except Exception:
    TODOS_LOS_MEDICOS = []

# --- LÓGICA DE FILTRADO (Deseo #6) ---
# Primero obtenemos las ciudades únicas disponibles
ciudades_disponibles = sorted(list(set(m.get('ciudad', 'General') for m in TODOS_LOS_MEDICOS)))
ciudades_disponibles.insert(0, "Todas las Ubicaciones")

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
        /* Disclaimer forzado visualmente (opcional, también va en texto) */
        .disclaimer-text {
            font-size: 0.7em;
            color: #666;
            margin-top: 10px;
            border-top: 1px solid #333;
            padding-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None
if "saludo_inicial" not in st.session_state: st.session_state.saludo_inicial = False

# ==========================================
# 🔐 PANTALLA DE LOGIN ZEN (Deseo #2 y #3)
# ==========================================
if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Access")
    
    # --- ANIMACIÓN ONDA ---
    st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=500)
    
    # --- MÚSICA LOFI (Deseo #2) ---
    # Reproductor pequeño. La URL es un stream de LoFi libre de derechos.
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", format="audio/mp3", loop=True)
    st.caption("🎵 Modo Zen: Activado. Relájate antes de consultar.")
    
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
                st.error(f"🚫 El código no es válido.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    st.stop()

# ==========================================
# 🚀 ZONA SEGURA (APP PRINCIPAL)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY.")
    st.stop()

# --- PREPARACIÓN DE DIRECTORIO CON NUEVOS CAMPOS (Deseo #4 y #5) ---
# Creamos un texto enriquecido para que la IA sepa dónde están los médicos y si atienden remoto
if TODOS_LOS_MEDICOS:
    info_medicos = []
    for m in TODOS_LOS_MEDICOS:
        remoto_str = "✅ Atiende Remoto" if m.get('remoto') else "🏠 Solo Presencial"
        info_medicos.append(f"- {m['nombre']} ({m['especialidad']}) en {m.get('ciudad')}, {m.get('colonia')}. {remoto_str}. Perfil: {m['desc']}")
    
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    INSTRUCCION_EXTRA = f"""
    TU MISIÓN COMERCIAL (INTELIGENTE):
    Tienes acceso a esta red de especialistas:
    {TEXTO_DIRECTORIO}
    
    INSTRUCCIONES DE REFERENCIA:
    1. Analiza el problema del usuario.
    2. Si coincide con una especialidad de la lista, RECOMIENDA al médico.
    3. Si el usuario menciona una ciudad, prioriza al médico de esa ciudad.
    4. Si el usuario busca atención online, prioriza a los que dicen "Atiende Remoto".
    """
else:
    INSTRUCCION_EXTRA = ""

# --- DISCLAIMER OBLIGATORIO (Deseo #1) ---
DISCLAIMER_TEXTO = "\n\n⚠️ *AVISO LEGAL: Quantum AI Health proporciona información educativa, no diagnósticos médicos. Consulta siempre a un especialista.*"

SYSTEM_PROMPT = f"""
Eres QUANTUM, un Asistente Experto en Salud.
Tu objetivo es orientar, calmar y educar.
{INSTRUCCION_EXTRA}
Al final de CADA respuesta, es OBLIGATORIO incluir el aviso legal.
"""

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- SALUDO AUTOMÁTICO (Deseo #3) ---
if not st.session_state.saludo_inicial:
    saludo = f"Hola {st.session_state.usuario_activo}, ¿Cómo estás hoy? 🌿 Dime, ¿Qué te preocupa o qué te trae por aquí? Estoy listo para escucharte."
    st.session_state.mensajes.append({"role": "assistant", "content": saludo})
    st.session_state.saludo_inicial = True

def crear_pdf(mensajes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt="Resumen de Consulta - QUANTUM AI", ln=1, align='C')
    pdf.ln(5)
    for m in mensajes:
        rol = "USUARIO" if m["role"] == "user" else "QUANTUM"
        # Limpieza básica de caracteres latinos
        texto = m['content'].replace('*', '') 
        try: texto = texto.encode('latin-1', 'replace').decode('latin-1')
        except: pass
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, txt=f"{rol}:", ln=1)
        pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 6, txt=texto); pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL (FILTROS Y DIRECTORIO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00C2FF;'>🧬 QUANTUM</h2>", unsafe_allow_html=True)
    st.success(f"👤 {st.session_state.usuario_activo}")
    
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.usuario_activo = None
        st.session_state.mensajes = []
        st.session_state.saludo_inicial = False
        st.rerun()
    
    st.markdown("---")
    
    # 1. PANEL DE CONTROL
    st.markdown("### ⚙️ Configuración")
    nivel = st.radio("Nivel:", ["Básica", "Media", "Experta"])
    
    c1, c2 = st.columns(2)
    if c1.button("Limpiar"):
        st.session_state.mensajes = []; st.session_state.saludo_inicial = False; st.rerun()
    if st.session_state.mensajes:
        pdf_bytes = crear_pdf(st.session_state.mensajes)
        c2.download_button("PDF", data=pdf_bytes, file_name="Quantum.pdf", mime="application/pdf")
    
    st.markdown("---")
    
    # 2. DIRECTORIO MÉDICO (FILTRABLE - Deseo #6)
    if TODOS_LOS_MEDICOS:
        st.markdown("### 👨‍⚕️ Red de Especialistas")
        
        # Filtro de Ciudad
        filtro_ciudad = st.selectbox("📍 Filtrar por Ubicación:", ciudades_disponibles)
        
        # Aplicar filtro
        if filtro_ciudad == "Todas las Ubicaciones":
            medicos_filtrados = TODOS_LOS_MEDICOS
        else:
            medicos_filtrados = [m for m in TODOS_LOS_MEDICOS if m.get('ciudad') == filtro_ciudad]
        
        if medicos_filtrados:
            if "indice_medico" not in st.session_state: st.session_state.indice_medico = 0
            if "indice_contacto" not in st.session_state: st.session_state.indice_contacto = 0
            
            total_visible = len(medicos_filtrados)
            medico_actual = medicos_filtrados[st.session_state.indice_medico % total_visible]
            
            # Contactos
            tipos_contacto = [
                {"icono": "📞", "label": "Teléfono", "valor": medico_actual.get("telefono", "N/D")},
                {"icono": "💬", "label": "WhatsApp", "valor": medico_actual.get("whatsapp", "N/D")},
                {"icono": "✉️", "label": "Email", "valor": medico_actual.get("email", "N/D")},
                {"icono": "🌐", "label": "Web", "valor": medico_actual.get("web", "N/D")}
            ]
            
            # Tarjeta Visual
            st.markdown(f"""
            <div class="medico-card">
                <strong>{medico_actual['nombre']}</strong><br>
                <span style="color: #00C2FF; font-weight: bold;">{medico_actual['especialidad']}</span><br>
                <small>📍 {medico_actual.get('ciudad')}, {medico_actual.get('colonia')}</small><br>
                <hr style="border-color: #333; margin: 5px 0;">
                <small style="color: #bbb;">{medico_actual['desc']}</small>
            </div>
            """, unsafe_allow_html=True)

            # Scroll Contacto
            contacto_actual = tipos_contacto[st.session_state.indice_contacto % len(tipos_contacto)]
            c_prev, c_display, c_next = st.columns([1, 4, 1])
            with c_prev:
                if st.button("◀", key="cp"): st.session_state.indice_contacto -= 1; st.rerun()
            with c_display:
                st.markdown(f"<div style='text-align:center'><span style='color:#888'>{contacto_actual['icono']} {contacto_actual['label']}</span><div class='contacto-dato'>{contacto_actual['valor']}</div></div>", unsafe_allow_html=True)
            with c_next:
                if st.button("▶", key="cn"): st.session_state.indice_contacto += 1; st.rerun()

            st.markdown("---")
            # Navegación Médicos
            cn1, cn2 = st.columns(2)
            with cn1:
                if st.button("⬅️ Otro Dr."): st.session_state.indice_medico -= 1; st.session_state.indice_contacto = 0; st.rerun()
            with cn2:
                if st.button("Siguiente ➡️"): st.session_state.indice_medico += 1; st.session_state.indice_contacto = 0; st.rerun()
            
            st.caption(f"Mostrando { (st.session_state.indice_medico % total_visible) + 1} de {total_visible}")
        else:
            st.info("No hay especialistas en esta ubicación aún.")

# --- CHAT PRINCIPAL ---
st.markdown('<h1 class="titulo-quantum">Quantum AI Health</h1>', unsafe_allow_html=True)

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]): st.markdown(m["content"])

prompt = st.chat_input(f"Escribe aquí...")

if prompt:
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    try:
        # Aquí la magia: Prompt con datos de médicos + Disclaimer forzado
        prompt_completo = f"{SYSTEM_PROMPT}\nCONTEXTO: Nivel {nivel}. Usuario pregunta: {prompt}"
        model = genai.GenerativeModel('gemini-2.5-flash')
        with st.spinner("Analizando..."):
            response = model.generate_content(prompt_completo)
            # Forzamos el disclaimer SIEMPRE al final de la respuesta generada
            texto_final = response.text + DISCLAIMER_TEXTO
        
        st.session_state.mensajes.append({"role": "assistant", "content": texto_final})
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# --- FOOTER ---
st.markdown("---")
c_ft1, c_ft2 = st.columns(2)
with c_ft1: st.markdown("**Quantum AI Health v3.0**\n© 2026 Todos los derechos reservados.")
#with c_ft2: st.markdown("![Visitas](https://visitor-badge.laobi.icu/badge?page_id=quantum_ai_health_main_access&left_text=Total&right_color=%2300C2FF)")
