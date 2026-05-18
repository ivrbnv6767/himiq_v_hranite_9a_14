import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# 1. Списък с вредни/спорни съставки (на български и английски)
# Можеш да допълваш този списък според нуждите си
HARMFUL_INGREDIENTS = [
    "e621", "е621", # Включени са латинско 'e' и кирилско 'е'
    "палмово масло", "palm oil", "палмова мазнина",
    "мононатриев глутамат", "monosodium glutamate", "msg",
    "аспартам", "aspartame", "e951", "е951",
    "високофруктозен царевичен сироп", "high fructose corn syrup",
    "натриев нитрит", "sodium nitrite", "e250", "е250",
    "bha", "bht", "e320", "e321", "е320", "е321",
    "сукралоза", "sucralose", "e955", "е955",
    "карагенан", "carrageenan", "e407", "е407"
]

# 2. Кеширане на OCR модела, за да не се зарежда при всяко натискане на бутон
@st.cache_resource
def load_reader():
    # Зареждаме моделите за български ('bg') и английски ('en')
    return easyocr.Reader(['bg', 'en'])

reader = load_reader()

# 3. Функция за търсене на вредни съставки в текста
def analyze_text(extracted_text):
    found_harmful = []
    # Обединяваме целия извлечен текст и го правим с малки букви за по-лесно търсене
    text_lower = " ".join(extracted_text).lower()
    
    for ingredient in HARMFUL_INGREDIENTS:
        if ingredient in text_lower:
            found_harmful.append(ingredient)
            
    return found_harmful

# 4. Основен интерфейс на Streamlit
st.set_page_config(page_title="Скенер за етикети", page_icon="🔍", layout="centered")

st.title("🔍 Скенер за вредни съставки")
st.write("Снимай или качи снимка на етикета със съставките, за да провериш за наличието на вредни добавки.")

# Избор на метод за добавяне на снимка
option = st.radio("Как искаш да добавиш снимката?", ("Качване на файл", "Снимка от камерата"))

image_file = None

if option == "Качване на файл":
    image_file = st.file_uploader("Избери снимка (JPG, PNG)", type=["jpg", "jpeg", "png"])
else:
    image_file = st.camera_input("Направи снимка на етикета")

# Ако потребителят е предоставил снимка
if image_file is not None:
    # Отваряне и показване на снимката
    image = Image.open(image_file)
    st.image(image, caption="Заредена снимка", use_container_width=True)
    
    with st.spinner("Анализиране на текста... моля, изчакайте (може да отнеме няколко секунди)."):
        # Преобразуване на изображението в numpy масив, както изисква EasyOCR
        img_array = np.array(image)
        
        # Извличане на текста (detail=0 връща само списък със стрингове, без координати)
        results = reader.readtext(img_array, detail=0)
        
        st.divider()
        
        # Показване на извлечения текст (полезно за проверка дали OCR се е справил добре)
        with st.expander("Виж извлечения текст (Raw Text)"):
            full_text = " ".join(results)
            st.write(full_text)
        
        # Анализ за вредни съставки
        st.subheader("Резултати от анализа:")
        harmful_found = analyze_text(results)
        
        if harmful_found:
            st.error("⚠️ **Внимание! Открити са следните потенциално вредни съставки:**")
            # Използваме set(), за да премахнем дубликати, ако съставката е спомената два пъти
            for item in set(harmful_found):
                st.write(f"- {item.capitalize()}")
        else:
            if len(results) == 0:
                st.warning("Не беше открит никакъв текст на снимката. Опитай да снимаш по-отблизо или на по-добра светлина.")
            else:
                st.success("✅ Не са открити познати вредни съставки от нашия списък!")
                
st.markdown("---")
st.caption("ℹ️ **Забележка:** Този инструмент използва изкуствен интелект (OCR) за четене на текста и може да допуска грешки, особено при размазани снимки или дребен шрифт. Списъкът с вредни съставки не е изчерпателен. Винаги четете етикета лично!")
