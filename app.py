import streamlit as st
import requests
import json
import os
import pandas as pd

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Plataforma de Modelos v3.1", layout="wide")
st.title("🚀 Plataforma de Modelos v3.1 (Formulario Dinámico)")

# ¡URL de tu API-Backend!
API_URL = "https://api-backend-570094060679.us-central1.run.app" 
# (Recuerda actualizar esta URL si tu backend tiene un nombre diferente)

# --- INICIALIZAR EL ESTADO DE SESIÓN ---
if 'features' not in st.session_state:
    st.session_state.features = []

tab_registry, tab_upload = st.tabs(["🏛️ Registro de Modelos", "⬆️ Subir Nuevo Modelo"])

# --- 2. Pestaña 1: Registro de Modelos ---
with tab_registry:
    # (Esta pestaña no tenía errores y sigue igual)
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


# --- 3. Pestaña 2: Subir un Nuevo Modelo (¡Refactorizado!) ---
with tab_upload:
    st.header("Subir un Nuevo Modelo (ONNX)")
    st.warning("Esta plataforma solo acepta modelos .onnx.", icon="🔒")
    
    # --- ¡ESTA ES LA CORRECCIÓN! ---
    # PARTE 1: Formulario dinámico de features (FUERA del form de subida)
    st.subheader("1. Definir Features de Entrada")
    
    # Iterar sobre las features guardadas en el estado
    for i, feature in enumerate(st.session_state.features):
        cols = st.columns([3, 2, 4, 1])
        # Usamos los 'key' para que Streamlit recuerde los valores
        st.session_state.features[i]['name'] = cols[0].text_input(f"Nombre Feature {i+1}", value=feature['name'], key=f"name_{i}")
        st.session_state.features[i]['type'] = cols[1].selectbox(f"Tipo {i+1}", ["numeric", "categorical"], index=0 if feature['type'] == 'numeric' else 1, key=f"type_{i}")
        
        if st.session_state.features[i]['type'] == 'categorical':
            st.session_state.features[i]['options_str'] = cols[2].text_input(f"Opciones {i+1} (separadas por coma)", value=feature.get('options_str', ''), key=f"options_{i}")
        
        # Botón para eliminar esta feature (st.button, FUERA del form)
        if cols[3].button(f"X", key=f"del_{i}"):
            st.session_state.features.pop(i)
            st.rerun() # Forzar re-dibujado

    # Botón para añadir una nueva feature (st.button, FUERA del form)
    if st.button("Añadir Feature (+)", use_container_width=True):
        st.session_state.features.append({"name": "", "type": "numeric", "options_str": ""})
        st.rerun()

    st.divider()

    # PARTE 2: Formulario de subida (SOLO para los datos estáticos)
    st.header("2. Subir el Modelo")
    with st.form(key="upload_form"):
        model_name = st.text_input("Nombre corto del modelo (ej: 'fish-sales-v1')")
        description = st.text_area("Descripción (¿Qué hace este modelo?)")
        model_file = st.file_uploader("Selecciona tu archivo .onnx", type=['onnx'])
        
        # El ÚNICO botón dentro del form
        submit_button = st.form_submit_button(label="Subir Modelo y Metadatos", use_container_width=True)

    if submit_button:
        # 3. Lógica de envío (combina los datos)
        if model_file is not None and model_name and description and st.session_state.features:
            
            # Procesar la lista de features desde st.session_state
            input_features_list = []
            valid = True
            for f in st.session_state.features:
                if not f['name']:
                    valid = False
                    break
                feature_dict = {"name": f['name'], "type": f['type']}
                if f['type'] == 'categorical':
                    feature_dict['options'] = [opt.strip() for opt in f.get('options_str', '').split(',')]
                input_features_list.append(feature_dict)

            if not valid:
                st.error("Error: Todas las features deben tener un nombre.")
            else:
                # Preparar 'files' (el .onnx)
                files = {
                    'model_file': (f"{model_name}.onnx", model_file.getvalue(), 'application/octet-stream'),
                }
                # Preparar 'data' (el texto del form + el JSON de features)
                data = {
                    'model_name': model_name,
                    'description': description,
                    'input_features_json': json.dumps(input_features_list)
                }
                upload_url = f"{API_URL}/upload"
                
                with st.spinner(f"Subiendo '{model_name}' a la API..."):
                    try:
                        response = requests.post(upload_url, files=files, data=data)
                        if response.status_code == 201:
                            st.success(f"¡Éxito! Modelo '{model_name}' subido.")
                            st.session_state.features = [] # Limpiar formulario
                            st.rerun()
                        else:
                            st.error(f"Error {response.status_code} desde la API:")
                            st.json(response.json())
                    except Exception as e:
                        st.error(f"Ocurrió un error inesperado: {e}")
        else:
            st.warning("Por favor, proporciona un nombre, descripción, al menos una feature, y un archivo .onnx.")