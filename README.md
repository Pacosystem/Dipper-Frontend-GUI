# 🚀 Plataforma de Gestión de Modelos ML v3.2 (Híbrida)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-Standard-lightgrey?style=for-the-badge&logo=onnx&logoColor=black)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **Una interfaz unificada para registrar, administrar y consumir modelos de Machine Learning en tiempo real.**

Esta aplicación es el **Frontend** de una arquitectura MLOps ligera. Permite a los Data Scientists subir sus modelos `.onnx` y a los usuarios finales realizar predicciones mediante formularios generados dinámicamente según los metadatos del modelo.

---

## 📸 Capturas de Pantalla

| **Panel de Predicción** | **Subida de Modelos (Constructor UI)** |
|:-----------------------:|:--------------------------------------:|
| *[Inserta aquí una captura de la pestaña 1]* | *[Inserta aquí una captura de la pestaña 2]* |

---

## ✨ Características Principales

### 1. 🏛️ Registro y Predicción Dinámica
La plataforma se adapta automáticamente a cualquier modelo subido:
* **Generación de UI al vuelo:** Si el modelo requiere 3 variables numéricas y 1 categórica, la app dibuja exactamente esos inputs.
* **Consumo de API:** Se comunica con un Backend REST para enviar los tensores y recibir las predicciones.
* **Visualización de Metadatos:** Muestra descripciones, tipos de datos y rangos esperados.

### 2. ⬆️ Sistema de Carga "Híbrido" (v3.2)
Ofrecemos flexibilidad total para registrar nuevos modelos:
* **Modo Rápido (Archivo .meta):** Para flujos automatizados. Sube el modelo `.onnx` junto con un `.json` pre-generado que describe las entradas.
* **Modo Manual (Constructor No-Code):** ¿No tienes el JSON a mano? Usa nuestra interfaz visual para definir las *features* (nombres, tipos y opciones) directamente en el navegador antes de subir el modelo.

---

## 🛠️ Arquitectura del Sistema

El sistema sigue un patrón de cliente-servidor desacoplado:



1.  **Frontend (Este Repo):** Streamlit. Maneja la UX/UI y la validación de formularios.
2.  **Backend (API):** (Alojado externamente). Procesa los archivos `.onnx`, almacena metadatos y ejecuta la inferencia.
3.  **Protocolo:** Comunicación vía HTTP (REST) usando JSON para metadatos y `multipart/form-data` para archivos.

---

## 🚀 Instalación y Uso Local

Sigue estos pasos para levantar la interfaz en tu máquina:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TU_USUARIO/TU_REPO.git](https://github.com/TU_USUARIO/TU_REPO.git)
cd TU_REPO
