from ultralytics import YOLO
import cv2
import numpy as np


class CrackDetector:
    def __init__(
        self,
        model_path="model/crack4.pt",
        conf=0.30,
        base_rate=18000,
        severity_multiplier=220000,
        min_cost_per_crack=20000,
        max_cost_per_crack=150000,
    ):
        self.model = YOLO(model_path)
        self.conf = conf
        self.base_rate = base_rate
        self.severity_multiplier = severity_multiplier
        self.min_cost_per_crack = min_cost_per_crack
        self.max_cost_per_crack = max_cost_per_crack

    # ---------------------------------------------------
    # MAIN DETECTION (BOX-BASED + DYNAMIC COST)
    # ---------------------------------------------------
    def detect_crack_from_image(self, img):
        if img is None or not isinstance(img, np.ndarray):
            return {
                "detected": False,
                "count": 0,
                "total_cost": 0,
                "boxes": []
            }

        img = img.copy()
        img_h = img.shape[0]

        results = self.model(
            source=img,
            conf=self.conf,
            imgsz=1024,
            verbose=False
        )[0]

        boxes = []
        total_cost = 0

        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                height = max(1, y2 - y1)  # avoid division by zero

                # ----------------------------
                # DYNAMIC COST CALCULATION
                # ----------------------------
                severity = height / img_h   # 0 → 1
                cost = int(self.base_rate + (severity * self.severity_multiplier))

                if cost < int(self.min_cost_per_crack):
                    cost = int(self.min_cost_per_crack)
                if cost > int(self.max_cost_per_crack):
                    cost = int(self.max_cost_per_crack)

                total_cost += cost

                boxes.append({
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "height": height,
                    "severity": round(severity, 3),
                    "cost": cost
                })

        crack_count = len(boxes)

        return {
            "detected": crack_count > 0,
            "count": crack_count,
            "total_cost": total_cost,
            "boxes": boxes,
            "results": results      # ✅ keep results for compatibility
        }

    # ---------------------------------------------------
    # DRAW PLAIN BOUNDING BOX ONLY (NO SEGMENTATION)
    # ---------------------------------------------------

    def get_boxes_crack(self,detection):
        return detection

    def draw_crack_lines(self, image, boxes,results=None):
        img = image.copy()

        for b in boxes:
            x1, y1, x2, y2 = b["x1"], b["y1"], b["x2"], b["y2"]

            # ✅ Draw plain bounding box
            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

        return img
