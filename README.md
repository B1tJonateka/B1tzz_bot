##                                                Creacion de prototipo de Bot para Telegram
Para este se es necesario la instalacion de la biblioteca Telebot de Python


## Cofiguracion 
1. Clana el repositorio
2. Instalar las dependencias usando 'pin install -r requirements.txt'
3. Crear un bot en Telegram a traves de BotFather y obtener el token de este.
4. Remplaza 'TU_TOKEN_AQUI' en 'main.py' con tu token.
5. Ejecuta el bot usando 'python main.py'


##                                                 Uso de comandos:
## Mostrar la lista de palabras prohibidas:

* Comando: /wordlist show
  - Respuesta esperada: La lista de palabras prohibidas actuales.

* Añadir una palabra a la lista de palabras prohibidas:
  - Comando: /wordlist add <palabra>
  - Ejemplo: /wordlist add spam
Respuesta esperada: Confirmación de que la palabra se ha añadido, por ejemplo: La palabra 'spam' ha sido añadida a la lista.
Eliminar una palabra de la lista de palabras prohibidas:

* Comando: /wordlist remove <palabra>
  - Ejemplo: /wordlist remove spam
Respuesta esperada: Confirmación de que la palabra se ha eliminado, por ejemplo: La palabra 'spam' ha sido eliminada de la lista.
Limpiar toda la lista de palabras prohibidas:

* Comando: /wordlist clear
Respuesta esperada: Confirmación de que la lista ha sido vaciada, por ejemplo: La lista de palabras prohibidas ha sido limpiada.
Resumen de comandos:


* /wordlist show – Muestra la lista de palabras prohibidas.
* /wordlist add <palabra> – Añade una palabra a la lista.
* /wordlist remove <palabra> – Elimina una palabra de la lista.
* /wordlist clear – Limpia toda la lista.



## Comandos para las reglas 

* Comando /rules:
  - Descripción: Este comando muestra las reglas del grupo.
  - Uso: Un usuario puede enviar el mensaje /rules en el chat.
  - Función:
    1. La función rules_info es llamada cuando el comando es recibido.
    2. Envía un mensaje al chat con las reglas definidas en la variable global rules


* Comando /rules_auto:
  - Descripción: Este comando permite a los administradores activar o desactivar la auto-mostración de las reglas del grupo cada minuto.
  - Uso: Un administrador debe enviar el mensaje /rules_auto on para activar la función o /rules_auto off para desactivarla.
  - Función:
    1. La función rules_auto es llamada cuando el comando es recibido.
    2. Si se pasa el argumento on, se activa la auto-mostración y se programa el trabajo que muestra las reglas cada minuto.
    3. Si se pasa el argumento off, se desactiva la auto-mostración y se eliminan los trabajos programados.
    4. Si el argumento no es válido, se muestra un mensaje indicando cómo usar el comando

* Comando /rules_edit:
  - Descripción: El comando /rules_edit permite a los administradores del grupo actualizar las reglas del grupo de manera sencilla y eficiente. En lugar de escribir nuevas reglas directamente en el comando, se pueden tomar de un mensaje anterior.
  - uso: Un administrador redacta un nuevo conjunto de reglas (que puede estar en un documento o mentalmente) y lo envía en otro mensaje, El administrador quiere que estas nuevas reglas reemplacen a las anteriores, así que envía el comando /rules_edit como respuesta al mensaje que contiene las reglas anteriores (debe seleccionar el mensaje anterior y hacer clic en "Responder"). Al hacer esto, el bot detectará que se está respondiendo a un mensaje y tomará el contenido de ese mensaje como las nuevas reglas.

  - Función:
    1. Si el administrador responde a un mensaje que contiene las reglas anteriores:
    2. El bot toma el contenido de ese mensaje como las nuevas reglas.
    3. Actualiza la variable global rules con el nuevo contenido.
    4. Envía un mensaje de confirmación al grupo indicando que las reglas han sido actualizadas.
    5. Si no se está respondiendo a un mensaje:
    6. El bot envía un mensaje solicitando que se responda a un mensaje que contenga las reglas para poder actualizarlas.


## Comandos para la configuración de bienvenida y despedida

* Comando /config welcome:
  - Descripción: Sirve para que los administradores configuren el mensaje y video/imagen de bienvenida
  - uso: El usuario con derechos de administrador debe ejecutar el comando /config welcome 
	1. Si el administrador quiere cambiar el mensaje de bienvenida debe ejecutar /config welcome (mensaje de bienvenida)
         posdata: si se quiere identificar el nombre del usuario se debe escribir '{first_name}' ejemplo: (/config welcome ¡Bienvenido/a, 	{first_name}! Esperamos que disfrutes tu estadía!), entonces el bot mostrara como mensaje '¡Bienvenido/a, (nombre de usuario)! 		Esperamos que disfrutes tu estadía!'
	
	2. Si el administrador quiero cambiar la foto/video del mensaje de bienvenida, entonces: 
	a) Debe de enviar de antemano una foto o video con la cual quiere actualizar en el mensaje de bienvenida
	b) Responder a este mensaje que contiene la foto/video con el comando /config welcome
        posdata: La foto o video ya puede haber sido enviada anterior mente por otro usuario, así que se puede seleccionar cualquier tipo de 	media subida en el grupo. Lo único obligatorio es que se debe responder a dicho mensaje con el comando /config welcome

	- Función: 
	  1. Al llamar el comando /config welcome, el bot primero revisa si el usuario tiene derechos de administrador. Si este no los tiene 	  entonces responderá a este diciendo que no tiene derechos para ejecutar el comando
	  2. Si al ejecutar el comando el administrador no esta respondiendo a ningún otro video, entonces este actualizara automáticamente el 	  mensaje de bienvenida, sin necesidad si este contiene un mensaje o no. Así que verifica primero si escribiste el mensaje con el que 	  quiere actualizar la bienvenida 
	  3. Si al ejecutar el comando /config welcome el administrador esta respondiendo a un mensaje. Primero, verifica si este mensaje    	  contiene una imagen o video, si no la tiene se lo hace saber. Segundo, verifica si el formato de la foto o video es compatible, si	  no lo es se lo hace saber. Tercero, si las verificaciones anteriores son correctas. Entonces le devuelve al administrador un 
  	  mensaje afirmado que se actualizo correctamente la imagen o video


* Comando /config goodbye:
  - Descripción: Sirve para que los administradores configuren el mensaje y video/imagen de despedida
  - uso: El usuario con derechos de administrador debe ejecutar el comando /config goodbye
	1. Si el administrador quiere cambiar el mensaje de despedida debe ejecutar /config goodbye (mensaje de despedida)
         posdata: si se quiere identificar el nombre del usuario se debe escribir '{first_name}' ejemplo: (/config goodbye {first_name} ha 	 salido del grupo. ¡Te extrañaremos!), entonces el bot mostrara como mensaje '(nombre de usuario) ha salido del grupo, ¡Te    	 	 extrañaremos!'	
	2. Si el administrador quiero cambiar la foto/video del mensaje de despedida, entonces: 
	a) Debe de enviar de antemano una foto o video con la cual quiere actualizar en el mensaje de despedida
	b) Responder a este mensaje que contiene la foto/video con el comando /config goodbye
        posdata: La foto o video ya puede haber sido enviada anterior mente por otro usuario, así que se puede seleccionar cualquier tipo de 	media subida en el grupo. Lo único obligatorio es que se debe responder a dicho mensaje con el comando /config goodbye

	- Función: 
	  1. Al llamar el comando /config goodbye, el bot primero revisa si el usuario tiene derechos de administrador. Si este no los tiene 	  entonces responderá a este diciendo que no tiene derechos para ejecutar el comando
	  2. Si al ejecutar el comando el administrador no esta respondiendo a ningún otro video, entonces este actualizara automáticamente el 	  mensaje de despedida, sin necesidad si este contiene un mensaje o no. Así que verifica primero si escribiste el mensaje con el que 	  quiere actualizar la despedida
	  3. Si al ejecutar el comando /config goodbye el administrador esta respondiendo a un mensaje. Primero, verifica si este mensaje    	  contiene una imagen o video, si no la tiene se lo hace saber. Segundo, verifica si el formato de la foto o video es compatible, si no lo es se lo hace saber. Tercero, si las verificaciones anteriores son correctas. Entonces le devuelve al administrador un mensaje afirmado que se actualizo correctamente la imagen o video

* Comando /set_welcome_media: 
  - Descripción: Este es similar al comando /config welcome. Pero con la diferencia que no actualiza el mensaje de bienvenida pero si la imagen/video. Esto lo hace por medio de un link
  - Uso: El usuario con derechos de administrador debe ejecutar el comando /set_welcome_media 
	1. Para cambiar por una foto se debe ejecutar el comando /set_welcome_media (link de la imagen). Este link obligatoriamente debe de terminar con un formato de imagen 		compatible, las cuales son: jpg, jpeg, png, webp. como por ejemplo: /set_welcome_media https://noticias.animeonegai.com/wp-content/uploads/2022/10/Tokidoki-Bosotto-	Roshia-Go-	de-Dereru-Tonari-no-Arya-San-NL-vol-5-min-1.webp 

	2. Para cambiar por un video se debe ejecutar el comando /set_welcome_media (link del vide) este link obligatoria mente debe de terminar con un formato de video compatible, los cuales son: mp4, mov, gif. como por ejemplo: /set_welcome_media https://tenor.com/iJEY8R2BS85.gif

  - Función:
    1. al llamar el comando  /set_welcome_media el bot revisa si copio algún link, si no se hizo el bot se lo hara saber a quien ejecuto el comando
    2. Si el bot detecta que se copio un link, este actualizara automáticamente el link de la media y se lo hara saber a quien ejecuto el comando

* Comando /set_goodbye_media: 
  - Descripción: Este es similar al comando /config goodbye. Pero con la diferencia que no actualiza el mensaje de despedida pero si la imagen/video. Esto lo hace por medio de un link
  - Uso: El usuario con derechos de administrador debe ejecutar el comando /set_goodbye_media 
	1. Para cambiar por una foto se debe ejecutar el comando /set_goodbye_media (link de la imagen). Este link obligatoriamente debe de terminar con un formato de imagen 		compatible, las cuales son: jpg, jpeg, png, webp. como por ejemplo: /set_goodbye_media https://somoskudasai.com/wp-content/uploads/2021/11/portada_tokidoki-4.jpg 

	2. Para cambiar por un video se debe ejecutar el comando /set_goodbye_media (link del vide) este link obligatoria mente debe de terminar con un formato de video compatible, los cuales son: mp4, mov, gif. como por ejemplo: /set_welcome_media https://tenor.com/iJEY8R2BS85.gif

  - Función:
    1. al llamar el comando  /set_goodbye_media el bot revisa si copio algún link, si no se hizo el bot se lo hara saber a quien ejecuto el comando
    2. Si el bot detecta que se copio un link, este actualizara automáticamente el link de la media y se lo hara saber a quien ejecuto el comando



## Comando para Banear
* Comando /ban:
  - Descripción: Banear a un usuario del grupo.
  - Uso: Los usuarios con derechos de administrador pueden ejecutar el comando /ban (nombre o username del usuario) o respondiendo a un mensaje 
  enviado por el usuario a banear con el comando /ban
  - Función:
    1. Si el administrador responde a un mensaje enviado por el usuario a banear o copiando su nombre o username con el comando '/ban' el usuario es baneado y eliminado
    2. Cuando el bot detecta que un usuario fue baneado, envía al grupo un mensaje que el usuario en cuestión fue baneado
    3. Si un usuario no administrador intenta usar el comando /ban, el bot le notificara que no tiene permisos suficientes para ejecutar el comando

* Comando /kick:
  - Descripción: eliminar a un usuario del grupo.
  - Uso: Los usuarios con derechos de administrador pueden ejecutar el comando /kick (nombre o username del usuario) o respondiendo a un mensaje 
  enviado por el usuario a kickear con el comando /kick
  - Función:
    1. Si el administrador responde a un mensaje enviado por el usuario a banear o copiando su nombre o username con el comando '/kick' el usuario es eliminado
    2. Cuando el bot detecta que un usuario fue eliminado, envía al grupo un mensaje que el usuario en cuestión se salió del grupo
    3. Si un usuario no administrador intenta usar el comando /kick, el bot le notificara que no tiene permisos suficientes para ejecutar el comando


* Comando /unban:
  - Descripción: desbanear a un usuario del grupo.
  - Uso: Los usuarios con derechos de administrador pueden ejecutar el comando /unban (nombre o username del usuario) o respondiendo a un mensaje 
  enviado por el usuario a quitar el ban con el comando /unban
  - Función:
    1. Si el administrador responde a un mensaje enviado por el usuario a desbanear o copiando su nombre o username con el comando '/unban' se quita el ban al usuario
    2. Cuando el bot detecta que un usuario fue desbaneado, envía al grupo un mensaje que el usuario en cuestión se le fue quitado el ban
    3. Si un usuario no administrador intenta usar el comando /unban, el bot le notificara que no tiene permisos suficientes para ejecutar el comando

* Comando /info 
  - Descripcion: Mostrar información sobre un usuario (ID, nombre, username)
  - Uso: Los usuarios con derechos de administrador pueden ejecutar el comando /info (nombre o username del usuario) o respondiendo a un mensaje 
  enviado por el usuario a ver informacion con el comando /info 

## Comando para el modo noche

/config night_mode on: Activa el modo nocturno.
/config night_mode off: Desactiva el modo nocturno.
Configurar horas del modo nocturno:

/config night_mode set_start HH:MM: Configura la hora de inicio del modo nocturno.
/config night_mode set_end HH:MM: Configura la hora de finalización del modo nocturno.
Este código permitirá que las configuraciones se