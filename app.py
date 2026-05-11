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
import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import io

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🔍 Ingredient Scanner",
    page_icon="🧪",
    layout="centered",
)

# ─── Translations ────────────────────────────────────────────────────────────
TEXTS = {
    "bg": {
        "title": "🔍 Скенер на съставки",
        "subtitle": "Качи снимка на етикет, за да провериш за вредни съставки",
        "upload_tab": "📁 Качи снимка",
        "camera_tab": "📷 Камера",
        "upload_label": "Избери снимка (jpg, jpeg, png)",
        "camera_label": "Снимай етикета",
        "analyze_btn": "🔎 Анализирай",
        "ocr_title": "📄 Разпознат текст",
        "no_text": "Не е разпознат текст. Опитай с по-ясна снимка.",
        "harmful_title": "⚠️ Открити вредни съставки",
        "clean_title": "✅ Не са открити вредни съставки",
        "clean_msg": "Продуктът изглежда чист!",
        "ingredient": "Съставка",
        "reason": "Причина",
        "found_in": "Намерено в текста",
        "spinner": "Анализираме...",
        "ocr_spinner": "Разпознаване на текст...",
        "lang_label": "Език на интерфейса",
        "severity_high": "🔴 Висок риск",
        "severity_medium": "🟡 Умерен риск",
        "severity_low": "🟢 Нисък риск",
        "no_image": "Моля, качи или снимай изображение.",
    },
    "en": {
        "title": "🔍 Ingredient Scanner",
        "subtitle": "Upload a label photo to check for harmful ingredients",
        "upload_tab": "📁 Upload image",
        "camera_tab": "📷 Camera",
        "upload_label": "Choose an image (jpg, jpeg, png)",
        "camera_label": "Take a photo of the label",
        "analyze_btn": "🔎 Analyze",
        "ocr_title": "📄 Recognized text",
        "no_text": "No text recognized. Try a clearer image.",
        "harmful_title": "⚠️ Harmful ingredients detected",
        "clean_title": "✅ No harmful ingredients found",
        "clean_msg": "The product looks clean!",
        "ingredient": "Ingredient",
        "reason": "Reason",
        "found_in": "Found in text",
        "spinner": "Analyzing...",
        "ocr_spinner": "Running OCR...",
        "lang_label": "Interface language",
        "severity_high": "🔴 High risk",
        "severity_medium": "🟡 Moderate risk",
        "severity_low": "🟢 Low risk",
        "no_image": "Please upload or capture an image.",
    },
}

# ─── Harmful ingredients database ────────────────────────────────────────────
HARMFUL = [
    # E-numbers
    {"pattern": r"\bE\s?621\b", "name": "E621 (MSG)", "reason_bg": "Усилвател на вкус — може да причини главоболие и алергии", "reason_en": "Flavor enhancer — may cause headaches and allergies", "severity": "medium"},
    {"pattern": r"\bE\s?951\b", "name": "E951 (Aspartame)", "reason_bg": "Изкуствен подсладител — противоречиви данни за безопасност", "reason_en": "Artificial sweetener — controversial safety data", "severity": "medium"},
    {"pattern": r"\bE\s?950\b", "name": "E950 (Acesulfame K)", "reason_bg": "Изкуствен подсладител — потенциален канцероген", "reason_en": "Artificial sweetener — potential carcinogen", "severity": "medium"},
    {"pattern": r"\bE\s?211\b", "name": "E211 (Sodium Benzoate)", "reason_bg": "Консервант — може да образува бензен при комбинация с витамин C", "reason_en": "Preservative — can form benzene with vitamin C", "severity": "high"},
    {"pattern": r"\bE\s?102\b", "name": "E102 (Tartrazine)", "reason_bg": "Жълт оцветител — може да причини хиперактивност при деца", "reason_en": "Yellow dye — may cause hyperactivity in children", "severity": "medium"},
    {"pattern": r"\bE\s?110\b", "name": "E110 (Sunset Yellow)", "reason_bg": "Оцветител — свързан с хиперактивност и алергии", "reason_en": "Dye — linked to hyperactivity and allergies", "severity": "medium"},
    {"pattern": r"\bE\s?124\b", "name": "E124 (Ponceau 4R)", "reason_bg": "Червен оцветител — подозира се за канцерогенност", "reason_en": "Red dye — suspected carcinogen", "severity": "high"},
    {"pattern": r"\bE\s?129\b", "name": "E129 (Allura Red)", "reason_bg": "Оцветител — хиперактивност при деца", "reason_en": "Dye — hyperactivity in children", "severity": "medium"},
    {"pattern": r"\bE\s?320\b", "name": "E320 (BHA)", "reason_bg": "Антиоксидант — потенциален канцероген", "reason_en": "Antioxidant — potential carcinogen", "severity": "high"},
    {"pattern": r"\bE\s?321\b", "name": "E321 (BHT)", "reason_bg": "Антиоксидант — потенциален канцероген", "reason_en": "Antioxidant — potential carcinogen", "severity": "high"},
    {"pattern": r"\bE\s?250\b", "name": "E250 (Sodium Nitrite)", "reason_bg": "Консервант в месо — може да образува канцерогенни нитрозамини", "reason_en": "Meat preservative — can form carcinogenic nitrosamines", "severity": "high"},
    {"pattern": r"\bE\s?249\b|\bE\s?251\b|\bE\s?252\b", "name": "E249/251/252 (Nitrates)", "reason_bg": "Нитрати — потенциални канцерогени", "reason_en": "Nitrates — potential carcinogens", "severity": "high"},
    # Oils & fats
    {"pattern": r"палмово\s*масло|palm\s*oil", "name": "Палмово масло / Palm oil", "reason_bg": "Наситени мазнини — риск за сърдечно-съдовата система", "reason_en": "Saturated fats — cardiovascular risk", "severity": "medium"},
    {"pattern": r"хидрогенизирано|hydrogenated", "name": "Хидрогенизирани мазнини / Hydrogenated fats", "reason_bg": "Трансмазнини — вредни за сърцето", "reason_en": "Trans fats — harmful to the heart", "severity": "high"},
    {"pattern": r"частично\s*хидрогенизирано|partially\s*hydrogenated", "name": "Частично хидрогенизирани мазнини", "reason_bg": "Трансмазнини — вредни за сърцето", "reason_en": "Trans fats — harmful to the heart", "severity": "high"},
    # Sugars
    {"pattern": r"кукурузен\s*сироп|царевичен\s*сироп|high.?fructose\s*corn\s*syrup|hfcs", "name": "HFCS / Царевичен сироп", "reason_bg": "Високо фруктозен царевичен сироп — свързан с затлъстяване", "reason_en": "High-fructose corn syrup — linked to obesity", "severity": "high"},
    # Flavor enhancers
    {"pattern": r"\bмsg\b|monosodium\s*glutamate|мононатриев\s*глутамат", "name": "MSG (Мононатриев глутамат)", "reason_bg": "Усилвател на вкус — може да причини нежелани реакции", "reason_en": "Flavor enhancer — may cause adverse reactions", "severity": "medium"},
    # Artificial sweeteners
    {"pattern": r"аспартам|aspartame", "name": "Аспартам / Aspartame", "reason_bg": "Изкуствен подсладител — противоречиви данни", "reason_en": "Artificial sweetener — controversial data", "severity": "medium"},
    {"pattern": r"захарин|saccharin", "name": "Захарин / Saccharin", "reason_bg": "Изкуствен подсладител — стар подозрителен канцероген", "reason_en": "Artificial sweetener — formerly suspected carcinogen", "severity": "low"},
    {"pattern": r"сукралоза|sucralose", "name": "Сукралоза / Sucralose", "reason_bg": "Изкуствен подсладител — може да наруши чревната флора", "reason_en": "Artificial sweetener — may disrupt gut flora", "severity": "low"},
    # Preservatives
    {"pattern": r"натриев\s*бензоат|sodium\s*benzoate", "name": "Натриев бензоат / Sodium benzoate", "reason_bg": "Консервант — може да образува бензен", "reason_en": "Preservative — may form benzene", "severity": "high"},
    {"pattern": r"калиев\s*сорбат|potassium\s*sorbate", "name": "Калиев сорбат / Potassium sorbate", "reason_bg": "Консервант — може да е алерген при чувствителни хора", "reason_en": "Preservative — potential allergen for sensitive people", "severity": "low"},
    # Colorings
    {"pattern": r"тартразин|tartrazine", "name": "Тартразин / Tartrazine", "reason_bg": "Оцветител — хиперактивност при деца", "reason_en": "Dye — hyperactivity in children", "severity": "medium"},
    {"pattern": r"карамелен\s*оцветител|caramel\s*color(?:ing)?", "name": "Карамелен оцветител / Caramel color", "reason_bg": "Клас IV може да съдържа 4-MEI — потенциален канцероген", "reason_en": "Class IV may contain 4-MEI — potential carcinogen", "severity": "medium"},
]

# ─── OCR loader (cached) ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_reader():
    return easyocr.Reader(["bg", "en"], gpu=False)

# ─── Core functions ──────────────────────────────────────────────────────────
def run_ocr(image: Image.Image) -> str:
    reader = load_reader()
    arr = np.array(image.convert("RGB"))
    results = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(results)


def find_harmful(text: str, lang: str) -> list[dict]:
    found = []
    text_lower = text.lower()
    for item in HARMFUL:
        match = re.search(item["pattern"], text_lower, re.IGNORECASE)
        if match:
            found.append({
                "name": item["name"],
                "reason": item[f"reason_{lang}"],
                "severity": item["severity"],
                "found": match.group(0),
            })
    return found


def severity_color(sev: str) -> str:
    return {"high": "#ff4b4b", "medium": "#ffa500", "low": "#2ecc71"}.get(sev, "#888")


def severity_label(sev: str, t: dict) -> str:
    return {"high": t["severity_high"], "medium": t["severity_medium"], "low": t["severity_low"]}.get(sev, sev)


# ─── UI ──────────────────────────────────────────────────────────────────────
# Language selector in sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    lang = st.selectbox("🌐 Language / Език", ["bg", "en"], format_func=lambda x: "🇧🇬 Български" if x == "bg" else "🇬🇧 English")
    st.markdown("---")
    st.markdown("**ℹ️ За приложението**" if lang == "bg" else "**ℹ️ About**")
    if lang == "bg":
        st.markdown("Приложението използва **EasyOCR** за разпознаване на текст от снимки на хранителни етикети и търси над **20 вредни съставки**.")
    else:
        st.markdown("This app uses **EasyOCR** to read text from food label photos and scans for over **20 harmful ingredients**.")

t = TEXTS[lang]

st.title(t["title"])
st.caption(t["subtitle"])
st.markdown("---")

# Image source tabs
tab_upload, tab_camera = st.tabs([t["upload_tab"], t["camera_tab"]])

image = None

with tab_upload:
    uploaded = st.file_uploader(t["upload_label"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, use_container_width=True)

with tab_camera:
    cam_photo = st.camera_input(t["camera_label"], label_visibility="collapsed")
    if cam_photo:
        image = Image.open(cam_photo)

# Analyze button
st.markdown("")
analyze = st.button(t["analyze_btn"], type="primary", use_container_width=True)

if analyze:
    if image is None:
        st.warning(t["no_image"])
    else:
        with st.spinner(t["ocr_spinner"]):
            ocr_text = run_ocr(image)

        with st.spinner(t["spinner"]):
            harmful_found = find_harmful(ocr_text, lang)

        # OCR result
        with st.expander(t["ocr_title"], expanded=False):
            if ocr_text.strip():
                st.text_area("", ocr_text, height=160, label_visibility="collapsed")
            else:
                st.info(t["no_text"])

        st.markdown("---")

        # Results
        if harmful_found:
            st.markdown(f"### {t['harmful_title']}")
            for item in harmful_found:
                color = severity_color(item["severity"])
                slabel = severity_label(item["severity"], t)
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border-left: 5px solid {color}; padding: 10px 16px; margin-bottom: 12px;
                                    background: {'rgba(255,75,75,0.07)' if item['severity']=='high' else 'rgba(255,165,0,0.07)' if item['severity']=='medium' else 'rgba(46,204,113,0.07)'};
                                    border-radius: 0 8px 8px 0;">
                            <strong style="font-size:1.05rem">{item['name']}</strong>
                            &nbsp;<span style="color:{color}; font-size:0.85rem">{slabel}</span><br>
                            <span style="color:#888; font-size:0.85rem">{t['reason']}: </span>{item['reason']}<br>
                            <span style="color:#888; font-size:0.85rem">{t['found_in']}: </span><code>{item['found']}</code>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.success(f"### {t['clean_title']}\n{t['clean_msg']}")

st.markdown("---")
st.caption("Powered by EasyOCR • Made with Streamlit")
