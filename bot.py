import os
import requests
import uuid
from telegram import (BotCommand,Update, InputFile, ReplyKeyboardMarkup, KeyboardButton,  
                    ReplyKeyboardRemove,  InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from text_utils import procesar_texto_imagen
from image_utils import comparar_imagenes
from qr_utils import decode_qr
from pathlib import Path

project_root = Path(__file__).resolve().parent

# Configuración
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_BASE_URL") 
API_KEY = os.getenv("API_KEY")
CARPETA_IMAGENES = "./cuadros"
CARPETA_TEMP = "temporal"
FILAS = 4
COLUMNAS = 4

# Estados para la conversación
WAITING_PHOTO, CHOOSING_OPTION, WAITING_QR_PHOTO = range(3)

# Asegura que la carpeta temporal exista
os.makedirs(CARPETA_TEMP, exist_ok=True)

async def post_init(app: Application) -> None:
    comandos = [
            BotCommand("iniciar", "Iniciar el bot"),
            BotCommand("ayuda", "Mostrar ayuda"),
            BotCommand("horario", "Ver horario de atención"),
            BotCommand("cancelar", "Cancelar la operación actual"),
        ]
    await app.bot.set_my_commands(comandos)

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📸 Analizar obra"), KeyboardButton("ℹ️ Información")],
        [KeyboardButton("🗓️ Horarios"), KeyboardButton("👋 Ayuda")],
        [KeyboardButton("⛶ Lector QR")]
    ], resize_keyboard=True)

def get_media_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎧 Audio", callback_data="audio"),
            InlineKeyboardButton("🎥 Video", callback_data="video")
        ],
        [
            InlineKeyboardButton("🖼️ Imagen", callback_data="imagen"),
            InlineKeyboardButton("📝 Texto", callback_data="texto")
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_msg = f"""
🎨 *Bienvenido al Museo Virtual, {update.effective_user.first_name}!* 🖼️

Soy tu guía personalizado. Puedes:
- 📸 Enviarme una foto de una obra de arte
- ℹ️ Pedir información sobre las colecciones
- 🗺️ Obtener un mapa del museo

¿En qué puedo ayudarte hoy?
"""
    await update.message.reply_text(
        welcome_msg,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    return CHOOSING_OPTION


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
ℹ️ *Cómo usar el bot:*
1. Toma una foto de una obra de arte en el museo
2. Envíamela y la analizaré
3. Te daré información detallada

También puedes usar estos comandos:
/iniciar - Reiniciar el bot
/ayuda - Mostrar esta ayuda
/horario - Ver el horario de atencion
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("De lunes a viernes, 08:00 a 20:00 hrs.")

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "📸 Analizar obra":
        await update.message.reply_text("Por favor, envíame una foto de la obra que quieres analizar.", 
            reply_markup=ReplyKeyboardRemove())
        return WAITING_PHOTO
    elif text == "⛶ Lector QR":  # Nuevo caso para QR
        await update.message.reply_text("Envía una foto del código QR que deseas escanear.",
            reply_markup=ReplyKeyboardRemove())
        return WAITING_QR_PHOTO
    elif text == "ℹ️ Información":
        await update.message.reply_text("""
            📚 *Colecciones disponibles:*
            - Arte clásico (siglos XV-XVIII)
            - Arte moderno (siglo XX)
            - Exposiciones temporales
            Usa /horarios para ver el horario de visita.
            """, parse_mode="Markdown")
    elif text == "🗓️ Horarios":
        await schedule(update, context)
    elif text == "👋 Ayuda":
        await help(update, context)
    return CHOOSING_OPTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Gracias por usar el bot del museo. ¡Vuelve cuando quieras!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def procesar_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Por favor, envíame una foto.")
        return

    # Obtener la imagen
    foto = update.message.photo[-1]
    file = await context.bot.get_file(foto.file_id)
    image_bytes = await file.download_as_bytearray()

    # ---- OCR ----
    try:
        extracted_text, image_with_boxes = procesar_texto_imagen(image_bytes)
    except Exception as e:
        await update.message.reply_text(f"Error procesando OCR: {e}")
        return

    
    if extracted_text.strip():
    # Enviar imagen con recuadros + texto
        #print(extracted_text)
        await update.message.reply_photo(
            photo=InputFile(image_with_boxes),
            caption="Texto detectado:\n" + (extracted_text or "No se detectó texto.")
        )
    else:
        #print("No se encontro un texto en la imagen.")
        await update.message.reply_text("No se encontro un texto en la imagen.")

    # ---- Comparación de imagen ----
    # Guardar temporalmente la imagen descargada
    nuevo_nombre = f"{uuid.uuid4().hex}.jpg"
    ruta_archivo = os.path.join(CARPETA_TEMP, nuevo_nombre)
    with open(ruta_archivo, "wb") as f:
        f.write(image_bytes)

    # Ejecutar la comparación
    resultado = comparar_imagenes(ruta_archivo, CARPETA_IMAGENES, filas=FILAS, columnas=COLUMNAS)

    if resultado:
        nombre_archivo = resultado
        await update.message.reply_text(
            f"Obra identificada: *{nombre_archivo}*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("No encontre una coincidencia, me podrias proporcionar otra foto con mejor claridad.")

    # Limpiar la imagen temporal
    os.remove(ruta_archivo)


async def procesar_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.photo:
            await update.message.reply_text("Por favor, envíame una foto con el código QR.")
            return
        
        # Descargar imagen
        foto = update.message.photo[-1]
        file = await context.bot.get_file(foto.file_id)
        image_bytes = await file.download_as_bytearray()
        
        # Guardar temporalmente
        nombre_temp = f"{uuid.uuid4().hex}_qr.jpg"
        ruta_temp = os.path.join(CARPETA_TEMP, nombre_temp)
        with open(ruta_temp, "wb") as f:
            f.write(image_bytes)
            
        # Procesar QR
        resultado = decode_qr(ruta_temp)
        
        if resultado:
            decoded_info, _ = resultado  
            obra_uuid = decoded_info
            
            # Headers con API Key
            headers = {"X-API-Key": os.getenv("API_KEY")}
            
            try:
                # Consultar obra
                response_obra = requests.get(
                    f"{API_URL}/obras/{obra_uuid}",
                    headers=headers
                )
                response_obra.raise_for_status()
                
            except requests.exceptions.HTTPError as e:
                error_msg = (
                    "🔐 Error de autenticación con la API" if e.response.status_code == 401 else
                    "❌ Obra no encontrada" if e.response.status_code == 404 else
                    "⚠️ Error al obtener datos"
                )
                await update.message.reply_text(error_msg)
                return
            
            obra_data = response_obra.json()
            #print(obra_data)
            # Validar nombre_archivo
            nombre_archivo = obra_data.get("nombre_archivo")
            if not nombre_archivo:
                await update.message.reply_text("❌ La obra no tiene imagen asociada")
                return
            
            ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
            #print("Ruta esperada:", os.path.abspath(ruta_imagen))
            #print("¿Existe?", os.path.exists(ruta_imagen))
            
            #print(ruta_imagen)
            # Verificar existencia de la imagen
            if not os.path.exists(ruta_imagen):
                await update.message.reply_text("⚠️ Imagen no disponible temporalmente")
                return
            
            # Construir texto sin indentación excesiva
            texto_info = (
                f"📖 *{obra_data.get('titulo', '')}*\n"
                f"👤 Autor: {obra_data.get('autor', 'Desconocido')}\n"
                f"📅 Año: {obra_data.get('año', '')}\n"
                f"🎨 Estilo: {obra_data.get('estilo', '')}\n\n"
                f"{obra_data.get('descripcion', '')}"
            )
            # Enviar imagen de la obra
            try:
                with open(ruta_imagen, "rb") as img_file:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=InputFile(img_file),
                        caption=texto_info,
                        parse_mode="Markdown",
                        reply_markup=get_media_keyboard()
                    )
            except FileNotFoundError:
                await update.message.reply_text("⚠️ Error al cargar la imagen")
            context.user_data["qr_data"] = {"obra_uuid": obra_uuid,"reply":False}
    except Exception as e:
        await update.message.reply_text(f"🚨 Error crítico: {str(e)}")
        
    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)
            
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data
    qr_data = context.user_data.get("qr_data", {})
    obra_uuid = qr_data.get("obra_uuid")
    
    #print(action)
    media_back = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver", callback_data="volver_opciones"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")]
            ])
    
        # Manejar acción de volver
    if action == "volver_opciones":
        await query.edit_message_reply_markup(
            reply_markup=get_media_keyboard()
        )
        return
    
    # Manejar cancelación
    elif action == "cancelar":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"Gracias por usar el bot del museo. ¡Vuelve cuando quieras! \nUsa /iniciar para comenzar de nuevo.",
            reply_markup=None
        )
        context.user_data.clear()
        return
    
    if not obra_uuid:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ Sesión expirada. Escanea el QR nuevamente.")
        return
    

    
    if action in {"audio", "video", "imagen", "texto"}:
        headers = {"X-API-Key": os.getenv("API_KEY")}
        try:
            response = requests.get(f"{API_URL}/medios/{obra_uuid}", headers=headers)
            response.raise_for_status()
            medios_data = response.json()
            #print(f"medios_data: {medios_data}")
            medio = next((m for m in medios_data if m["tipo_medio"] == action), None)
            
            if not medio:
                #print("qr_data =", context.user_data["qr_data"])
                await query.edit_message_reply_markup(reply_markup=None)
                if not context.user_data["qr_data"]["reply"]:
                    await query.message.reply_text(
                        f"⚠️ No hay {action} disponible",
                        reply_markup=media_back
                    )
                    context.user_data["qr_data"]["reply"] = True
                    return
                else:
                    await query.edit_message_text(
                        text= f"{query.message.text}\n⚠️ No hay {action} disponible",
                        reply_markup=media_back)
                    return
            context.user_data["qr_data"]["reply"] = False
            data_media = next((medio for medio in medios_data if medio.get("tipo_medio") == action))
            await query.edit_message_reply_markup(reply_markup=None)
            if action == "audio":
                ruta = f"{project_root}{data_media['ruta_local']}"
                await context.bot.send_audio(
                    chat_id=query.message.chat.id,
                    audio=open(ruta,'rb'),
                    caption=f"🎧 {medio.get('descripcion', 'Audio descriptivo')}",
                    reply_markup=media_back
                )
            elif action == "video":
                ruta = f"{project_root}{data_media['ruta_local']}"
                #print(f"\nruta del video: {project_root}")
                await context.bot.send_video(
                    chat_id=query.message.chat.id,
                    video=open(ruta,'rb'),
                    caption=f"🎥 {medio.get('descripcion', 'Video explicativo')}",
                    reply_markup=media_back
                )
            elif action == "imagen":
                ruta = f"{project_root}{data_media['ruta_local']}"
                await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=InputFile(medio["ruta_local"]),
                    caption=f"🖼️ {medio.get('descripcion', 'Imagen adicional')}",
                    reply_markup=media_back
                )
            elif action == "texto":
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text= data_media["info"],
                    reply_markup=media_back
                )
        except requests.exceptions.HTTPError as e:
            error_msg = "🔐 Error de autenticación" if e.response.status_code == 401 else "⚠️ Error en el servidor"

            try:
                if query.message.text:
                    await query.edit_message_text(
                        text=f"❌ {error_msg}. Código: {e.response.status_code}",
                        reply_markup=media_back
                    )
                else:
                    await query.edit_message_caption(
                        caption=f"{query.message.caption}\n❌ {error_msg}. Código: {e.response.status_code}",
                        reply_markup=media_back
                    )
            except BadRequest:
                #print("Error 1")
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f"❌ {error_msg}. Código: {e.response.status_code}",
                    reply_markup=media_back
                )

        except Exception as e:
            #print("Error 2")
            msg_error = f"❌ Error inesperado: {str(e)}"
            try:
                if query.message.caption:
                    await query.edit_message_caption(
                        caption=f"{query.message.caption}\n{msg_error}",
                        reply_markup=media_back
                    )
                else:
                    await query.edit_message_text(
                        text=msg_error,
                        reply_markup=media_back
                    )
            except BadRequest:
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text=msg_error,
                    reply_markup=media_back
                )

# Inicialización del bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("iniciar", start)],
    states={
    CHOOSING_OPTION: [
        MessageHandler(filters.TEXT & filters.Regex(r'^(📸 Analizar obra|⛶ Lector QR)$'), handle_menu)
    ],
    WAITING_PHOTO: [
        MessageHandler(filters.PHOTO, procesar_imagen),
        CommandHandler("cancelar", cancel)
    ],
    WAITING_QR_PHOTO: [
        MessageHandler(filters.PHOTO, procesar_qr),
        CommandHandler("cancelar", cancel)
    ]},
    fallbacks=[CommandHandler("cancelar", cancel)]
)
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("ayuda", help))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    
    #print("🤖 Bot iniciado...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)