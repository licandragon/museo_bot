import cv2
import numpy as np
import pytesseract

def preprocess_image(img: np.ndarray) -> np.ndarray:
    # Convertir a escala de grises y aplicar eliminación de ruido no local
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=17, templateWindowSize=7)
    
    # Mejorar contraste usando CLAHE (Limitación de Contraste Adaptativo)
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Umbralización adaptativa combinada con método Gaussiano
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 12
    )
    
    # Operaciones morfológicas para limpieza y unión de caracteres
    kernel_clean = np.ones((1, 1), np.uint8)  # Eliminar pequeños artefactos
    kernel_join = np.ones((2, 2), np.uint8)   # Conectar partes de caracteres
    
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_clean)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_join)
    
    return thresh

def procesar_texto_imagen(image_bytes: bytearray) -> tuple[str, bytes]:
    # Decodificar imagen desde bytes a array numpy
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Error en decodificación de imagen")

    # Redimensionamiento para optimizar procesamiento en imágenes grandes
    h, w = img.shape[:2]
    if w > 1600:
        ratio = 1600 / w
        img = cv2.resize(img, (1600, int(h * ratio)))

    original_img = img.copy()  # Copia para visualización de resultados
    thresh = preprocess_image(img)  # Aplicar preprocesamiento

    # Configuración Tesseract para múltiples idiomas y alta precisión
    config = (
        '--oem 3 --psm 1 '    # Motor 3 (LSTM), Modo Página segmentada
        '-l spa+eng+equ '     # Idiomas: español, inglés y ecuaciones
        '--dpi 300'           # Asumir alta resolución de imagen
    )
    
    # Ejecutar OCR 
    data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)

    lines = {}  # Almacenar texto agrupado por líneas
    for i, text in enumerate(data['text']):
        text = text.strip()
        confianza = int(data['conf'][i])
        
        # Filtrar texto vacío o con baja confianza (<60)
        if not text or confianza < 60:
            continue

        # Agrupar palabras por número de línea detectada
        line_num = data['line_num'][i]
        lines.setdefault(line_num, []).append(text)

        # Dibujar rectángulos en imagen original para visualización
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(original_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Construir texto final uniendo líneas detectadas
    extracted_text = "\n".join([" ".join(line) for line in lines.values()])

    # Codificar imagen modificada con rectángulos a formato JPG
    _, buffer = cv2.imencode(".jpg", original_img)
    return extracted_text.strip(), buffer.tobytes()