from zk import ZK, const
import inspect

def obtener_asistencias(ip, puerto):

    zk = ZK(ip, puerto, force_udp=False,timeout=5)
    registros = []

    try:
        conn = zk.connect()
        conn.disable_device()

        asistencias = conn.get_attendance()

        print(inspect.signature(conn.get_attendance))

        for asistencia in asistencias:
            registros.append((asistencia.user_id, asistencia.timestamp, asistencia.status, asistencia.punch, asistencia.uid))

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return registros


def obtener_usuarios(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)
    usuarios = []

    try:
        conn = zk.connect()
        conn.disable_device()

        usuarios_bio = conn.get_users()

        for usuario in usuarios_bio:
            usuarios.append((usuario.user_id, usuario.name))

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return usuarios

def set_time(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)

    try:
        conn = zk.connect()
        conn.disable_device()

        from datetime import datetime
        now = datetime.now()
        conn.set_time(now)

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return True

def get_info(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)

    try:
        conn = zk.connect()
        conn.disable_device()

        info = {
            "device_name": conn.get_device_name(),
            "serial_number": conn.get_serialnumber(),
            "firmware_version": conn.get_firmware_version(),
            "platform": conn.get_platform(),
            "mac": conn.get_mac()
        }

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return info

def eliminar_asistencias(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)

    try:
        conn = zk.connect()
        conn.disable_device()

        conn.clear_attendance()

        conn.enable_device()
        conn.disconnect()
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    return True