import json
import os

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
            "precio": self.precio
        }


class sistemaSolicitudes:
    def __init__(self, archivo="solicitudes.json"):
        self.archivo = archivo
        self.solicitudes = []
        self.cargar_datos()

    def cargar_datos(self):
        data = self.cargar_solicitudes()
        try:
            self.solicitudes = [Solicitud(**item) for item in data]
        except Exception:
            self.solicitudes = []

    def cargar_solicitudes(self):
        if not os.path.exists(self.archivo):
            return []
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                if f.read().strip() == "":
                    return []
                f.seek(0)
                data = json.load(f)
                # Migración de claves antiguas si existieran
                for item in data:
                    if "id_transporte" in item and "transporte" not in item:
                        item["transporte"] = item.pop("id_transporte")
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar_datos(self):
        try:
            serializado = [s.to_dict() for s in self.solicitudes]
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(serializado, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
            
    def cargar_solicitud_activa(self, id_usuario):
        try:
            solicitudes = self.cargar_solicitudes()
            for s in solicitudes:
                if s["id_usuario"] == id_usuario and s["estado"].lower() == "activo":
                    return s 
            return None
        except Exception as e:
            print(f"Error al cargar solicitud activa: {e}")
            return None

    def calcular_ruta(self, punto_origen, punto_destino, transporte):
        import re

        # velocidades por tipo de transporte (minúsculas)
        velocidades = {
            "motocicleta": 40.0,
            "automóvil": 30.0,
            "autobus": 25.0,   # sin tilde por robustez
            "autobús": 25.0,
            "tren": 35.0,
        }
        v = velocidades.get((transporte or "").lower(), 30.0)

        # 1) Intentar con coordenadas reales
        c1 = self._parse_coordenadas(punto_origen)
        c2 = self._parse_coordenadas(punto_destino)
        if c1 and c2:
            distancia = self._haversine_km(c1[0], c1[1], c2[0], c2[1])
            distancia = max(0.5, round(distancia, 2))  # mínimo razonable
        else:
            # 2) Fallback por zonas
            try:
                numeros_origen = re.findall(r'\d+', punto_origen or "")
                numeros_destino = re.findall(r'\d+', punto_destino or "")
                zona_origen = int(numeros_origen[0]) if numeros_origen else 1
                zona_destino = int(numeros_destino[0]) if numeros_destino else 1
                diferencia_zonas = abs(zona_destino - zona_origen)
                distancia = max(2.0, diferencia_zonas * 3.0)
            except Exception:
                distancia = 5.0  # valor por defecto seguro
            distancia = round(distancia, 2)

        # Tiempo = distancia / velocidad * 60 (min)
        tiempo = int(max(5, round((distancia / v) * 60)))
        return distancia, tiempo


    def calcular_precio(self, distancia, tiempo):
        return round((distancia * 3.0) + (tiempo * 0.4), 2)


    def crear_solicitud(self, id_usuario, punto_origen, punto_destino, transporte, estado):
        try:
            # Validaciones
            if not all([str(id_usuario).strip(), punto_origen.strip(), punto_destino.strip(), transporte.strip(), estado.strip()]):
                return {"success": False, "message": "Todos los campos son obligatorios"}
        
            if not self.validar_estado(estado):
                return {"success": False, "message": "Estado inválido"}
        
            if not self.validar_transporte(transporte):
                return {"success": False, "message": "Transporte inválido"}
        
            # Cálculo automático
            distancia, tiempo = self.calcular_ruta(punto_origen, punto_destino, transporte)
            precio = self.calcular_precio(distancia, tiempo)
        
            # Crear solicitud
            nuevo_id = len(self.solicitudes) + 1
            nueva_solicitud = Solicitud(
                nuevo_id, id_usuario, punto_origen, punto_destino, 
                transporte, estado, distancia, tiempo, precio)
        
            self.solicitudes.append(nueva_solicitud)
            self.guardar_datos()
        
            return {
                "success": True, 
                "message": "✅ Solicitud creada correctamente",
                "data": {
                    "id": nuevo_id,
                    "distancia": distancia,
                    "tiempo": tiempo,
                    "precio": precio
                }
            }
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    

    def ver_solicitudes(self, id_usuario):
        try:
            solicitudes_usuario = [s for s in self.solicitudes if s.id_usuario == id_usuario]
            
            if not solicitudes_usuario:
                return {"success": False, "message": "No hay solicitudes para este usuario"}
            
            return {
                "success": True,
                "solicitudes": [s.to_dict() for s in solicitudes_usuario]
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
        

    def actualizar_solicitud(self, id_solicitud, nuevo_estado):
        """Actualiza el estado de una solicitud"""
        try:
            for solicitud_item in self.solicitudes:
                if solicitud_item.id == id_solicitud:
                    if self.validar_estado(nuevo_estado):
                        solicitud_item.estado = nuevo_estado
                        self.guardar_datos()
                        return {"success": True, "message": "Estado actualizado correctamente"}
                    else:
                        return {"success": False, "message": "Estado inválido"}
            
            return {"success": False, "message": "Solicitud no encontrada"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    # ---------- Utilidades y validaciones ----------
    def validar_estado(self, estado):
        estados_validos = {"activo", "pendiente", "finalizado", "cancelado"}
        return (estado or "").strip().lower() in estados_validos

    def validar_transporte(self, transporte):
        t = (transporte or "").strip().lower()
        validos = {"autobús", "autobus", "automóvil", "automovil", "motocicleta", "tren"}
        return t in validos

    def _parse_coordenadas(self, texto):
        """Devuelve (lat, lon) en float si encuentra dos números en el texto, si no None."""
        import re
        if not texto:
            return None
        numeros = re.findall(r"[-+]?\d+(?:\.\d+)?", texto)
        if len(numeros) < 2:
            return None
        try:
            lat = float(numeros[0])
            lon = float(numeros[1])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return None
            return (lat, lon)
        except ValueError:
            return None

    def _haversine_km(self, lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, asin, sqrt
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return R * c

