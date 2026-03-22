import streamlit as st
import cv2
import numpy as np
import easyocr
from PIL import Image
from streamlit_lottie import st_lottie
import requests

# --- CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="NutriHealthAI", page_icon="🥗", layout="wide")

# Custom CSS for modern UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #2E7D32;
        color: white;
    }
    .card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

@st.cache_resource
def load_ocr_reader():
    # This will download the model on first run
    return easyocr.Reader(['en'])

# Database of common ingredients
INGREDIENT_DB = {
    "sugar": {"impact": "Red", "desc": "High glycemic index, spikes insulin.", "hindi": "चीनी: उच्च ग्लाइसेमिक इंडेक्स, इंसुलिन बढ़ाता है।", "bad_for": ["Diabetes", "PCOS", "PCOD"]},
    "sucrose": {"impact": "Red", "desc": "Hidden sugar, bad for metabolism.", "hindi": "सुक्रोज: छिपी हुई चीनी, मेटाबॉलिज्म के लिए खराब।", "bad_for": ["Diabetes"]},
    "salt": {"impact": "Yellow", "desc": "High sodium can increase blood pressure.", "hindi": "नमक: उच्च सोडियम रक्तचाप बढ़ा सकता है।", "bad_for": ["Thyroid"]},
    "sodium": {"impact": "Yellow", "desc": "Excessive intake causes water retention.", "hindi": "सोडियम: अधिक सेवन से शरीर में पानी की अधिकता हो जाती है।", "bad_for": ["Thyroid"]},
    "palm oil": {"impact": "Red", "desc": "High saturated fat, bad for heart.", "hindi": "पाम तेल: उच्च संतृप्त वसा, हृदय के लिए खराब।", "bad_for": ["None"]},
    "maltodextrin": {"impact": "Red", "desc": "Very high GI, worse than sugar.", "hindi": "माल्टोडेक्सट्रिन: बहुत अधिक जीआई, चीनी से भी बदतर।", "bad_for": ["Diabetes", "PCOS"]},
    "maida": {"impact": "Red", "desc": "Refined flour, lacks fiber.", "hindi": "मैदा: परिष्कृत आटा, फाइबर की कमी।", "bad_for": ["Diabetes", "PCOS", "PCOD"]},
    "wheat": {"impact": "Green", "desc": "Good source of fiber if whole grain.", "hindi": "गेहूं: साबुत अनाज होने पर फाइबर का अच्छा स्रोत।", "bad_for": []},
    "soy": {"impact": "Yellow", "desc": "Process soy can affect hormones.", "hindi": "सोया: प्रोसेस्ड सोया हार्मोन को प्रभावित कर सकता है।", "bad_for": ["Thyroid"]},
    "iron": {"impact": "Green", "desc": "Essential for blood production.", "hindi": "लोहा: रक्त उत्पादन के लिए आवश्यक।", "bad_for": []},
    "vitamin c": {"impact": "Green", "desc": "Boosts immunity.", "hindi": "विटामिन सी: इम्युनिटी बढ़ाता है।", "bad_for": []},
}

# --- SIDEBAR SETTINGS ---
st.sidebar.title("NutriHealth Settings")
lang = st.sidebar.radio("Language / भाषा", ["English", "Hindi"])
disease = st.sidebar.selectbox(
    "Lifestyle Disease / रोग",
    ["None", "Diabetes", "Thyroid", "PCOS", "PCOD", "Anemia"]
)

# Translations
TEXT = {
    "English": {
        "title": "NutriHealthAI",
        "subtitle": "Smart Food Label Analyzer for Healthy Living",
        "upload": "Upload Food Label",
        "analyze": "Start Analysis",
        "result_title": "Analysis Report",
        "score": "Health Rating",
        "scanning": "AI is reading the label...",
    },
    "Hindi": {
        "title": "न्यूट्रिहेल्थ एआई",
        "subtitle": "स्वस्थ जीवन के लिए स्मार्ट फूड लेबल विश्लेषक",
        "upload": "फूड लेबल अपलोड करें",
        "analyze": "विश्लेषण शुरू करें",
        "result_title": "विश्लेषण रिपोर्ट",
        "score": "स्वास्थ्य रेटिंग",
        "scanning": "एआई लेबल पढ़ रहा है...",
    }
}
t = TEXT[lang]

# --- MAIN PAGE UI ---
st.markdown(f"<h1 class='main-title'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# Lottie Animation with Error Handling
lottie_url = "https://lottie.host/790757d2-7d0e-473d-8869-797305943a4e/S0mDbeuS6y.json"
lottie_json = load_lottieurl(lottie_url)

col1, col2 = st.columns([1, 1])

with col1:
    if lottie_json:
        st_lottie(lottie_json, height=300, key="health_anim")
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2424/2424388.png", width=200)

with col2:
    st.write(f"### {t['upload']}")
    img_file = st.file_uploader("", type=['jpg', 'png', 'jpeg'])
    camera_file = st.camera_input("OR Take Photo")

input_file = img_file if img_file else camera_file

# --- PROCESSING ---
if input_file:
    image = Image.open(input_file)
    st.image(image, caption="Target Label", width=300)
    
    if st.button(t['analyze']):
        with st.spinner(t['scanning']):
            # 1. OCR Extraction
            reader = load_ocr_reader()
            img_np = np.array(image)
            results = reader.readtext(img_np)
            raw_text = " ".join([res[1].lower() for res in results])
            
            # 2. Analysis Logic
            found = []
            final_score = 10
            
            for key, info in INGREDIENT_DB.items():
                if key in raw_text:
                    impact = info['impact']
                    # Condition for Disease
                    if disease in info['bad_for']:
                        impact = "Red"
                    
                    found.append({
                        "name": key.title(),
                        "impact": impact,
                        "desc": info['hindi'] if lang == "Hindi" else info['desc']
                    })
                    
                    if impact == "Red": final_score -= 2
                    elif impact == "Yellow": final_score -= 1

            final_score = max(0, final_score)

            # 3. UI Results
            st.markdown(f"## {t['result_title']}")
            st.metric(label=t['score'], value=f"{final_score} / 10")
            st.progress(final_score * 10)

            if not found:
                st.warning("No ingredients identified. Please try a clearer photo.")
            else:
                for item in found:
                    bg_color = "#FFEBEE" if item['impact'] == "Red" else "#FFF9C4" if item['impact'] == "Yellow" else "#E8F5E9"
                    border_color = "#D32F2F" if item['impact'] == "Red" else "#FBC02D" if item['impact'] == "Yellow" else "#2E7D32"
                    
                    st.markdown(f"""
                        <div class="card" style="background-color: {bg_color}; border-left: 8px solid {border_color};">
                            <h4 style="margin:0; color: {border_color};">{item['name']} - {item['impact']}</h4>
                            <p style="margin:5px 0;">{item['desc']}</p>
                        </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Disclaimer: This tool is for informational purposes and not a substitute for medical advice.")