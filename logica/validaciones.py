def validar_datos(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    largo = datos["largo"]
    peralte = datos["peralte"]
    longitudBase = datos["longitudBase"]

    if alto < 3 or alto > 12:
        raise ValueError("El alto debe estar entre 3 y 12 metros.")
    if ancho < 6 or ancho > 50:
        raise ValueError("El ancho debe estar entre 6 y 50 metros.")
    if largo <= 0 or largo > 100 or largo % 6 != 0 or largo < ancho:
        raise ValueError("El largo debe estar entre 0 y 100 metros, ser múltiplo de 6 y mayor que el ancho.")
    if peralte <= alto or peralte > alto + 5:
        raise ValueError("El peralte debe ser mayor que el alto y no exceder en más de 5 metros al alto.")
    if longitudBase < ancho:
        raise ValueError("La longitud base del perfil HEB300 debe ser mayor o igual al ancho del galpón para poder construir los tirantes de las cerchas.")
