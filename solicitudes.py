import json
import os

class solicitud:
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
            
    def cargar_solicitud_activa(self, id_usuario):
        for solicitud in self.solicitudes:
            if solicitud.id_usuario == id_usuario and solicitud.estado.lower() == "activo":
                # Cargar datos en los widgets
                self.combox_pto_inicial.setCurrentText(solicitud.punto_origen)
                self.combox_pto_destino.setCurrentText(solicitud.punto_destino)
                self.combox_transporte.setCurrentText(solicitud.transporte)
                self.lab_estado.setText(solicitud.estado)
                self.lab_distancia.setText(f"{solicitud.distancia} km")
                self.lab_tiempo.setText(f"{solicitud.tiempo} min")
                self.lab_precio.setText(f"Q{solicitud.precio}")

                # Cambiar visibilidad de botones
                self.btn_crear.hide()
                self.btn_actualizar.show()
                self.btn_finalizar.show()
                self.btn_cancelar.show()
                return True

        return False

    def calcular_ruta(self, punto_origen, punto_destino, transporte):
        import re  # por si no estaba importado

        velocidades = { 
            "Motocicleta": 40.0,
            "Automóvil": 30.0,
            "Autobús": 25.0,
            "Tren": 35.0}
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
            for solicitud in self.solicitudes:
                if solicitud.id == id_solicitud:
                    if self.validar_estado(nuevo_estado):
                        solicitud.estado = nuevo_estado
                        self.guardar_datos()
                        return {"success": True, "message": "Estado actualizado correctamente"}
                    else:
                        return {"success": False, "message": "Estado inválido"}
            
            return {"success": False, "message": "Solicitud no encontrada"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

