from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from usuarios import usuarios
from sesion import sesion

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
            self._mostrar_mensaje("Algunos campos están vacíos")
            return

        if self.sesion.iniciar_sesion(nombre, contrasena):
            datos_usuario = usuarios().leer_usuario(nombre)
            nueva_ventana = servicioUsuario(datos_usuario)
            nueva_ventana.show()
            self.hide()
        else:
            self._mostrar_mensaje("Usuario o contraseña incorrectos")

    def crear_usuario(self):
        nombre = self.txt_nuevo_nombre.toPlainText().strip()
        contrasena = self.txt_nueva_contra.toPlainText().strip()

        if not nombre or not contrasena:
            self._mostrar_mensaje("Algunos campos están vacíos")
            return

        usuarios_lista = self.usuarios.cargar_usuarios()
        user_id = max([u["id"] for u in usuarios_lista], default=0) + 1
        mensaje = self.usuarios.crear_usuario(user_id, nombre, contrasena)
        self._mostrar_mensaje(mensaje)
        self.mostrar_inicio()
        
        self.txt_nuevo_nombre.clear()
        self.txt_nueva_contra.clear()

    def _mostrar_mensaje(self, texto):
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

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(self.width(), self.height())

        self.lab_bienvenido.setText(f"¡Bienvenido {self.usuario['nombre']}!")
        self.lab_nombre.setText(self.usuario['nombre'])
        self.lab_contra.setText(self.usuario['contrasena'])
        self.txt_nombre.setPlainText(self.usuario['nombre'])
        self.txt_contra.setPlainText(self.usuario['contrasena'])
        
        self.configurar_tabla()
        self.btn_actualizar.hide()
        self.btn_finalizar.hide()
        self.btn_cancelar.hide()

        self.btn_salir.mousePressEvent = lambda event: self.regresar_ventana()
        self.btn_inicio.mousePressEvent = lambda event: self.mostrar_inicio()
        self.btn_solicitud.mousePressEvent = lambda event: self.mostrar_solicitud()
        self.btn_historial.mousePressEvent = lambda event: self.mostrar_historial()
        self.btn_cuenta.mousePressEvent = lambda event: self.mostrar_cuenta()
        self.btn_editar.mousePressEvent = lambda event: self.mostrar_editar_cuenta()
        self.btn_cancelar_ed.mousePressEvent = lambda event: self.mostrar_cuenta()
        self.btn_crear.mousePressEvent = lambda event: self.crear_solicitud()
        self.btn_cancelar.mousePressEvent = lambda event: self.solicitud()
        self.btn_finalizar.mousePressEvent = lambda event: self.solicitud()
        
    def configurar_tabla(self):
        self.table_historial.verticalHeader().setVisible(False)
        self.table_historial.hideColumn(0)
        widths = [170, 170, 80, 70, 70, 70, 70]
        for i, w in enumerate(widths, start=1):
            self.table_historial.setColumnWidth(i, w)

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

    def _set_btn_estilo(self, btn, color="#243769"):
        btn.setStyleSheet(
            f"background-color: {color}; font: bold 9pt Verdana; color: #FFFFFF; border: {color}; border-radius: 10px;"
        )

    def mostrar_inicio(self):
        self.stacked.setCurrentWidget(self.page_inicio)
        self._set_btn_estilo(self.btn_solicitud)
        self._set_btn_estilo(self.btn_historial)
        self._set_btn_estilo(self.btn_cuenta)

    def mostrar_solicitud(self):
        self.stacked.setCurrentWidget(self.page_solicitud)
        self._set_btn_estilo(self.btn_solicitud, color="#9CC0F6")
        self._set_btn_estilo(self.btn_historial)
        self._set_btn_estilo(self.btn_cuenta)

    def mostrar_historial(self):
        self.stacked.setCurrentWidget(self.page_historial)
        self._set_btn_estilo(self.btn_historial, color="#9CC0F6")
        self._set_btn_estilo(self.btn_solicitud)
        self._set_btn_estilo(self.btn_cuenta)

    def mostrar_cuenta(self):
        self.stacked.setCurrentWidget(self.page_cuenta)
        self._set_btn_estilo(self.btn_cuenta, color="#9CC0F6")
        self._set_btn_estilo(self.btn_solicitud)
        self._set_btn_estilo(self.btn_historial)

    def mostrar_editar_cuenta(self):
        self.stacked.setCurrentWidget(self.page_editar)

    def solicitud(self):
        self.btn_crear.show()
        self.btn_actualizar.hide()
        self.btn_finalizar.hide()
        self.btn_cancelar.hide()

    def crear_solicitud(self):
        self.btn_crear.hide()
        self.btn_actualizar.show()
        self.btn_finalizar.show()
        self.btn_cancelar.show
        
app = QApplication([])
w = inicioSesion()
w.show()
app.exec_()
