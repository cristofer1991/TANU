
import streamlit as st
import requests
from pathlib import Path

st.title("Descargador de imágenes de aves desde iNaturalist (API)")
st.write("Esta versión usa la API oficial de iNaturalist para obtener imágenes confiables por especie.")

especies = {
    "Tiuque (Milvago chimango)": "Milvago chimango",
    "Queltehue (Vanellus chilensis)": "Vanellus chilensis",
    "Carancho (Caracara plancus)": "Caracara plancus",
    "Cauquén (Chloephaga picta)": "Chloephaga picta"
}

especie_seleccionada = st.selectbox("Selecciona una especie", list(especies.keys()))
cantidad = st.slider("Cantidad de imágenes a descargar", min_value=10, max_value=100, value=50)

if st.button("Iniciar descarga"):
    nombre_cientifico = especies[especie_seleccionada]
    carpeta_destino = Path("dataset") / nombre_cientifico.replace(" ", "_")
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    st.write(f"Buscando imágenes para: {nombre_cientifico}...")

    api_url = f"https://api.inaturalist.org/v1/observations?taxon_name={nombre_cientifico.replace(' ', '%20')}&photos=true&per_page=200"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        fotos = []
        for obs in data["results"]:
            for foto in obs.get("photos", []):
                fotos.append(foto["url"].replace("square", "original"))
                if len(fotos) >= cantidad:
                    break
            if len(fotos) >= cantidad:
                break

        if not fotos:
            st.error("No se encontraron fotos para esta especie.")
        else:
            progreso = st.progress(0)
            for i, url in enumerate(fotos):
                ext = url.split('.')[-1].split('?')[0]
                img_data = requests.get(url).content
                with open(carpeta_destino / f"{nombre_cientifico.replace(' ', '_')}_{i}.{ext}", "wb") as f:
                    f.write(img_data)
                progreso.progress((i + 1) / len(fotos))
            st.success(f"Descarga completada: {len(fotos)} imágenes guardadas en {carpeta_destino}")
    else:
        st.error("Error al acceder a la API de iNaturalist.")
