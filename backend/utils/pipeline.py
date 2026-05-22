# from ultralytics import YOLO
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import timm
# import json
# import cv2
# from PIL import Image
# from torchvision import transforms
# from utils.calories import get_calories

# device = "cuda" if torch.cuda.is_available() else "cpu"

# # =========================
# # LOAD MODELS ONCE
# # =========================
# yolo_model = YOLO("models/best.pt")

# with open("models/classes.json", "r") as f:
#     class_names = json.load(f)

# cls_model = timm.create_model("efficientnet_b0", pretrained=False)
# cls_model.classifier = nn.Linear(cls_model.classifier.in_features, len(class_names))
# cls_model.load_state_dict(torch.load("models/classifier.pth", map_location=device))

# cls_model = cls_model.to(device)
# cls_model.eval()

# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # =========================
# # FIX LABEL BUG
# # =========================
# def fix_label(label):
#     if label == "sutar_feni":
#         return "rice"
#     return label

# # =========================
# # MAIN FUNCTION
# # =========================
# def process_image(image_path):
#     image = cv2.imread(image_path)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#     results = yolo_model.predict(image_path, conf=0.1, iou=0.6)

#     output = []
#     total_calories = 0

#     for r in results:
#         for box in r.boxes:
#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             crop = image[y1:y2, x1:x2]
#             if crop.size == 0:
#                 continue

#             pil_img = Image.fromarray(crop)
#             input_tensor = transform(pil_img).unsqueeze(0).to(device)

#             with torch.no_grad():
#                 outputs = cls_model(input_tensor)
#                 probs = F.softmax(outputs, dim=1)

#             idx = torch.argmax(probs).item()
#             label = fix_label(class_names[idx])
#             conf = float(probs[0][idx])

#             cal = get_calories(label)
#             total_calories += cal

#             output.append({
#                 "name": label,
#                 "confidence": round(conf, 2),
#                 "calories": cal
#             })

#     return {
#         "items": output,
#         "total_calories": total_calories
#     }

from ultralytics import YOLO
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
import json
import cv2
from PIL import Image
from torchvision import transforms
from utils.calories import get_calories

device = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# LOAD MODELS ONCE
# =========================
yolo_model = YOLO("models/best.pt")

with open("models/classes.json", "r") as f:
    class_names = json.load(f)

cls_model = timm.create_model("efficientnet_b0", pretrained=False)
cls_model.classifier = nn.Linear(cls_model.classifier.in_features, len(class_names))
cls_model.load_state_dict(torch.load("models/classifier.pth", map_location=device))

cls_model = cls_model.to(device)
cls_model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# =========================
# FIX LABEL BUG
# =========================
def fix_label(label):
    if label == "sutar_feni":
        return "rice"
    return label

# =========================
# MAIN FUNCTION
# =========================
def process_image(image_path):

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = yolo_model.predict(
        image_path,
        conf=0.1,
        iou=0.6
    )

    # 🔥 NEW: store best prediction per class
    best_items = {}

    for r in results:
        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            pil_img = Image.fromarray(crop)
            input_tensor = transform(pil_img).unsqueeze(0).to(device)

            with torch.no_grad():
                outputs = cls_model(input_tensor)
                probs = F.softmax(outputs, dim=1)

            # ✅ KEEP SAME LOGIC (TOP-1)
            idx = torch.argmax(probs).item()
            label = fix_label(class_names[idx])
            conf = float(probs[0][idx])

            # 🔥 KEY FIX: keep only best confidence per class
            if label not in best_items or conf > best_items[label]["confidence"]:
                best_items[label] = {
                    "confidence": conf
                }

    # =========================
    # FINAL OUTPUT
    # =========================
    output = []
    total_calories = 0

    for label, data in best_items.items():

        conf = data["confidence"]
        cal = get_calories(label)

        total_calories += cal

        output.append({
            "name": label,
            "confidence": round(conf, 2),
            "calories": cal
        })

    return {
        "items": output,
        "total_calories": total_calories
    }