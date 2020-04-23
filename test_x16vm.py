from x16asm import machine_code
from x16vm import Opu


def log(*args, **kwargs):
    print(*args, **kwargs)


def ensure(condition, message):
    if not condition:
        log('*** 测试失败:', message)
    else:
        log('*** 测试成功')


def test_function_multiply():
    asm = """
        jump @1024
        .memory 1024
        set2 f1 3
        jump @function_end

        @function_multiply ; 1031
        set2 a3 2
        save_from_register2 a1 f1 ; a1 入栈
        add2 a3 f1 f1
        save_from_register2 a2 f1 ; a2 入栈
        add2 a3 f1 f1
        set2 a3 2

        @while_start ;
        set2 a2 2
        subtract2 f1 a2 a2
        load_from_register2 a2 a2
        compare a2 a3 ;
        jump_if_less @while_end ; 一旦 a2 小于 a3，就结束循环
        set2 a2 1
        add2 a3 a2 a3           ; a3 + 1

        set2 a2 4
        subtract2 f1 a2 a2
        load_from_register2 a2 a2
        add2 a1 a2 a1           ; 累加结果

        jump @while_start
        @while_end ;72
        .return 4
        @function_end

        set2 a1 5
        set2 a2 100
        .call @function_multiply
        halt
    """
    code = machine_code(asm)
    memory = code + [0] * (2 ** 16 - len(code))
    cpu = Opu(memory)
    cpu.run()
    output = [
        cpu.registers["a1"],
    ]
    print("output", output)
    expected = [
        500,
    ]
    ensure(expected == output, 'test_function_multiply')
    assert expected == output


def test_factorial():
    asm = """
        jump @1024
        .memory 1024
        set2 f1 3
        jump @function_end
        ;
        ;
        @function_multiply
        set2 a3 2 ; 因为下面用 a2 < a3 做判断，所以 a3 从 2 开始
        save2 a1 @65534
        @while_start ; 循环开始
        compare a2 a3 ;
        jump_if_less @while_end ; 一旦 a2 小于 a3，就结束循环
        save2 a2 @65532
        set2 a2 1
        add2 a3 a2 a3
        load2 @65534 a2
        add2 a1 a2 a1
        load2 @65532 a2
        jump @while_start
        @while_end
        set2 a3 2
        subtract2 f1 a3 f1
        load_from_register2 f1 a2
        jump_from_register a2
        ;
        ;
        @factorial
        ; 存 a1 f1 += 2
        save_from_register2 a1 f1
        set2 a3 2
        add2 f1 a3 f1

        ; if n < 2
        set2 a2 2
        compare a1 a2
        jump_if_less @factorial_return

        ; n - 1
        set2 a2 1
        subtract2 a1 a2 a1

        ; 递归
        .call @factorial

        ; 取出上次暂存的 a1 放入 a2
        set2 a3 2
        subtract2 f1 a3 f1
        load_from_register2 f1 a2
        .call @function_multiply
        .return 0

        ; 返回 1
        @factorial_return
        set2 a1 1
        .return 2
        ;
        ;
        @function_end
        set2 a1 4
        .call @factorial
        halt
    """
    code = machine_code(asm)
    memory = code + [0] * (2 ** 16 - len(code))
    cpu = Opu(memory)
    cpu.run()
    output = [
        cpu.registers["a1"],
    ]
    expected = [
        24,
    ]
    ensure(expected == output, 'test_factorial')
    assert output == expected, output


def test_shift_right():
    asm = """
        set a1 20
        shift_right a1
        halt
    """
    code = machine_code(asm)
    memory = code + [0] * (2 ** 16 - len(code))
    cpu = Opu(memory)
    cpu.run()
    expected = [
        10,
    ]
    output = [
        cpu.registers["a1"],
    ]

    print("register", cpu.registers)
    assert expected == output


def test_and():
    asm = """
        set a1 31
        set a2 12
        and a1 a2 a3
        halt
    """
    code = machine_code(asm)
    memory = code + [0] * (2 ** 16 - len(code))
    cpu = Opu(memory)
    cpu.run()
    expected = [
        31,
        12,
        12,
    ]
    output = [
        cpu.registers["a1"],
        cpu.registers["a2"],
        cpu.registers["a3"],
    ]
    print("register", cpu.registers)
    assert expected == output


def test05():
    """
   以下汇编函数相当于在做这个事情
    a = 1
    b = 2
    c = 6
    d = 9
    e = d - c - b -a
    """
    asm = """
        jump @33795
        .memory 33795
        set2 f1 32772 ;栈内存
        set2 a3 2;
        add2 f1 a3 f1;为显存留一个地方

        set2 a1 1 ; a=1
        save_from_register2 a1 f1; a入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        set2 a1 2 ; b=2
        save_from_register2 a1 f1; b入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        set2 a1 6 ; c=6
        save_from_register2 a1 f1; c入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        set2 a1 9 ; d=9
        save_from_register2 a1 f1; d入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        .call @bin_add
        halt

        ; a1， a2 承受局部变量
        ; a1 保存最后的结果
        ; a3 工具
        @bin_add
        set2 a3 4
        subtract2 f1 a3 a3 ;d出栈
        load_from_register2 a3 a1

        set2 a3 10
        subtract2 f1 a3 a3 ;a出栈
        load_from_register2 a3 a2

        subtract2 a1 a2 a1 ; e = d - a

        set2 a3 8
        subtract2 f1 a3 a3 ;b出栈
        load_from_register2 a3 a2

        subtract2 a1 a2 a1 ; e = d - a - b

        set2 a3 6
        subtract2 f1 a3 a3 ;c出栈
        load_from_register2 a3 a2

        subtract2 a1 a2 a1 ; e = d - a - b - c
        halt
        .return 0

    """
    memory = machine_code(asm)
    memory = memory + [0] * (2 ** 16 - len(memory))
    cpu = Opu(memory)
    cpu.run()
    output = cpu.registers['a1']
    expected = 0
    print('output', output)
    assert output == expected, output


def test06():
    asm = """
        jump @33795
        .memory 33795
        set2 f1 32772 ;栈内存

        set2 a3 3 ; 显存地址
        save_from_register2 a3 f1; 显存地址入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        set2 a1 5 ; x=5
        save_from_register2 a1 f1; x入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        set2 a1 5 ; y=5
        save_from_register2 a1 f1; y入栈
        set2 a3 2
        add2 f1 a3 f1 ;f1+2

        .call @function_draw_point
        halt

        ; a1， a2 承受局部变量
        ; a1 保存最后的结果
        ; a3 工具
        @function_draw_point
        set2 a3 32772
        load_from_register2 a3 a1 ;显存地址出栈

        set2 a3 6
        subtract2 f1 a3 a3 ;x出栈
        load_from_register2 a3 a2 ;a2 = 5

        save_from_register2 a2 a1 ; 把x保存到当前的显存地址([3]=5)

        set2 a3 2
        add2 a3 a1 a2 ; 显存地址+2(3+2=5)

        set2 a3 32772
        save_from_register2 a2 a3 ;显存地址存到栈内存里面


        set2 a3 32772
        load_from_register2 a3 a1 ;显存地址出栈

        set2 a3 4
        subtract2 f1 a3 a3 ;y出栈
        load_from_register2 a3 a2

        save_from_register2 a2 a1 ; 把y保存到当前的显存地址(5)

        set2 a3 2
        add2 a3 a2 a2 ; 显存地址+2(5+2)
        ;我要如何把加完以后的显存地址存到f1里面去呢
        set2 a3 32772
        save_from_register2 a2 a3 ;显存地址存到栈内存里面


        set2 a3 32772
        load_from_register2 a3 a2 ;显存地址出栈

        set2 a1 255
        save_from_register a1 a2

        set2 a3 2
        add2 a3 a2 a2 ; 显存地址+2(7+2)
        set2 a3 32772
        save_from_register2 a2 a3 ;显存地址存到栈内存里面

        .return 0
    """
    memory = machine_code(asm)
    memory = memory + [0] * (2 ** 16 - len(memory))
    cpu = Opu(memory)
    cpu.run()
    output = cpu.memory[3:9]
    expected = [5, 0, 5, 0, 255, 0]
    print("32772", cpu.memory[32772])
    assert output == expected, output


def main():
    test_function_multiply()
    test_factorial()
    test_shift_right()
    test_and()
    test05()
    test06()


if __name__ == '__main__':
    main()
