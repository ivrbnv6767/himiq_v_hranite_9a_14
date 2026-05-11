# app.py

import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# -----------------------------------
# НАСТРОЙКИ НА СТРАНИЦАТА
# -----------------------------------

st.set_page_config(
    page_title="AI Food Scanner",
    page_icon="🧪",
    layout="centered"
)

# -----------------------------------
# ЗАГЛАВИЕ
# -----------------------------------

st.title("🧪 AI Скенер за вредни съставки")

st.write("""
Това приложение използва:
- Streamlit
- EasyOCR
- NumPy
- Pillow

за разпознаване на вредни съставки в храните.
""")

# -----------------------------------
# ВРЕДНИ СЪСТАВКИ
# -----------------------------------

harmful = {
    "E621": "Мононатриев глутамат",
    "E250": "Натриев нитрит",
    "E951": "Аспартам",
    "E211": "Натриев бензоат",
    "PALM OIL": "Палмово масло",
    "HYDROGENATED": "Хидрогенирани мазнини"
}

# -----------------------------------
# EASYOCR
# -----------------------------------

@st.cache_resource
def load_ocr():
    return easyocr.Reader(["bg", "en"], gpu=False)

reader = load_ocr()

# -----------------------------------
# ИЗБОР НА ИЗТОЧНИК
# -----------------------------------

choice = st.radio(
    "Изберете:",
    ["📁 Качване на снимка", "📷 Камера"]
)

image = None

# -----------------------------------
# FILE UPLOAD
# -----------------------------------

if choice == "📁 Качване на снимка":

    file = st.file_uploader(
        "Качи снимка",
        type=["jpg", "jpeg", "png"]
    )

    if file is not None:
        image = Image.open(file)

# -----------------------------------
# CAMERA
# -----------------------------------

if choice == "📷 Камера":

    camera = st.camera_input("Направи снимка")

    if camera is not None:
        image = Image.open(camera)

# -----------------------------------
# ПОКАЗВАНЕ НА СНИМКА
# -----------------------------------

if image is not None:

    st.image(image, caption="Избрана снимка")

    # -----------------------------------
    # OCR БУТОН
    # -----------------------------------

    if st.button("🔍 Сканирай"):

        with st.spinner("EasyOCR разпознава текста..."):

            # PIL -> NumPy
            img_array = np.array(image)

            # OCR
            result = reader.readtext(
                img_array,
                detail=0
            )

            # Текст
            text = " ".join(result)

            # -----------------------------------
            # ПОКАЗВАНЕ НА ТЕКСТА
            # -----------------------------------

            st.subheader("📄 Разпознат текст")

            st.write(text)

            # -----------------------------------
            # ТЪРСЕНЕ НА ВРЕДНИ СЪСТАВКИ
            # -----------------------------------

            st.subheader("⚠️ Намерени вредни съставки")

            text_upper = text.upper()

            found = False

            for item in harmful:

                if item in text_upper:

                    found = True

                    st.error(
                        item + " → " + harmful[item]
                    )

            if found is False:

                st.success(
                    "Няма открити вредни съставки."
                )

# -----------------------------------
# ИНФОРМАЦИЯ
# -----------------------------------

with st.expander("ℹ️ Как работи приложението?"):

    st.write("""
1. Качвате снимка
2. EasyOCR разпознава текста
3. Приложението търси вредни Е-та
4. Показва резултатите
""")

with st.expander("🧪 Примерни вредни съставки"):

    for item in harmful:

        st.write(
            item + " → " + harmful[item]
        )

# -----------------------------------
# FOOTER
# -----------------------------------

st.markdown("---")

st.caption(
    "Проект: Как ИИ помага да разберем химията на храните"
)
