# DYNAMIC QR CODE GENERATOR
#### Video Demo: [https://youtu.be/_28d_gK2h8Q](URL)
#### Descripción:

Esta aplicación de Flask genera codigos QR que almacenan una dirección única al host de la aplicación, redirigiendo a la URL activa para ese código QR, manteniendo seguimiento de la cantidad de veces que fue leído el código QR para determinada URL y permitiendo cambiar la URL a la que redirige el mismo código.

#### Planteamiento del problema:
Dependiendo de la cantidad de datos/caracteres que un código QR almace, la complejidad de la imagen y la matriz de sus cuadros aumentará exponencialmente. Es decir, que en caso de almacenar texto o una URL con muchos caracteres, la imagen contendrá un patrón de cuadros cada vez más complejo, lo que dificulta por ejemplo imprimir esa imagen en tamaños pequeños como el caso de tarjetas de presentación, llaveros o placas.

Manteniendo la cantidad de caracteres que contiene el código QR al mínimo, se puede mantener un patrón simple facil de imprimir y leer.

Entonces, si se puede crear un código QR, cuyo patrón simple conecte a una base de datos donde se almacenen datos más complejos, es posible guardar grandes cantidades de datos en una imagen QR sin necesidad de aumentar la complejidad de esta.

## Principales dependencias:

- Flask
- Qrcode
- Sqlalchemy
- Bcrypt
- Shortuuid

### Flask

Contiene la aplicación principal y permite correr la aplicación en un entorno web de producción.

### QRCode

Generador de códigos QR que son almacenados en formato .pgn.

### SQLAlchemy
Enlace con la base de datos usada, para este caso un archivo .db de sqlite3.

### BCrypt
Encriptador para las contraseñas creadas para cada código QR.

### ShortUUID
Genera la ruta única para cada código QR a partir de un codigo UUID.

## Estructura de base de datos

### Tabla QR

| Campo          | Tipo   | Clave Primaria | Único | Nulo | Descripción                  |
|----------------|--------|----------------|-------|------|-----------------------------|
| qr_id          | Integer| Sí             | No    | No   | ID único del código QR     |
| short_url      | String | No             | Sí    | Sí   | URL corta del código QR     |
| path           | String | No             | Sí    | Sí   | Ruta del código QR          |
| qr_image       | String | No             | No    | Sí   | Ruta de la imagen del QR   |
| password       | String | No             | No    | Sí   | Contraseña del QR           |
| info           | Relación| No             | No    | No   | Relación con la tabla Info |

### Tabla Info

| Campo          | Tipo   | Clave Primaria | Único | Nulo | Descripción                           |
|----------------|--------|----------------|-------|------|--------------------------------------|
| info_id        | Integer| Sí             | No    | No   | ID único de la información           |
| qr_id          | Integer| No             | No    | No   | ID del código QR relacionado         |
| original_url   | String | No             | No    | No   | URL original a la que se redirige    |
| number_opened  | Integer| No             | No    | No   | Número de veces que se ha abierto    |
| current_link   | Integer| No             | No    | No   | Enlace actual activo (0 o 1)         |
| qr             | Relación| No             | No    | No   | Relación con la tabla QR             |


## Vistas
### index:
#### Template: index.html
Vista simple que redirige a la página principal de la aplicación.
### generate:
#### Template: generate.html
Dirige a la página para generar un código qr.

Mediante un formulario se ingresa el enlace al que se quiere redirigir el código QR, y se agrega una contraseña que servirá para poder acceder a los datos de dicho código qr.

Mediante la lógica interna de esta vista se almacenará en la base de datos la ruta única a la que dirigirá el código QR, el nombre de la imágen del código qr y la contraseña para acceder a la información del código QR. Además, en la tabla que contiene la información del código QR se almacenará el registro de la URL real a la que redirige el código QR, la cantidad de veces que el código QR ha redirigido a dicha URL y, mediante un valor booleano, si esa es la ruta a la que actualmente redirige el código QR.

### get_info:
#### Template: get_info.html
Mediante un formulario se ingresa la ruta corta y la contraseña del código QR, en caso de ser correctos esta vista redirige a la página de información del código QR que quedará almacenado en la sesión del navegador.

### info:
#### Template: info.html
Esta vista mostrará la información correspondiente al código qr almacenado en la sesión del navegador.

La página mostrará la imagen del código QR, la ruta corta y una tabla con el historial de URLs a las que se ha enlazado dicho QR. Este historial mustra cada enlace real al que redirige el código QR, la cantidad de veces que se ha abierto y si es el enlace activo al cual redirige el código QR, de todos los enlaces del historial, siempre será sólo uno el que esté activo, y el resto serán mostrados como inactivos.

Además, se agrega un formulario para cambiar la URL activa a la que redirige el código QR, en caso de que esta URL ya se encuentre en los registros del mismo código QR, se vuelve a activar. En el caso de que sea un nuevo registro, este se agrega y se marca como activo, desactivando el último registro activo.

### dynamic_redirect:
Esta vista toma como argumento la ruta de 6 caracteres generada por cada código, busca en los registros de la tabla qr de la base de datos y si lo encuentra redirige a la URL marcada como activa para ese código QR. En caso de que no exista dicha ruta de 6 caracteres devuelve error 404.

### clear_session:
Si el usuario tiene un código QR editable activo en la sesión de su navegador, puede dar click en el boton "limpiar sesion" del navbar y limpiar la sesión para evitar que otros puedan acceder a la información del último código QR consultado.

