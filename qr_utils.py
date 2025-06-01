import numpy as np
import cv2
import os

def decode_qr(img_path) -> tuple[str, bytes] | None:
    try:
        qr_img = cv2.imread(img_path)
        if qr_img is None:
            return None

        qr_code = cv2.QRCodeDetector()
        decoded_info, points, _ = qr_code.detectAndDecode(qr_img)

        if points is not None and decoded_info:
            # Dibujar contorno del QR
            points = points[0].astype(int)
            cv2.polylines(qr_img, [points], isClosed=True, color=(0, 255, 0), thickness=3)
            
            # Codificar imagen a bytes correctamente
            success, encoded_image = cv2.imencode(".jpg", qr_img)
            if not success:
                return None
                
            return decoded_info.strip(), encoded_image.tobytes()
        
        return None

    except Exception as e:
        print(f"Error en decode_qr: {e}")
        return None
