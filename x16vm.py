class Opu(object):
    def __init__(self, memory):
        self.memory = memory
        self.registers = dict(
            pa=0,
            a1=0,
            a2=0,
            a3=0,
            c1=0,
            f1=0,
        )

    def run(self):
        while True:
            pa = self.registers['pa']
            op = self.memory[pa]
            # set
            if op == 0:
                self.registers['pa'] += 3
                reg = self.memory[pa + 1]
                value = self.memory[pa + 2]
                self.set_registers(reg, value)
            # load
            elif op == 1:
                self.registers['pa'] += 4
                value1 = self.memory[pa + 1]
                value2 = self.memory[pa + 2]
                address = self.get_memory_u16(value1, value2)
                value = self.memory[address]
                reg = self.memory[pa + 3]
                self.set_registers(reg, value)
            # add
            elif op == 2:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                reg3 = self.memory[pa + 3]
                value = self.register(reg1) + self.register(reg2)
                low_value = self.set_memory_u16(value)[0]
                self.set_registers(reg3, low_value)
            # save
            elif op == 3:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                value1 = self.memory[pa + 2]
                value2 = self.memory[pa + 3]
                address = self.get_memory_u16(value1, value2)
                value = self.register(reg1)
                self.memory[address] = value
            # compare
            elif op == 4:
                self.registers['pa'] += 3
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                value1 = self.register(reg1)
                value2 = self.register(reg2)
                if value1 > value2:
                    self.registers['c1'] = 2
                elif value1 == value2:
                    self.registers['c1'] = 1
                else:
                    self.registers['c1'] = 0
            # jump_if_less
            elif op == 5:
                self.registers['pa'] += 3
                low_address = self.memory[pa + 1]
                high_address = self.memory[pa + 2]
                address = self.get_memory_u16(low_address, high_address)
                if self.registers['c1'] == 0:
                    self.registers['pa'] = address
            # jump
            elif op == 6:
                self.registers['pa'] += 3
                low_address = self.memory[pa + 1]
                high_address = self.memory[pa + 2]
                address = self.get_memory_u16(low_address, high_address)
                self.registers['pa'] = address
            # save_from_register
            elif op == 7:
                self.registers['pa'] += 3
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                value = self.register(reg1)
                address = self.register(reg2)
                low_value = self.set_memory_u16(value)[0]
                low_address = self.set_memory_u16(address)[0]
                self.memory[low_address] = low_value
            # set2
            elif op == 8:
                self.registers['pa'] += 4
                reg = self.memory[pa + 1]
                value1 = self.memory[pa + 2]
                value2 = self.memory[pa + 3]
                value = self.get_memory_u16(value1, value2)
                self.set_registers(reg, value)
            # load2
            elif op == 9:
                self.registers['pa'] += 4
                value1 = self.memory[pa + 1]
                value2 = self.memory[pa + 2]
                address = self.get_memory_u16(value1, value2)
                address1 = address + 1
                low = self.memory[address]
                high = self.memory[address1]
                value = self.get_memory_u16(low, high)
                reg = self.memory[pa + 3]
                self.set_registers(reg, value)
            # add2
            elif op == 10:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                reg3 = self.memory[pa + 3]
                value1 = self.register(reg1)
                value2 = self.register(reg2)
                value3 = value1 + value2
                self.set_registers(reg3, value3)
            # save2
            elif op == 11:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                value1 = self.memory[pa + 2]
                value2 = self.memory[pa + 3]
                address = self.get_memory_u16(value1, value2)
                address1 = address + 1
                value = self.register(reg1)
                low = self.set_memory_u16(value)[0]
                high = self.set_memory_u16(value)[1]
                self.memory[address] = low
                self.memory[address1] = high
            # subtract2
            elif op == 12:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                reg3 = self.memory[pa + 3]
                value1 = self.register(reg1)
                value2 = self.register(reg2)
                value3 = value1 - value2
                self.set_registers(reg3, value3)
            # load_from_register
            elif op == 13:
                self.registers['pa'] += 3
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                address = self.register(reg1)
                low_address = self.set_memory_u16(address)[0]
                value = self.register(reg2)
                low_value = self.set_memory_u16(value)[0]
                self.set_registers(low_address, low_value)
            # load_from_register2
            elif op == 14:
                self.registers['pa'] += 3
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                low_address = self.register(reg1)
                high_address = low_address + 1
                value1 = self.memory[low_address]
                value2 = self.memory[high_address]
                value = self.get_memory_u16(value1, value2)
                self.set_registers(reg2, value)
            # save_from_register2
            elif op == 15:
                self.registers['pa'] += 3
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                value = self.register(reg1)
                low_address = self.register(reg2)
                high_address = low_address + 1
                value1 = self.set_memory_u16(value)[0]
                value2 = self.set_memory_u16(value)[1]
                self.memory[low_address] = value1
                self.memory[high_address] = value2
            # jump_from_register
            elif op == 16:
                self.registers['pa'] += 2
                reg = self.memory[pa + 1]
                address = self.register(reg)
                self.registers['pa'] = address
            # shift_right
            elif op == 17:
                self.registers['pa'] += 2
                reg = self.memory[pa + 1]
                value1 = self.register(reg)
                if reg % 2 == 0:
                    value2 = value1 / 2
                else:
                    value2 = (value1 - 1) / 2
                self.set_registers(reg, int(value2))
            # and
            elif op == 19:
                self.registers['pa'] += 4
                reg1 = self.memory[pa + 1]
                reg2 = self.memory[pa + 2]
                reg3 = self.memory[pa + 3]
                value1 = bin(self.register(reg1))
                value2 = bin(self.register(reg2))
                l1 = len(value1)
                l2 = len(value2)
                length = min(l1, l2)
                i = length - 1
                j = l1 - 1
                k = l2 - 1
                result = ''
                while i >= 0:
                    if value1[j] == '1' and value2[k] == '1':
                        result = '1' + result
                    elif value1[j] == 'b' or value2[k] == 'b':
                        break
                    else:
                        result = '0' + result
                    i = i - 1
                    j = j - 1
                    k = k - 1
                value3 = int(result, 2)
                self.set_registers(reg3, value3)
            # halt
            elif op == 255:
                self.registers['pa'] += 1
                break

    def register(self, reg):
        if reg == 0:
            v = self.registers['pa']
        if reg == 16:
            v = self.registers['a1']
        if reg == 32:
            v = self.registers['a2']
        if reg == 48:
            v = self.registers['a3']
        if reg == 64:
            v = self.registers['c1']
        if reg == 80:
            v = self.registers['f1']
        return v

    def set_registers(self, reg, value):
        if reg == 0:
            self.registers['pa'] = value
        if reg == 16:
            self.registers['a1'] = value
        if reg == 32:
            self.registers['a2'] = value
        if reg == 48:
            self.registers['a3'] = value
        if reg == 64:
            self.registers['c1'] = value
        if reg == 80:
            self.registers['f1'] = value

    def get_memory_u16(self, value1, value2):
        low = value1
        high = value2
        value = (high << 8) + low
        return value

    def set_memory_u16(self, number: int):
        low = number & 0xFF
        high = (number >> 8) & 0xFF
        return low, high
