import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Diagnóstico Gemini", page_icon="🔍")
st.title("🔍 Escáner de Modelos Disponibles")

# 1. Intentar obtener la API KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # Mostramos los últimos 4 caracteres para verificar que usas la llave correcta
    st.info(f"🔑 Probando conexión con la llave que termina en: ...{api_key[-4:]}")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ Error leyendo Secrets: {e}")
    st.stop()

# 2. Llamar a ListModels
st.write("⏳ Contactando a Google para listar modelos...")

try:
    modelos_encontrados = []
    for m in genai.list_models():
        # Solo nos interesan los modelos que sirven para generar texto (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            modelos_encontrados.append(m.name)

    # 3. Mostrar resultados
    if len(modelos_encontrados) > 0:
        st.success(f"✅ ¡Conexión Exitosa! Se encontraron {len(modelos_encontrados)} modelos.")
        st.markdown("### Copia uno de estos nombres exactos:")
        for nombre in modelos_encontrados:
            st.code(nombre) # Esto mostrará algo como models/gemini-pro
    else:
        st.warning("⚠️ La conexión funciona, pero la lista de modelos está vacía. Tu llave no tiene permisos para ver modelos.")

except Exception as e:
    st.error("❌ ERROR CRÍTICO AL LISTAR MODELOS:")
    st.error(e)
    st.markdown("""
    **Posibles causas:**
    1. La API Key es inválida.
    2. El proyecto de Google Cloud no tiene habilitada la "Generative Language API".
    3. Tu IP o región está bloqueada.
    """)
