# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 18:28:50 2023

@author: salma
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt
import pandas as pd
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic
import datetime 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from math import radians, cos, sin, asin, sqrt
import folium
import numpy as np
import webbrowser


##Calcular distancias de dos puntos
def distancia_tierra(lat1, lat2, lon1, lon2):
    
    # Convertir grados a radianes.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Formula Haversine, para calcular la distancia entre dos puntos de una esfera dadas sus coordenadas de longitud y latitud
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    
    # Radio de la tierra en km.
    r = 6371
    
    respuesta = ((c * r)/24.9)*60
    # Calcular la distancia final en Km.
    return respuesta

    # Agregar la función prioridad
def prioridad(NumSolicitudes, Tdesplazamiento, Mdescoupa):
        # Si el número de solicitudes esta entre 0 y 2
        if NumSolicitudes >= 0 and NumSolicitudes <= 2:
            beta = 0.55
            alpha = 0.45
        # Si el número de solicitudes esta entre 3 y 4
        elif NumSolicitudes >= 3 and NumSolicitudes <= 4:
            beta = 0.65
            alpha = 0.35
        # Si el número de solicitudes esta entre 5 o más
        elif NumSolicitudes >= 5:
            beta = 0.75
            alpha = 0.25
    
        # Calculamos la prioridad
        pesoPrioridad = NumSolicitudes * alpha + Tdesplazamiento + Mdescoupa * beta
    
        return pesoPrioridad

def convertMin(minutos):
    # Obtenemos la fecha de hoy
    fecha_actual = datetime.date.today()
    # Combinamos la fecha de hoy con la hora 0:00:00
    fecha_hora = datetime.datetime.combine(fecha_actual, datetime.time.min) + datetime.timedelta(minutes=minutos)
    # Convertimos la fecha y hora a formato de cadena
    fecha_hora_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
    return fecha_hora_str



class MiAplicacion(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        

    def initUI(self):
        # Crear diccionario para pacientes, médicos y clientes
        self.pacientes = {}
        self.doctores = {}
        self.Clientes = {}

        # Configurar la interfaz para pacientes
        self.label_paciente = QLabel("Paciente")
        self.id_servicio_label = QLabel("ID servicio:")
        self.llegada_label = QLabel("Llegada:")
        self.atencion_label = QLabel("Atención:")
        self.direccion_label = QLabel("Dirección:")
        self.entidad_label = QLabel("Entidad:")

        self.id_servicio_input = QLineEdit()
        self.llegada_input = QTimeEdit()
        self.llegada_input.setDisplayFormat("HH:mm") 
        self.atencion_input = QLineEdit()
        self.direccion_input = QLineEdit()
        self.entidad_input = QLineEdit()
   

        self.agregar_paciente_btn = QPushButton("Agregar Paciente")
        self.cargar_pacientes_excel_btn = QPushButton("Añadir Pacientes Excel")
        self.cargar_pacientes_excel_btn.clicked.connect(self.cargar_pacientes_excel)
        self.cargar_pacientes_excel_btn.setFixedWidth(630)
        
        
        
        ##Tabla pacientes
        self.mostrar_pacientes_text = QTableWidget()  
        hor_pacientes=QHBoxLayout()
        hor_pacientes.addWidget(self.id_servicio_label)
        hor_pacientes.addWidget(self.id_servicio_input)
        hor_pacientes.addWidget(self.llegada_label)
        hor_pacientes.addWidget(self.llegada_input)
        hor_pacientes.addWidget(self.atencion_label)
        hor_pacientes.addWidget(self.atencion_input)

        
        
        self.labelpaciente=QWidget()
        self.labelpaciente.setLayout(hor_pacientes)
        
        hor_pacientes2=QHBoxLayout()
        hor_pacientes2.addWidget(self.direccion_label)
        hor_pacientes2.addWidget(self.direccion_input)
        hor_pacientes2.addWidget(self.entidad_label)
        hor_pacientes2.addWidget(self.entidad_input)
        self.labelpaciente2=QWidget()
        self.labelpaciente2.setLayout(hor_pacientes2)
        layout_paciente = QVBoxLayout()
        
        #Se creal el frame para pacientes
        frame1 = QFrame(self)
        frame1.setFrameShape(QFrame.StyledPanel)        
        layout_paciente.addWidget(frame1)
        layout_pacientes = QVBoxLayout(frame1)
        layout_pacientes.addWidget(self.label_paciente)
        layout_pacientes.addWidget(self.labelpaciente)
        layout_pacientes.addWidget(self.labelpaciente2)
        layout_pacientes.addWidget(self.agregar_paciente_btn)
        layout_pacientes.addWidget(self.cargar_pacientes_excel_btn)
        layout_pacientes.addWidget(self.mostrar_pacientes_text)
        
        
        # Configurar la tabla de pacientes
        self.setup_tabla()

        # Configurar la interfaz para médicos
        self.label_medico = QLabel("Médico")
        self.id_medico_label = QLabel("ID médico:")
        self.inicio_jornada_label = QLabel("Inicio Jornada:")
        self.fin_jornada_label = QLabel("Fin Jornada:")

        self.id_medico_input = QLineEdit()
        self.inicio_jornada_input = QTimeEdit()
        self.inicio_jornada_input.setDisplayFormat("HH:mm") 
        self.fin_jornada_input = QTimeEdit()
        self.fin_jornada_input.setDisplayFormat("HH:mm") 

        self.agregar_medico_btn = QPushButton("Agregar Médico")
        self.cargar_medicos_excel_btn = QPushButton("Añadir Médicos Excel")
        self.cargar_medicos_excel_btn.clicked.connect(self.cargar_medicos_excel)

        #Tabla médicos
        self.mostrar_medicos_text = QTableWidget()
        hor_medicos=QHBoxLayout()
        hor_medicos.addWidget(self.inicio_jornada_label)
        hor_medicos.addWidget(self.inicio_jornada_input)
        hor_medicos.addWidget(self.fin_jornada_label)
        hor_medicos.addWidget(self.fin_jornada_input)
        self.labelmedicos=QWidget()
        self.labelmedicos.setLayout(hor_medicos)

        layout_medico = QVBoxLayout()
        
        #Se creal el frame para medicos
        frame2 = QFrame(self)
        frame2.setFrameShape(QFrame.StyledPanel)        
        layout_medico.addWidget(frame2)
        layout_medicos = QVBoxLayout(frame2)
        layout_medicos.addWidget(self.label_medico)
        layout_medicos.addWidget(self.id_medico_label)
        layout_medicos.addWidget(self.id_medico_input)
        layout_medicos.addWidget(self.labelmedicos)
        layout_medicos.addWidget(self.agregar_medico_btn)
        layout_medicos.addWidget(self.cargar_medicos_excel_btn)
        layout_medicos.addWidget(self.mostrar_medicos_text)
        
        # Configurar la tabla de médicos
        self.setup_tabla_medicos()
        
        # Crear un QLabel para mostrar la imagen
        label_imagen = QLabel(self)
        pixmap = QPixmap('C:/Users/salma/Documentos/2023-2/TESIS/adom.png').scaled(200, 200, Qt.KeepAspectRatio)  # Reemplaza 'ruta_de_tu_imagen.jpg' con la ruta de tu imagen
        label_imagen.setPixmap(pixmap)
        label_imagen.setAlignment(Qt.AlignTop | Qt.AlignLeft)
      #  label_imagen.setFixedWidth(200)
     

        # Configurar la interfaz para clientes
        
        self.agregar_clientes_btn = QPushButton("Añadir clientes(excel)")
        self.agregar_clientes_btn.setFixedSize(240,25)
        self.agregar_clientes_btn.clicked.connect(self.cargar_clientes_desde_excel)
        

        ##TABLA
        self.mostrar_clientes_text = QTableWidget()
        self.mostrar_clientes_text.setFixedWidth(240)
       # self.mostrar_clientes_text.setReadOnly(True)
 
      
        layout_clientes = QVBoxLayout()
        layout_clientes.addWidget(label_imagen)
        frame3 = QFrame(self)
        frame3.setFrameShape(QFrame.StyledPanel)        
        layout_clientes.addWidget(frame3)
        layout_clientess = QVBoxLayout(frame3)
        
        layout_clientess.addWidget(self.agregar_clientes_btn)
        layout_clientess.addWidget(self.mostrar_clientes_text)

        # Crear pestañas para pacientes, médicos y clientes
        self.tab_paciente = QWidget()
        self.tab_paciente.setLayout(layout_paciente)
       # self.tab_paciente.setFixedSize(500, 430)

        self.tab_medico = QWidget()
        self.tab_medico.setLayout(layout_medico)

        self.tab_clientes = QWidget()
       # self.tab_clientes.setFixedWidth(240)
        self.tab_clientes.setLayout(layout_clientes)
        
        # Agregar el botón "Mostrar asignación" en la sección de interfaz para pacientes
        self.mostrar_asignacion_btn = QPushButton("Mostrar Asignación")
        layout_paciente.addWidget(self.mostrar_asignacion_btn)

        # Conectar el botón "Mostrar asignación" a la función que mostrará los resultados
        self.mostrar_asignacion_btn.clicked.connect(self.mostrar_asignacion)

        # Agregar pestañas a la ventana principal
        self.tabs = QHBoxLayout()
        self.tabs.addWidget(self.tab_paciente)
        self.tabs.addWidget(self.tab_medico)
        self.tabs.addWidget(self.tab_clientes)
        
            # Agregar una línea gruesa horizontal
        self.linea_horizontal = QLabel()
        self.linea_horizontal.setFrameShape(4)
        self.linea_horizontal.setFrameShadow(0)
    
          # Agregar un título para los indicadores
        self.titulo_indicadores = QLabel("Indicadores")
        
        # Crear botón para mostrar los indicadores
        self.mostrar_indicadores_btn = QPushButton("Mostrar Indicadores")
        self.mostrar_indicadores_btn.clicked.connect(self.calcular_indicadores)
        self.mostrar_ind_text=QTableWidget()
        
        # Crear un botón de exportar
        self.boton_exportar = QPushButton("Exportar Indicadores")
        self.boton_exportar.clicked.connect(self.exportar_indicadores)
   
        #Indicadores generales
        # Agregar un título para los indicadores generales
        self.titulo_graficas = QLabel("Indicadores generales")
        # Crear botón para mostrar los indicadores
        self.mostrar_indicadoresg_btn = QPushButton("Mostrar gráfico")
        self.mostrar_indicadoresg_btn.clicked.connect(self.mostrar_grafico)
        self.mostrar_indicadoresg_btn.setEnabled(False)  # Deshabilitar inicialmente
        self.mostrar_indicadoresmym_btn= QPushButton("Mostrar indicadores generales")
        self.mostrar_indicadoresmym_btn.clicked.connect(self.mostrar_indicadores_generales)
        self.mostrar_indicadoresmym_btn.setEnabled(False)  # Deshabilitar inicialmente
        
        #linea indicador4es generales
        # Agregar una línea gruesa horizontal
        self.linea_horizontal2 = QLabel()
        self.linea_horizontal2.setFrameShape(4)
        self.linea_horizontal2.setFrameShadow(0)
        
        # Figura y eje para el gráfico de torta
        # Crear la figura y los ejes para el gráfico
        plt.ioff()
        self.fig, self.ax = plt.subplots(figsize=(2, 2))
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas = FigureCanvas(self.fig)
     
        # Tabla indicadores generales
        self.tablageneral=QTableWidget()
        
         #Añadir objetos a layout indicadores
         
        layout_indicadores = QVBoxLayout()
        
        layout_indicadores.addWidget(self.linea_horizontal)
        layout_indicadores.addWidget(self.titulo_indicadores)
        layout_indicadores.addWidget(self.mostrar_ind_text)
        layout_indicadores.addWidget(self.mostrar_indicadores_btn)
        layout_indicadores.addWidget(self.boton_exportar)
        
        ##Layout tabla y grafica
        layout_tyg=QHBoxLayout()
        layout_tyg.addWidget(self.canvas)
        layout_tyg.addWidget(self.tablageneral)
        self.tyg = QWidget()
        self.tyg.setLayout(layout_tyg)
        
        layout_graficas= QVBoxLayout()
        layout_graficas.addWidget(self.linea_horizontal2)
        layout_graficas.addWidget(self.titulo_graficas)
        layout_graficas.addWidget(self.tyg)
        layout_graficas.addWidget(self.mostrar_indicadoresg_btn)
        layout_graficas.addWidget(self.mostrar_indicadoresmym_btn)
        
        
        
        self.tabs_2 = QHBoxLayout()
        self.tab_indicadores = QWidget()
        self.tab_indicadores.setLayout(layout_indicadores)
        self.tab_graficas = QWidget()
        self.tab_graficas.setLayout(layout_graficas)
        
        self.tabs_2 = QHBoxLayout()
        self.tabs_2.addWidget(self.tab_indicadores)
        self.tabs_2.addWidget(self.tab_graficas)
        self.agregar_paciente_btn.clicked.connect(self.agregar_paciente)
        self.agregar_medico_btn.clicked.connect(self.agregar_medico)
   
    
          # Establecer el diseño general
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.tabs)
        self.layout.addLayout(self.tabs_2)
        # self.layout.addLayout(layout_graficas)
        
        self.setLayout(self.layout)
     

       # Establecer la geometría de la ventana
        self.setGeometry(0, 0, 700, 400)  
        self.setWindowTitle('Asignación e indicadores de médicos')
        self.show()
        
    def convertir_a_minutos(self):
        # Obtener el tiempo del QTimeEdit
        tiempo = self.llegada_input.time()

        # Calcular los minutos desde la medianoche
        minutos_del_dia = tiempo.hour() * 60 + tiempo.minute()
        
        return int(minutos_del_dia)
    
    def convertir_a_minutos_inicioj(self):
        # Obtener el tiempo del QTimeEdit
        tiempoi = self.inicio_jornada_input.time()

        # Calcular los minutos desde la medianoche
        minutos_del_diainicio = tiempoi.hour() * 60 + tiempoi.minute()
        
        return int(minutos_del_diainicio)
    
    def convertir_a_minutos_finj(self):
        # Obtener el tiempo del QTimeEdit
        tiempof = self.fin_jornada_input.time()

        # Calcular los minutos desde la medianoche
        minutos_del_diafin = tiempof.hour() * 60 + tiempof.minute()
        
        return int(minutos_del_diafin)

        

    def agregar_paciente(self):
       
        id_servicio = int(self.id_servicio_input.text())
        llegada = int(self.convertir_a_minutos())
        atencion = int(self.atencion_input.text())
        direccion = self.direccion_input.text()
        entidad = str(self.entidad_input.text())

        geolocator = ArcGIS()
        location = geolocator.geocode(direccion)

        if location:
            latitud = location.latitude
            longitud = location.longitude
        else:
            latitud = None
            longitud = None

        if id_servicio in self.pacientes:
            self.pacientes[id_servicio].append([llegada, atencion, latitud, longitud, entidad])
        else:
            self.pacientes[id_servicio] = [int(llegada), int(atencion), latitud, longitud, str(entidad)]

        # Limpiar campos de entrada
        self.id_servicio_input.clear()
        self.llegada_input.clear()
        self.atencion_input.clear()
        self.direccion_input.clear()
        self.entidad_input.clear()

        # Actualizar la tabla
        self.actualizar_tabla()

    def agregar_medico(self):
        # global doctores
        id_medico = self.id_medico_input.text()
        Inicioj = int(self.convertir_a_minutos_inicioj())
        Finj = int(self.convertir_a_minutos_finj())
        llave = id_medico
        Disponibiidad = 0
        UltOcupado = 0
        NumSol = 0
        lat = 4.681230925773865
        lon = -74.06200456196707
        
        if llave in self.doctores:
            self.doctores[llave].append([Disponibiidad, UltOcupado, lat, lon, NumSol, Inicioj, Finj])
        else:
            self.doctores[llave] = [int(Disponibiidad), int(UltOcupado),lat, lon, NumSol, int(Inicioj), int(Finj)]

          # Limpiar campos de entrada
        self.id_medico_input.clear()
        self.inicio_jornada_input.clear()
        self.fin_jornada_input.clear()
    
        # Actualizar la tabla
        self.actualizar_tabla_medicos()

    def cargar_clientes_desde_excel(self):
        global Clientes
    
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly
    
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel de Clientes", "", "Archivos Excel (*.xlsx *.xls)", options=opciones)
    
        if archivo:
            try:
                df = pd.read_excel(archivo)
    
           
                self.mostrar_clientes_text.clear()
    
   
                self.mostrar_clientes_text.setRowCount(len(df))
    
        
                self.mostrar_clientes_text.setColumnCount(2)  # Assuming 2 columns: Tipo y Tiempo
                self.mostrar_clientes_text.setHorizontalHeaderLabels(['Tipo', 'Tiempo'])
    
       
                for index, row in df.iterrows():
                    tipo = row['Tipo']
                    tiempo = row['Tiempo']
                    self.Clientes[tipo] = tiempo
                    tipo_item = QTableWidgetItem(str(tipo))
                    tiempo_item = QTableWidgetItem(str(tiempo))
                    self.mostrar_clientes_text.setItem(index, 0, tipo_item)
                    self.mostrar_clientes_text.setItem(index, 1, tiempo_item)
    
            except Exception as e:
               # Mostrar el error en un cuadro de diálogo
               self.mostrar_error("Error al cargar el archivo: " + str(e))


    def cargar_medicos_excel(self):
        global doctores
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel de Médicos", "", "Archivos Excel (*.xlsx *.xls)", options=opciones)

        if archivo:
            try:
                df = pd.read_excel(archivo)
                for index, row in df.iterrows():
                    llave = row["ID Medico"]
                    Disponibiidad = 0
                    UltOcupado = 0
                    NumSol = 0
                    lat = 4.681230925773865
                    lon = -74.06200456196707
                    Inicioj = row["Inicio Jornada"]
                    Finj = row["Fin Jornada"]
                    
                    if llave in self.doctores:
                        self.doctores[llave].append([Disponibiidad, UltOcupado, lat, lon, NumSol, Inicioj, Finj])
                    else:
                        self.doctores[llave] = [int(Disponibiidad), int(UltOcupado),lat, lon, NumSol, int(Inicioj), int(Finj)]
                   
                # Actualizar la tabla
                self.actualizar_tabla_medicos()
            except Exception as e:
                # Mostrar el error en un cuadro de diálogo
                self.mostrar_error("Error al cargar el archivo Excel de Médicos: " + str(e))

    #  mostrar errores en un cuadro de diálogo
    def mostrar_error(self, mensaje):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(mensaje)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()
        
    def setup_tabla_medicos(self):
            self.mostrar_medicos_text.setColumnCount(3)   
            self.mostrar_medicos_text.setHorizontalHeaderLabels(["ID Médico", "Inicio Jornada", "Fin Jornada"])
                    
    def actualizar_tabla_medicos(self):
        # Limpiar la tabla antes de actualizar
        self.mostrar_medicos_text.setRowCount(0)
    
        # Llenar la tabla con los datos de médicos
        for id_medico, medico_data in self.doctores.items():
            row_position = self.mostrar_medicos_text.rowCount()
            self.mostrar_medicos_text.insertRow(row_position)
    
            self.mostrar_medicos_text.setItem(row_position, 0, QTableWidgetItem(str(id_medico)))
            self.mostrar_medicos_text.setItem(row_position, 1, QTableWidgetItem(str(medico_data[5])))  # Inicio Jornada
            self.mostrar_medicos_text.setItem(row_position, 2, QTableWidgetItem(str(medico_data[6])))  # Fin Jornada


    def cargar_pacientes_excel(self):
        global pacientes
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel de Pacientes", "", "Archivos Excel (*.xlsx *.xls)", options=opciones)

        if archivo:
            try:
                df = pd.read_excel(archivo)
                for index, row in df.iterrows():
                    id_servicio = row["ID Servicio"]
                    llegada = row["Llegada"]
                    atencion = row["Atencion"]
                    latitud = row["Latitud"]
                    longitud=row["Longitud"]
                    entidad = row["Entidad"]
                    direccion = row["Direccion"]
                    
                    
                    
                    # geolocator = ArcGIS()
                    # location = geolocator.geocode(direccion)

                    # if location:
                    #     latitud= latitud
                    #     longitud=longitud
                    #     # latitud = location.latitude
                    #     # longitud = location.longitude
                    # else:
                    #     latitud = None
                    #     longitud = None
                    if id_servicio in self.pacientes:
                        self.pacientes[id_servicio].append([llegada, atencion, latitud, longitud, entidad])
                    else:
                        self.pacientes[id_servicio] = [int(llegada), int(atencion), latitud, longitud, str(entidad)]
                        
                # Actualizar la tabla
                self.actualizar_tabla()
            except Exception as e:
                self.mostrar_error("Error al cargar el archivo: " + str(e))
                
    def setup_tabla(self):
        self.mostrar_pacientes_text.setColumnCount(6)
        self.mostrar_pacientes_text.setHorizontalHeaderLabels(["ID Servicio", "Llegada", "Atencion", "Latitud", "Longitud", "Entidad"])
        
    def actualizar_tabla(self):
        # Limpiar la tabla antes de actualizar
        self.mostrar_pacientes_text.setRowCount(0)
        
        # Llenar la tabla con los datos de pacientes
        for id_servicio, paciente_data in self.pacientes.items():
            row_position = self.mostrar_pacientes_text.rowCount()
            self.mostrar_pacientes_text.insertRow(row_position)

            self.mostrar_pacientes_text.setItem(row_position, 0, QTableWidgetItem(str(id_servicio)))
            self.mostrar_pacientes_text.setItem(row_position, 1, QTableWidgetItem(str(paciente_data[0])))  # Llegada
            self.mostrar_pacientes_text.setItem(row_position, 2, QTableWidgetItem(str(paciente_data[1])))  # Atencion
            self.mostrar_pacientes_text.setItem(row_position, 3, QTableWidgetItem(str(paciente_data[2])))  # Latitud
            self.mostrar_pacientes_text.setItem(row_position, 4, QTableWidgetItem(str(paciente_data[3])))  # Longitud
            self.mostrar_pacientes_text.setItem(row_position, 5, QTableWidgetItem(paciente_data[4]))  # Entidad

 
    def asignar_doctor(self,atencion,latitud, longitud, minuto, gantt, IDservicio, TipoCliente):    
        # Lista de posible asignacion
        posibleAsignacion = []
        doctores=self.doctores
        Clientes=self.Clientes
   
        
        # Actualizar estado de los médicos
        if minuto > 0:
            for i in doctores:
                # Si el minuto actual es mayor al ultimo ocupado significa que el médico esta disponible
                if minuto > doctores[i][1]:
                    # Actualizar estado del médico
                    doctores[i][0] = 0
  
        for i in doctores:
            # Si el médico esta en su jornada laboral y esta disponible
            if minuto >= doctores[i][5] and minuto <= doctores[i][6] and doctores[i][0] == 0:
                # Agregar médico y su distancia a la lista de posible asignacion
    
                # Encontrar distancia de los médicos al paciente
                distancia = distancia_tierra(doctores[i][2], latitud, doctores[i][3], longitud)
                # Agregar médico y su distancia a la lista de posible asignacion
                posibleAsignacion.append([i, distancia])
      
        # Si no hay ningún médico disponible
        if len(posibleAsignacion) == 0:
            # Se buscan médicos que esten en su jornada laboral para asignarles el paciente usando la regla de prioridad
    
            for i in doctores:
                # Si el doctor esta en su jornada laboral
                if minuto >= doctores[i][5] and minuto <= doctores[i][6]:
                    # Se aplican las reglas de prioridad
    
                    # Calcular tiempo de desplazamiento
                    Tdesplazamiento = distancia_tierra(doctores[i][2], latitud, doctores[i][3], longitud)
                    # Calcular tiempo de desocupacion
                    Mdesocupa = doctores[i][1]
                    # Calcular prioridad
                    pesoPrioridad = prioridad(doctores[i][4], Tdesplazamiento, Mdesocupa)
                    # Agregar a la lista de posible asignacion
                    posibleAsignacion.append([i, pesoPrioridad])
                
            
    
            # Si existen médicos en su jornada laboral
            if len(posibleAsignacion) > 0:
                # Escoger el médico con mayor prioridad, es decir, el que tenga menor peso
    
                # Filtrar a los médicos que cumplan con el tiempo de servicio
                for i in posibleAsignacion:
                    # calcular el desplazamiento del medico
                    Tdesplazamiento = distancia_tierra(doctores[i[0]][2], latitud, doctores[i[0]][3], longitud)
    
                    # Si el médico no cumple con el tiempo de servicio se elimina de la lista de posible asignacion
                    if minuto + Tdesplazamiento > minuto + Clientes[TipoCliente]:
                        #crear lista de médicos que no cumplen con el tiempo de servicio
                        listaMedicosNoCumplen = []
                        #agregar médicos que no cumplen con el tiempo de servicio
                        listaMedicosNoCumplen.append(i[0])
                        #eliminar médicos que no cumplen con el tiempo de servicio
                        posibleAsignacion.remove(i)
         
                # si existen médicos que cumplan con el tiempo de servicio
                if len(posibleAsignacion) > 0:
                    # Ordenar la lista de posible asignacion
                    posibleAsignacion.sort(key=lambda x: x[1])
                    # Asignar el doctor con menor prioridad
                    doc_Asignar = posibleAsignacion[0]
    
                    # Actualizar variables del médico asignado
                    Mdesocupa = doctores[doc_Asignar[0]][1]
                    Tdesplazamiento = distancia_tierra(doctores[doc_Asignar[0]][2], latitud, doctores[doc_Asignar[0]][3], longitud)
    
                    # Actualizar el gantt
                    gantt.append({'Solicitud': IDservicio, 'Medico': doc_Asignar[0], 'Inicio': convertMin(Mdesocupa + Tdesplazamiento), 'Fin': convertMin(Mdesocupa + Tdesplazamiento + atencion), 'Distancia': Tdesplazamiento, 'Inicio Jornada': doctores[doc_Asignar[0]][5], 'Fin Jornada': doctores[doc_Asignar[0]][6], 'Inicio traslado': Mdesocupa, 'Fin traslado': Mdesocupa + Tdesplazamiento, 'Inicio atencion': Mdesocupa + Tdesplazamiento, 'Fin atencion': Mdesocupa + Tdesplazamiento + atencion, 'Llegada solicitud': minuto, 'Tiempo contratado': Clientes[TipoCliente], 'Tipo de asignacion': 'Tipo 1'})
                    
                    # Actualizar estado del médico
                    doctores[doc_Asignar[0]][0] = 1
                    doctores[doc_Asignar[0]][1] = Mdesocupa + Tdesplazamiento + atencion
                    doctores[doc_Asignar[0]][2] = latitud
                    doctores[doc_Asignar[0]][3] = longitud
                    doctores[doc_Asignar[0]][4] = doctores[doc_Asignar[0]][4] + 1
    
                # Si no existen médicos que cumplan con el tiempo de servicio
                else:
                    # Calcular el médico que atienda la solicitud más rapido
                    for i in listaMedicosNoCumplen:
                        # Calcular tiempo de desplazamiento
                        Tdesplazamiento = distancia_tierra(doctores[i][2], latitud, doctores[i][3], longitud)
                        # Calcular tiempo de desocupacion
                        Mdesocupa = doctores[i][1]
                        # Cambiar el peso de prioridad por el tiempo de desplazamiento
                        listaMedicosNoCumplen[i][1] = Mdesocupa + Tdesplazamiento
    
                    # Ordenar la lista de posible asignacion
                    listaMedicosNoCumplen.sort(key=lambda x: x[1])
    
                    # Asignar el médico con menor tiempo de desplazamiento
                    doc_Asignar = listaMedicosNoCumplen[0]
    
                    # Actualizar variables del médico asignado
                    Mdesocupa = doctores[doc_Asignar[0]][1]
                    Tdesplazamiento = distancia_tierra(doctores[doc_Asignar[0]][2], latitud, doctores[doc_Asignar[0]][3], longitud)
    
                    # Actualizar el gantt
                    gantt.append({'Solicitud': IDservicio, 'Medico': doc_Asignar[0], 'Inicio': convertMin(Mdesocupa + Tdesplazamiento), 'Fin': convertMin(Mdesocupa + Tdesplazamiento + atencion), 'Distancia': Tdesplazamiento, 'Inicio Jornada': doctores[doc_Asignar[0]][5], 'Fin Jornada': doctores[doc_Asignar[0]][6], 'Inicio traslado': Mdesocupa, 'Fin traslado': Mdesocupa + Tdesplazamiento, 'Inicio atencion': Mdesocupa + Tdesplazamiento, 'Fin atencion': Mdesocupa + Tdesplazamiento + atencion, 'Llegada solicitud': minuto, 'Tiempo contratado': Clientes[TipoCliente], 'Tipo de asignacion': 'Tipo 2'})
    
                    # Actualizar estado del médico
                    doctores[doc_Asignar[0]][0] = 1
                    doctores[doc_Asignar[0]][1] = Mdesocupa + Tdesplazamiento + atencion
                    doctores[doc_Asignar[0]][2] = latitud
                    doctores[doc_Asignar[0]][3] = longitud
                    doctores[doc_Asignar[0]][4] = doctores[doc_Asignar[0]][4] + 1
            else:
                # No hay médicos disponibles
                print("No hay médicos disponibles")
                    
        # Si hay uno o más médicos disponibles
        elif len(posibleAsignacion) > 0:
            # Se filtrarán los médicos que no cumplan con el tiempo de servicio
            for i in posibleAsignacion:
                # Si el médico no cumple con el tiempo de servicio se elimina de la lista de posible asignacion
                
                if minuto + i[1] > minuto + Clientes[TipoCliente]:
                    #crear lista de médicos que no cumplen con el tiempo de servicio
                    listaMedicosNoCumplen = []
                    #agregar médicos que no cumplen con el tiempo de servicio
                    listaMedicosNoCumplen.append(i[0])
                    #eliminar médicos que no cumplen con el tiempo de servicio
                    posibleAsignacion.remove(i)
            
            # Si existen médicos que cumplan con el tiempo de servicio
            if len(posibleAsignacion) > 0:
    
                # calcular el peso de prioridad de cada médico
                for i in posibleAsignacion:
                    # Calcular tiempo de desplazamiento
                    Tdesplazamiento = distancia_tierra(doctores[i[0]][2], latitud, doctores[i[0]][3], longitud)
                    # Calcular tiempo de desocupacion
                    Mdesocupa = doctores[i[0]][1]
                    # Calcular prioridad
                    pesoPrioridad = prioridad(doctores[i[0]][4], Tdesplazamiento, Mdesocupa)
    
                    # Cambiar el tiempo de desplazamiento por el peso de prioridad
                    i[1] = pesoPrioridad
                
                # Ordenar la lista de posible asignacion
                posibleAsignacion.sort(key=lambda x: x[1])
    
                # Asignar el médico con menor prioridad
                doc_Asignar = posibleAsignacion[0]
                # Actualizar variables del médico asignado
                Mdesocupa = doctores[doc_Asignar[0]][1]
                Tdesplazamiento = distancia_tierra(doctores[doc_Asignar[0]][2], latitud, doctores[doc_Asignar[0]][3], longitud)
    
                # Actualizar el gantt
                gantt.append({'Solicitud': IDservicio, 'Medico': doc_Asignar[0], 'Inicio': convertMin(minuto + Tdesplazamiento), 'Fin': convertMin(minuto + Tdesplazamiento + atencion), 'Distancia': Tdesplazamiento, 'Inicio Jornada': doctores[doc_Asignar[0]][5], 'Fin Jornada': doctores[doc_Asignar[0]][6], 'Inicio traslado': minuto, 'Fin traslado': minuto + Tdesplazamiento, 'Inicio atencion': minuto + Tdesplazamiento, 'Fin atencion': minuto + Tdesplazamiento + atencion, 'Llegada solicitud': minuto, 'Tiempo contratado': Clientes[TipoCliente], 'Tipo de asignacion': 'Tipo 3'})
                # Actualizar estado del médico
                doctores[doc_Asignar[0]][0] = 1
                doctores[doc_Asignar[0]][1] = minuto + Tdesplazamiento + atencion
                doctores[doc_Asignar[0]][2] = latitud
                doctores[doc_Asignar[0]][3] = longitud
                doctores[doc_Asignar[0]][4] = doctores[doc_Asignar[0]][4] + 1
            
            # Si no existen médicos que cumplan con el tiempo de servicio
            else:
                # Se asignará el médico con menor tiempo de desplazamiento
                print(listaMedicosNoCumplen)
                for i in listaMedicosNoCumplen:
                    # Calcular tiempo de desplazamiento
                    Tdesplazamiento = distancia_tierra(doctores[i][2], latitud, doctores[i][3], longitud)
                    # Cambiar el peso de prioridad por el tiempo de desplazamiento
                    listaMedicosNoCumplen[listaMedicosNoCumplen.index(i)] = [i, Tdesplazamiento]
                
                # Ordenar la lista de posible asignacion
                listaMedicosNoCumplen.sort(key=lambda x: x[1])
    
                # Asignar el médico con menor tiempo de desplazamiento
                doc_Asignar = listaMedicosNoCumplen[0]
    
                # Actualizar variables del médico asignado
                Mdesocupa = doctores[doc_Asignar[0]][1]
                Tdesplazamiento = distancia_tierra(doctores[doc_Asignar[0]][2], latitud, doctores[doc_Asignar[0]][3], longitud)
    
                # Actualizar el gantt
                gantt.append({'Solicitud': IDservicio, 'Medico': doc_Asignar[0], 'Inicio': convertMin(minuto + Tdesplazamiento), 'Fin': convertMin(minuto + Tdesplazamiento + atencion), 'Distancia': Tdesplazamiento, 'Inicio Jornada': doctores[doc_Asignar[0]][5], 'Fin Jornada': doctores[doc_Asignar[0]][6], 'Inicio traslado': minuto, 'Fin traslado': minuto + Tdesplazamiento, 'Inicio atencion': minuto + Tdesplazamiento, 'Fin atencion': minuto + Tdesplazamiento + atencion, 'Llegada solicitud': minuto, 'Tiempo contratado': Clientes[TipoCliente], 'Tipo de asignacion': 'Tipo 4'})
    
                # Actualizar estado del médico
                doctores[doc_Asignar[0]][0] = 1
                doctores[doc_Asignar[0]][1] = minuto + Tdesplazamiento + atencion
                doctores[doc_Asignar[0]][2] = latitud
                doctores[doc_Asignar[0]][3] = longitud
                doctores[doc_Asignar[0]][4] = doctores[doc_Asignar[0]][4] + 1
    
        return gantt
    
                
    def asignacion_doctor1(self):
       gantt = []
       lista=[]
       cont=0
          
       pacientes1 = dict(sorted(self.pacientes.items(), key=lambda item: item[1][0]))

       for i in pacientes1:
           # Asignar doctor a paciente
           atencion = int(pacientes1[i][1])
           minuto = int(pacientes1[i][0])
           latitud = float(pacientes1[i][2])
           longitud = float(pacientes1[i][3])
           IDservicio = int(i)
           TipoCliente = str(pacientes1[i][4])
       
           gantt = self.asignar_doctor(atencion, latitud, longitud, minuto, gantt, IDservicio, TipoCliente)
       return gantt
           
    
    def mostrar_asignacion(self):
        # Llamar a la función de asignación de médicos
        gantt = self.asignacion_doctor1()
  
        Pacientes=self.pacientes
 

        # Ordenar el diccionario de pacientes por la clave 
        Pacientes_ordenado = dict(sorted(Pacientes.items()))

        # Ordenar la lista de diccionarios por la clave 'Solicitud' de mayor a menor
        gantt_ordenado = sorted(gantt, key=lambda x: x['Solicitud'], reverse=False)

        # Crear un nuevo diccionario
        solicitudes_datos = {}
        cont=0
        # Recorrer el diccionario original
        for clave, lista in Pacientes_ordenado.items():
            # Conservar solo los elementos 3 y 4 de la lista
            nuevos_elementos = lista[2:4]
            Medico_asig=gantt_ordenado[cont]['Medico']
            Inicio_asig=gantt_ordenado[cont]['Inicio']
            Fin_asig=gantt_ordenado[cont]['Fin']
            nuevos_elementos.append(Medico_asig)
            nuevos_elementos.append(Inicio_asig) 
            nuevos_elementos.append(Fin_asig)

            # Crear un nuevo par clave-valor en el nuevo diccionario
            solicitudes_datos[clave] = nuevos_elementos
            cont+=1


        ###MOSTRAR MAPA
        # Extraer los IDs de médicos sin repetir
        ids_medicos = set(solicitud[2] for solicitud in solicitudes_datos.values())

       
        # Crear un mapa centrado en una ubicación inicial 
        mapa = folium.Map(location=[4.681230925773865, -74.06200456196707], zoom_start=10)

        # Agregar marcadores al mapa
        for numero_solicitud, solicitud in solicitudes_datos.items():
            latitud, longitud, id_medico, Inicio, Fin = solicitud
            folium.Marker([latitud, longitud], popup=f'Médico {id_medico},Latitud {latitud},Longitud ´{longitud}, Inicio {Inicio},Fin {Fin}').add_to(mapa)

        # Guardar el mapa como un archivo HTML
        # Guardar el mapa en una ubicación específica
        ruta_guardado = "C:/Users/salma/Documentos/2023-2/TESIS/tu_mapa.html"
        mapa.save(ruta_guardado)
        
        # Abrir el mapa en el navegador web predeterminado
        webbrowser.open(ruta_guardado)
                
        # Mostrar un cuadro de diálogo de mensaje
        mensaje = f'Se ha guardado exitosamente el mapa en: {ruta_guardado}'
        QMessageBox.information(self, 'Éxito', mensaje)
        
        # Crear un cuadro de diálogo para mostrar los resultados
        asignacion_dialog = QMessageBox()
        asignacion_dialog.setWindowTitle("Asignación de Doctores")
        
        # Crear un widget de texto para los resultados
        tabla_resultados = QTableWidget()
        tabla_resultados.setColumnCount(5)
        # Establecer las etiquetas de las columnas
        column_labels = ['Solicitud', 'Médico', 'Inicio', 'Fin', 'Ubicación']
        tabla_resultados.setHorizontalHeaderLabels(column_labels)
        
           # Agregar los resultados a la tabla
        for row, asignacion in enumerate(gantt):
           solicitud = asignacion['Solicitud']
           medico = asignacion['Medico']
           inicio = asignacion['Inicio']
           fin = asignacion['Fin']
           ubicacion = f"({solicitudes_datos[solicitud][0]}, {solicitudes_datos[solicitud][1]})"
    
           # Insertar datos en la tabla
           tabla_resultados.insertRow(row)
           tabla_resultados.setItem(row, 0, QTableWidgetItem(str(solicitud)))
           tabla_resultados.setItem(row, 1, QTableWidgetItem(str(medico)))
           tabla_resultados.setItem(row, 2, QTableWidgetItem(str(inicio)))
           tabla_resultados.setItem(row, 3, QTableWidgetItem(str(fin)))
           tabla_resultados.setItem(row, 4, QTableWidgetItem(ubicacion))

        tabla_resultados.setMinimumSize(700, 500)  # Establece el tamaño mínimo del cuadro de texto
        
        # Establecer el widget de texto en el cuadro de diálogo
        asignacion_dialog.layout().addWidget(tabla_resultados)
        
        # Mostrar el cuadro de diálogo
        asignacion_dialog.exec_()
        

    
    def calcular_indicadores(self):
     from datetime import datetime 
     # Llamar a la función de asignación de médicos
     gantt = self.asignacion_doctor1()
     # Crear un dataframe con los datos de los doctores
     res = pd.DataFrame(columns=['Medico', 'Distancia total', 'Cantidad de solicitudes', 'Tiempo trabajado', 'Tiempo ocioso', 'Tiempo de espera', 'Cantidad de solicitudes demoradas', 'Tiempo de demora', 'Tiempo en servicio', 'Tiempo extra', 'Cantidad de solicitudes por hora', 'Tiempo de espera promedio'])

     # Agregar los médicos al dataframe
     for i in gantt:
         if i['Medico'] not in res['Medico'].values:
             row = {'Medico': i['Medico'], 'Distancia total': 0, 'Cantidad de solicitudes': 0, 'Tiempo trabajado': 0,'Tiempo ocioso':0, 'Tiempo de espera': 0, 'Cantidad de solicitudes demoradas': 0, 'Tiempo de demora': 0, 'Tiempo en servicio': 0, 'Tiempo extra': 0, 'Cantidad de solicitudes por hora': 0, 'Tiempo de espera promedio': 0}
             res = pd.concat([res, pd.DataFrame(row, index=[0])], ignore_index=True)

     # Calcular los datos de los médicos
     for i in gantt:

         fin_solicitud = datetime.strptime(i['Fin'], "%Y-%m-%d %H:%M:%S")
         inicio_solicitud = datetime.strptime(i['Inicio'], "%Y-%m-%d %H:%M:%S")

         inicio_jornada = i['Inicio Jornada']
         fin_jornada = i['Fin Jornada']
         fin_traslado = i['Fin traslado']
         llegada_solicitud = i['Llegada solicitud']
         inicio_traslado = i['Inicio traslado']
         tiempo_contratado = i['Tiempo contratado']
         if fin_solicitud.date() != inicio_solicitud.date() or fin_solicitud.hour * 60 + fin_solicitud.minute < inicio_traslado:
             # Se pasa fin solicitud a minutos y se agrega 1440 minutos que son los minutos de un día
             fin_solicitud = fin_solicitud.hour * 60 + fin_solicitud.minute + 1440
         else:
             fin_solicitud = fin_solicitud.hour * 60 + fin_solicitud.minute

         if inicio_solicitud.hour * 60 + inicio_solicitud.minute < llegada_solicitud:
             inicio_solicitud = inicio_solicitud.hour * 60 + inicio_solicitud.minute + 1440 + inicio_solicitud.second / 60
         else:
             inicio_solicitud = inicio_solicitud.hour * 60 + inicio_solicitud.minute + inicio_solicitud.second / 60

         # Calcular la distancia total recorrida por cada médico
         res.loc[res['Medico'] == i['Medico'], 'Distancia total'] += i['Distancia']

         # Calcular la cantidad de solicitudes atendidas por cada médico
         res.loc[res['Medico'] == i['Medico'], 'Cantidad de solicitudes'] += 1

         # Calcular el tiempo trabajado por cada médico
         tiempo_trabajando = fin_solicitud - inicio_traslado
         res.loc[res['Medico'] == i['Medico'], 'Tiempo trabajado'] += tiempo_trabajando

         # Calcular el tiempo de espera de cada médico
         tiempo_espera = inicio_solicitud - llegada_solicitud
         res.loc[res['Medico'] == i['Medico'], 'Tiempo de espera'] += tiempo_espera

         # Calcular la cantidad de solicitudes demoradas por cada médico
         if inicio_solicitud - llegada_solicitud > tiempo_contratado:
             res.loc[res['Medico'] == i['Medico'], 'Cantidad de solicitudes demoradas'] += 1

         # Calcular el tiempo de demora de cada médico
         if inicio_solicitud - llegada_solicitud > tiempo_contratado:
             tiempo_demora = inicio_solicitud - llegada_solicitud - tiempo_contratado
             res.loc[res['Medico'] == i['Medico'], 'Tiempo de demora'] += tiempo_demora

     # Para cada médico encontrar el maximo tiempo de fin solicitud
     for i in res['Medico']:
         maximo = 0
         for j in gantt:
             if j['Medico'] == i:
                 if j['Fin atencion']> maximo:
                     maximo = j['Fin atencion']
                     # Calcular el tiempo ocioso de cada médico
                     maximo = maximo - j['Inicio Jornada']

         res.loc[res['Medico'] == i, 'Tiempo ocioso'] = maximo - res.loc[res['Medico'] == i, 'Tiempo trabajado']

     # Calcular el tiempo en servicio de cada médico
     res['Tiempo en servicio'] = res['Tiempo trabajado'] + res['Tiempo ocioso']

     # Calcular el tiempo extra de cada médico si es negativo es 0
     res['Tiempo extra'] = res['Tiempo en servicio'] - 480
     res.loc[res['Tiempo extra'] < 0, 'Tiempo extra'] = 0

     # Calcular la cantidad de solicitudes por hora de cada médico
     res['Cantidad de solicitudes por hora'] = res['Cantidad de solicitudes'] / (res['Tiempo en servicio'] / 60)

     # Calcular el tiempo de espera promedio de cada médico
     res['Tiempo de espera promedio'] = res['Tiempo de espera'] / res['Cantidad de solicitudes']
     
     # Configurar el QTableWidget con el DataFrame
     self.mostrar_ind_text.setRowCount(len(res.index))
     self.mostrar_ind_text.setColumnCount(len(res.columns))
     self.mostrar_ind_text.setHorizontalHeaderLabels(res.columns)

     # Llenar la tabla con datos
     for i in range(len(res.index)):
            for j in range(len(res.columns)):
                item = QTableWidgetItem(str(round(float(res.iloc[i, j]),2)))
                self.mostrar_ind_text.setItem(i, j, item)
                
     self.df_actual = res  # Guardar el DataFrame actual
     # Habilitar el botón después de calcular los indicadores
     self.mostrar_indicadoresg_btn.setEnabled(True)
     self.mostrar_indicadoresmym_btn.setEnabled(True)
    
                
                
    def exportar_indicadores(self):
        if hasattr(self, 'df_actual'):  # Asegurarse de que existe un DataFrame para exportar
            # Abrir un cuadro de diálogo para seleccionar la ubicación del archivo
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, 'Guardar como', '', 'Excel Files (*.xlsx)')

            if file_path:
                # Escribir el DataFrame en el archivo Excel
                self.df_actual.to_excel(file_path, index=False)
        else:
            print("No hay datos para exportar.")
            
    def mostrar_grafico(self):
       # Limpiar el gráfico antes de volver a dibujar
       self.ax.clear()
    
       # Calcular el tiempo total trabajado por todos los médicos
       tiempo_total_trabajado = self.df_actual['Tiempo en servicio'].sum()
    
       # Calcular el porcentaje de tiempo ocioso y trabajado
       porcentaje_ocioso = (self.df_actual['Tiempo ocioso'].sum() / tiempo_total_trabajado) * 100
       porcentaje_trabajado = (self.df_actual['Tiempo trabajado'].sum() / tiempo_total_trabajado) * 100
    
       # Etiquetas y datos para el gráfico de torta
       labels = ['Ocio', 'Trabajo']
       sizes = [porcentaje_ocioso, porcentaje_trabajado]
    
       # Crear el gráfico de torta
       self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
       self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
       self.ax.set_xticks([])  # Quitar los números del eje x
       self.ax.set_yticks([])  # Quitar los números del eje y
    
       # Actualizar el canvas para mostrar el nuevo gráfico
       self.canvas.draw()
       
    def mostrar_indicadores_generales(self):
        # Calcular indicadores generales
        indicadores_generales = {
            'Indicador': [
                'Distancia total', 'Cantidad de solicitudes', 'Tiempo trabajado',
                'Tiempo ocioso', 'Tiempo de espera', 'Cantidad de solicitudes demoradas',
                'Tiempo de demora', 'Tiempo en servicio', 'Tiempo extra',
                'Cantidad de solicitudes por hora', 'Tiempo de espera promedio'
            ],
            'Mínimo': [
                round(self.df_actual['Distancia total'].min(),2),
                round(self.df_actual['Cantidad de solicitudes'].min(),2),
                round(self.df_actual['Tiempo trabajado'].min(),2),
                round(self.df_actual['Tiempo ocioso'].min(),2),
                round(self.df_actual['Tiempo de espera'].min(),2),
                round(self.df_actual['Cantidad de solicitudes demoradas'].min(),2),
                round(self.df_actual['Tiempo de demora'].min(),2),
                round(self.df_actual['Tiempo en servicio'].min(),2),
                round(self.df_actual['Tiempo extra'].min(),2),
                round(self.df_actual['Cantidad de solicitudes por hora'].min(),2),
                round(self.df_actual['Tiempo de espera promedio'].min(),2)
            ],
            'Máximo': [
                round(self.df_actual['Distancia total'].max(),2),
                round(self.df_actual['Cantidad de solicitudes'].max(),2),
                round(self.df_actual['Tiempo trabajado'].max(),2),
                round(self.df_actual['Tiempo ocioso'].max(),2),
                round(self.df_actual['Tiempo de espera'].max(),2),
                round(self.df_actual['Cantidad de solicitudes demoradas'].max(),2),
                round(self.df_actual['Tiempo de demora'].max(),2),
                round(self.df_actual['Tiempo en servicio'].max(),2),
                round(self.df_actual['Tiempo extra'].max(),2),
                round(self.df_actual['Cantidad de solicitudes por hora'].max(),2),
                round(self.df_actual['Tiempo de espera promedio'].max(),2)
            ],
            'Promedio': [
                round(self.df_actual['Distancia total'].mean(),2),
                round(self.df_actual['Cantidad de solicitudes'].mean(),2),
                round(self.df_actual['Tiempo trabajado'].mean(),2),
                round(self.df_actual['Tiempo ocioso'].mean(),2),
                round(self.df_actual['Tiempo de espera'].mean(),2),
                round(self.df_actual['Cantidad de solicitudes demoradas'].mean(),2),
                round(self.df_actual['Tiempo de demora'].mean(),2),
                round(self.df_actual['Tiempo en servicio'].mean(),2),
                round(self.df_actual['Tiempo extra'].mean(),2),
                round(self.df_actual['Cantidad de solicitudes por hora'].mean(),2),
                round(self.df_actual['Tiempo de espera promedio'].mean(),2)
            ]
        }

        # Crear un DataFrame con los indicadores generales
        indicadores_df = pd.DataFrame(indicadores_generales)

        # Configurar el QTableWidget con el DataFrame
        self.tablageneral.setRowCount(len(indicadores_df.index))
        self.tablageneral.setColumnCount(len(indicadores_df.columns))
        self.tablageneral.setHorizontalHeaderLabels(indicadores_df.columns)

        # Llenar la tabla con datos
        for i in range(len(indicadores_df.index)):
            for j in range(len(indicadores_df.columns)):
                item = QTableWidgetItem(str(indicadores_df.iloc[i, j]))
                self.tablageneral.setItem(i, j, item)
        
     

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MiAplicacion()
    ventana.show()
    sys.exit(app.exec_())
