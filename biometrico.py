from zk import ZK, const
from datetime import datetime, timedelta, timezone
import ntplib


def get_ntp_time():
    """Intenta obtener la hora actual desde un servidor NTP (UTC)."""
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc)
    except Exception:
        return None


def obtener_asistencias(ip, puerto):

    zk = ZK(ip, puerto, force_udp=False,timeout=10)
    registros = []

    try:
        conn = zk.connect()
        conn.disable_device()

        asistencias = conn.get_attendance()

        #print(inspect.signature(conn.get_attendance))

        for asistencia in asistencias:
            registros.append((asistencia.uid, asistencia.user_id, asistencia.timestamp, asistencia.status, asistencia.punch))

    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    finally:
        conn.enable_device()
        conn.disconnect()
    return registros



def get_usuarios(ip, puerto):

    # shorter timeout and prefer UDP to avoid slow TCP checks
    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)
    usuarios = []

    try:
        conn = zk.connect()
        conn.disable_device()

        usuarios_bio = conn.get_users()

        for usuario in usuarios_bio:
            if usuario.name[:3] == "NN-":
                nombre = ""
            else:
                nombre = usuario.name
            usuarios.append((usuario.user_id, nombre, usuario.privilege, usuario.password, usuario.card))
            #print(usuario.uid,usuario.user_id)
    
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    finally:
        conn.enable_device()
        conn.disconnect()
    
    return usuarios

def set_time(ip, puerto):

    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)

    try:
        conn = zk.connect()
        conn.disable_device()
        #obtenemos hora de internet
        ahora = get_ntp_time()
        #ajustamos a hora de peru
        ahora_peru = ahora.astimezone(timezone(timedelta(hours=-5)))

        #debug
        #print("Hora obtenida de internet:", ahora_peru)
        #print("Hora local del sistema:", datetime.now())

        #si no se pudo obtener la hora de internet, usamos la hora local del sistema 
        if not ahora_peru:      
            ahora_peru = datetime.now()
        #seteamos la hora en el biometrico
        conn.set_time(ahora_peru)
        return True
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    finally:
        conn.enable_device()
        conn.disconnect()


def get_info(ip, puerto):

    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)

    try:
        conn = zk.connect()
        conn.disable_device()
        conn.read_sizes()
        info = {
            "nombre_dispositivo": conn.get_device_name(),
            "numero_de_serie": conn.get_serialnumber(),
            "firmware_version": conn.get_firmware_version(),
            "platforma": conn.get_platform(),
            "MAC": conn.get_mac(),
            "fecha_hora": conn.get_time(),
            "face_version": f"ZKFace VX{conn.get_face_version()}",
            "fp_version": f"ZKFinger VX{conn.get_fp_version()}",
            "cant_usuarios": conn.users,
            "cant_usuarios_max": conn.users_cap,
            "cant_huellas": conn.fingers,
            "cant_huellas_max": conn.fingers_cap,
            "cant_rostros": conn.faces,
            "cant_rostros_max": conn.faces_cap,
            "cant_asistencias": conn.records,
            "cant_asistencias_max": conn.rec_cap
        }
       
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    finally:
        conn.enable_device()
        conn.disconnect()
    
    return info

def eliminar_asistencias(ip, puerto):

    zk = ZK(ip, puerto, timeout=5)

    try:
        conn = zk.connect()
        conn.disable_device()

        conn.clear_attendance()
    except Exception as e:
        raise Exception(f"No se pudo conectar al biometrico: {e}")
    
    finally:
        conn.enable_device()
        conn.disconnect()
    
    return True

def delete_users(ip, puerto, users):
    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)

    try:
        conn = zk.connect()
        if not conn:
            return False
        
        # Verificar lista vacía
        if not users:
            conn.disconnect()
            return False
        
        conn.disable_device()
        # Aseguramos que sea tupla
        users = tuple(users)

        # Eliminamos cada usuario
        for user in users:
            conn.delete_user(user_id=user)
        return True

    except Exception as e:
        print(f"[Error delete_users] {e}")
        return False
    finally:
        conn.enable_device()
        conn.disconnect()

def set_usuario(ip, puerto, user):
    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)

    try:
        conn = zk.connect()
        if not conn:
            return False

        conn.disable_device()

        if not user:
            conn.enable_device()
            conn.disconnect()
            return False
    
        conn.set_user(**user)
        return True

    except Exception as e:
        print(f"error: {e}")
        return False
    
    finally:
        conn.enable_device()
        conn.disconnect()

def get_last_uid(ip, puerto):
    zk = ZK(ip, puerto, timeout=5, force_udp=False, ommit_ping=True)

    try:
        conn = zk.connect()
        if not conn:
            return False
        
        conn.disable_device()
        
        users = conn.get_users()
        uid = 0

        if not users:
            conn.enable_device()
            conn.disconnect()
            return False
        for user in users:
            uid = user.uid
        return int(uid)
    
    except Exception as e: 
        print(f"error: {e}")
        return False
    finally:
        conn.enable_device()
        conn.disconnect

