from random import choice
from xml.dom import minidom

def parse_svg(svg_string):
    doc = minidom.parseString(svg_string)

    # position color: array of point-color pairs
    position_color = []

    for path in doc.getElementsByTagName('path'):
        instructions = path.getAttribute('d')
        instruction_stack = instructions.split(' ')
        path_color = choice([[7,0,0], [0,7,0], [0,0,7]])

        for i, detail in enumerate(instruction_stack):
            if i == 0 and detail in 'Mm':
                mode = 'move'
            elif detail == 'L':
                mode = 'location'
            elif detail == 'l':
                mode = 'location_relative'
            elif detail == 'H':
                mode = 'horizontal'
            elif detail == 'h':
                mode = 'horizontal_relative'
            elif detail == 'V':
                mode = 'vertical'
            elif detail == 'v':
                mode = 'vertical_relative'
            elif detail in 'zZ':
                position_color.append([position_color[1][0],[0,0,0]])
            else:
                match mode:
                    case 'move':
                        position_color.append([[0,0], [0,0,0]])
                        pair = []
                        xy = []
                        for s in detail.split(','):
                            xy.append(int(float(s)))
                        pair.append(xy)
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'location':
                        pair = []
                        xy = []
                        for s in detail.split(','):
                            xy.append(int(float(s)))
                        pair.append(xy)
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'location_relative':
                        pair = []
                        xy = []
                        x, y = detail.split(',')
                        xy = [float(int(x)) + position_color[-1][0][0], float(int(y)) + position_color[-1][0][1]]
                        pair.append(xy)
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'horizontal':
                        pair = [[int(float(detail)), position_color[-1][0][1]]]
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'horizontal_relative':
                        pair = [[int(float(detail)) + position_color[-1][0][0], position_color[-1][0][1]]]
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'vertical':
                        pair = [[position_color[-1][0][0], int(float(detail))]]
                        pair.append(path_color)
                        position_color.append(pair)
                    case 'vertical_relative':
                        pair = [[position_color[-1][0][0], position_color[-1][0][1] + int(float(detail))]]
                        pair.append(path_color)
                        position_color.append(pair) 
        else:
            position_color[-1][1] = [0,0,0]    
    doc.unlink()
    return position_color

def get_bin_offset(hex):
    if hex == 0:
        return 0
    else:
        offset = 0
        while hex & 1 == 0:
            offset += 1
            hex >>= 1
        return offset

def packetify(packet_info):
    bits = [0xFF800000,0x007FC000,0x00003800,0x00000700,0x000000E0,0x00000001]
    components = [(packet << get_bin_offset(mask)) & mask for packet, mask in zip(packet_info, bits)]
    sum = 0
    for comp in components:
        sum ^= comp

    return sum

def get_parsed(svg_string):
    parsed = parse_svg(svg_string)

    return '\n'.join(['{:08X}'.format(packetify(pos + color)) for pos, color in parsed])

