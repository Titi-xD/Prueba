import json
import os

class usuarios:
    def __init__(self, archivo="usuarios.json"):
        self.archivo = archivo
        if not os.path.exists(self.archivo):
            with open(self.archivo, "w") as f:
                json.dump([], f)

    def cargar_usuarios(self):
        try:
            with open(self.archivo, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar_usuarios(self, usuarios):
        try:
            with open(self.archivo, "w") as f:
                json.dump(usuarios, f, indent=4)
            return "Datos guardados correctamente."
        except Exception as e:
            return f"Error al guardar los datos: {e}"

    def crear_usuario(self, user_id, nombre, contrasena):
        try:
            usuarios = self.cargar_usuarios()

            for u in usuarios:
                if u["nombre"].lower() == nombre.lower():
                    return "El usuario ya existe."

            nuevo_usuario = {
                "id": user_id,
                "nombre": nombre,
                "contrasena": contrasena
            }
            usuarios.append(nuevo_usuario)
            resultado = self.guardar_usuarios(usuarios)
            return "Usuario registrado exitosamente." if "Error" not in resultado else resultado
        except Exception as e:
            return f"Error al crear el usuario: {e}"

    def leer_usuario(self, nombre):
        try:
            usuarios = self.cargar_usuarios()
            for u in usuarios:
                if u["nombre"].lower() == nombre.lower():
                    return {
                        "id": u["id"],
                        "nombre": u["nombre"],
                        "contraseña": u["contraseña"]
                    }
            return None
        except Exception as e:
            return {"error": "Ocurrió un error."}

    def actualizar_usuario(self, user_id, nuevo_nombre=None, nueva_contrasena=None):
        try:
            usuarios = self.cargar_usuarios()
            for u in usuarios:
                if u["id"] == user_id:
                    if nuevo_nombre:
                        u["nombre"] = nuevo_nombre
                    if nueva_contrasena:
                        u["contraseña"] = nueva_contrasena
                    resultado = self.guardar_usuarios(usuarios)
                    return "Usuario actualizado correctamente." if "Error" not in resultado else resultado
            return "Ocurrió un error."
        except Exception as e:
            return f"Error al actualizar usuario: {e}"

    def eliminar_usuario(self, user_id):
        try:
            usuarios = self.cargar_usuarios()
            nuevos_usuarios = [u for u in usuarios if u["id"] != user_id]
            if len(usuarios) != len(nuevos_usuarios):
                resultado = self.guardar_usuarios(nuevos_usuarios)
                return "Usuario eliminado correctamente." if "Error" not in resultado else resultado
            else:
                return "Ocurrió un error."
        except Exception as e:
            return f"Error al eliminar usuario: {e}"  
