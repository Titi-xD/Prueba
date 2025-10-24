import json
import os

class sesion:
    def __init__(self, archivo="usuarios.json"):
        self.archivo = archivo
        self.usuario_actual = None

    def iniciar_sesion(self, nombre, contrasena):
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False      

        nombre = nombre.strip().lower()
        contrasena = contrasena.strip()

        for u in usuarios:
            if u["nombre"].strip().lower() == nombre and u["contrasena"].strip() == contrasena:
                self.usuario_actual = {
                    "id": u["id"],
                    "nombre": u["nombre"],
                    "contrasena": u["contrasena"]
                }
                return True
        return False
