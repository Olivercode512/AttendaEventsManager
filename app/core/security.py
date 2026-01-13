# app/core/security.py - Seguridad: hashing y verificación de contraseñas
import bcrypt

def hash_password(password: str) -> str:
    """
    Encripta una contraseña en texto plano usando bcrypt.
    Uso: al crear un usuario nuevo
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con la encriptada.
    Uso: al hacer login
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Ejemplo de uso (puedes borrar esto después)
if __name__ == "__main__":
    password = "1234"
    hashed = hash_password(password)
    print("Contraseña encriptada:", hashed)
    print("Verificación:", verify_password("1234", hashed))  # True
    print("Verificación mala:", verify_password("wrong", hashed))  # False