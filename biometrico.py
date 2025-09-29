from zk import ZK, const


def obtener_asistencias(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)
    registros = []

    try:
        conn = zk.connect()
        conn.disable_device()

        asistencias = conn.get_attendance()

        for asistencia in asistencias:
            registros.append((asistencia.user_id, asistencia.timestamp))

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return registros