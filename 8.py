import PySimpleGUI as sg
import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# Archivos
Archivos_Usuarios = 'usuarios.txt'
Archivos_Eventos = 'eventos.json'
Archivos_Participantes = 'participantes.csv'
Archivos_Configuracion = 'configuracion.json'

# Variables
usuarios = []
eventos = []
participantes = []
configuracion = {}

# Leer archivos al inicio
def cargar_datos():
    # Cargar usuarios
    try:
        with open(Archivos_Usuarios, 'r') as file:
            for linea in file:
                usuarios.append(linea.strip())
    except FileNotFoundError:
        sg.popup_error('Archivo de usuarios no encontrado')

    # Cargar eventos
    try:
        global eventos
        with open(Archivos_Eventos, 'r') as file:
            eventos = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        eventos = []

    # Cargar participantes
    try:
        global participantes
        participantes = pd.read_csv(Archivos_Participantes).to_dict(orient='records')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        participantes = []

    # Cargar configuracion
    try:
        global configuracion
        with open(Archivos_Configuracion, 'r') as file:
            configuracion = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        configuracion = {
            "-VALIDAR_AFORO-": False,
            "-SOLICITAR_IMAGENES-": False,
            "-MODIFICAR_REGISTROS-": False,
            "-ELIMINAR_REGISTROS-": False
        }

# Guardar datos
def guardar_datos():
    with open(Archivos_Eventos, 'w') as file:
        json.dump(eventos, file, indent=4)

    pd.DataFrame(participantes).to_csv(Archivos_Participantes, index=False)

    with open(Archivos_Configuracion, 'w') as file:
        json.dump(configuracion, file, indent=4)

# Interfaz de Login
def login_window():
    layout = [
        [sg.Text("Usuario"), sg.Input(size=(20, 1), key="-USUARIO-")],
        [sg.Text("Contraseña"), sg.Input(size=(20, 1), key="-CONTRASEÑA-", password_char='*')],
        [sg.Button("Ingresar", key="-INGRESAR-")]
    ]
    return sg.Window("Login", layout, finalize=True)

# Cargar datos iniciales
cargar_datos()

# Crear ventana de login
window = login_window()

logged_in = False

# Manejo de eventos de la ventana de login
while not logged_in:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    if event == "-INGRESAR-":
        usuario = values["-USUARIO-"]
        contrasena = values["-CONTRASEÑA-"]
        if f"{usuario},{contrasena}" in usuarios:
            logged_in = True
        else:
            sg.popup_error("Usuario o contraseña incorrectos")

guardar_datos()
window.close()

# Crear ventana principal
layout1 = [
    [sg.Text("Nombre del Evento"), sg.Input(size=(20, 1), key="-NOMBRE_EVENTO-"),
    sg.Text("Lugar"), sg.Input(size=(20, 1), key="-LUGAR-")],

    [sg.Text("Fecha"), sg.Input(size=(20, 1), key="-FECHA-"),
    sg.Text("Hora"), sg.Input(size=(20, 1), key="-HORA-")],

    [sg.Text("Cupo"), sg.Input(size=(20, 1), key="-CUPO-"),
    sg.Text("Imagen"), sg.Input(size=(20, 1), key="-IMAGEN_EVENTO-"),
    sg.FileBrowse("Buscar", key="-BROWSE_IMAGEN-", visible=False)],

    [sg.Button("Agregar", size=(10, 1), key="-AGREGAR_EVENTO-", visible=False),
    sg.Button("Modificar", size=(10, 1), key="-MODIFICAR_EVENTO-", visible=False),
    sg.Button("Eliminar", size=(10, 1), key="-ELIMINAR_EVENTO-", visible=False)],

    [sg.Listbox(values=[e['nombre'] for e in eventos], size=(40, 10), key="-LISTA_EVENTOS-"),
    sg.Image(key="-IMAGEN_EVENTO_DISPLAY-", size=(100, 100))]
]

layout2 = [
    [sg.Text("Eventos"), sg.Listbox(values=[e['nombre'] for e in eventos], size=(40, 5), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key="-EVENTOS_PARTICIPANTE-"),
    sg.Text("Nombre"), sg.Input(size=(20, 1), key="-NOMBRE_PARTICIPANTE-")],

    [sg.Text("Tipo de Documento"), sg.Input(size=(20, 1), key="-TIPO_DOCUMENTO-"),
    sg.Text("Número de Documento"), sg.Input(size=(20, 1), key="-NUMERO_DOCUMENTO-")],

    [sg.Text("Teléfono"), sg.Input(size=(20, 1), key="-TELEFONO-"),
    sg.Text("Tipo de Participante"), 
    sg.Combo(values=["Estudiante", "Profesional"], size=(20, 1), key="-TIPO_PARTICIPANTE-")],

    [sg.Text("Dirección"), sg.Input(size=(20, 1), key="-DIRECCION-"),
    sg.Text("Foto"), sg.Input(size=(20, 1), key="-FOTO_PARTICIPANTE-"),
    sg.FileBrowse("Buscar", key="-BROWSE_FOTO-")],

    [sg.Button("Agregar", size=(10, 1), key="-AGREGAR_PARTICIPANTE-", visible=False),
    sg.Button("Modificar", size=(10, 1), key="-MODIFICAR_PARTICIPANTE-", visible=False),
    sg.Button("Eliminar", size=(10, 1), key="-ELIMINAR_PARTICIPANTE-", visible=False)],

    [sg.Listbox(values=[p['nombre'] for p in participantes], size=(40, 10), key="-LISTA_PARTICIPANTES-"),
    sg.Image(key="-FOTO_PARTICIPANTE_DISPLAY-", size=(100, 100))]
]

layout3 = [
    [sg.Checkbox("Validar aforo al agregar participantes", key="-VALIDAR_AFORO-", enable_events=True)],
    [sg.Checkbox("Solicitar imágenes", key="-SOLICITAR_IMAGENES-", enable_events=True)],
    [sg.Checkbox("Modificar registros", key="-MODIFICAR_REGISTROS-", enable_events=True)],
    [sg.Checkbox("Eliminar registros", key="-ELIMINAR_REGISTROS-", enable_events=True)],
    [sg.Button("Guardar", size=(13, 1))]
]

layout_analysis = [
    [sg.Text("Análisis de Participantes")],
    [sg.Text("Participantes que fueron a todos los eventos")],
    [sg.Listbox(values=[], size=(40, 5), key="-TODOS_EVENTOS-")],
    [sg.Text("Participantes que fueron al menos a un evento")],
    [sg.Listbox(values=[], size=(40, 5), key="-AL_MENOS_UN_EVENTO-")],
    [sg.Text("Participantes que fueron solo al primer evento")],
    [sg.Listbox(values=[], size=(40, 5), key="-SOLO_PRIMER_EVENTO-")],
    [sg.Button("Actualizar Análisis", key="-ACTUALIZAR_ANALISIS-")]
]

layout_graphs = [
    [sg.Text("Gráficos de Eventos")],
    [sg.Button("Mostrar Gráficos", key="-MOSTRAR_GRAFICOS-")],
]

layout = [
    [sg.TabGroup([[
        sg.Tab("Eventos", layout1),
        sg.Tab("Participantes", layout2),
        sg.Tab("Configuración", layout3),
        sg.Tab("Análisis", layout_analysis),
        sg.Tab("Gráficos", layout_graphs)
    ]])],
    [sg.Button("Salir")]
]

window = sg.Window("Gestor de COP 16", layout, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Salir":
        guardar_datos()
        break

    # Checkbox
    if values.get("-SOLICITAR_IMAGENES-"):
        configuracion["-SOLICITAR_IMAGENES-"] = True
        window["-BROWSE_IMAGEN-"].update(visible=True)
        window["-BROWSE_FOTO-"].update(visible=True)
        window["-IMAGEN_EVENTO-"].update(visible=True)
        window["-FOTO_PARTICIPANTE-"].update(visible=True)
    else:
        configuracion["-SOLICITAR_IMAGENES-"] = False
        window["-BROWSE_IMAGEN-"].update(visible=False)
        window["-BROWSE_FOTO-"].update(visible=False)
        window["-IMAGEN_EVENTO-"].update(visible=False)
        window["-FOTO_PARTICIPANTE-"].update(visible=False)

    if values.get("-VALIDAR_AFORO-"):
        configuracion["-VALIDAR_AFORO-"] = True
        window["-AGREGAR_EVENTO-"].update(visible=True)
    else:
        configuracion["-VALIDAR_AFORO-"] = False
        window["-AGREGAR_EVENTO-"].update(visible=False)

    if values.get("-MODIFICAR_REGISTROS-"):
        configuracion["-MODIFICAR_REGISTROS-"] = True
        window["-MODIFICAR_EVENTO-"].update(visible=True)
    else:
        configuracion["-MODIFICAR_REGISTROS-"] = False
        window["-MODIFICAR_EVENTO-"].update(visible=False)

    if values.get("-ELIMINAR_REGISTROS-"):
        configuracion["-ELIMINAR_REGISTROS-"] = True
        window["-ELIMINAR_EVENTO-"].update(visible=True)
    else:
        configuracion["-ELIMINAR_REGISTROS-"] = False
        window["-ELIMINAR_EVENTO-"].update(visible=False)

    # Guardar automáticamente la configuración al cambiar los checkboxes
    guardar_datos()

    # Layout 2
    if values.get("-VALIDAR_AFORO-"):
        window["-AGREGAR_PARTICIPANTE-"].update(visible=True)
    else:
        window["-AGREGAR_PARTICIPANTE-"].update(visible=False)

    if values.get("-MODIFICAR_REGISTROS-"):
        window["-MODIFICAR_PARTICIPANTE-"].update(visible=True)
    else:
        window["-MODIFICAR_PARTICIPANTE-"].update(visible=False)

    if values.get("-ELIMINAR_REGISTROS-"):
        window["-ELIMINAR_PARTICIPANTE-"].update(visible=True)
    else:
        window["-ELIMINAR_PARTICIPANTE-"].update(visible=False)

    # Manejo de eventos
    if event == "-AGREGAR_EVENTO-":
        # Validar que todos los campos estén completos
        if not all([values["-NOMBRE_EVENTO-"], values["-LUGAR-"], values["-FECHA-"], values["-HORA-"], values["-CUPO-"], values["-IMAGEN_EVENTO-"]]):
            sg.popup_error("Todos los campos son obligatorios.")
            continue

        # Validar si el nombre del evento ya existe
        if any(e['nombre'] == values["-NOMBRE_EVENTO-"] for e in eventos):
            sg.popup_error("Ya existe un evento con este nombre.")
            continue

        # Validar valor numérico en el campo "Cupo"
        try:
            cupo = int(values["-CUPO-"])
        except ValueError:
            sg.popup_error("El campo 'Cupo' debe ser un valor numérico.")
            continue

        # Verificar si la imagen existe
        imagen_path = values["-IMAGEN_EVENTO-"]
        if imagen_path and not os.path.isfile(imagen_path):
            sg.popup_error("La imagen especificada no se encuentra.")
            continue

        nuevo_evento = {
            "nombre": values["-NOMBRE_EVENTO-"],
            "lugar": values["-LUGAR-"],
            "fecha": values["-FECHA-"],
            "hora": values["-HORA-"],
            "cupo": cupo,
            "imagen": imagen_path
        }
        eventos.append(nuevo_evento)

        # Guardar cambios en el archivo JSON
        guardar_datos()

        # Actualizar lista y combo de eventos
        window["-LISTA_EVENTOS-"].update(values=[e['nombre'] for e in eventos])
        window["-EVENTOS_PARTICIPANTE-"].update(values=[e['nombre'] for e in eventos])

        # Limpiar campos de entrada
        window["-NOMBRE_EVENTO-"].update("")
        window["-LUGAR-"].update("")
        window["-FECHA-"].update("")
        window["-HORA-"].update("")
        window["-CUPO-"].update("")
        window["-IMAGEN_EVENTO-"].update("")

    elif event == "-MODIFICAR_EVENTO-":
        evento_seleccionado = values["-LISTA_EVENTOS-"]
        if evento_seleccionado:
            index = [e['nombre'] for e in eventos].index(evento_seleccionado[0])  # índice del evento seleccionado
            # Validar que todos los campos estén completos
            if not all([values["-NOMBRE_EVENTO-"], values["-LUGAR-"], values["-FECHA-"], values["-HORA-"], values["-CUPO-"], values["-IMAGEN_EVENTO-"]]):
                sg.popup_error("Todos los campos son obligatorios.")
                continue

            # Validar si el nombre del evento ya existe (y no es el mismo evento que se está modificando)
            if any(e['nombre'] == values["-NOMBRE_EVENTO-"] and eventos.index(e) != index for e in eventos):
                sg.popup_error("Ya existe un evento con este nombre.")
                continue

            # Validar valor numérico en el campo "Cupo"
            try:
                cupo = int(values["-CUPO-"])
            except ValueError:
                sg.popup_error("El campo 'Cupo' debe ser un valor numérico.")
                continue

            # Verificar si la imagen existe
            imagen_path = values["-IMAGEN_EVENTO-"]
            if imagen_path and not os.path.isfile(imagen_path):
                sg.popup_error("La imagen especificada no se encuentra.")
                continue

            eventos[index] = {
                "nombre": values["-NOMBRE_EVENTO-"],
                "lugar": values["-LUGAR-"],
                "fecha": values["-FECHA-"],
                "hora": values["-HORA-"],
                "cupo": cupo,
                "imagen": imagen_path
            }

            # Guardar cambios en el archivo JSON
            guardar_datos()

            window["-LISTA_EVENTOS-"].update(values=[e['nombre'] for e in eventos])
            window["-EVENTOS_PARTICIPANTE-"].update(values=[e['nombre'] for e in eventos])

    elif event == "-ELIMINAR_EVENTO-":
        evento_seleccionado = values["-LISTA_EVENTOS-"]
        if evento_seleccionado:
            index = [e['nombre'] for e in eventos].index(evento_seleccionado[0])
            eventos.pop(index)  # Eliminar el evento seleccionado de la lista

            # Guardar cambios en el archivo JSON
            guardar_datos()

            window["-LISTA_EVENTOS-"].update(values=[e['nombre'] for e in eventos])
            window["-EVENTOS_PARTICIPANTE-"].update(values=[e['nombre'] for e in eventos])

    # Participantes
    if event == "-AGREGAR_PARTICIPANTE-":
        # Validar que todos los campos estén completos
        if not all([values["-NOMBRE_PARTICIPANTE-"], values["-TIPO_DOCUMENTO-"], values["-EVENTOS_PARTICIPANTE-"], values["-NUMERO_DOCUMENTO-"], values["-TELEFONO-"], values["-TIPO_PARTICIPANTE-"], values["-FOTO_PARTICIPANTE-"], values["-DIRECCION-"]]):
            sg.popup_error("Todos los campos son obligatorios.")
            continue

        # Validar valor numérico en el campo "Número de Documento"
        try:
            numero_documento = int(values["-NUMERO_DOCUMENTO-"])
        except ValueError:
            sg.popup_error("El campo 'Número de Documento' debe ser un valor numérico.")
            continue

        # Verificar duplicidad de número de documento
        if any(p['documento'] == numero_documento for p in participantes):
            sg.popup_error("Ya existe un participante con este número de documento.")
            continue

        # Verificar si la imagen del participante existe
        imagen_path = values["-FOTO_PARTICIPANTE-"]
        if imagen_path and not os.path.isfile(imagen_path):
            sg.popup_error("La imagen del participante especificada no se encuentra.")
            continue

        # Agregar participante a múltiples eventos
        eventos_seleccionados = values["-EVENTOS_PARTICIPANTE-"]
        for evento_nombre in eventos_seleccionados:
            evento = next((e for e in eventos if e['nombre'] == evento_nombre), None)
            if evento:
                participantes_evento = [p for p in participantes if p['evento'] == evento_nombre]
                if len(participantes_evento) >= evento['cupo']:
                    sg.popup_error(f"No se puede agregar el participante, el cupo del evento '{evento_nombre}' ha sido alcanzado.")
                    continue

                nuevo_participante = {
                    "evento": evento_nombre,
                    "nombre": values["-NOMBRE_PARTICIPANTE-"],
                    "documento": numero_documento,
                    "telefono": values["-TELEFONO-"],
                    "tipo": values["-TIPO_PARTICIPANTE-"],
                    "direccion": values["-DIRECCION-"],
                    "foto": imagen_path
                }
                participantes.append(nuevo_participante)

        # Guardar cambios en el archivo CSV
        guardar_datos()

        # Actualizar la lista de participantes
        window["-LISTA_PARTICIPANTES-"].update(values=[p['nombre'] for p in participantes])

        # Limpiar campos de entrada
        window["-NOMBRE_PARTICIPANTE-"].update("")
        window["-TIPO_DOCUMENTO-"].update("")
        window["-NUMERO_DOCUMENTO-"].update("")
        window["-TELEFONO-"].update("")
        window["-TIPO_PARTICIPANTE-"].update("")
        window["-DIRECCION-"].update("")
        window["-FOTO_PARTICIPANTE-"].update("")

    elif event == "-MODIFICAR_PARTICIPANTE-":
        participante_seleccionado = values["-LISTA_PARTICIPANTES-"]
        if participante_seleccionado:
            index = [p['nombre'] for p in participantes].index(participante_seleccionado[0]) 
            # Validar que todos los campos estén completos
            if not all([values["-NOMBRE_PARTICIPANTE-"], values["-TIPO_DOCUMENTO-"], values["-EVENTOS_PARTICIPANTE-"], values["-NUMERO_DOCUMENTO-"], values["-TELEFONO-"], values["-TIPO_PARTICIPANTE-"], values["-FOTO_PARTICIPANTE-"], values["-DIRECCION-"]]):
                sg.popup_error("Todos los campos son obligatorios.")
                continue

            # Validar valor numérico en el campo "Número de Documento"
            try:
                numero_documento = int(values["-NUMERO_DOCUMENTO-"])
            except ValueError:
                sg.popup_error("El campo 'Número de Documento' debe ser un valor numérico.")
                continue

            # Verificar si la imagen del participante existe
            imagen_path = values["-FOTO_PARTICIPANTE-"]
            if imagen_path and not os.path.isfile(imagen_path):
                sg.popup_error("La imagen del participante especificada no se encuentra.")
                continue

            # Modificar los eventos asociados al participante
            eventos_seleccionados = values["-EVENTOS_PARTICIPANTE-"]
            participantes[index] = {
                "evento": eventos_seleccionados,
                "nombre": values["-NOMBRE_PARTICIPANTE-"],
                "documento": numero_documento,
                "telefono": values["-TELEFONO-"],
                "tipo": values["-TIPO_PARTICIPANTE-"],
                "direccion": values["-DIRECCION-"],
                "foto": imagen_path
            }

            # Guardar cambios en el archivo CSV
            guardar_datos()

            # Actualizar la lista de participantes
            window["-LISTA_PARTICIPANTES-"].update(values=[p['nombre'] for p in participantes])

    elif event == "-ELIMINAR_PARTICIPANTE-":
        participante_seleccionado = values["-LISTA_PARTICIPANTES-"]
        if participante_seleccionado:
            index = [p['nombre'] for p in participantes].index(participante_seleccionado[0])  # Obtener el índice del participante seleccionado
            participantes.pop(index)  # Eliminar el participante seleccionado

            # Guardar cambios en el archivo CSV
            guardar_datos()

            window["-LISTA_PARTICIPANTES-"].update(values=[p['nombre'] for p in participantes])

    # Manejo de eventos para guardar configuración
    if event == "-GUARDAR_CONFIG-":
        configuracion["-VALIDAR_AFORO-"] = values["-VALIDAR_AFORO-"]
        configuracion["-SOLICITAR_IMAGENES"] = values["-SOLICITAR_IMAGENES-"]
        configuracion["-MODIFICAR_REGISTROS-"] = values["-MODIFICAR_REGISTROS-"]
        configuracion["-ELIMINAR_REGISTROS-"] = values["-ELIMINAR_REGISTROS-"]
        guardar_datos()
        sg.popup("Configuración guardada")

    # Manejo de eventos para análisis
    if event == "-ACTUALIZAR_ANALISIS-":
        df = pd.DataFrame(participantes)

        # Participantes que fueron a todos los eventos
        participantes_todos_eventos = df['nombre'].value_counts()[df['nombre'].value_counts() == len(eventos)].index.tolist()
        window["-TODOS_EVENTOS-"].update(values=participantes_todos_eventos)

        # Participantes que fueron al menos a un evento
        participantes_al_menos_un_evento = df['nombre'].unique().tolist()
        window["-AL_MENOS_UN_EVENTO-"].update(values=participantes_al_menos_un_evento)

        # Participantes que fueron solo al primer evento
        if len(eventos) > 0:
            primer_evento = eventos[0]['nombre']
            participantes_solo_primer_evento = df[df['evento'] == primer_evento]
            participantes_solo_primer_evento = participantes_solo_primer_evento[~participantes_solo_primer_evento['nombre'].isin(df[df['evento'] != primer_evento]['nombre'])]['nombre'].tolist()
            window["-SOLO_PRIMER_EVENTO-"].update(values=participantes_solo_primer_evento)

    # Manejo de eventos para mostrar gráficos
    if event == "-MOSTRAR_GRAFICOS-":
        df = pd.DataFrame(participantes)
        if not df.empty:
            # Gráfico 1: Distribución de participantes por tipo de participante (sin duplicados)
            df_unicos = df.drop_duplicates(subset='documento')
            df_tipo_participante = df_unicos['tipo'].value_counts()
            df_tipo_participante.plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.ylabel('')
            plt.title('Distribución de participantes por tipo de participante')
            plt.show()

            # Gráfico 2: Participantes por evento
            df_eventos = df['evento'].value_counts()
            df_eventos.plot(kind='bar')
            plt.xlabel('Evento')
            plt.ylabel('Número de Participantes')
            plt.title('Participantes por evento')
            plt.show()

            # Gráfico 3: Eventos por fecha
            df_fechas = pd.Series([e['fecha'] for e in eventos]).value_counts()
            df_fechas.plot(kind='barh')
            plt.xlabel('Cantidad de eventos')
            plt.ylabel('Fecha')
            plt.title('Eventos por fecha')
            plt.show()

window.close()