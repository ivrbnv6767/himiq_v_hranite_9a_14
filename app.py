import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# Настройка на страницата
st.set_page_config(page_title="Food AI Scanner", page_icon="🧪")

# 1. База данни с вредни съставки (Е-номера и думи)
harmful_ingredients = {
    "E621": "Мононатриев глутамат (Овкусител) - Може да причини главоболие и алергии.",
    "E407": "Карагенан (Сгъстител) - Свързва се с възпаления на стомашно-чревния тракт.",
    "E250": "Натриев нитрит (Консервант) - Потенциално канцерогенен в месни продукти.",
    "E951": "Аспартам (Подсладител) - Изкуствен подсладител, избягвайте при чувствителност.",
    "E450": "Дифосфати - Прекомерната употреба вреди на бъбреците и костите.",
    "ПАЛМОВО МАСЛО": "Палмово масло - Високо съдържание на наситени мазнини.",
    "PALM OIL": "Palm Oil - High saturated fat content.",
    "TRANS FAT": "Трансмазнини - Вредни за сърдечно-съдовата система.",
}

# 2. Инициализиране на EasyOCR (Български и Английски)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['bg', 'en'])

reader = load_ocr()

# Интерфейс
st.title("🧪 AI Химия на храните")
st.subheader("Сканирай етикет за вредни съставки")

# Опции за качване
source = st.radio("Избери източник:", ["Качи снимка", "Използвай камера"])
uploaded_file = None

if source == "Качи снимка":
    uploaded_file = st.file_uploader("Избери файл...", type=["jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("Снимай етикета")

if uploaded_file is not None:
    # Показване на снимката
    image = Image.open(uploaded_file)
    st.image(image, caption='Качен етикет', use_container_width=True)
    
    with st.spinner('Анализирам текста с ИИ...'):
        # Конвертиране за OCR
        img_np = np.array(image)
        results = reader.readtext(img_np, detail=0)
        full_text = " ".join(results).upper()
        
        st.write("---")
        st.subheader("🔍 Резултати от анализа:")
        
        found_any = False
        found_list = []
        
        # Търсене на съвпадения
        for key, description in harmful_ingredients.items():
            if key in full_text:
                st.error(f"⚠️ **Намерено: {key}**")
                st.write(description)
                found_list.append(key)
                found_any = True
        
        if not found_any:
            st.success("✅ Не са открити критични вредни съставки от списъка.")
        
        # Показване на целия разпознат текст (по избор)
        with st.expander("Виж целия разпознат текст"):
            st.text(full_text)

        # 3. Алтернативи
        if found_any:
            st.info("💡 **Здравословни алтернативи:**")
            st.write("- Избирайте продукти с по-кратък списък от съставки.")
            st.write("- Търсете био продукти без синтетични консерванти.")
            st.write("- Заменете преработените меса с прясно изпечено месо.")

st.sidebar.markdown("### Проект: Химия на храните\nИзработено с Python & EasyOCR")
