def type_of_inst(key):
    INSTRUCTION_TYPES = {
    # R-Type Instructions
    "add": "R", "sub": "R", "mul": "R", "and": "R", "or": "R", "xor": "R", "sll": "R", "slt": "R",

    # I-Type Instructions (ALU and Load)
    "addi": "I", "slti": "I", "sltiu": "I", "xori": "I", "ori": "I", "andi": "I",
    "slli": "I", "srli": "I", "srai": "I",
    "lw": "I", "jalr": "I",

    # S-Type Instructions
    "sw": "S", "sh": "S", "sb": "S",

    # B-Type Instructions
    "beq": "B", "bne": "B", "blt": "B", "bge": "B",

    # U-Type Instructions
    "lui": "U", "auipc": "U",

    # J-Type Instructions
    "jal": "J"
    }
    return INSTRUCTION_TYPES.get(key.strip().lower())

def registor_binary(key):
    REGISTERS = {
    "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100", 
    "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "fp": "01000", "s1": "01001", 
    "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110", "a5": "01111", 
    "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011", "s4": "10100", "s5": "10101", 
    "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011", 
    "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"
    }
    return REGISTERS.get(key.strip().lower(),'imm')

def function_f3(operation):
    FUNCT3 = {
    # R-Type
    "add":  "000", "sub":  "000",
    "sll":  "001", "slt":  "010", "sltu": "011",
    "xor":  "100", "srl":  "101", "sra":  "101",
    "or":   "110", "and":  "111",

    # I-Type
    "addi": "000", "slti": "010", "sltiu": "011",
    "xori": "100", "ori": "110", "andi": "111",
    "slli": "001", "srli": "101", "srai": "101",
    "lw":   "010", "jalr": "000",

    # S-Type
    "sw":   "010", "sh": "001", "sb": "000",

    # B-Type
    "beq":  "000", "bne": "001",
    "blt":  "100", "bge": "101",
    "bltu": "110", "bgeu": "111"
    }

    return FUNCT3.get(operation,'imm')

def op_code(operation):
    INSTRUCTIONS = {
    # R-Type Instructions (opcode = 0110011)
    "add":  "0110011", "sub":  "0110011",
    "sll":  "0110011", "slt":  "0110011", "sltu": "0110011",
    "xor":  "0110011", "srl":  "0110011", "sra":  "0110011",
    "or":   "0110011", "and":  "0110011",

    # I-Type Instructions (opcode = 0010011 for ALU, 0000011 for Load, 1100111 for JALR)
    "addi": "0010011", "slti": "0010011", "sltiu": "0010011",
    "xori": "0010011", "ori": "0010011", "andi": "0010011",
    "slli": "0010011", "srli": "0010011", "srai": "0010011",
    "lw":   "0000011", "jalr": "1100111",

    # S-Type Instructions (opcode = 0100011)
    "sw":   "0100011", "sh": "0100011", "sb": "0100011",

    # B-Type Instructions (opcode = 1100011)
    "beq":  "1100011", "bne": "1100011",
    "blt":  "1100011", "bge": "1100011",
    "bltu": "1100011", "bgeu": "1100011",

    # U-Type Instructions (opcode = 0110111 for LUI, 0010111 for AUIPC)
    "lui":  "0110111", "auipc": "0010111",

    # J-Type Instructions (opcode = 1101111)
    "jal":  "1101111"
    }


    return INSTRUCTIONS.get(operation.strip().lower())

def convert_to_binary(num):
    if num == 0:
        return "0"
    
    binary = ""
    while num > 0:
        binary = str(num % 2) + binary  
        num //= 2
    
    binary = str(binary)
    while (len(binary)<5):
        binary = '0' + binary

    return binary

def to_twos_complement(num, k): # take integer input 
    
    if num < 0:
        # Compute two's complement for negative numbers
        num = (1 << k) + num  
    else:
        # Ensure number fits within k bits
        num = num & ((1 << k) - 1)  

    # Convert to binary and pad with zeros
    return format(num, f'0{k}b')

def hex_to_binary(hex_num): # take string input 
    # Convert hex to integer
    num = int(hex_num, 16)
    
    # Convert to binary and remove '0b' prefix
    return bin(num)[2:]

filename = input()
with open(filename) as f:
    lst = f.readlines()
    for sentence in lst:
        instruction = sentence.replace('\n','')
        a = instruction.replace(', ',',').split(' ')
        oprtn = a[0].strip().lower()
        b = a[1].split(',')

        opcode = op_code(oprtn)

        if type_of_inst(key=oprtn) == 'R' :
            f3 = function_f3(oprtn)
            f7 = '0100000' if oprtn == 'sub' else '0000000'
            rd = registor_binary(b[0])
            rs1 = registor_binary(b[1]) if registor_binary(b[1])!='imm' else to_twos_complement(b[1],5)
            rs2 = registor_binary(b[2]) if registor_binary(b[2])!='imm' else to_twos_complement(b[2],5)
            binary_inst = f7 + ' ' + rs2 + ' ' + rs1 + ' ' + f3 + ' ' + rd + ' ' + opcode
            print(binary_inst)

        elif type_of_inst(key=oprtn) == 'J':

            rd = registor_binary(b[0])
            if '0x' in b[1]:
                imm = hex_to_binary(b[1])
                imm = (20-len(imm))*'0' + imm

            else :
                imm = to_twos_complement(int(b[1]),20)
            binary_inst = imm[0] + ' ' + imm[10:20] + ' ' + imm[9] + ' ' + imm[1:9] +' '+rd+' '+opcode
            print(binary_inst)

        elif type_of_inst(key=oprtn) =='I':
            f3 = function_f3(oprtn)
            rd = registor_binary(b[0])
            if len(b)==3:
                rs1 = registor_binary(b[1])
                if '0x' in b[2]:
                    imm = hex_to_binary(b[2])
                    imm = (12-len(imm))*'0' + imm
                else :
                    imm = to_twos_complement(int(b[2]),12)
            else :
                if '[' in b[1]:
                    c = b[1].replace(']','').split('[')
                elif '(' in b[1]:
                    c = b[1].replace(')','').split('(')

                rs1 = registor_binary(c[1])
                imm = to_twos_complement(int(c[0]),12)

            binary_inst = imm + ' ' + rs1 + ' ' + f3 + ' ' + rd + ' ' + opcode
            print(binary_inst)
