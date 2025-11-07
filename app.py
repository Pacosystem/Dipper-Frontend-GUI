import streamlit as st
import requests
import json
import os
import pandas as pd # Para el testing

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Plataforma de Modelos v3.0 (ONNX)", layout="wide")
st.title("🚀 Plataforma de Modelos v3.0 (Formato ONNX)")

# ¡IMPORTANTE! Esta es la URL de tu API-Backend que ya desplegamos
API_URL = "https://api-backend-945900646359.us-central1.run.app" 

# Definir las pestañas
tab_registry, tab_upload = st.tabs(["🏛️ Registro de Modelos", "⬆️ Subir Nuevo Modelo"])

# --- 2. Pestaña 1: Registro de Modelos ---
with tab_registry:
    st.header("Modelos Disponibles en la Plataforma")
    try:
        # Llamar al endpoint /models de tu backend
        response = requests.get(f"{API_URL}/models")
        
        if response.status_code == 200:
            model_names = response.json()
            if not model_names:
                st.info("Aún no se ha subido ningún modelo. Ve a la pestaña 'Subir Nuevo Modelo'.")
            else:
                # Menú para seleccionar un modelo
                selected_model = st.selectbox("Selecciona un modelo:", model_names)
                
                if selected_model:
                    # Si se selecciona uno, llamar al endpoint /models/<nombre>
                    meta_response = requests.get(f"{API_URL}/models/{selected_model}")
                    
                    if meta_response.status_code == 200:
                        metadata = meta_response.json()
                        st.subheader(f"Detalles de: '{selected_model}'")
                        st.markdown(f"**Descripción:** `{metadata.get('description', 'N/A')}`")
                        
                        # Formulario de predicción dinámico
                        st.subheader("Probar este modelo")
                        with st.form(key=f"predict_form_{selected_model}"):
                            input_data = []
                            feature_info = metadata.get('input_features', [])
                            
                            st.markdown(f"**Features de Entrada ({len(feature_info)}):**")
                            
                            # Construir el formulario dinámicamente (¡Lección aprendida!)
                            for feature in feature_info:
                                f_name = feature['name']
                                f_type = feature['type']
                                
                                if f_type == "numeric":
                                    val = st.number_input(label=f_name, value=feature.get('default', 0.0), format="%.2f")
                                    input_data.append(val)
                                elif f_type == "categorical":
                                    val = st.selectbox(label=f_name, options=feature.get('options', []))
                                    input_data.append(val)
                            
                            predict_button = st.form_submit_button("¡Predecir!")
                            
                            if predict_button:
                                # Enviar los datos a la API de predicción
                                payload = {"features": input_data}
                                predict_url = f"{API_URL}/predict/{selected_model}"
                                
                                with st.spinner(f"Llamando a la API de ONNX para '{selected_model}'..."):
                                    pred_res = requests.post(predict_url, json=payload)
                                    
                                    if pred_res.status_code == 200:
                                        st.success("¡Predicción recibida!")
                                        st.json(pred_res.json())
                                    else:
                                        st.error(f"Error {pred_res.status_code} desde la API de predicción:")
                                        st.json(pred_res.json())
                    else:
                        st.error(f"No se pudieron cargar los metadatos de '{selected_model}'.")
        else:
            st.error(f"Error al contactar la API: {response.status_code}")
            st.json(response.json())
            
    except requests.exceptions.ConnectionError:
        st.error(f"Error de Conexión: No se pudo conectar a la API en {API_URL}. ¿Está desplegada?")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado en la GUI: {e}")


# --- 3. Pestaña 2: Subir un Nuevo Modelo ---
with tab_upload:
    st.header("Subir un Nuevo Modelo (ONNX + META)")
    st.warning("Esta plataforma solo acepta modelos .onnx y sus .meta (JSON) asociados.", icon="🔒")

    with st.form(key="upload_form"):
        model_name = st.text_input("Nombre corto del modelo (ej: 'fish-sales-v1')", help="Este será el nombre en la API, sin espacios ni .onnx")
        
        # Subir 2 archivos
        st.subheader("1. Sube el modelo ONNX")
        model_file = st.file_uploader("Selecciona tu archivo .onnx", type=['onnx'])
        
        st.subheader("2. Sube los metadatos JSON")
        meta_file = st.file_uploader("Selecciona tu archivo .meta", type=['meta', 'json'])
        
        submit_button = st.form_submit_button(label="Subir Modelo")

    if submit_button:
        # Validar que todo esté lleno
        if model_file is not None and meta_file is not None and model_name:
            
            # Preparar los archivos para la API
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
                        st.json(response.json())
                        st.info("Ve a la pestaña 'Registro de Modelos' y refresca para verlo.")
                    else:
                        st.error(f"Error {response.status_code} desde la API:")
                        st.json(response.json())
                        
                except requests.exceptions.ConnectionError:
                    st.error(f"Error de Conexión: No se pudo conectar a la API en {API_URL}")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")
        else:
            st.warning("Por favor, proporciona un nombre y ambos archivos (.onnx y .meta).")