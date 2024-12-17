def validar_datos(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    largo = datos["largo"]
    peralte = datos["peralte"]
    longitudesBase = datos["longitudesBase"]

    # Validaciones para las medidas del galpón
    if alto < 3 or alto > 12:
        raise ValueError("El alto debe estar entre 3 y 12 metros.")
    if ancho < 6 or ancho > 50:
        raise ValueError("El ancho debe estar entre 6 y 50 metros.")
    if largo <= 0 or largo > 100 or largo < ancho:
        raise ValueError("El largo debe estar entre 0 y 100 metros y ser mayor que el ancho.")
    if peralte <= alto or peralte > alto + 5:
        raise ValueError("El peralte debe ser mayor que el alto y no exceder en más de 5 metros al alto.")

    # Validación de longitudes base
    if not longitudesBase:
        raise ValueError("Debe ingresar al menos una longitud base.")
    
    # Verificar que al menos una longitud base sea mayor o igual al ancho
    if not any(longitud >= ancho for longitud in longitudesBase):
        raise ValueError(f"Al menos una longitud base debe ser mayor o igual al ancho ({ancho} metros).")
    
    # Verificar que no haya valores vacíos o negativos en las longitudes base
    for longitud in longitudesBase:
        if longitud <= 0:
            raise ValueError("Las longitudes base deben ser mayores que cero.")
