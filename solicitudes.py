import json
import os
import re
import math

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

    @staticmethod
    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0  # km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def cargar_datos(self):
        if os.path.exists(self.archivo):
            with open(self.archivo, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for item in data:
                        if 'id_transporte' in item:
                            item['transporte'] = item.pop('id_transporte')
                    self.solicitudes = [Solicitud(**item) for item in data]
                except (json.JSONDecodeError, KeyError):
                    self.solicitudes = []
        else:
            self.solicitudes = []
            
    def mostrar_solicitud_activa(self, id_usuario):
        try:
            self.cargar_datos()
            for s in self.solicitudes:
                if str(s.id_usuario) == str(id_usuario) and s.estado.lower() == "Activa":
                    return s.to_dict()
            return None
        except Exception as e:
            print(f"Error al cargar solicitud activa: {e}")
            return None

    def guardar_datos(self):
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                # Convertir cada solicitud a diccionario
                json.dump([s.to_dict() for s in self.solicitudes], f, ensure_ascii=False, indent=4)
            return "Datos guardados correctamente"
        except Exception as e:
            return f"Error al guardar: {e}"
    
    def calcular_ruta(self, punto_origen, punto_destino, transporte):
        coordenadas = {
            "Municipalidad de Guatemala": (14.627115, -90.514714),
            "Hospital General San Juan de Dios": (14.639510, -90.521928),
            "Café León": (14.639894, -90.511868),
            "Restaurante San Martín": (14.639018, -90.514373),
            "Instituto Nacional Central para Varones": (14.639584, -90.511003),
            "Universidad San Carlos (Extensión Centro)": (14.635832, -90.508978),
            "Teatro Nacional Miguel Ángel Asturias": (14.627499, -90.518080),
            "Parque Central": (14.642549, -90.514758) }
        
        velocidades = { 
            "Motocicleta": 25.0,
            "Automóvil": 20.0,
            "Autobús": 15.0,
            "Tren": 30.0 }
        
        v = velocidades.get(transporte, 30.0)

        # 1) Intentar con coordenadas reales
        c1 = coordenadas.get(punto_origen)
        c2 = coordenadas.get(punto_destino)
        if c1 and c2:
            distancia = self.haversine_km(c1[0], c1[1], c2[0], c2[1])
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
        tiempo = round((distancia / v) * 60, 2)
        return distancia, tiempo


    def calcular_precio(self, distancia, tiempo, transporte):
        factores = {"Motocicleta": 2.5, "Automóvil": 2.0, "Autobús": 1.5, "Tren": 3.0}
        f = factores.get(transporte, 2.0)
        precio_base = (distancia * 3.0) + (tiempo * 0.4)
        return round(precio_base * f, 2)

    def validar_estado(self, estado):
        return isinstance(estado, str) and estado.lower() in ["Activa", "Cancelada", "Finalizada"]

    def validar_transporte(self, transporte):
        return isinstance(transporte, str) and transporte.lower() in ["motocicleta", "automovil", "autobus", "tren"]


    def crear_solicitud(self, id_usuario, punto_origen, punto_destino, transporte, estado):
        try:        
            # Cálculo automático
            distancia, tiempo = self.calcular_ruta(punto_origen, punto_destino, transporte)
            precio = self.calcular_precio(distancia, tiempo, transporte)
        
            # Crear solicitud
            nuevo_id = len(self.solicitudes) + 1
            nueva_solicitud = Solicitud(
                nuevo_id, id_usuario, punto_origen, punto_destino, 
                transporte, estado, distancia, tiempo, precio)
        
            self.solicitudes.append(nueva_solicitud)
            self.guardar_datos()
        
            return {
                "success": True, 
                "message": "Solicitud creada correctamente",
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

