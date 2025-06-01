import cv2
import numpy as np
import os

N_FEATURES=1000

def recortar_centro(img, porcentaje=0.6):
    alto, ancho = img.shape
    nuevo_alto = int(alto * porcentaje)
    nuevo_ancho = int(ancho * porcentaje)
    inicio_y = (alto - nuevo_alto) // 2
    inicio_x = (ancho - nuevo_ancho) // 2
    return img[inicio_y:inicio_y+nuevo_alto, inicio_x:inicio_x+nuevo_ancho]

def dividir_imagen(img, filas=3, columnas=3):
    alto, ancho = img.shape
    tiles = []
    h_tile = alto // filas
    w_tile = ancho // columnas
    for i in range(filas):
        for j in range(columnas):
            tile = img[i*h_tile:(i+1)*h_tile, j*w_tile:(j+1)*w_tile]
            tiles.append(((i, j), tile))
    return tiles

def comparar_imagenes(archivo_referencia, carpeta_imagenes, filas=3, columnas=3):
    UMBRAL_INLIERS = 30
    img_ref = cv2.imread(archivo_referencia, cv2.IMREAD_GRAYSCALE)
    if img_ref is None:
        raise ValueError(f"No se pudo cargar la imagen: {archivo_referencia}")

    img_ref = cv2.GaussianBlur(img_ref, (5, 5), 0)
    img_ref = cv2.equalizeHist(img_ref)
    img_ref = recortar_centro(img_ref, porcentaje=0.6)

    detector = cv2.ORB_create(nfeatures=N_FEATURES)
    kp1, des1 = detector.detectAndCompute(img_ref, None)
    if des1 is None or len(des1) < 10:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=False)
    mejor_puntuacion = 0
    mejor_info = None

    for archivo in os.listdir(carpeta_imagenes):
        ruta_imagen = os.path.join(carpeta_imagenes, archivo)
        img = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        # Preprocesamiento para imágenes de la base de datos
        img = cv2.GaussianBlur(img, (5, 5), 0)
        img = cv2.equalizeHist(img)
        tiles = dividir_imagen(img, filas, columnas)

        for (fila, columna), tile in tiles:
            kp2, des2 = detector.detectAndCompute(tile, None)
            if des2 is None or len(des2) < 10:
                continue

            matches = bf.knnMatch(des1, des2, k=2)
            good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
            if len(good_matches) < 10:
                continue

            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
            _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if mask is None:
                continue

            inliers = np.sum(mask)
            if inliers > mejor_puntuacion:
                mejor_puntuacion = inliers
                mejor_info = (archivo, (fila, columna))
    
    print(f'Mejor puntuacion: {mejor_puntuacion}')
    if mejor_puntuacion > UMBRAL_INLIERS:
        print(f"Coincidencia válida: {mejor_info} (inliers: {mejor_puntuacion})")
        return mejor_info
    else:
        print("No se encontraron coincidencias significativas.")
        return None