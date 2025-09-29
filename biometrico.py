from zk import ZK, const

DEVICE_IP = '192.168.1.201'
DEVICE_PORT = 4370

def obtener_asistencias():

    zk = ZK(DEVICE_IP, DEVICE_PORT, timeout=5)
    registros = []

    try:
        conn = zk.connect()
        conn.disable_device()

        attendance = conn.get_attendance()
        if attendance:
            for record in attendance:
                registros.append(record.user_id, record.timestamp)

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return registros