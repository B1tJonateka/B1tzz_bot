from telegram import Update, BotCommandScopeAllChatAdministrators
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, time
import asyncio
import nest_asyncio
import os
import re
import json

# Archivo donde se guardarán las configuraciones
CONFIG_FILE = "group_configs.json"

# Diccionario para almacenar configuraciones por grupo
group_configs = {}
user_warnings = {}
night_mode_configs = {}

# Aplicar nest_asyncio
nest_asyncio.apply()

# Lista de palabras prohibidas
banned_words = ["pc", "cp", "cambio","intercambio","pv","priv","privado"]

# Diccionarios para rastrear advertencias de usuarios y las configuraciones
user_warnings = {}
last_welcome_photo = None
last_goodbye_photo = None

# Cargar configuraciones desde archivo
def load_configs():
    global group_configs
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            group_configs = json.load(f)
    else:
        group_configs = {}

# Función para guardar las configuraciones en un archivo JSON
def save_group_configs():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(group_configs, f, indent=4)

# Función para obtener o inicializar la configuración de un grupo
def get_group_config(chat_id):
    chat_id = str(chat_id)
    if chat_id not in group_configs:
        group_configs[chat_id] = {
            "welcome_message": "¡Bienvenido/a, {first_name}! \n\n¡Esperamos que disfrutes tu estadía!",
            "goodbye_message": "{first_name} ha salido del grupo. \n\n¡Te extrañaremos!",
            "welcome_media": "https://noticias.animeonegai.com/wp-content/uploads/2022/10/Tokidoki-Bosotto-Roshia-Go-de-Dereru-Tonari-no-Arya-San-NL-vol-5-min-1.webp",
            "goodbye_media": "https://somoskudasai.com/wp-content/uploads/2021/11/portada_tokidoki-4.jpg",
            "rules": "1. No spam\n2. Respeta a los demás\n3. No contenido inapropiado",
            "auto_rules_enabled": False,
            "night_mode_enabled": False,
            "night_mode_start": "01:30",
            "night_mode_end": "05:00"
        }
        save_group_configs()  # Guardar las configuraciones al crear un nuevo grupo
    return group_configs[chat_id]

# Actualizar la configuración de un grupo y guardarla
def update_group_config(chat_id, key, value):
    if str(chat_id) not in group_configs:
        group_configs[str(chat_id)] = {}
    group_configs[str(chat_id)][key] = value
    save_group_configs()

# Verificar si el usuario es administrador
async def is_admin(update: Update):
    chat_member = await update.effective_chat.get_member(update.effective_user.id)
    return chat_member.status in ['administrator', 'creator']

# Función para obtener el ID del usuario
async def get_user_id(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id

    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "text_mention":
                return entity.user.id
            elif entity.type == "mention":
                 mentioned_username = update.message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                 try:
                     member = await update.effective_chat.get_member_by_username(mentioned_username)
                     return member.user.id
                 except Exception as e:
                     print(f"Error al obtener el ID del usuario mencionado: {e}")
                     return None

    return None

def is_url(url):
    # Expresión regular para verificar si la URL tiene un formato válido
    return re.match(r'^(https?://.*\.(jpg|jpeg|png|webp|gif|mp4|mov|GIF))$', url) is not None

# Función para enviar mensaje de bienvenida
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_welcome_photo

    chat_id = update.effective_chat.id
    config = get_group_config(chat_id)  # Obtener la configuración del grupo actual

    member = update.message.new_chat_members[0]
    if member:
        if last_welcome_photo:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_welcome_photo)
            except Exception as e:
                print(f"Error al eliminar el último mensaje de bienvenida: {e}")

        welcome_message = config['welcome_message'].format(first_name=member.first_name)
        welcome_media = config['welcome_media']
        sent_message = None

        print(f"Enviando mensaje de bienvenida con media: {welcome_media}")

        try:
            if is_url(welcome_media):
                if welcome_media.endswith(('.mp4', '.mov')):
                    sent_message = await context.bot.send_video(chat_id=chat_id, video=welcome_media, caption=welcome_message)
                elif welcome_media.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=welcome_media, caption=welcome_message)
                else:
                    print(f"Formato de media no soportado: {welcome_media}")
                    return
            elif welcome_media.startswith('AgA') or welcome_media.startswith('BA'):
                try:
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=welcome_media, caption=welcome_message)
                except Exception as e:
                    print(f"Error al enviar el file_id como foto: {e}")
                    try:
                        sent_message = await context.bot.send_video(chat_id=chat_id, video=welcome_media, caption=welcome_message)
                    except Exception as e:
                        print(f"Error al enviar el file_id como video: {e}")
                        return
            else:
                if welcome_media.endswith(('.mp4', '.mov', '.gif', '.GIF')):
                    sent_message = await context.bot.send_video(chat_id=chat_id, video=welcome_media, caption=welcome_message)
                elif welcome_media.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=welcome_media, caption=welcome_message)
                else:
                    print(f"Formato de media no soportado: {welcome_media}")
                    return

            if sent_message:
                last_welcome_photo = sent_message.message_id

        except Exception as e:
            print(f"Error al enviar el mensaje de bienvenida: {e}")

        # Guardar configuraciones actualizadas
        save_group_configs()

        await asyncio.sleep(10)
        try:
            if last_welcome_photo:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_welcome_photo)
        except Exception as e:
            print(f"Error al eliminar el mensaje de bienvenida: {e}")

# Función para enviar mensaje de despedida (modificación con más controles)
async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_goodbye_photo

    chat_id = update.effective_chat.id
    config = get_group_config(chat_id)  # Obtener la configuración del grupo actual

    member = update.message.left_chat_member
    if member:
        # Intentar eliminar el último mensaje de despedida si existe
        if last_goodbye_photo:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_goodbye_photo)
            except Exception as e:
                print(f"Error al eliminar el último mensaje de despedida: {e}")

        # Obtener o asignar valores predeterminados de mensaje y media
        goodbye_message = config.get('goodbye_message', 'Adiós, {first_name}. ¡Te echaremos de menos!')
        goodbye_message = goodbye_message.format(first_name=member.first_name)

        goodbye_media = config.get('goodbye_media', '')  # Si no hay media, se asegura que esté vacío

        # Guardar la configuración antes de enviar el mensaje para asegurar su persistencia
        config['goodbye_message'] = goodbye_message
        config['goodbye_media'] = goodbye_media

        # Guardar configuraciones actualizadas (proceso explícito antes del envío)
        save_group_configs()  
        print(f"Guardando configuraciones antes de enviar el mensaje de despedida para el grupo {chat_id}")

        sent_message = None
        print(f"Enviando mensaje de despedida con media: {goodbye_media}")

        try:
            # Verificar si goodbye_media es una URL o un file_id
            if is_url(goodbye_media):
                if goodbye_media.endswith(('.mp4', '.mov', '.gif', '.GIF')):
                    sent_message = await context.bot.send_video(chat_id=chat_id, video=goodbye_media, caption=goodbye_message)
                elif goodbye_media.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=goodbye_media, caption=goodbye_message)
                else:
                    print(f"Formato de media no soportado: {goodbye_media}")
                    return
            elif goodbye_media.startswith('BA'):
                try:
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=goodbye_media, caption=goodbye_message)
                except Exception as e:
                    print(f"Error al enviar el file_id como foto: {e}")
                    try:
                        sent_message = await context.bot.send_video(chat_id=chat_id, video=goodbye_media, caption=goodbye_message)
                    except Exception as e:
                        print(f"Error al enviar el file_id como video: {e}")
                        return
            else:
                # Verificar tipos de archivo adicionales
                if goodbye_media.endswith(('.mp4', '.mov', '.gif', '.GIF')):
                    sent_message = await context.bot.send_video(chat_id=chat_id, video=goodbye_media, caption=goodbye_message)
                elif goodbye_media.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    sent_message = await context.bot.send_photo(chat_id=chat_id, photo=goodbye_media, caption=goodbye_message)
                else:
                    print(f"Formato de media no soportado: {goodbye_media}")
                    return

            # Si se envió un mensaje, actualizamos el ID del último mensaje de despedida
            if sent_message:
                last_goodbye_photo = sent_message.message_id

            # Guardar configuraciones actualizadas de nuevo después de enviar el mensaje
            save_group_configs()  
            print(f"Configuración del grupo guardada correctamente después de enviar el mensaje para el grupo: {chat_id}")

        except Exception as e:
            print(f"Error al enviar el mensaje de despedida: {e}")

        # Eliminar el mensaje de despedida después de 10 segundos
        await asyncio.sleep(10)
        try:
            if last_goodbye_photo:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_goodbye_photo)
        except Exception as e:
            print(f"Error al eliminar el mensaje de despedida: {e}")

# Comando para actualizar el media de bienvenida por un enlace
async def set_welcome_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # Obtener el ID del grupo
    group_config = get_group_config(chat_id)  # Obtener la configuración específica del grupo

    if await is_admin(update):  # Verifica si el usuario es administrador usando tu función
        try:
            new_media_link = context.args[0]
            # Validar si es un enlace
            if new_media_link.startswith('http'):
                group_config['welcome_media'] = new_media_link  # Actualizar el media de bienvenida solo para este grupo
                save_group_configs()  # Guardar las configuraciones después de actualizar el enlace
                await update.message.reply_text(f"El enlace del media de bienvenida ha sido actualizado a:\n{new_media_link}")
            else:
                await update.message.reply_text("El enlace proporcionado no es válido. Asegúrate de que sea un enlace completo.")
        except IndexError:
            await update.message.reply_text("Por favor, proporciona un enlace después del comando.")
    else:
        await update.message.reply_text("No tienes permisos para ejecutar este comando.")

# Comando para actualizar el media de despedida por un enlace
async def set_goodbye_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # Obtener el ID del grupo
    group_config = get_group_config(chat_id)  # Obtener la configuración específica del grupo

    if await is_admin(update):  # Verifica si el usuario es administrador usando tu función
        try:
            new_media_link = context.args[0]
            # Validar si es un enlace
            if new_media_link.startswith('http'):
                group_config['goodbye_media'] = new_media_link  # Actualizar el media de despedida solo para este grupo
                save_group_configs()  # Guardar las configuraciones después de actualizar el enlace
                await update.message.reply_text(f"El enlace del media de despedida ha sido actualizado a:\n{new_media_link}")
            else:
                await update.message.reply_text("El enlace proporcionado no es válido. Asegúrate de que sea un enlace completo.")
        except IndexError:
            await update.message.reply_text("Por favor, proporciona un enlace después del comando.")
    else:
        await update.message.reply_text("No tienes permisos para ejecutar este comando.")

async def configure(update: Update, context):
    chat_id = update.effective_chat.id  # Obtener el ID del grupo
    group_config = get_group_config(chat_id)  # Obtener la configuración específica del grupo

    if not await is_admin(update):
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return

    # Verificar si es una respuesta a un mensaje
    if update.message.reply_to_message:
        replied_message = update.message.reply_to_message

        # Verificar si el mensaje respondido contiene medios (foto, video, sticker o documento)
        if replied_message.photo or replied_message.video or replied_message.sticker or replied_message.document:
            option = None
            if 'welcome' in update.message.text.lower():
                option = "welcome"
            elif 'goodbye' in update.message.text.lower():
                option = "goodbye"

            if option:
                # Guardar el medio subido (foto, video, sticker, documento)
                if replied_message.photo:
                    file_id = replied_message.photo[-1].file_id
                    if option == "welcome":
                        group_config['welcome_media'] = file_id
                        await update.message.reply_text("Imagen de bienvenida actualizada.")
                    elif option == "goodbye":
                        group_config['goodbye_media'] = file_id
                        await update.message.reply_text("Imagen de despedida actualizada.")
                elif replied_message.video:
                    file_id = replied_message.video.file_id
                    if option == "welcome":
                        group_config['welcome_media'] = file_id
                        await update.message.reply_text("Video de bienvenida actualizado.")
                    elif option == "goodbye":
                        group_config['goodbye_media'] = file_id
                        await update.message.reply_text("Video de despedida actualizado.")
                elif replied_message.sticker:
                    file_id = replied_message.sticker.file_id
                    if option == "welcome":
                        group_config['welcome_media'] = file_id
                        await update.message.reply_text("Sticker de bienvenida actualizado.")
                    elif option == "goodbye":
                        group_config['goodbye_media'] = file_id
                        await update.message.reply_text("Sticker de despedida actualizado.")
                elif replied_message.document:
                    file_id = replied_message.document.file_id
                    if option == "welcome":
                        group_config['welcome_media'] = file_id
                        await update.message.reply_text("Documento de bienvenida actualizado.")
                    elif option == "goodbye":
                        group_config['goodbye_media'] = file_id
                        await update.message.reply_text("Documento de despedida actualizado.")
                return

    # Si no es respuesta a un mensaje, entonces manejar el cambio de texto
    args = context.args

    if len(args) == 0:
        await update.message.reply_text("Uso: /config <welcome|goodbye> <mensaje|media>")
        return

    option = args[0].lower()
    content = " ".join(args[1:])

    if option == "welcome":
        group_config['welcome_message'] = content
        await update.message.reply_text(f"Mensaje de bienvenida actualizado: {group_config['welcome_message']}")

    elif option == "goodbye":
        group_config['goodbye_message'] = content
        await update.message.reply_text(f"Mensaje de despedida actualizado: {group_config['goodbye_message']}")

    else:
        await update.message.reply_text("Opción inválida. Usa 'welcome' o 'goodbye'.")

# Función para obtener o inicializar advertencias por grupo
def get_warnings_for_group(chat_id):
    if chat_id not in user_warnings:
        user_warnings[chat_id] = {}
    return user_warnings[chat_id]

# Función para advertir a los usuarios
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si el usuario es administrador
    if not await is_admin(update):
        await update.message.reply_text("Lo siento, solo los administradores pueden usar este comando.")
        return

    # Obtener el ID del chat (grupo) y del usuario
    chat_id = update.effective_chat.id
    user_id = await get_user_id(update)
    
    if user_id is None:
        await update.message.reply_text("Por favor, menciona a un usuario o responde a su mensaje.")
        return

    # Obtener o inicializar las advertencias para el grupo actual
    group_warnings = get_warnings_for_group(chat_id)

    # Incrementar el contador de advertencias para el usuario en este chat
    group_warnings[user_id] = group_warnings.get(user_id, 0) + 1
    await update.message.reply_text(f"Usuario con ID {user_id} ha sido advertido. Número de advertencias en este grupo: {group_warnings[user_id]}")

    # Si el usuario acumula 3 o más advertencias, banearlo del grupo
    if group_warnings[user_id] >= 3:
        await update.effective_chat.ban_member(user_id)
        await update.message.reply_text(f"Usuario con ID {user_id} ha sido baneado por acumular 3 advertencias en este grupo.")

# Función para banear a un usuario
async def ban_user(update: Update, context):
    user_id = await get_user_id(update)
    if user_id is None:
        await update.message.reply_text("Por favor, menciona a un usuario o responde a su mensaje.")
        return

    await update.effective_chat.ban_member(user_id)
    await update.message.reply_text(f"Usuario con ID {user_id} ha sido baneado del grupo.")

# Función para expulsar a un usuario (kick)
async def kick_user(update: Update, context):
    user_id = await get_user_id(update)
    if user_id is None:
        await update.message.reply_text("Por favor, menciona a un usuario o responde a su mensaje.")
        return

    await update.effective_chat.ban_member(user_id)
    await update.effective_chat.unban_member(user_id)  # Desbanea inmediatamente
    await update.message.reply_text(f"Usuario con ID {user_id} ha sido expulsado del grupo.")

# Función para desbanear a un usuario
async def unban_user(update: Update, context):
    user_id = await get_user_id(update)
    if user_id is None:
        await update.message.reply_text("Por favor, menciona a un usuario o responde a su mensaje.")
        return

    await update.effective_chat.unban_member(user_id)
    await update.message.reply_text(f"Usuario con ID {user_id} ha sido desbaneado.")

# Función para mostrar información del usuario
async def user_info(update: Update, context):
    user_id = await get_user_id(update)
    if user_id is None:
        await update.message.reply_text("Por favor, menciona a un usuario o responde a su mensaje.")
        return

    try:
        user = await update.effective_chat.get_member(user_id)
        await update.message.reply_text(f"Información del usuario:\n\nID: {user.user.id}\nNombre: {user.user.first_name}\nUsername: @{user.user.username if user.user.username else 'No tiene username'}")
    except Exception as e:
        print(f"Error al obtener información del usuario: {e}")
        await update.message.reply_text("No se pudo obtener la información del usuario.")

# Función para establecer comandos del bot
async def set_commands(application):
    commands = [
        ("ban", "Banear a un usuario"),
        ("kick", "Expulsar a un usuario"),
        ("warn", "Advertir a un usuario"),
        ("unban", "Desbanear a un usuario"),
        ("info", "Mostrar información del usuario"),
        ("config", "Configurar mensajes e imágenes/videos de bienvenida y despedida"),
        ("wordlist", "configuración de la lista de palabras prohibidas"),
        ("set_welcome_media", "Actualiza la imagen o video de bienvenida pero con un link"),
        ("set_goodbye_media", "Actualiza la imagen o video de despedida pero con un link"),
        ("rules","muestra las reglas del grupo"),
        ("rules_auto","activa o desactiva la muestra de reglas las cada 30 minutos "),
        ("rules_edit","actualiza las reglas del grupo"),
        ("night_mode","Configuracion para el modo noche")
    ]
    await application.bot.set_my_commands(commands, scope=BotCommandScopeAllChatAdministrators())

# Función para gestionar la lista de palabras prohibidas
async def manage_banned_words(update: Update, context):
    if not await is_admin(update):
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return

    args = context.args

    if len(args) == 0:
        await update.message.reply_text("Uso: /wordlist <add|remove|clear|show> [palabra]")
        return

    action = args[0].lower()

    if action == "show":
        if banned_words:
            words = "\n".join(banned_words)
            await update.message.reply_text(f"Lista de palabras prohibidas:\n{words}")
        else:
            await update.message.reply_text("La lista de palabras prohibidas está vacía.")
    
    elif action == "add":
        if len(args) < 2:
            await update.message.reply_text("Debes especificar una palabra para añadir.")
            return
        
        new_word = args[1].lower()
        if new_word in banned_words:
            await update.message.reply_text(f"La palabra '{new_word}' ya está en la lista.")
        else:
            banned_words.append(new_word)
            await update.message.reply_text(f"La palabra '{new_word}' ha sido añadida a la lista.")
    
    elif action == "remove":
        if len(args) < 2:
            await update.message.reply_text("Debes especificar una palabra para eliminar.")
            return
        
        word_to_remove = args[1].lower()
        if word_to_remove in banned_words:
            banned_words.remove(word_to_remove)
            await update.message.reply_text(f"La palabra '{word_to_remove}' ha sido eliminada de la lista.")
        else:
            await update.message.reply_text(f"La palabra '{word_to_remove}' no está en la lista.")
    
    elif action == "clear":
        banned_words.clear()
        await update.message.reply_text("La lista de palabras prohibidas ha sido limpiada.")
    
    else:
        await update.message.reply_text("Acción inválida. Usa 'show', 'add', 'remove' o 'clear'.")

# Función para verificar si el mensaje contiene palabras prohibidas
async def check_forbidden_words(update: Update, context):
    user_id = update.effective_user.id
    user_message = update.message.text.lower()

    # Verificar si el usuario no es administrador
    if not await is_admin(update):
        for word in banned_words:
            if word in user_message:
                # Eliminar el mensaje del usuario
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                except Exception as e:
                    print(f"Error al eliminar el mensaje: {e}")

                # Aplicar advertencia
                user_warnings[user_id] = user_warnings.get(user_id, 0) + 1

                # Enviar advertencia al usuario después de eliminar el mensaje
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⚠️ {update.effective_user.first_name}, has recibido una advertencia por usar una palabra prohibida. "
                         f"Advertencia {user_warnings[user_id]}/4."
                )

                # Banear si llega a 4 advertencias
                if user_warnings[user_id] >= 4:
                    await update.effective_chat.ban_member(user_id)
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"🚫 {update.effective_user.first_name} ha sido baneado por acumular 4 advertencias."
                    )
                return  # No continuar verificando más palabras si ya se encontró una

# Función para mostrar las reglas manualmente
async def rules_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    config = get_group_config(chat_id)
    await update.message.reply_text(f"Reglas del grupo:\n{config['rules']}")

# Función para activar o desactivar la auto-mostración de reglas
async def rules_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    config = get_group_config(chat_id)

    # Verificar si el usuario es administrador
    if not await is_admin(update):
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return

    if context.args and context.args[0].lower() == 'on':
        config['auto_rules_enabled'] = True
        await update.message.reply_text("La auto-mostración de reglas ha sido activada.")
        save_group_configs()  # Guardar las configuraciones al crear un nuevo grupo

        # Programar la tarea recurrente
        remove_existing_job(context, chat_id)
        context.job_queue.run_repeating(show_rules_auto, interval=1800, first=10, name=f"rules_auto_job_{chat_id}", chat_id=chat_id)

    elif context.args and context.args[0].lower() == 'off':
        config['auto_rules_enabled'] = False
        await update.message.reply_text("La auto-mostración de reglas ha sido desactivada.")
        save_group_configs()  # Guardar las configuraciones al crear un nuevo grupo
        # Detener el job si está corriendo
        remove_existing_job(context, chat_id)
    else:
        await update.message.reply_text("Uso: /rules_auto on | off")

# Función para mostrar las reglas automáticamente
async def show_rules_auto(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    config = get_group_config(chat_id)
    
    if config['auto_rules_enabled']:
        message = await context.bot.send_message(chat_id, f"Reglas del grupo:\n{config['rules']}")
        await asyncio.sleep(20)  # Espera 20 segundos
        await context.bot.delete_message(chat_id, message.message_id)

# Función para editar las reglas respondiendo a un mensaje anterior
async def rules_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    config = get_group_config(chat_id)

    # Verificar si el usuario es administrador
    if not await is_admin(update):
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    if update.message.reply_to_message:
        # Obtener el contenido del mensaje al que se está respondiendo
        new_rules = update.message.reply_to_message.text
        config['rules'] = new_rules
        save_group_configs()  # Guardar las configuraciones al crear un nuevo grupo
        await update.message.reply_text(f"Las reglas han sido actualizadas a:\n{config['rules']}")
    else:
        await update.message.reply_text("Por favor, responde al mensaje que contiene las reglas anteriores con el comando /rules_edit.")

# Eliminar cualquier trabajo anterior que esté programado para el grupo
def remove_existing_job(context: ContextTypes.DEFAULT_TYPE, chat_id):
    current_jobs = context.job_queue.get_jobs_by_name(f"rules_auto_job_{chat_id}")
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()

# Función que maneja los mensajes y elimina los que no sean texto durante el "night mode"
async def handle_message(update: Update, context):
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Obtener la configuración del modo nocturno para el grupo actual
    config = night_mode_configs.get(chat_id, {
        "enabled": False,
        "start": time(1, 30),  # Hora por defecto: 01:30
        "end": time(5, 0)       # Hora por defecto: 05:00
    })

    current_time = datetime.now().time()

    # Verificar si el modo nocturno está activado y si estamos en las horas configuradas
    if config["enabled"] and (config["start"] <= current_time or current_time <= config["end"]):
        # Obtener la lista de administradores
        admin_ids = [admin.user.id for admin in await context.bot.get_chat_administrators(chat_id)]

        # Si el usuario no es administrador, solo permitir mensajes de texto
        if user.id not in admin_ids:
            message = update.message

            # Si el mensaje no es texto, eliminarlo
            if not message.text:
                await message.delete()
                return

# Función para gestionar el comando /night_mode
async def night_mode(update: Update, context):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Obtener la configuración del modo nocturno para el grupo actual
    config = night_mode_configs.get(chat_id, {
        "enabled": False,
        "start": time(1, 30),  # Hora por defecto: 01:30
        "end": time(5, 0)       # Hora por defecto: 05:00
    })

    # Verificar si el usuario es administrador
    if user.id not in [admin.user.id for admin in await context.bot.get_chat_administrators(chat_id)]:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return

    # Analizar los argumentos del comando
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /night_mode [on/off/set_start/set_end]")
        return

    action = context.args[0].lower()

    if action == "on":
        config["enabled"] = True
        night_mode_configs[chat_id] = config  # Guardar la configuración
        await update.message.reply_text("Modo nocturno activado.")
    elif action == "off":
        config["enabled"] = False
        night_mode_configs[chat_id] = config  # Guardar la configuración
        await update.message.reply_text("Modo nocturno desactivado.")
    elif action == "set_start" and len(context.args) == 2:
        try:
            config["start"] = datetime.strptime(context.args[1], "%H:%M").time()
            night_mode_configs[chat_id] = config  # Guardar la configuración
            await update.message.reply_text(f"Hora de inicio del modo nocturno configurada a {context.args[1]}.")
        except ValueError:
            await update.message.reply_text("Formato de hora inválido. Usa HH:MM (24 horas).")
    elif action == "set_end" and len(context.args) == 2:
        try:
            config["end"] = datetime.strptime(context.args[1], "%H:%M").time()
            night_mode_configs[chat_id] = config  # Guardar la configuración
            await update.message.reply_text(f"Hora de finalización del modo nocturno configurada a {context.args[1]}.")
        except ValueError:
            await update.message.reply_text("Formato de hora inválido. Usa HH:MM (24 horas).")
    else:
        await update.message.reply_text("Opción no válida. Usa 'on', 'off', 'set_start' o 'set_end'.")

# Eliminar cualquier trabajo anterior que esté programado para el grupo
def remove_existing_job(context: ContextTypes.DEFAULT_TYPE, chat_id):
    current_jobs = context.job_queue.get_jobs_by_name(f"rules_auto_job_{chat_id}")
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()

# Función principal para ejecutar el bot
async def main():
    application = Application.builder().token("8094482824:AAHIXYxVtaYbSy1mhG3GCuAcvj5MCF8CbJg").build()
    # Cargar configuraciones al iniciar el bot
    load_configs()

    # Establecer los comandos
    await set_commands(application)
    
    # Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_forbidden_words))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("kick", kick_user))
    application.add_handler(CommandHandler("warn", warn_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("info", user_info))
    application.add_handler(CommandHandler("config", configure))
    application.add_handler(CommandHandler("wordlist", manage_banned_words))

    # Agregar manejadores
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))

    # Añadir manejadores para los nuevos comandos
    application.add_handler(CommandHandler("set_welcome_media", set_welcome_media))
    application.add_handler(CommandHandler("set_goodbye_media", set_goodbye_media))

    # Manejadores de comandos
    application.add_handler(CommandHandler("rules", rules_info))
    application.add_handler(CommandHandler("rules_auto", rules_auto))
    application.add_handler(CommandHandler("rules_edit", rules_edit))

    # Añadir el manejador para el comando /night_mode
    application.add_handler(CommandHandler("night_mode", night_mode))

    # Añadir el manejador para filtrar mensajes durante el modo nocturno
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    await application.run_polling()
    await set_commands(application)

# Ejecutar la función main
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
