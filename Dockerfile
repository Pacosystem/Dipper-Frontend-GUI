# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar todo (app.py, requirements.txt, y la carpeta .streamlit)
COPY . .

# Instalar las librerías
RUN pip install --no-cache-dir -r requirements.txt

# Comando final para ejecutar la GUI (con todos los arreglos)
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=true --server.enableXsrfProtection=false"]