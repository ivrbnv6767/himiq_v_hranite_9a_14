# app.py
import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import tempfile
import cv2

# -----------------------------------
# Конфигурация
# -----------------------------------
st.set_page_config(
    page_title="Food Ingredient Scanner",
    layout="centered"
)

# -----------------------------------
# Опасни / нежелани съставки
# -----------------------------------
HARMFUL_INGREDIENTS = {
    "E621": {
        "bg": "Мононатриев глутамат (MSG)",
        "en": "Monosodium glutamate (MSG)"
    },
    "PALM OIL": {
        "bg": "Палмово масло",
        "en": "Palm oil"
    },
    "E250": {
        "bg": "Натриев нитрит",
        "en": "Sodium nitrite"
    },
    "E951": {
        "bg": "Аспартам",
        "en": "Aspartame"
    },
    "E211": {
        "bg": "Натриев бензоат",
        "en": "Sodium benzoate"
    },
    "HYDROGENATED": {
        "bg": "Хидрогенирани мазнини",
        "en": "Hydrogenated fats"
    }
}

# -----------------------------------
# Зареждане на OCR модела
# -----------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_reader()

# -----------------------------------
# UI
# -----------------------------------
st.title("🧾 Food Ingredient Scanner")
st.write("Разпознаване на съставки от снимка и откриване на вредни добавки.")

# -----------------------------------
# Източник на изображение
# -----------------------------------
source = st.radio(
    "Изберете източник:",
    ["Качване на снимка", "Камера"]
)

image = None

if source == "Качване на снимка":
    uploaded_file = st.file_uploader(
        "Качи изображение",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

elif source == "Камера":
    camera_image = st.camera_input("Направи снимка")

    if camera_image is not None:
        image = Image.open(camera_image)

# -----------------------------------
# OCR обработка
# -----------------------------------
if image is not None:
    st.image(image, caption="Избрано изображение", use_container_width=True)

    if st.button("🔍 Сканирай"):
        with st.spinner("Разпознаване на текст..."):

            # PIL -> NumPy
            img_np = np.array(image)

            # OCR
            results = reader.readtext(img_np, detail=0)

            extracted_text = " ".join(results)

            st.subheader("📄 Разпознат текст")
            st.write(extracted_text)

            # -----------------------------------
            # Търсене на вредни съставки
            # -----------------------------------
            normalized_text = extracted_text.upper()

            found = []

            for ingredient_key, translations in HARMFUL_INGREDIENTS.items():
                pattern = re.escape(ingredient_key)

                if re.search(pattern, normalized_text):
                    found.append(translations)

            st.subheader("⚠️ Открити рискови съставки")

            if found:
                for item in found:
                    st.error(
                        f"🇧🇬 {item['bg']}\n\n🇬🇧 {item['en']}"
                    )
            else:
                st.success("Няма открити опасни съставки.")

# -----------------------------------
# Информация
# -----------------------------------
with st.expander("ℹ️ Поддържани езици"):
    st.write("""
    - Български
    - English
    """)

with st.expander("⚠️ Примерни вредни съставки"):
    for key, val in HARMFUL_INGREDIENTS.items():
        st.write(f"- {key}: {val['bg']} / {val['en']}")
