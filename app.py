# app.py

import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# ---------------------------------
# НАСТРОЙКИ НА СТРАНИЦАТА
# ---------------------------------

st.set_page_config(
    page_title="Скенер за вредни храни",
    page_icon="🧪",
    layout="centered"
)

# ---------------------------------
# ЗАГЛАВИЕ
# ---------------------------------

st.title("🧪 AI Скенер за вредни съставки")
st.write(
    "Приложение, което използва EasyOCR и изкуствен интелект "
    "за разпознаване на вредни съставки в храните."
)

# ---------------------------------
# ВРЕДНИ СЪСТАВКИ
# ---------------------------------

harmful_ingredients = {
    "E621": {
        "bg": "Мононатриев глутамат",
        "en": "Monosodium Glutamate",
        "danger": "Може да предизвика главоболие и алергии."
    },

    "E250": {
        "bg": "Натриев нитрит",
        "en": "Sodium Nitrite",
        "danger": "Използва се в колбаси и може да бъде вреден."
    },

    "E951": {
        "bg": "Аспартам",
        "en": "Aspartame",
        "danger": "Изкуствен подсладител."
    },

    "PALM OIL": {
        "bg": "Палмово масло",
        "en": "Palm Oil",
        "danger": "Съдържа наситени мазнини."
    },

    "E211": {
        "bg": "Натриев бензоат",
        "en": "Sodium Benzoate",
        "danger": "Консервант, който може да бъде вреден."
    },

    "HYDROGENATED": {
        "bg": "Хидрогенирани мазнини",
        "en": "Hydrogenated Fats",
        "danger": "Повишават риска от сърдечни заболявания."
    }
}

# ---------------------------------
# OCR МОДЕЛ
# ---------------------------------

@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_reader()

# ---------------------------------
# ИЗБОР НА ИЗТОЧНИК
# ---------------------------------

option = st.radio(
    "Изберете начин за сканиране:",
    ["📁 Качване на снимка", "📷 Камера"]
)

image = None

# ---------------------------------
# КАЧВАНЕ НА СНИМКА
# ---------------------------------

if option == "📁 Качване на снимка":

    uploaded_file = st.file_uploader(
        "Качете снимка на етикет",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# ---------------------------------
# КАМЕРА
# ---------------------------------

if option == "📷 Камера":

    camera_photo = st.camera_input("Направете снимка")

    if camera_photo is not None:
        image = Image.open(camera_photo)

# ---------------------------------
# ОБРАБОТКА
# ---------------------------------

if image is not None:

    st.image(image, caption="Избрана снимка", use_container_width=True)

    if st.button("🔍 Анализирай"):

        with st.spinner("EasyOCR разпознава текста..."):

            # Превръщане в numpy масив
            image_np = np.array(image)

            # OCR
            results = reader.readtext(image_np, detail=0)

            # Обединяване на текста
            text = " ".join(results)

            st.subheader("📄 Разпознат текст")
            st.write(text)

            # ---------------------------------
            # ТЪРСЕНЕ НА ВРЕДНИ СЪСТАВКИ
            # ---------------------------------

            st.subheader("⚠️ Открити вредни съставки")

            text_upper = text.upper()

            found = False

            for ingredient, info in harmful_ingredients.items():

                if ingredient in text_upper:

                    found = True

                    st.error(
                        f"""
🇧🇬 {info['bg']}

🇬🇧 {info['en']}

⚠️ {info['danger']}
"""
                    )

            if not found:
                st.success("Няма открити вредни съставки.")

# ---------------------------------
# ИНФОРМАЦИЯ
# ---------------------------------

with st.expander("ℹ️ Как работи приложението?"):

    st.write("""
1. Качвате снимка или използвате камера.
2. EasyOCR разпознава текста от етикета.
3. Приложението търси вредни Е-та и съставки.
4. Показва предупреждения на екрана.
""")

with st.expander("📚 Използвани технологии"):

    st.write("""
- Python
- Streamlit
- EasyOCR
- Pillow
- NumPy
""")

with st.expander("🧪 Примерни вредни съставки"):

    for ingredient, info in harmful_ingredients.items():

        st.write(
            f"• {ingredient} → {info['bg']} / {info['en']}"
        )

# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.caption(
    "Проект: Как ИИ помага да разберем химията на храните"
)
