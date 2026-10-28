import math
import random
import turtle


ANCHO_VENTANA = 800
ALTO_VENTANA = 600
TAMANO_CELDA = 20
ANCHO_CELDAS = 19
ALTO_CELDAS = 14
INTERVALO_BASE = 150
XP_INICIAL_PARA_SUBIR = 5

ventana = turtle.Screen()
ventana.setup(width=ANCHO_VENTANA, height=ALTO_VENTANA)
ventana.bgcolor("black")
ventana.title("Snake Survivor")
ventana.tracer(0)

texto_puntuacion = turtle.Turtle()
texto_puntuacion.hideturtle()
texto_puntuacion.color("white")
texto_puntuacion.penup()

barra_xp = turtle.Turtle()
barra_xp.hideturtle()
barra_xp.speed(0)
barra_xp.penup()

texto_menu = turtle.Turtle()
texto_menu.hideturtle()
texto_menu.color("white")
texto_menu.penup()

texto_mensaje = turtle.Turtle()
texto_mensaje.hideturtle()
texto_mensaje.color("white")
texto_mensaje.penup()

snake = [(0, 0), (-TAMANO_CELDA, 0), (-2 * TAMANO_CELDA, 0)]
direccion = "right"
siguiente_direccion = "right"
partes_serpiente = []
manzana = turtle.Turtle()
manzana.shape("circle")
manzana.color("red")
manzana.penup()
manzana.shapesize(stretch_wid=0.8, stretch_len=0.8)

puntuacion = 0
nivel = 1
experiencia = 0
xp_para_subir = XP_INICIAL_PARA_SUBIR
xp_pendiente = 0
juego_terminado = False
pausado_mejoras = False
niveles_pendientes = 0
enemigos = []
proyectiles = []
ticks = 0
disparos_automaticos = 0
mejoras = {
    "velocidad": 0,
    "longitud": 0,
    "rastro": 0,
    "aura": 0,
}
cargas_escudo = 0
opciones_actuales = []

CATALOGO_MEJORAS = {
    "proyectiles": (
        "Disparo automatico",
        "Dispara proyectiles teledirigidos con mas frecuencia.",
    ),
    "velocidad": (
        "Serpiente veloz",
        "Aumenta la velocidad de movimiento.",
    ),
    "longitud": (
        "Crecimiento",
        "Anade dos segmentos a la serpiente.",
    ),
    "rastro": (
        "Rastro danino",
        "El cuerpo elimina a los enemigos que lo tocan.",
    ),
    "aura": (
        "Aura y escudo",
        "Dania enemigos cercanos y bloquea un choque.",
    ),
}


def crear_sprite(forma, color, tamano=1.0):
    sprite = turtle.Turtle()
    sprite.shape(forma)
    sprite.color(color)
    sprite.penup()
    sprite.shapesize(stretch_wid=tamano, stretch_len=tamano)
    return sprite


def dibujar_hud():
    texto_puntuacion.clear()
    texto_puntuacion.goto(0, 267)
    texto_puntuacion.write(
        f"Puntuacion: {puntuacion}   Nivel: {nivel}   Escudos: {cargas_escudo}",
        align="center",
        font=("Arial", 14, "normal"),
    )
    texto_puntuacion.goto(0, 242)
    texto_puntuacion.write(
        f"XP: {experiencia}/{xp_para_subir}",
        align="center",
        font=("Arial", 11, "normal"),
    )

    barra_xp.clear()
    ancho_barra = 300
    alto_barra = 10
    porcentaje = min(experiencia / xp_para_subir, 1)
    barra_xp.goto(-ancho_barra / 2, 226)
    barra_xp.pendown()
    barra_xp.color("white")
    for dx, dy in ((ancho_barra, 0), (0, alto_barra), (-ancho_barra, 0), (0, -alto_barra)):
        barra_xp.setheading(math.degrees(math.atan2(dy, dx)))
        barra_xp.forward(math.hypot(dx, dy))
    barra_xp.penup()
    if porcentaje:
        barra_xp.goto(-ancho_barra / 2, 226)
        barra_xp.setheading(0)
        barra_xp.color("lime")
        barra_xp.begin_fill()
        for dx, dy in (
            (ancho_barra * porcentaje, 0),
            (0, alto_barra),
            (-ancho_barra * porcentaje, 0),
            (0, -alto_barra),
        ):
            barra_xp.setheading(math.degrees(math.atan2(dy, dx)))
            barra_xp.forward(math.hypot(dx, dy))
        barra_xp.end_fill()
        barra_xp.penup()


def generar_manzana():
    ocupadas = set(snake)
    ocupadas.update((enemigo["x"], enemigo["y"]) for enemigo in enemigos)
    while True:
        x = random.randint(-ANCHO_CELDAS, ANCHO_CELDAS) * TAMANO_CELDA
        y = random.randint(-ALTO_CELDAS, ALTO_CELDAS) * TAMANO_CELDA
        if (x, y) not in ocupadas:
            manzana.goto(x, y)
            return


def cambiar_direccion(nueva_direccion):
    global siguiente_direccion
    opuestos = {"left": "right", "right": "left", "up": "down", "down": "up"}
    if nueva_direccion in opuestos and opuestos[nueva_direccion] != direccion:
        siguiente_direccion = nueva_direccion


def dibujar_serpiente():
    while len(partes_serpiente) < len(snake):
        parte = crear_sprite("square", "green")
        partes_serpiente.append(parte)

    for indice, parte in enumerate(partes_serpiente):
        if indice < len(snake):
            parte.goto(snake[indice])
            parte.showturtle()
            parte.color("lime" if indice == 0 else "green")
        else:
            parte.hideturtle()


def dibujar_enemigos():
    for enemigo in enemigos:
        enemigo["sprite"].goto(enemigo["x"], enemigo["y"])


def generar_enemigo():
    for _ in range(100):
        lado = random.choice(("left", "right", "top", "bottom"))
        if lado in ("left", "right"):
            x = random.choice((-ANCHO_CELDAS, ANCHO_CELDAS)) * TAMANO_CELDA
            y = random.randint(-ALTO_CELDAS, ALTO_CELDAS) * TAMANO_CELDA
        else:
            x = random.randint(-ANCHO_CELDAS, ANCHO_CELDAS) * TAMANO_CELDA
            y = random.choice((-ALTO_CELDAS, ALTO_CELDAS)) * TAMANO_CELDA
        if (x, y) not in snake and (x, y) != (manzana.xcor(), manzana.ycor()):
            enemigo = {
                "x": x,
                "y": y,
                "sprite": crear_sprite("circle", "orange", 0.8),
            }
            enemigo["sprite"].goto(x, y)
            enemigos.append(enemigo)
            return


def eliminar_enemigo(enemigo):
    if enemigo not in enemigos:
        return
    enemigos.remove(enemigo)
    enemigo["sprite"].hideturtle()
    ganar_xp(2)


def ganar_xp(cantidad):
    global xp_pendiente
    xp_pendiente += cantidad


def procesar_xp_pendiente():
    global experiencia, nivel, xp_para_subir, niveles_pendientes, xp_pendiente
    experiencia += xp_pendiente
    xp_pendiente = 0
    while experiencia >= xp_para_subir:
        experiencia -= xp_para_subir
        nivel += 1
        niveles_pendientes += 1
        xp_para_subir = XP_INICIAL_PARA_SUBIR + (nivel - 1) * 3
    dibujar_hud()
    if niveles_pendientes and not pausado_mejoras:
        mostrar_mejoras()


def mostrar_mejoras():
    global pausado_mejoras, opciones_actuales, niveles_pendientes
    pausado_mejoras = True
    niveles_pendientes -= 1
    opciones_actuales = random.sample(list(CATALOGO_MEJORAS), 3)
    texto_menu.clear()
    texto_menu.goto(0, 80)
    texto_menu.write(
        f"Nivel {nivel} - Elige una mejora (teclas 1, 2 o 3)",
        align="center",
        font=("Arial", 18, "bold"),
    )
    for indice, clave in enumerate(opciones_actuales, start=1):
        nombre, descripcion = CATALOGO_MEJORAS[clave]
        texto_menu.goto(0, 35 - (indice - 1) * 55)
        texto_menu.write(
            f"{indice}. {nombre}\n   {descripcion}",
            align="center",
            font=("Arial", 12, "normal"),
        )
    ventana.update()


def aplicar_mejora(clave):
    global disparos_automaticos, cargas_escudo
    if clave == "proyectiles":
        disparos_automaticos += 1
    elif clave == "longitud":
        mejoras["longitud"] += 1
        cola_x, cola_y = snake[-1]
        anterior_x, anterior_y = snake[-2]
        dx = cola_x - anterior_x
        dy = cola_y - anterior_y
        snake.extend(((cola_x + dx, cola_y + dy), (cola_x + 2 * dx, cola_y + 2 * dy)))
        dibujar_serpiente()
    elif clave == "aura":
        mejoras["aura"] += 1
        cargas_escudo += 1
    else:
        mejoras[clave] += 1


def elegir_mejora(indice):
    global pausado_mejoras
    if not pausado_mejoras or not 1 <= indice <= len(opciones_actuales):
        return
    aplicar_mejora(opciones_actuales[indice - 1])
    texto_menu.clear()
    pausado_mejoras = False
    dibujar_hud()
    if niveles_pendientes:
        mostrar_mejoras()
    else:
        ventana.update()
        mover_serpiente()


def disparar_proyectil():
    if not enemigos:
        return
    cabeza_x, cabeza_y = snake[0]
    objetivo = min(
        enemigos,
        key=lambda enemigo: math.hypot(enemigo["x"] - cabeza_x, enemigo["y"] - cabeza_y),
    )
    sprite = crear_sprite("circle", "yellow", 0.35)
    sprite.goto(cabeza_x, cabeza_y)
    proyectiles.append({"sprite": sprite, "objetivo": objetivo})


def actualizar_proyectiles():
    for proyectil in proyectiles[:]:
        objetivo = proyectil["objetivo"]
        if objetivo not in enemigos:
            proyectil["sprite"].hideturtle()
            proyectiles.remove(proyectil)
            continue
        sprite = proyectil["sprite"]
        dx = objetivo["x"] - sprite.xcor()
        dy = objetivo["y"] - sprite.ycor()
        distancia = math.hypot(dx, dy)
        if distancia <= 14:
            sprite.hideturtle()
            proyectiles.remove(proyectil)
            eliminar_enemigo(objetivo)
            continue
        paso = min(14, distancia)
        sprite.goto(sprite.xcor() + dx / distancia * paso, sprite.ycor() + dy / distancia * paso)


def mover_enemigos():
    global cargas_escudo
    cabeza_x, cabeza_y = snake[0]
    for enemigo in enemigos[:]:
        dx = cabeza_x - enemigo["x"]
        dy = cabeza_y - enemigo["y"]
        if abs(dx) >= abs(dy) and dx:
            enemigo["x"] += TAMANO_CELDA if dx > 0 else -TAMANO_CELDA
        elif dy:
            enemigo["y"] += TAMANO_CELDA if dy > 0 else -TAMANO_CELDA
        if (enemigo["x"], enemigo["y"]) == snake[0]:
            if cargas_escudo:
                cargas_escudo -= 1
                enemigos.remove(enemigo)
                enemigo["sprite"].hideturtle()
                ganar_xp(2)
            else:
                fin_del_juego()
                return


def actualizar_mejoras_ofensivas():
    global ticks
    if disparos_automaticos:
        intervalo = max(3, 8 - (disparos_automaticos - 1) * 2)
        if ticks % intervalo == 0:
            disparar_proyectil()
    actualizar_proyectiles()

    if mejoras["rastro"]:
        posiciones_cuerpo = set(snake[1:])
        for enemigo in enemigos[:]:
            if (enemigo["x"], enemigo["y"]) in posiciones_cuerpo:
                eliminar_enemigo(enemigo)

    if mejoras["aura"] and ticks % 6 == 0:
        cabeza_x, cabeza_y = snake[0]
        for enemigo in enemigos[:]:
            if math.hypot(enemigo["x"] - cabeza_x, enemigo["y"] - cabeza_y) <= 40:
                eliminar_enemigo(enemigo)


def fin_del_juego():
    global juego_terminado
    juego_terminado = True
    texto_mensaje.clear()
    texto_mensaje.goto(0, 35)
    texto_mensaje.write(
        f"Game Over\nPuntuacion: {puntuacion}  Nivel: {nivel}\nPresiona R para reiniciar",
        align="center",
        font=("Arial", 17, "normal"),
    )
    ventana.update()


def limpiar_entidades():
    for enemigo in enemigos:
        enemigo["sprite"].hideturtle()
    enemigos.clear()
    for proyectil in proyectiles:
        proyectil["sprite"].hideturtle()
    proyectiles.clear()


def reiniciar_juego():
    global snake, direccion, siguiente_direccion, puntuacion, nivel, experiencia
    global xp_para_subir, xp_pendiente, juego_terminado, pausado_mejoras, niveles_pendientes
    global ticks, disparos_automaticos, mejoras, cargas_escudo, opciones_actuales

    if not juego_terminado:
        return
    limpiar_entidades()
    for parte in partes_serpiente:
        parte.hideturtle()
    partes_serpiente.clear()
    snake = [(0, 0), (-TAMANO_CELDA, 0), (-2 * TAMANO_CELDA, 0)]
    direccion = "right"
    siguiente_direccion = "right"
    puntuacion = 0
    nivel = 1
    experiencia = 0
    xp_para_subir = XP_INICIAL_PARA_SUBIR
    xp_pendiente = 0
    juego_terminado = False
    pausado_mejoras = False
    niveles_pendientes = 0
    ticks = 0
    disparos_automaticos = 0
    mejoras = {"velocidad": 0, "longitud": 0, "rastro": 0, "aura": 0}
    cargas_escudo = 0
    opciones_actuales = []
    texto_mensaje.clear()
    texto_menu.clear()
    dibujar_serpiente()
    generar_manzana()
    dibujar_hud()
    ventana.update()
    mover_serpiente()


def mover_serpiente():
    global direccion, puntuacion, juego_terminado, cargas_escudo, ticks

    if juego_terminado or pausado_mejoras:
        return

    ticks += 1
    direccion = siguiente_direccion
    cabeza_x, cabeza_y = snake[0]
    movimientos = {
        "right": (TAMANO_CELDA, 0),
        "left": (-TAMANO_CELDA, 0),
        "up": (0, TAMANO_CELDA),
        "down": (0, -TAMANO_CELDA),
    }
    dx, dy = movimientos[direccion]
    nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)

    if (
        abs(nueva_cabeza[0]) > ANCHO_CELDAS * TAMANO_CELDA
        or abs(nueva_cabeza[1]) > ALTO_CELDAS * TAMANO_CELDA
        or nueva_cabeza in snake
    ):
        fin_del_juego()
        return

    enemigo_en_cabeza = next(
        (
            enemigo
            for enemigo in enemigos
            if (enemigo["x"], enemigo["y"]) == nueva_cabeza
        ),
        None,
    )
    if enemigo_en_cabeza:
        if cargas_escudo:
            cargas_escudo -= 1
            enemigos.remove(enemigo_en_cabeza)
            enemigo_en_cabeza["sprite"].hideturtle()
            ganar_xp(2)
        else:
            fin_del_juego()
            return

    snake.insert(0, nueva_cabeza)
    if nueva_cabeza == (manzana.xcor(), manzana.ycor()):
        puntuacion += 1
        generar_manzana()
        ganar_xp(1)
    else:
        snake.pop()

    if ticks % 3 == 0:
        mover_enemigos()
        if juego_terminado:
            return
    if ticks % 25 == 0 and len(enemigos) < 10:
        for _ in range(min(1 + (nivel - 1) // 3, 4)):
            if len(enemigos) < 10:
                generar_enemigo()

    actualizar_mejoras_ofensivas()
    procesar_xp_pendiente()
    dibujar_serpiente()
    dibujar_enemigos()
    dibujar_hud()
    ventana.update()
    if not pausado_mejoras and not juego_terminado:
        intervalo = max(70, INTERVALO_BASE - mejoras["velocidad"] * 12)
        ventana.ontimer(mover_serpiente, intervalo)


dibujar_serpiente()
generar_manzana()
dibujar_hud()
ventana.listen()
ventana.onkey(lambda: cambiar_direccion("up"), "Up")
ventana.onkey(lambda: cambiar_direccion("down"), "Down")
ventana.onkey(lambda: cambiar_direccion("left"), "Left")
ventana.onkey(lambda: cambiar_direccion("right"), "Right")
ventana.onkey(lambda: cambiar_direccion("up"), "w")
ventana.onkey(lambda: cambiar_direccion("down"), "s")
ventana.onkey(lambda: cambiar_direccion("left"), "a")
ventana.onkey(lambda: cambiar_direccion("right"), "d")
ventana.onkey(lambda: elegir_mejora(1), "1")
ventana.onkey(lambda: elegir_mejora(2), "2")
ventana.onkey(lambda: elegir_mejora(3), "3")
ventana.onkey(reiniciar_juego, "r")
ventana.onkey(reiniciar_juego, "R")

mover_serpiente()
ventana.mainloop()
