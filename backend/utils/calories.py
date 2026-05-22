calories = {
    "rice": 130,
    "chapati": 120,
    "bhatura": 300,
    "naan": 260,
    "butter_chicken": 490,
    "paneer_butter_masala": 450,
    "palak_paneer": 350,
    "kadai_paneer": 400,
    "dal_makhani": 330,
    "dal_tadka": 250,
    "biryani": 290,
    "poha": 180,
    "jalebi": 150,
    "gulab_jamun": 175,
    "rasgulla": 120,
    "default": 200
}

def get_calories(label):
    return calories.get(label, calories["default"])