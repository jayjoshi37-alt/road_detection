from ultralytics import YOLO
import cv2
import numpy as np


class PotholeDetector:
    def __init__(
        self,
        model_path="model/pothole_model.pt",
        conf=0.02,
        base_rate=18000,
        area_multiplier=220000,
        min_cost_per_pothole=20000,
        max_cost_per_pothole=150000,
    ):
        self.model = YOLO(model_path)
        self.conf = conf
        self.base_rate = base_rate
        self.area_multiplier = area_multiplier
        self.min_cost_per_pothole = min_cost_per_pothole
        self.max_cost_per_pothole = max_cost_per_pothole

    # ---------------------------------------------------
    # MAIN DETECTION (NUMPY IMAGE INPUT)
    # ---------------------------------------------------
    def detect_pothole_from_image(self, img):
        if img is None or not isinstance(img, np.ndarray):
            return {
                "detected": False,
                "count": 0,
                "detections": []
            }

        img = img.copy()

        results = self.model(
            source=img,        # ✅ explicit source
            conf=self.conf,
            verbose=False
        )

        detections = []

        if results and results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                detections.append({
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                })

        return {
            "detected": len(detections) > 0,
            "count": len(detections),
            "detections": detections
        }

    # ---------------------------------------------------
    # ✅ NEW: GET BOXES (FIXES YOUR ERROR)
    # ---------------------------------------------------
    def get_boxes(self, detections):
        """
        Keeps compatibility with existing code
        """
        return detections

    # ---------------------------------------------------
    # DRAW BOXES (NUMPY IMAGE)
    # ---------------------------------------------------
    def draw_boxes(self, image, boxes):
        if image is None:
            return image

        img = image.copy()

        for b in boxes:
            cv2.rectangle(
                img,
                (b["x1"], b["y1"]),
                (b["x2"], b["y2"]),
                (0, 0, 255),
                2
            )
            cv2.putText(
                img,
                "POTHOLE",
                (b["x1"], b["y1"] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        return img

    # ---------------------------------------------------
    # COST ESTIMATION
    # ---------------------------------------------------
    def estimate_cost(self, boxes, image_shape=None):
        if not boxes:
            return 0

        img_area = None
        try:
            if image_shape is not None and len(image_shape) >= 2:
                img_area = float(image_shape[0]) * float(image_shape[1])
        except Exception:
            img_area = None

        total_cost = 0
        for b in boxes:
            w = max(1, int(b["x2"]) - int(b["x1"]))
            h = max(1, int(b["y2"]) - int(b["y1"]))

            if img_area:
                severity = (float(w) * float(h)) / img_area
                cost = int(self.base_rate + (severity * self.area_multiplier))
            else:
                cost = int(self.base_rate)

            if cost < int(self.min_cost_per_pothole):
                cost = int(self.min_cost_per_pothole)
            if cost > int(self.max_cost_per_pothole):
                cost = int(self.max_cost_per_pothole)

            total_cost += cost

        return int(total_cost)
