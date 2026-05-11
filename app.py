# app.py

import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.title("🧪 AI Food Scanner")

harmful = {
    "E621": "Мононатриев глутамат",
    "E250": "Натриев нитрит",
    "E951": "Аспартам",
    "PALM OIL": "Палмово масло"
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_reader()

choice = st.radio(
    "Избери:",
    ["Качване", "Камера"]
)

image = None

if choice == "Качване":

    file = st.file_uploader(
        "Качи снимка",
        type=["jpg", "png", "jpeg"]
    )

    if file:
        image = Image.open(file)

if choice == "Камера":

    camera = st.camera_input("Снимай")

    if camera:
        image = Image.open(camera)

if image:

    st.image(image)

    if st.button("Сканирай"):

        img = np.array(image)

        result = reader.readtext(
            img,
            detail=0
        )

        text = " ".join(result)

        st.subheader("Разпознат текст")
        st.write(text)

        st.subheader("Вредни съставки")

        found = False

        upper_text = text.upper()

        for item in harmful:

            if item in upper_text:

                found = True

                st.error(
                    item + " → " + harmful[item]
                )

        if not found:

            st.success(
                "Няма намерени вредни съставки"
            )
