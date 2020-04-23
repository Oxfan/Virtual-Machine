def order_mapper():
    o = dict(
        pa=0b00000000,  #0
        a1=0b00010000,  #16
        a2=0b00100000,  #32
        a3=0b00110000,  #48
        c1=0b01000000,  #64
        f1=0b01010000,  #80
    )
    return o


def is_number(s):
    number = '0123456789'
    n = 0
    for i in range(len(s)):
        if s[i] in number:
            n += 1
    return n == len(s)


def lines_split(lines):
    for i in range(len(lines)):
        if ';' in lines[i]:
            lines[i] = lines[i].split(';')[0]
    return lines


# 把数据分成高8位、低8位
def apart_data(data):
    low = data & 0xff
    high = data >> 8 & 0xff
    return low, high


# 从高低8位恢复成完整数据
def restore_data(low, high):
    data = low + (high << 8)
    return data


# 伪代码转换
def change_call_return(asm):
    c = """
        set2 a3 14
        add2 pa a3 a3
        save_from_register2 a3 f1
        set2 a3 2
        add2 f1 a3 f1
        """
    r = """
        set2 a3 2
        add2 a2 a3 a3
        subtract2 f1 a3 f1
        load_from_register2 f1 a2
        jump_from_register a2
        """
    length = len(asm)
    i = 0
    n = 0
    while i < length:
        if asm[i:i + 5] == '.call':
            function = ''
            for k in range(len(asm[i + 6:])):
                if asm[i + 6:][k] == ' ':
                    function = asm[i + 6: i + 6 + k + 1]
                    n = k
                    k = len(asm[i + 6:])
                    break
            asm = asm[0:i] + c + 'jump ' + function + asm[i + 6:][n + 1:]
        if asm[i:i + 7] == '.return':
            number = 0
            for k in range(len(asm[i + 8:])):
                if not is_number(asm[i + 8:][k]):
                    number = asm[i + 8:i + 8 + k + 1]
                    n = k
                    k = len(asm[i + 8:])
                    break
            asm = asm[0:i] + 'set2 a2 ' + number + r + asm[i + 8:][n + 1:]
        length = len(asm)
        i = i + 1
    return asm


def machine_code(asm):
    asm = change_call_return(asm)
    order = order_mapper()
    result = []
    lines = asm.split('\n')
    lines = lines_split(lines)
    code_address = {}
    offset = 0
    for i in range(len(lines)):
        line = lines[i]
        code = line.split()
        if line.strip() == '':
            continue
        c = code[0]
        if c == 'set':
            offset += 3
            result.append(0)
            result.append(order[code[1]])
            low = apart_data(int(code[2]))[0]
            result.append(low)
        elif c == 'load':
            offset += 4
            result.append(1)
            low = apart_data(int(code[1][1:]))[0]
            high = apart_data(int(code[1][1:]))[1]
            result.append(low)
            result.append(high)
            result.append(order[code[2]])
        elif c == 'add':
            offset += 4
            result.append(2)
            result.append(order[code[1]])
            result.append(order[code[2]])
            result.append(order[code[3]])
        elif c == 'save':
            offset += 4
            result.append(3)
            result.append(order[code[1]])
            low = apart_data(int(code[2][1:]))[0]
            high = apart_data(int(code[2][1:]))[1]
            result.append(low)
            result.append(high)
        elif c == 'compare':
            offset += 3
            result.append(4)
            result.append(order[code[1]])
            result.append(order[code[2]])
        elif c == 'jump_if_less':
            offset += 3
            result.append(5)
            result.append(code[1][1:])
        elif c == 'jump':
            offset += 3
            result.append(6)
            result.append(code[1][1:])
        elif c == '.memory':
            number = int(code[1]) - 3
            offset += number
            i = 0
            while i < number:
                result.append(0)
                i = i + 1
        elif c == 'save_from_register':
            offset += 3
            result.append(7)
            result.append(order[code[1]])
            result.append(order[code[2]])
        elif c == 'set2':
            offset += 4
            result.append(8)
            result.append(order[code[1]])
            low = apart_data(int(code[2]))[0]
            high = apart_data(int(code[2]))[1]
            result.append(low)
            result.append(high)
        elif c == 'load2':
            offset += 4
            result.append(9)
            low = apart_data(int(code[1][1:]))[0]
            high = apart_data(int(code[1][1:]))[1]
            result.append(low)
            result.append(high)
            result.append(order[code[2]])
        elif c == 'add2':
            offset += 4
            result.append(10)
            result.append(order[code[1]])
            result.append(order[code[2]])
            result.append(order[code[3]])
        elif c == 'save2':
            offset += 4
            result.append(11)
            result.append(order[code[1]])
            low = apart_data(int(code[2][1:]))[0]
            high = apart_data(int(code[2][1:]))[1]
            result.append(low)
            result.append(high)
        elif c == 'subtract2':
            offset += 4
            result.append(12)
            result.append(order[code[1]])
            result.append(order[code[2]])
            result.append(order[code[3]])
        elif c == 'load_from_register':
            offset += 3
            result.append(13)
            result.append(order[code[1]])
            result.append(order[code[2]])
        elif c == 'load_from_register2':
            offset += 3
            result.append(14)
            result.append(order[code[1]])
            result.append(order[code[2]])
        elif c == 'save_from_register2':
            offset += 3
            result.append(15)
            result.append(order[code[1]])
            result.append(order[code[2]])
        elif c == 'jump_from_register':
            offset += 2
            result.append(16)
            result.append(order[code[1]])
        elif c == 'shift_right':
            offset += 2
            result.append(17)
            result.append(order[code[1]])
        elif c == 'and':
            offset += 4
            result.append(19)
            result.append(order[code[1]])
            result.append(order[code[2]])
            result.append(order[code[3]])
        elif c == 'halt':
            offset += 1
            result.append(255)
        elif c[0] == '@':
            code_address[c[1:]] = offset
    length = len(result)
    i = 0
    while i < length:
        r = result[i]
        if isinstance(r, str):
            if is_number(r):
                r = int(r)
                low = apart_data(r)[0]
                high = apart_data(r)[1]
                result[i] = low
                result = result[0:i + 1] + [high] + result[i + 1:]
                length += 1
            else:
                address = code_address[r]
                low = apart_data(address)[0]
                high = apart_data(address)[1]
                result[i] = low
                result = result[0:i + 1] + [high] + result[i + 1:]
                length += 1
        i = i + 1
    return result
