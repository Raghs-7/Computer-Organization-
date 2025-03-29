import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

pc_map = {}

with open(input_file) as f:
    lst = [x.strip() for x in f.readlines()]
    for i in range(len(lst)):
        pc_map[i * 4] = lst[i]  


registers = [0] * 32  
memory = {}  
pc = 0  

def get_bits(instruction, start, end):
    temp = int(instruction, 2)  
    extracted = (temp >> end) & ((1 << (start - end + 1)) - 1)  
    return format(extracted, f'0{start - end + 1}b')  

def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def to_32bit_binary(value):
    if value >= 0:
        return "0b"+format(value, '032b')  
    else:
        return "0b"+format((1 << 32) + value, '032b')  

def decode_r_instruction(funct7, funct3):
    r_instructions = {
        ("0000000", "000"): "ADD",
        ("0100000", "000"): "SUB",
        ("0000000", "111"): "AND",
        ("0000000", "110"): "OR",  
        ("0000000", "101"): "SRL",    
        ("0000000", "010"): "SLT",  
    }
    return r_instructions.get((funct7, funct3), "UNKNOWN INSTRUCTION")

def extract_b_type_imm(instruction):
    imm_12 = get_bits(instruction, 31, 31)  
    imm_10_5 = get_bits(instruction, 30, 25)  
    imm_4_1 = get_bits(instruction, 11, 8)  
    imm_11 = get_bits(instruction, 7, 7)  

    imm_binary = imm_12 + imm_11 + imm_10_5 + imm_4_1 + "0"  
    imm = sign_extend(int(imm_binary, 2), 13)
    return imm

def extract_j_type_imm(instruction):
    imm_20 = get_bits(instruction, 31, 31)  
    imm_10_1 = get_bits(instruction, 30, 21)  
    imm_11 = get_bits(instruction, 20, 20)  
    imm_19_12 = get_bits(instruction, 19, 12)  

    imm_binary = imm_20 + imm_19_12 + imm_11 + imm_10_1 + "0"  
    imm = sign_extend(int(imm_binary, 2), 21)
    return imm

def execute_instruction(instruction, output_file):
    global pc

    try:
        rd = int(get_bits(instruction, 11, 7), 2)
        rs1 = int(get_bits(instruction, 19, 15), 2)
        rs2 = int(get_bits(instruction, 24, 20), 2)
        funct3 = get_bits(instruction, 14, 12)
        funct7 = get_bits(instruction, 31, 25)
        opcode = get_bits(instruction, 6, 0)

        # R-type Instructions
        if opcode == "0110011":
            operation = decode_r_instruction(funct7, funct3)
            if operation == "ADD":
                registers[rd] = registers[rs1] + registers[rs2]
            elif operation == "SUB":
                registers[rd] = registers[rs1] - registers[rs2]
            elif operation == "AND":
                registers[rd] = registers[rs1] & registers[rs2]
            elif operation == "OR":
                registers[rd] = registers[rs1] | registers[rs2]  
            elif operation == "SRL":
                registers[rd] = registers[rs1] >> (registers[rs2] & 0x1F)
            elif operation == "SLT":
                registers[rd] = int(registers[rs1] < registers[rs2])
            else:
                print("Unkown operation at pc =",pc)

            if rd == 0:  
                registers[0] = 0  
            pc += 4
            binary_registers = [to_32bit_binary(reg) for reg in registers]
            output_file.write(f"{to_32bit_binary(pc)} {' '.join(binary_registers)}\n")

        # I-type Instructions 
        elif opcode in ["0010011", "0000011", "1100111"]:
            imm = sign_extend(int(get_bits(instruction, 31, 20), 2), 12)
            if opcode == "0010011":  # ADDI
                registers[rd] = registers[rs1] + imm
                pc += 4
            elif opcode == "0000011":  # LW
                address = registers[rs1] + imm
                registers[rd] = memory.get(address, 0)
                pc += 4
            elif opcode == "1100111":  # JALR
                temp = pc + 4
                pc = (registers[rs1] + imm) & ~1
                registers[rd] = temp
            if rd == 0:
                registers[0] = 0
            binary_registers = [to_32bit_binary(reg) for reg in registers]
            output_file.write(f"{to_32bit_binary(pc)} {' '.join(binary_registers)}\n")

        # S-type 
        elif opcode == "0100011":
            imm = sign_extend(int(get_bits(instruction, 31, 25) + get_bits(instruction, 11, 7), 2), 12)
            if funct3 == "010":  # SW
                address = registers[rs1] + imm
                memory[address] = registers[rs2]
            pc += 4
            binary_registers = [to_32bit_binary(reg) for reg in registers]
            output_file.write(f"{to_32bit_binary(pc)} {' '.join(binary_registers)}\n")

        # B-type (BEQ, BNE)
        elif opcode == "1100011":
            imm = extract_b_type_imm(instruction)  
            should_branch = (registers[rs1] == registers[rs2]) if funct3 == "000" else (registers[rs1] != registers[rs2])
            pc = pc + imm if should_branch else pc + 4
            binary_registers = [to_32bit_binary(reg) for reg in registers]
            output_file.write(f"{to_32bit_binary(pc)} {' '.join(binary_registers)}\n")


        elif opcode == "1101111":  # JAL
            imm = extract_j_type_imm(instruction)  
            if rd != 0:  
                registers[rd] = pc + 4
            registers[0] = 0  
            pc += imm  

            binary_registers = [to_32bit_binary(reg) for reg in registers]
            output_file.write(f"{to_32bit_binary(pc)} {' '.join(binary_registers)}\n")
            

    except Exception as e:
        print(f"Exception at PC={pc}: {str(e)}\n")
        output_file.write(f"Exception at PC={pc}: {str(e)}\n")

def simulate_riscv(output_filename):
    global pc, registers, memory

    pc = 0
    registers = [0] * 32
    registers[2] = 380
    memory = {}

    with open(output_filename, 'w') as output_file:
        while pc < len(pc_map)*4:
            try:
                instruction = pc_map[pc].strip()
            except:
                print("error at pc =",pc)
                break
            # print("executing instruction in",instruction,"at pc =",pc)
            execute_instruction(instruction, output_file)

            opcode = get_bits(instruction, 6, 0)

            if opcode == "1101111":  # J-type 
                imm = sign_extend(int(get_bits(instruction, 31, 31) + get_bits(instruction, 19, 12) + get_bits(instruction, 20, 20) + get_bits(instruction, 30, 21), 2), 21)
                if imm == 0:
                    break

            if opcode == "1100011":  # B-type 
                imm = sign_extend(int(get_bits(instruction, 31, 31) + get_bits(instruction, 7, 7) + get_bits(instruction, 30, 25) + get_bits(instruction, 11, 8), 2), 13)
                if imm == 0:
                    break
            
            # print(registers)

        base_addr = 0x00010000
        for i in range(32): 
            addr = base_addr + (i * 4)
            value = memory.get(addr, 0)
            binary_value = to_32bit_binary(value)
            val = f"{addr:08x}"
            output_file.write(f"0x{val.upper()}:{binary_value}\n")

simulate_riscv(output_file)