# app.py

import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# ---------------------------------
# НАСТРОЙКИ
# ---------------------------------

st.set_page_config(
    page_title="AI Скенер за вредни храни",
    page_icon="🧪",
    layout="centered"
)

# ---------------------------------
# ЗАГЛАВИЕ
# ---------------------------------

st.title("🧪 AI Скенер за вредни съставки")

st.write(
    "Приложение, което използва EasyOCR "
    "за разпознаване на вредни съставки."
)

# ---------------------------------
# ВРЕДНИ СЪСТАВКИ
# ---------------------------------

harmful_ingredients = {
    "E621": "Мононатриев глутамат",
    "E250": "Натриев нитрит",
    "E951": "Аспартам",
    "E211": "Натриев бензоат",
    "PALM OIL": "Палмово масло",
    "HYDROGENATED": "Хидрогенирани мазнини"
}

# ---------------------------------
# OCR МОДЕЛ
# ---------------------------------

@st.cache_resource
def load_reader():
    return easyocr.Reader(["bg", "en"], gpu=False)

reader = load_reader()

# ---------------------------------
# ИЗБОР НА СНИМКА
# ---------------------------------

option = st.radio(
    "Изберете начин:",
    ["Качване на снимка", "Камера"]
)

image = None

# ---------------------------------
# FILE UPLOAD
# ---------------------------------

if option == "Качване на снимка":

    uploaded_file = st.file_uploader(
        "Качи снимка",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# ---------------------------------
# CAMERA
# ---------------------------------

if option == "Камера":

    camera_photo = st.camera_input("Направи снимка")

    if camera_photo is not None:
        image = Image.open(camera_photo)

# ---------------------------------
# ПОКАЗВАНЕ НА СНИМКАТА
# ---------------------------------

if image is not None:

    st.image(image, caption="Избрана снимка")

    if st.button("🔍 Анализирай"):

        with st.spinner("Сканиране..."):

            # PIL -> NumPy
            img_array = np.array(image)

            # OCR
            results = reader.readtext(img_array, detail=0)

            # Текст
            extracted_text = " ".join(results)

            st.subheader("📄 Разпознат текст")
            st.write(extracted_text)

            # ---------------------------------
            # ТЪРСЕНЕ НА ВРЕДНИ СЪСТАВКИ
            # ---------------------------------

            st.subheader("⚠️ Намерени вредни съставки")

            text_upper = extracted_text.upper()

            found = False

            for ingredient in harmful_ingredients:

                if ingredient in text_upper:

                    found = True

                    st.error(
                        ingredient + " → " +
                        harmful_ingredients[ingredient]
                    )

            if not found:
                st.success("Няма открити вредни съставки.")

# ---------------------------------
# ИНФОРМАЦИЯ
# ---------------------------------

with st.expander("ℹ️ Използвани технологии"):

    st.write("""
    - Python
    - Streamlit
    - EasyOCR
    - NumPy
    - Pillow
    """)

with st.expander("🧪 Примерни вредни съставки"):

    for ingredient in harmful_ingredients:

        st.write(
            ingredient + " → " +
            harmful_ingredients[ingredient]
        )
