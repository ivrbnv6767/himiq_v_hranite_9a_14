# app.py
import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import pandas as pd
import re

# -----------------------------------
# Настройки на страницата
# -----------------------------------
st.set_page_config(
    page_title="Food Ingredient Scanner",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 Food Ingredient Scanner")
st.write("Качи снимка или направи снимка с камера за разпознаване на съставки.")

# -----------------------------------
# Опасни / нежелани съставки
# -----------------------------------
harmful_ingredients = {
    "e621": "Мононатриев глутамат (MSG)",
    "msg": "Мононатриев глутамат (MSG)",
    "palm oil": "Палмово масло",
    "палмово масло": "Палмово масло",
    "e102": "Тартразин",
    "e110": "Sunset Yellow",
    "e211": "Натриев бензоат",
    "aspartame": "Аспартам",
    "аспартам": "Аспартам",
    "high fructose corn syrup": "HFCS",
    "hfcs": "HFCS",
    "e250": "Натриев нитрит",
    "e951": "Аспартам",
    "e330": "Лимонена киселина"
}

# -----------------------------------
# Зареждане на OCR модел
# -----------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_reader()

# -----------------------------------
# Вход от файл или камера
# -----------------------------------
uploaded_file = st.file_uploader(
    "📁 Качи изображение",
    type=["png", "jpg", "jpeg"]
)

camera_image = st.camera_input("📷 Или направи снимка")

image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)

elif camera_image is not None:
    image = Image.open(camera_image)

# -----------------------------------
# OCR обработка
# -----------------------------------
if image is not None:

    st.image(image, caption="Избрано изображение", use_container_width=True)

    img_array = np.array(image)

    with st.spinner("🔍 Разпознаване на текст..."):
        results = reader.readtext(img_array, detail=0)

    extracted_text = " ".join(results)

    st.subheader("📄 Разпознат текст")
    st.text_area(
        "OCR Резултат",
        extracted_text,
        height=200
    )

    # -----------------------------------
    # Търсене на вредни съставки
    # -----------------------------------
    found_ingredients = []

    text_lower = extracted_text.lower()

    for ingredient, description in harmful_ingredients.items():

        pattern = r'\b' + re.escape(ingredient.lower()) + r'\b'

        if re.search(pattern, text_lower):
            found_ingredients.append({
                "Съставка": ingredient,
                "Описание": description
            })

    st.subheader("⚠️ Открити потенциално вредни съставки")

    if found_ingredients:
        df = pd.DataFrame(found_ingredients)
        st.dataframe(df, use_container_width=True)

        st.error(
            f"Намерени са {len(found_ingredients)} потенциално нежелани съставки."
        )

    else:
        st.success("Не са открити опасни съставки.")

# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.header("ℹ️ Информация")

st.sidebar.write("""
Приложението използва:
- Streamlit
- EasyOCR
- OCR разпознаване на български и английски
- Проверка за вредни съставки
""")
