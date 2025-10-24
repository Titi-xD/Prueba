from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from usuarios import usuarios
from sesion import sesion
from solicitudes import sistemaSolicitudes as solicitudes

class inicioSesion(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("inicio_sesion.ui", self)
        self.usuarios = usuarios()
        self.sesion = sesion()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(self.width(), self.height())

        self.lab_salir.mousePressEvent = lambda event: self.cerrar_programa()
        self.lab_iniciar.mousePressEvent = lambda event: self.mostrar_inicio()
        self.lab_registro.mousePressEvent = lambda event: self.mostrar_registro()
        self.btn_acceder.mousePressEvent = lambda event: self.abrir_ventana()
        self.btn_crear.mousePressEvent = lambda event: self.crear_usuario()

    def cerrar_programa(self):
        self.close()

    def mostrar_inicio(self):
        self.stacked.setCurrentWidget(self.page_iniciar)
        self.lab_iniciar.setStyleSheet("background-color: #9CD0DC; border: #FFFFFF;")
        self.lab_registro.setStyleSheet("background-color: #BDE2EA; border: #FFFFFF;")

    def mostrar_registro(self):
        self.stacked.setCurrentWidget(self.page_registro)
        self.lab_registro.setStyleSheet("background-color: #9CD0DC; border: #FFFFFF;")
        self.lab_iniciar.setStyleSheet("background-color: #BDE2EA; border: #FFFFFF;")

    def abrir_ventana(self):
        nombre = self.txt_nombre.toPlainText().strip()
        contrasena = self.txt_contra.toPlainText().strip()

        if not nombre or not contrasena:
            self.mostrar_mensaje("Algunos campos están vacíos")
            return

        if self.sesion.iniciar_sesion(nombre, contrasena):
            datos_usuario = usuarios().leer_usuario(nombre)
            nueva_ventana = servicioUsuario(datos_usuario)
            nueva_ventana.show()
            self.hide()
        else:
            self.mostrar_mensaje("Usuario o contraseña incorrectos")

    def crear_usuario(self):
        nombre = self.txt_nuevo_nombre.toPlainText().strip()
        contrasena = self.txt_nueva_contra.toPlainText().strip()

        if not nombre or not contrasena:
            self.mostrar_mensaje("Algunos campos están vacíos")
            return

        usuarios_lista = self.usuarios.cargar_usuarios()
        user_id = max([u["id"] for u in usuarios_lista], default=0) + 1
        mensaje = self.usuarios.crear_usuario(user_id, nombre, contrasena)
        self.mostrar_mensaje(mensaje)
        self.mostrar_inicio()
        
        self.txt_nuevo_nombre.clear()
        self.txt_nueva_contra.clear()

    def mostrar_mensaje(self, texto):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.exec_()

class servicioUsuario(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        loadUi("servicio_usuario.ui", self)

        self.usuario = usuario
        self.solicitudes = solicitudes()
        id_usuario = self.usuario["id"]

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(self.width(), self.height())

        self.lab_bienvenido.setText(f"¡Bienvenido {self.usuario['nombre']}!")
        self.lab_nombre.setText(self.usuario['nombre'])
        self.lab_contra.setText(self.usuario['contrasena'])
        self.txt_nombre.setPlainText(self.usuario['nombre'])
        self.txt_contra.setPlainText(self.usuario['contrasena'])
        
        solicitud_activa = self.solicitudes.cargar_solicitud_activa(id_usuario)
        if solicitud_activa:
            self.mostrar_solicitud_activa(solicitud_activa)
        else:
            self.ocultar_botones()
    
        self.configurar_tabla()

        self.btn_salir.mousePressEvent = lambda event: self.regresar_ventana()
        self.btn_inicio.mousePressEvent = lambda event: self.mostrar_inicio()
        self.btn_solicitud.mousePressEvent = lambda event: self.mostrar_solicitud()
        self.btn_historial.mousePressEvent = lambda event: self.mostrar_historial()
        self.btn_cuenta.mousePressEvent = lambda event: self.mostrar_cuenta()
        self.btn_editar.mousePressEvent = lambda event: self.mostrar_editar_cuenta()
        self.btn_cancelar_ed.mousePressEvent = lambda event: self.mostrar_cuenta()
        self.btn_editar_ed.mousePressEvent = lambda event: self.actualizar_cuenta()
        self.btn_eliminar.mousePressEvent = lambda event: self.eliminar_cuenta()
        self.btn_crear.mousePressEvent = lambda event: self.crear_solicitud()
        self.btn_cancelar.mousePressEvent = lambda event: self.ocultar_botones()
        self.btn_finalizar.mousePressEvent = lambda event: self.ocultar_botones()
        
        
    def configurar_tabla(self):
        self.table_historial.verticalHeader().setVisible(False)
        self.table_historial.hideColumn(0)
        widths = [170, 170, 80, 70, 70, 70, 70]
        for i, w in enumerate(widths, start=1):
            self.table_historial.setColumnWidth(i, w)
            
    def set_btn_estilo(self, btn, color="#243769"):
        btn.setStyleSheet(
            f"background-color: {color}; font: bold 9pt Verdana; color: #FFFFFF; border: {color}; border-radius: 10px;")
        
    def mostrar_mensaje(self, texto):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Información")
        msg.setText(texto)
        msg.exec_()

    def regresar_ventana(self):
        from PyQt5.QtWidgets import QMessageBox
        from red_optima import inicioSesion
        try:
            ventana_inicio = inicioSesion()
            ventana_inicio.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudo regresar: {str(e)}")
            msg.exec_()

    def mostrar_inicio(self):
        self.stacked.setCurrentWidget(self.page_inicio)
        self.set_btn_estilo(self.btn_solicitud)
        self.set_btn_estilo(self.btn_historial)
        self.set_btn_estilo(self.btn_cuenta)

    def mostrar_solicitud(self):
        self.stacked.setCurrentWidget(self.page_solicitud)
        self.set_btn_estilo(self.btn_solicitud, color="#9CC0F6")
        self.set_btn_estilo(self.btn_historial)
        self.set_btn_estilo(self.btn_cuenta)

    def mostrar_historial(self):
        self.stacked.setCurrentWidget(self.page_historial)
        self.set_btn_estilo(self.btn_historial, color="#9CC0F6")
        self.set_btn_estilo(self.btn_solicitud)
        self.set_btn_estilo(self.btn_cuenta)

    def mostrar_cuenta(self):
        self.stacked.setCurrentWidget(self.page_cuenta)
        self.set_btn_estilo(self.btn_cuenta, color="#9CC0F6")
        self.set_btn_estilo(self.btn_solicitud)
        self.set_btn_estilo(self.btn_historial)

    def mostrar_editar_cuenta(self):
        self.stacked.setCurrentWidget(self.page_editar)
        
    def actualizar_cuenta(self):
        nuevo_nombre = self.txt_nombre.toPlainText().strip()
        nueva_contrasena = self.txt_contra.toPlainText().strip()
        if not nuevo_nombre or not nueva_contrasena:
            self.mostrar_mensaje("Algunos campos están vacíos")
            return
        from usuarios import usuarios

        gestor = usuarios()
        resultado = gestor.actualizar_usuario(
            self.usuario["id"],
            nuevo_nombre = nuevo_nombre,
            nueva_contrasena = nueva_contrasena)
        if "Error" in resultado:
            self._mostrar_mensaje(resultado)
        else:
            self.usuario["nombre"] = nuevo_nombre
            self.usuario["contrasena"] = nueva_contrasena

            self.lab_nombre.setText(nuevo_nombre)
            self.lab_contra.setText(nueva_contrasena)

            self.mostrar_mensaje("Cuenta actualizada correctamente")
            self.mostrar_cuenta()
            
    def eliminar_cuenta(self):
        from usuarios import usuarios

        gestor = usuarios()
        user_id = self.usuario["id"]

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que quieres eliminar tu cuenta?",
            QMessageBox.Yes | QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            resultado = gestor.eliminar_usuario(user_id)
            if "Error" in resultado:
                self.mostrar_mensaje(resultado)
            else:
                self.mostrar_mensaje("Cuenta eliminada correctamente")
                self.regresar_ventana()
        else:
            self.mostrar_mensaje("Eliminación cancelada.")       

    def ocultar_botones(self):
        self.btn_crear.show()
        self.btn_actualizar.hide()
        self.btn_finalizar.hide()
        self.btn_cancelar.hide()
        
    def mostrar_botones(self):
        self.btn_crear.hide()
        self.btn_actualizar.show()
        self.btn_finalizar.show()
        self.btn_cancelar.show()
            
    def crear_solicitud(self):
        try:
            punto_origen = self.combox_pto_inicial.currentText().strip()
            punto_destino = self.combox_pto_destino.currentText().strip()
            transporte = self.combox_transporte.currentText().strip()
        
            if punto_origen == punto_destino:
                QMessageBox.warning(self, "Error", "El punto de origen y destino no pueden ser el mismo")
                return

            distancia, tiempo = self.solicitudes.calcular_ruta(punto_origen, punto_destino, transporte)

            precio = self.solicitudes.calcular_precio(distancia, tiempo, transporte)

            self.lab_estado.setText("Activo")
            self.lab_distancia.setText(f"{distancia} km")
            self.lab_tiempo.setText(f"{tiempo} min")
            self.lab_precio.setText(f"Q{precio}")

            self.mostrar_botones()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al crear la solicitud: {e}")
    
    def mostrar_solicitud_activa(self, solicitud):
        self.combox_pto_inicial.setCurrentText(solicitud["punto_origen"])
        self.combox_pto_destino.setCurrentText(solicitud["punto_destino"])
        self.combox_transporte.setCurrentText(solicitud["transporte"])
        self.lab_estado.setText(solicitud["estado"])
        self.lab_distancia.setText(f"{solicitud['distancia']} km")
        self.lab_tiempo.setText(f"{solicitud['tiempo']} min")
        self.lab_precio.setText(f"Q{solicitud['precio']}")

        self.btn_crear.hide()
        self.btn_actualizar.show()
        self.btn_finalizar.show()
        self.btn_cancelar.show()
        
app = QApplication([])
w = inicioSesion()
w.show()
app.exec_()
