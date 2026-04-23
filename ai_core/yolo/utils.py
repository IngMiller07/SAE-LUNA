historial = []

def suavizar(estado):
    historial.append(estado)

    if len(historial) > 10:
        historial.pop(0)

    return max(set(historial), key=historial.count)