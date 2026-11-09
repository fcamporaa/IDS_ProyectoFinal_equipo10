"""Validaciones genéricas de texto de URL y formularios, compartidas por todos los módulos del front."""
def validar_entero_positivo(valor: str, etiqueta: str) -> int:
    """Convierte a int un texto de URL o formulario; lanza ValueError si no es un entero positivo."""
    valor = valor.strip()
    # isascii() evita dígitos como "²": isdigit() los acepta pero int() falla con ellos
    if not valor.isascii() or not valor.isdigit() or int(valor) <= 0:
        raise ValueError(f"El campo '{etiqueta}' debe ser un número válido.")
    return int(valor)


def validar_texto_maximo(valor: str, etiqueta: str, largo_max: int) -> str:
    """Devuelve el texto sin espacios sobrantes; lanza ValueError si supera largo_max caracteres."""
    valor = valor.strip()
    if len(valor) > largo_max:
        raise ValueError(f"El campo '{etiqueta}' no puede superar los {largo_max} caracteres.")
    return valor
