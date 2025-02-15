R = ['add', 'sub', 'and', 'or', 'srl', 'slt']
S = ['sw']
B = ['beq', 'bne']
J = ['jal']
I = ['addi', 'jalr', 'lw']  

REGISTERS = {
    "zero": "00000", "ra": "00001", "sp": "00010",
    "gp": "00011", "tp": "00100", "t0": "00101",
    "t1": "00110", "t2": "00111", "s0": "01000",
    "s1": "01001", "a0": "01010", "a1": "01011",
    "a2": "01100", "a3": "01101", "a4": "01110",
    "a5": "01111", "a6": "10000", "a7": "10001",
    "s2": "10010", "s3": "10011",
    "s4": "10100", "s5": "10101", "s6": "10110",
    "s7": "10111", "s8": "11000", "s9": "11001",
    "s10": "11010", "s11": "11011", "t3": "11100",
    "t4": "11101", "t5": "11110", "t6": "11111"
}

OPCODES = {
    "add": "0110011", "sub": "0110011", "slt": "0110011",
    "srl": "0110011", "or": "0110011", "and": "0110011",
    "addi": "0010011", "lw": "0000011", "sw": "0100011",
    "beq": "1100011", "bne": "1100011", "jal": "1101111",
    "jalr": "1100111"
}

FUNCT3 = {
    "add": "000", "sub": "000", "slt": "010",
    "srl": "101", "or": "110", "and": "111",
    "addi": "000", "lw": "010", "sw": "010",
    "beq": "000", "bne": "001", "jalr": "000",
    "jal": "000"
}

def INSTRUCTIONTYPE(string):
    a = string.split()[0]
    if a in R:
        return 'R'
    elif a in S:
        return 'S'
    elif a in I:
        return 'I'
    elif a in B:
        return 'B'
    elif a in J:
        return 'J'
    else:
        return 'Unknown'

def TWOCOMPLEMENT(value, bits):
    if value < 0:
        value = (1 << bits) + value
    return format(value, f'0{bits}b')

def SType(string):
    parts = string.split()
    if len(parts) != 2:
        return "Error: Incorrect format"
    
    opcode = parts[0]
    func3 = parts[0]
    operands = parts[1].split(',')
    if len(operands) != 2:
        return "Error: Incorrect format"
    
    rs2 = REGISTERS.get(operands[0])
    if rs2 is None:
        return "Error: Invalid register"
    
    try:
        offset, rs1 = operands[1].split('(')
        rs1 = rs1[:-1] 
        rs1 = REGISTERS.get(rs1)
        opcode = OPCODES.get(opcode)
        func3 = FUNCT3.get(func3)
        if rs1 is None:
            return "Error: Invalid register"
        imm = TWOCOMPLEMENT(int(offset), 12)
        imm_high = imm[:7]
        imm_low = imm[7:]
        return f"{imm_high}{rs2}{rs1}{func3}{imm_low}{opcode}"
    except ValueError:
        return "Error: Incorrect format"


instruction = "sw s3,-4(s0)"
print(SType(instruction))  
