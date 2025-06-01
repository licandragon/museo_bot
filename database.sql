-- Habilitar extensión para generar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS medios CASCADE;
DROP TABLE IF EXISTS obras CASCADE;

-- Tabla 'obras' con clave primaria SERIAL y campo UUID único
CREATE TABLE obras (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    nombre_archivo VARCHAR(255) NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    autor VARCHAR(100),
    año INTEGER CHECK (año >= 0),
    estilo VARCHAR(50),
    descripcion TEXT
);

-- Tabla 'medios' con referencia a 'obras.id' (entero)
CREATE TABLE medios (
    id SERIAL PRIMARY KEY,
    obra_id INTEGER NOT NULL,
    tipo_medio VARCHAR(20) CHECK (tipo_medio IN ('audio', 'video', 'imagen', 'texto')),
    url VARCHAR(500) DEFAULT NULL,
    ruta_local VARCHAR(500) DEFAULT NULL,
    info TEXT DEFAULT NULL,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);

-- Índices para optimización de consultas
CREATE INDEX idx_medios_obra_id ON medios(obra_id);
CREATE INDEX idx_medios_tipo_medio ON medios(tipo_medio);


-- OBRAS MAESTRAS DEL ARTE (PostgreSQL)
INSERT INTO obras (uuid, nombre_archivo, titulo, autor, año, estilo, descripcion) VALUES
-- 1. Pintura Renacentista
(
    'edd0e49a-aa96-4980-b316-a83ebfa99180',
    '960px-Leonardo_da_Vinci_-_Mona_Lisa_(Louvre,_Paris).jpg',
    'Mona Lisa',
    'Leonardo da Vinci',
    1503,
    'Renacimiento',
    'Retrato emblemático con enigmática sonrisa, considerado el cuadro más famoso del mundo.'
),

-- 2. Pintura Postimpresionista
(
    '4c943d0c-483e-4593-bd50-2d4ad17dfb01',
    '1364px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
    'La Noche Estrellada',
    'Vincent van Gogh',
    1889,
    'Postimpresionismo',
    'Representación expresiva del cielo nocturno sobre Saint-Rémy-de-Provence.'
),

-- 3. Pintura Expresionista
(
    'c58be7f5-b2e2-4ccc-be15-b9ba473a9fdd',
    'el_grito.jpg',
    'El Grito',
    'Edvard Munch',
    1893,
    'Expresionismo',
    'Icono universal de la angustia existencial con figura andrógina en primer plano.'
),

-- 4. Pintura Surrealista
(
    '5abe7709-6336-46f1-8a5c-74175a7e80b1',
    'persistencia_de_la_memoria.jpg',
    'La Persistencia de la Memoria',
    'Salvador Dalí',
    1931,
    'Surrealismo',
    'Famosos relojes derretidos en paisaje onírico, símbolo de la relatividad del tiempo.'
),

-- 5. Fresco Renacentista
(
    '66be3dd9-6e55-4c3b-b67a-df6afe26dcfc',
    '1920px-Michelangelo_-_Creation_of_Adam_(cropped).jpg',
    'La Creación de Adán',
    'Miguel Ángel',
    1512,
    'Renacimiento',
    'Detalle central de la Capilla Sixtina donde las manos de Dios y Adán casi se tocan.'
),

-- 6. Pintura Barroca
(
    'ff0bca36-a80e-4728-a34e-4bced57a419d',
    '960px-Las_Meninas_01.jpg',
    'Las Meninas',
    'Diego Velázquez',
    1656,
    'Barroco',
    'Compleja escena palaciega que juega con perspectivas y espejos.'
),

-- 7. Pintura Cubista
(
    'cb1f841b-2f3b-487b-9391-5eab6682dfd2',
    'DE00050.jpg',
    'Guernica',
    'Pablo Picasso',
    1937,
    'Cubismo',
    'Monumental denuncia del bombardeo nazi durante la Guerra Civil Española.'
),

-- 8. Escultura Neoclásica
(
    '0c19befb-bc77-4da1-aadf-9d47f589e68e',
    'venus_milo.jpg',
    'Venus de Milo',
    'Alejandro de Antioquía',
    130,
    'Helenístico',
    'Escultura griega de Afrodita famosa por sus brazos faltantes y drapeado.'
),

-- 9. Pintura Impresionista
(
    '31fe7690-c7de-496d-9e0e-6c7de730573f',
    '1392px-Monet_-_Impression,_Sunrise.jpg',
    'Impresión, sol naciente',
    'Claude Monet',
    1872,
    'Impresionismo',
    'Obra que dio nombre al movimiento impresionista, puerto de Le Havre al amanecer.'
),

-- 10. Pintura Modernista
(
    '4de8fb95-fe1e-42b4-b876-c30ae75efb73',
    '1076px-The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg',
    'El Beso',
    'Gustav Klimt',
    1908,
    'Modernismo',
    'Icono de la Secesión Vienesa con decoración dorada y formas geométricas.'
);



INSERT INTO medios (obra_id,tipo_medio,ruta_local) VALUES (1,'audio','/media/audio/La Mona Lisa en 90 segundos. Todo lo que deberías saber.mp3');

INSERT INTO medios (obra_id,tipo_medio,ruta_local) VALUES (1,'video','/media/video/La Mona Lisa en 90 segundos. Todo lo que deberías saber.mp4');

INSERT INTO medios (obra_id,tipo_medio,info) VALUES (1,'texto','¿Sabías que la Mona Lisa no fue famosa hasta que fue robada?
Aunque hoy es probablemente la pintura más famosa del mundo, la Mona Lisa (o La Gioconda) no era tan célebre hasta que fue robada en 1911 del Museo del Louvre por un trabajador italiano llamado Vincenzo Peruggia.
🕵️‍♂️ Peruggia la escondió en su casa durante más de dos años, creyendo que debía ser devuelta a Italia por patriotismo.
📰 El robo fue un escándalo internacional, apareció en todos los periódicos, y entre los sospechosos incluso estuvo Pablo Picasso.
Cuando la pintura fue recuperada en 1913, se convirtió en un fenómeno mediático, y desde entonces su fama no ha parado de crecer.');
