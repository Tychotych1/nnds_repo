import os
import numpy as np
import cv2
import mrcnn.config
import mrcnn.utils
from mrcnn.model import MaskRCNN
from pathlib import Path


# Configuratie die wordt gebruikt door de bibliotheek Mask-RCNN
class MaskRCNNConfig(mrcnn.config.Config):
	NAME = "coco_pretrained_model_config"
	IMAGES_PER_GPU = 1
	GPU_COUNT = 1
	NUM_CLASSES = 1 + 80  # COCO-gegevensset heeft 80 klassen + één achtergrondklasse
	DETECTION_MIN_CONFIDENCE = 0.6


# Filter een lijst met maskeer R-CNN detectieresultaten om alleen de gedetecteerde auto's / vrachtwagens te krijgen
def get_car_boxes(boxes, class_ids):
	car_boxes = []

	for i, box in enumerate(boxes):
		# Als het gedetecteerde object geen auto / vrachtwagen is, slaat u het over
		if class_ids[i] in [3, 8, 6]:
			car_boxes.append(box)

	return np.array(car_boxes)


# Hoofddirectory van het project
ROOT_DIR = Path(".")

# Directory om logboeken en getraind model op te slaan
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Lokaal pad naar bestand met getrainde gewichten
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Download COCO getrainde gewichten van releases indien nodig
if not os.path.exists(COCO_MODEL_PATH):
	mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

# Directory van afbeeldingen om detectie uit te voeren
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

# Te verwerken videobestand of camera / zet op 0 voor webcam
VIDEO_SOURCE = "images/test.jpg"

# Maak een Mask-RCNN-model in de inferentiemodus
model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=MaskRCNNConfig())

# Laad vooraf opgeleid model
model.load_weights(COCO_MODEL_PATH, by_name=True)

# Locatie van parkeerplaatsen
parked_car_boxes = None

# Laad het videobestand waarop we detectie willen uitvoeren
video_capture = cv2.VideoCapture(VIDEO_SOURCE)

# Loop over elk videoframe
while video_capture.isOpened():
	success, frame = video_capture.read()
	if not success:
		break

	# Converteer de afbeelding van BGR-kleur (die OpenCV gebruikt) naar RGB-kleur
	rgb_image = frame[:, :, ::-1]

	# Voer de afbeelding door het masker R-CNN-model om resultaten te krijgen.
	results = model.detect([rgb_image], verbose=0)

	# Masker R-CNN gaat ervan uit dat we detectie uitvoeren op meerdere afbeeldingen.
	# We hebben slechts één afbeelding gepasseerd om te detecteren, dus pak alleen het eerste resultaat.
	r = results[0]

	# De variabele r heeft nu de resultaten van detectie:
	# - r ['rois'] zijn het selectiekader van elk gedetecteerd object
	# - r ['class_ids'] zijn de klasse-id (type) van elk gedetecteerd object
	# - r ['scores'] zijn de betrouwbaarheidsscores voor elke detectie
	# - r ['maskers'] zijn de objectmaskers voor elk gedetecteerd object (waarmee u de objectomtrek krijgt)

	# Filter de resultaten om alleen de begrenzingsboxen voor auto / vrachtwagen te pakken
	car_boxes = get_car_boxes(r['rois'], r['class_ids'])

	print("Cars found in frame of video:")

	# Teken elk vak op het frame
	for box in car_boxes:
		print("Car: ", box)

		y1, x1, y2, x2 = box

		# Teken het frame
		cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

	# Laat het videoframe op het scherm zien
	cv2.imshow('Video', frame)
	cv2.imwrite('images/export_image.jpg', frame)

	# Druk op 'q' om te stoppen
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Verwijder alles wanneer je klaar bent
video_capture.release()
cv2.destroyAllWindows()
