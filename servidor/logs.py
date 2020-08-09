def logs(id_, user, id_type, detail):
    template = '{:^4} | {:^12} | {:^40} | {:^20} |'
    table = [id_, user]
    if id_type == 99:
        table.append("Acción")
        table.append("Descripción")
    elif id_type == 98:
        print(template.replace(':', ':-').format('', '', '', ''))
        return
    elif id_type == 1:
        table.append("Conexión de cliente")
        table.append("")
    elif id_type == 2:
        table.append("Desconexión de cliente")
        table.append("")
    elif id_type == 3:
        table.append("Solicitud de ingreso")
        table.append(f"Aceptada")
        if not detail:
            table[3] = "Rechazada"
    elif id_type == 4:
        table.append("Salida de sala de espera")
        table.append("")
    elif id_type == 5:
        table.append("Salida del juego")
        table.append("")
    elif id_type == 6:
        table.append("Sacar Carta")
        table.append(f"")
    elif id_type == 7:
        table.append("Enviar Carta")
        table.append(f"{detail[0]} {detail[1]}")
    elif id_type == 8:
        table.append("Enviar Reverso Carta")
        table.append(f"")
    elif id_type == 9:
        table.append("Jugar Carta")
        table.append(f"{detail['tipo']} {detail['color']}")
    elif id_type == 10:
        table.append("Elección de color")
        table.append(f"{detail['color']}")
    elif id_type == 11:
        table.append("Grito DDCuatro")
        table.append(f"")
    elif id_type == 12:
        table.append("Sacar carta por grito")
        table.append("")
    elif id_type == 13:
        table.append(f"Enviar json tipo: {detail[0].replace('_', ' ')}")
        table.append(detail[1])
    print(template.format(*table))