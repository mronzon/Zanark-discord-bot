import cv2
import pytesseract
import numpy as np
import re

# Paramètres
# Configuration de pytesseract (ajustez le chemin si nécessaire)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_scores(image_path):
  # Charger l'image
  img = cv2.imread(image_path)
  if img is None:
      raise FileNotFoundError(f"Image non trouvée: {image_path}")

  # Convertir en niveaux de gris
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  # Binarisation adaptative
  thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 31, 15)

  # Trouver les contours (pour détecter les zones de scores)
  contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # Filtrer les contours à droite (scores)
  height, width = img.shape[:2]
  score_boxes = []
  for cnt in contours:
      x, y, w, h = cv2.boundingRect(cnt)
      if w > 80 and h > 20 and x > width * 0.7:
          score_boxes.append((x, y, w, h))

  # Trier les boxes du haut vers le bas
  score_boxes = sorted(score_boxes, key=lambda b: b[1])

  results = []
  for i, (x, y, w, h) in enumerate(score_boxes):
      # Extraction score avec marge réduite pour éviter les artefacts
      margin = 5
      roi_score = gray[y+margin:y+h-margin, x+margin:x+w-margin]
      roi_score = cv2.threshold(roi_score, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
      
      config_score = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
      text_score = pytesseract.image_to_string(roi_score, config=config_score)
      
      # Nettoyage du score : si il y a un espace, prendre seulement la partie après l'espace
      if ' ' in text_score:
          score_raw = text_score.split(' ')[-1]  # Prendre la dernière partie après l'espace
      else:
          score_raw = text_score
      
      score = ''.join(filter(str.isdigit, score_raw))

      # Extraction nom à gauche du score
      name_x1 = max(0, x - 1000)
      name_x2 = x - 10
      roi_name = gray[y:y+h, name_x1:name_x2]
      roi_name = cv2.threshold(roi_name, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
      
      config_name = r'--oem 3 --psm 7'
      text_name = pytesseract.image_to_string(roi_name, config=config_name)
      # Nettoyage du nom : extraire le premier mot de 3+ lettres sans caractères spéciaux
      matches = re.findall(r'[A-Za-zÀ-ÿ0-9]{3,}', text_name)
      name = matches[0] if matches else ''

      if score and name:
          results.append((name, int(score)))
  return results

