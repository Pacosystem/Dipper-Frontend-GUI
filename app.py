import streamlit as st
import requests
import json
import os
import pandas as pd

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Plataforma de Modelos v3.1 (ONNX)", layout="wide")
st.title("🚀 Plataforma de Modelos v3.1 (Formulario Dinámico)")

# ¡URL de tu API-Backend!
# (Asegúrate de que esta sea la URL de tu 'api-backend' desplegado)
API_URL = "https://api-backend-570094060679.us-central1.run.app" 

# --- INICIALIZAR EL ESTADO DE SESIÓN ---
if 'features' not in st.session_state:
    st.session_state.features = []

tab_registry, tab_upload = st.tabs(["🏛️ Registro de Modelos", "⬆️ Subir Nuevo Modelo"])

# --- 2. Pestaña 1: Registro de Modelos ---
with tab_registry:
    # (Esta pestaña no tiene cambios)
    st.header("Modelos Disponibles en la Plataforma")
    try:
        response = requests.get(f"{API_URL}/models")
        if response.status_code == 200:
            model_names = response.json()
            if not model_names:
                st.info("Aún no se ha subido ningún modelo. Ve a la pestaña 'Subir Nuevo Modelo'.")
            else:
                selected_model = st.selectbox("Selecciona un modelo:", model_names, key="model_selector")
                
                if selected_model:
                    meta_response = requests.get(f"{API_URL}/models/{selected_model}")
                    if meta_response.status_code == 200:
                        metadata = meta_response.json()
                        st.subheader(f"Detalles de: '{selected_model}'")
                        st.markdown(f"**Descripción:** `{metadata.get('description', 'N/A')}`")
                        
                        st.subheader("Probar este modelo")
                        with st.form(key=f"predict_form_{selected_model}"):
                            input_data = []
                            feature_info = metadata.get('input_features', [])
                            st.markdown(f"**Features de Entrada ({len(feature_info)}):**")

                            for feature in feature_info:
                                f_name = feature.get('name', 'N/A')
                                f_type = feature.get('type', 'numeric')
                                
                                if f_type == "numeric":
                                    val = st.number_input(label=f_name, value=feature.get('default', 0.0), format="%.2f")
                                    input_data.append(val)
                                elif f_type == "categorical":
                                    val = st.selectbox(label=f_name, options=feature.get('options', []))
                                    input_data.append(val)
                            
                            predict_button = st.form_submit_button("¡Predecir!")
                            
                            if predict_button:
                                payload = {"features": input_data}
                                predict_url = f"{API_URL}/predict/{selected_model}"
                                with st.spinner(f"Llamando a la API..."):
                                    pred_res = requests.post(predict_url, json=payload)
                                    if pred_res.status_code == 200:
                                        st.success("¡Predicción recibida!")
                                        st.json(pred_res.json())
                                    else:
                                        st.error(f"Error {pred_res.status_code} desde la API:")
                                        st.json(pred_res.json())
                    else:
                        st.error(f"No se pudieron cargar los metadatos de '{selected_model}'.")
        else:
            st.error(f"Error al contactar la API: {response.status_code}")
            try: st.json(response.json())
            except: st.text(response.text)
    except Exception as e:
        st.error(f"Error de Conexión o inesperado en la GUI: {e}")


# --- 3. Pestaña 2: Subir un Nuevo Modelo ---
with tab_upload:
    st.header("Subir un Nuevo Modelo (ONNX)")
    st.warning("Esta plataforma solo acepta modelos .onnx. Los archivos .pkl o .skops no son compatibles.", icon="🔒")

    # --- ¡¡AQUÍ ESTÁ TU MINITUTORIAL!! ---
    with st.expander("¿Cómo creo un archivo .onnx y .meta? (Minitutorial)"):
        st.markdown("""
        Tu API solo acepta modelos en formato ONNX para ser segura y universal. Debes convertir tu modelo en tu script de entrenamiento (ej. Colab).
        
        **Necesitarás dos archivos:**
        1.  `mi_modelo.onnx`: El modelo matemático.
        2.  `mi_modelo.meta`: Un JSON con la descripción y las features.

        ---
        **Paso 1: Instala las librerías en Colab**
        """)
        st.code("!pip install scikit-learn skl2onnx pandas", language="bash")
        
        st.markdown("**Paso 2: Exporta tu modelo entrenado**")
        st.markdown("Asume que `model_pipeline` es tu pipeline de Sklearn entrenado y `X_train` son tus datos de entrada.")
        
        st.code("""
import pandas as pd
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import StringTensorType, FloatTensorType

# --- Define los tipos de entrada para ONNX ---
# (ONNX necesita saber los tipos de datos de entrada)
initial_types = []
for col_name in X_train.columns:
    if pd.api.types.is_string_dtype(X_train[col_name].dtype):
        # [batch_size, 1] para strings
        initial_types.append((col_name, StringTensorType([None, 1])))
    else:
        # [batch_size, 1] para números (convertidos a float32)
        initial_types.append((col_name, FloatTensorType([None, 1])))

# --- Convierte el pipeline a ONNX ---
print("Convirtiendo modelo a ONNX...")
onnx_model = convert_sklearn(
    model_pipeline, 
    "mi_pipeline_onnx", # Nombre interno
    initial_types=initial_types,
    target_opset=12 # Opset común
)

# --- Guarda el archivo .onnx ---
with open("mi_modelo.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
    
print("¡Modelo .onnx guardado!")
        """, language="python")
        
        st.markdown("**Paso 3: Crea tu archivo .meta**")
        st.markdown("Crea un JSON que describa tu modelo. Los nombres (`name`) deben coincidir *exactamente* con las columnas de tus datos.")
        
        st.code("""
import json

# Define los metadatos (¡esto alimenta la GUI!)
metadata = {
    "description": "Predice las ventas (Sales) de un videojuego basado en sus features.",
    "input_features": [
        {
            "name": "Metacritic", 
            "type": "numeric", 
            "default": 70.0
        },
        {
            "name": "Release Year", 
            "type": "numeric",
            "default": 2020.0
        },
        {
            "name": "Console", 
            "type": "categorical", 
            "options": ["PS4", "PS5", "PS3"]
        },
        {
            "name": "Genres", 
            "type": "categorical", 
            "options": ["Action", "RPG", "Sports"]
        },
        {
            "name": "Rating", 
            "type": "categorical", 
            "options": ["M", "T", "E", "E10+"]
        }
    ]
}

# --- Guarda el archivo .meta ---
with open("mi_modelo.meta", "w") as f:
    json.dump(metadata, f, indent=2)

print("¡Metadatos .meta guardados!")
        """, language="python")
        
        st.success("¡Listo! Ahora sube los archivos `mi_modelo.onnx` y `mi_modelo.meta` aquí abajo.")
    
    # --- Formulario dinámico de subida (Sin cambios) ---
    st.divider()
    st.header("Formulario de Subida")
    
    st.subheader("1. Definir Features (Solo para tu referencia)")
    for i, feature in enumerate(st.session_state.features):
        cols = st.columns([3, 2, 4, 1])
        st.session_state.features[i]['name'] = cols[0].text_input(f"Nombre Feature {i+1}", value=feature['name'], key=f"name_{i}")
        st.session_state.features[i]['type'] = cols[1].selectbox(f"Tipo {i+1}", ["numeric", "categorical"], index=0 if feature['type'] == 'numeric' else 1, key=f"type_{i}")
        if st.session_state.features[i]['type'] == 'categorical':
            st.session_state.features[i]['options_str'] = cols[2].text_input(f"Opciones {i+1} (separadas por coma)", value=feature.get('options_str', ''), key=f"options_{i}")
        if cols[3].button(f"X", key=f"del_{i}"):
            st.session_state.features.pop(i)
            st.rerun() 

    if st.button("Añadir Feature (+)", use_container_width=True):
        st.session_state.features.append({"name": "", "type": "numeric", "options_str": ""})
        st.rerun()

    st.divider()
    st.subheader("2. Subir Archivos")
    
    with st.form(key="upload_form"):
        model_name = st.text_input("Nombre corto del modelo (ej: 'fish-sales-v1')")
        
        st.markdown("**Sube el modelo ONNX**")
        model_file = st.file_uploader("Selecciona tu archivo .onnx", type=['onnx'], label_visibility="collapsed")
        
        st.markdown("**Sube los metadatos JSON**")
        meta_file = st.file_uploader("Selecciona tu archivo .meta", type=['meta', 'json'], label_visibility="collapsed")
        
        submit_button = st.form_submit_button(label="Subir Modelo", use_container_width=True)

    if submit_button:
        # (El resto de la lógica de subida no cambia)
        if model_file is not None and meta_file is not None and model_name:
            files = {
                'model_file': (f"{model_name}.onnx", model_file.getvalue(), 'application/octet-stream'),
                'meta_file': (f"{model_name}.meta", meta_file.getvalue(), 'application/json')
            }
            data = {'model_name': model_name}
            upload_url = f"{API_URL}/upload"
            
            with st.spinner(f"Subiendo '{model_name}' a la API..."):
                try:
                    response = requests.post(upload_url, files=files, data=data)
                    if response.status_code == 201:
                        st.success(f"¡Éxito! Modelo '{model_name}' subido.")
                        st.session_state.features = [] 
                        st.rerun()
                    else:
                        st.error(f"Error {response.status_code} desde la API:")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")
        else:
            st.warning("Por favor, proporciona un nombre y ambos archivos (.onnx y .meta).")