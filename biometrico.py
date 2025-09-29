from zk import ZK, const

DEVICE_IP = '192.168.1.201'
DEVICE_PORT = 4370

def obtener_asistencias(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)
    registros = []

    try:
        conn = zk.connect()
        conn.disable_device()

        asistencias = conn.get_attendance()
        if asistencias:
            for asistencia in asistencias:
                registros.append((asistencia.user_id, asistencia.timestamp))

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return registros