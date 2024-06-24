import serial

def hex_dec(T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = 18000  # 1800C is max, use as threshold to check that the hex is neg
        hex_max = 0xFFFF  # FFFF max
        if T_val > T_max:
            T = -(hex_max - T_val + 1) / 10  # handling negative value                                                      
        else:
            T = T_val / 10
        return T

    except ValueError:
        return 'err'


def parse_temp(response):
    response_hex = response.hex()
    temperatures = []
    for i in range(8):
        hex_str = response_hex[34+i*4:36+i*4] + response_hex[32+i*4:34+i*4]
        temperatures.append(hex_dec(hex_str))
    return tuple(temperatures)
