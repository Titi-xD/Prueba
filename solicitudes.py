import json
import os
import math
import re


class Solicitud:
    def __init__(self, id, id_usuario, punto_origen, punto_destino, transporte, estado, distancia, tiempo, precio):
        self.id = id
        self.id_usuario = id_usuario
        self.punto_origen = punto_origen
        self.punto_destino = punto_destino
        self.transporte = transporte
        self.estado = estado
        self.distancia = distancia
        self.tiempo = tiempo
        self.precio = precio

    def to_dict(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "punto_origen": self.punto_origen,
            "punto_destino": self.punto_destino,
            "transporte": self.transporte,
            "estado": self.estado,
            "distancia": self.distancia,
            "tiempo": self.tiempo,
            "precio": self.precio,
        }


class sistemaSolicitudes:
    def __init__(self, archivo="solicitudes.json"):
        self.archivo = archivo
        self.solicitudes = []
        self.cargar_datos()

    # Persistencia
    def cargar_datos(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    data = json.load(f) or []
            except (json.JSONDecodeError, FileNotFoundError):
                data = []
        else:
            data = []

        # Compatibilidad con versiones antiguas
        normalizados = []
        for item in data:
            if "id_transporte" in item and "transporte" not in item:
                item["transporte"] = item.pop("id_transporte")
            normalizados.append(item)

        self.solicitudes = [Solicitud(**it) for it in normalizados] if normalizados else []

    def guardar_datos(self):
        contenido = [s.to_dict() for s in self.solicitudes]
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)

    # Consultas
    def get_solicitud_activa(self, id_usuario):
        for s in self.solicitudes:
            if s.id_usuario == id_usuario and str(s.estado).strip().lower() == "activo":
                return s
        return None

    def ver_solicitudes(self, id_usuario):
        try:
            solicitudes_usuario = [s for s in self.solicitudes if s.id_usuario == id_usuario]
            if not solicitudes_usuario:
                return {"success": False, "message": "No hay solicitudes para este usuario"}
            return {"success": True, "solicitudes": [s.to_dict() for s in solicitudes_usuario]}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    # Reglas de negocio
    def validar_estado(self, estado):
        permitidos = {"activo", "finalizado", "cancelado", "pendiente"}
        return str(estado).strip().lower() in permitidos

    def validar_transporte(self, transporte):
        permitidos = {"motocicleta", "automóvil", "automovil", "autobús", "autobus", "tren"}
        return str(transporte).strip().lower() in permitidos

    # Cálculos de ruta y precio
    def calcular_ruta(self, punto_origen, punto_destino, transporte):
        velocidades_kmh = {
            "motocicleta": 40.0,
            "automóvil": 30.0,
            "automovil": 30.0,
            "autobús": 25.0,
            "autobus": 25.0,
            "tren": 35.0,
        }
        clave = str(transporte or "").strip().lower()
        velocidad = velocidades_kmh.get(clave, 30.0)

        c1 = self._parse_coordenadas(punto_origen)
        c2 = self._parse_coordenadas(punto_destino)
        if c1 and c2:
            distancia = self._haversine_km(c1[0], c1[1], c2[0], c2[1])
            distancia = max(0.5, round(distancia, 2))
        else:
            try:
                numeros_origen = re.findall(r"\d+", punto_origen or "")
                numeros_destino = re.findall(r"\d+", punto_destino or "")
                zona_origen = int(numeros_origen[0]) if numeros_origen else 1
                zona_destino = int(numeros_destino[0]) if numeros_destino else 1
                diferencia_zonas = abs(zona_destino - zona_origen)
                distancia = max(2.0, diferencia_zonas * 3.0)
            except Exception:
                distancia = 5.0
            distancia = round(distancia, 2)

        tiempo = int(max(5, round((distancia / velocidad) * 60)))
        return distancia, tiempo

    def calcular_precio(self, distancia, tiempo):
        return round((distancia * 3.0) + (tiempo * 0.4), 2)

    # Mutaciones
    def crear_solicitud(self, id_usuario, punto_origen, punto_destino, transporte, estado):
        try:
            if not all([
                str(id_usuario).strip(),
                str(punto_origen).strip(),
                str(punto_destino).strip(),
                str(transporte).strip(),
                str(estado).strip(),
            ]):
                return {"success": False, "message": "Todos los campos son obligatorios"}

            if str(punto_origen).strip().lower() == str(punto_destino).strip().lower():
                return {"success": False, "message": "El origen y destino no pueden ser iguales"}

            if not self.validar_estado(estado):
                return {"success": False, "message": "Estado inválido"}

            if not self.validar_transporte(transporte):
                return {"success": False, "message": "Transporte inválido"}

            if self.get_solicitud_activa(id_usuario):
                return {"success": False, "message": "Ya existe una solicitud activa"}

            distancia, tiempo = self.calcular_ruta(punto_origen, punto_destino, transporte)
            precio = self.calcular_precio(distancia, tiempo)

            nuevo_id = (max([s.id for s in self.solicitudes], default=0) + 1) if self.solicitudes else 1
            nueva = Solicitud(
                nuevo_id,
                id_usuario,
                str(punto_origen).strip(),
                str(punto_destino).strip(),
                str(transporte).strip(),
                str(estado).strip().capitalize(),
                distancia,
                tiempo,
                precio,
            )

            self.solicitudes.append(nueva)
            self.guardar_datos()
            return {
                "success": True,
                "message": "Solicitud creada correctamente",
                "data": {"id": nuevo_id, "distancia": distancia, "tiempo": tiempo, "precio": precio},
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def actualizar_solicitud(self, id_solicitud, nuevo_estado):
        try:
            if not self.validar_estado(nuevo_estado):
                return {"success": False, "message": "Estado inválido"}
            for s in self.solicitudes:
                if s.id == id_solicitud:
                    s.estado = str(nuevo_estado).strip().capitalize()
                    self.guardar_datos()
                    return {"success": True, "message": "Estado actualizado correctamente"}
            return {"success": False, "message": "Solicitud no encontrada"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    # Helpers
    def _parse_coordenadas(self, texto):
        try:
            if not texto:
                return None
            texto = str(texto).strip()
            # formatos: "14.62,-90.52" o "(14.62, -90.52)"
            texto = texto.replace("(", "").replace(")", "")
            partes = [p.strip() for p in texto.split(",")]
            if len(partes) != 2:
                return None
            lat = float(partes[0])
            lon = float(partes[1])
            return lat, lon
        except Exception:
            return None

    def _haversine_km(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

