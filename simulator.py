import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

pc_map = {}

with open(input_file) as f:
    lst = [ x.strip() for x in f.readlines() ]
    for i in range(len(lst)):
        pc_map[i*4] = lst[i]


registers = [0] * 32  
memory = {}  
pc = 0  
label_map = {}  


def get_bits(instruction, start, end):
    return (instruction >> end) & ((1 << (start - end + 1)) - 1)


def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def decode_r_instruction(funct7, funct3):
    r_instructions = {
        (0b0000000, 0b000): "ADD",
        (0b0100000, 0b000): "SUB",
        (0b0000000, 0b111): "AND",
        (0b0000000, 0b110): "OR",  
        (0b0000000, 0b101): "SRL",    
        (0b0000000, 0b010): "SLT",  
    }
    
    return r_instructions.get((funct7, funct3), "UNKNOWN INSTRUCTION")

def decode_i_instruction(opcode, funct3,):

    if opcode == "0010011":  
        funct3_map = {
            "000": "ADDI",
        }
        return funct3_map.get(funct3, "Unknown")

    elif opcode == "0000011":  
        funct3_map = {
            "010": "LW",   
        }
        return funct3_map.get(funct3, "Unknown")

    elif opcode == "1100111":  
        if funct3 == "000":
            return "JALR"
        return "Unknown"

    return "Unknown"  



def execute_instruction(instruction_bin, output_file):
    global pc
    try:
        instruction = int(instruction_bin, 2)
        
        opcode = get_bits(instruction, 6, 0)

        if opcode == 0b0110011:  # R-type 
            rd = get_bits(instruction, 11, 7)
            rs1 = get_bits(instruction, 19, 15)
            rs2 = get_bits(instruction, 24, 20)
            funct3 = get_bits(instruction, 14, 12)
            funct7 = get_bits(instruction, 31, 25)
            operation = decode_r_instruction(funct3,funct7)

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
                raise ValueError(f"Unsupported R-type funct3={funct3}, funct7={funct7}")
            if rd == 0:  
                registers[0] = 0
            pc += 4

        elif opcode in  [0b0010011,0b0000011,0b1100111]:  # I-type 
            rd = get_bits(instruction, 11, 7)
            rs1 = get_bits(instruction, 19, 15)
            imm = sign_extend(get_bits(instruction, 31, 20), 12)
            funct3 = get_bits(instruction, 14, 12)

            if operation == "ADDI":
                registers[rd] = registers[rs1] + imm

            elif operation == "LW":
                address = registers[rs1] + imm
                registers[rd] = memory[address]
            
            elif operation == "JALR":
                temp = pc + 4  
                pc = (registers[rs1] + imm) & ~1  
                registers[rd] = temp

            else:
                raise ValueError(f"Unsupported I-type funct3={funct3}")
            
            if rd == 0:
                registers[0] = 0
            pc += 4


        elif opcode == 0b1101111:  # J-type 
            rd = get_bits(instruction, 11, 7)
            imm = sign_extend(
                (get_bits(instruction, 31, 31) << 20) | 
                (get_bits(instruction, 19, 12) << 12) | 
                (get_bits(instruction, 20, 20) << 11) |
                (get_bits(instruction, 30, 21) << 1), 21)
            registers[rd] = pc + 4  
            if rd == 0:
                registers[0] = 0
            pc = pc + imm  

        else:
            raise ValueError(f"Unsupported opcode: {bin(opcode)}")

        output_file.write(f"{pc} {' '.join(map(str, registers))}\n") 

    except Exception as e:
        output_file.write(f"Exception at PC={pc}: {str(e)}\n")


def simulate_riscv(input_filename, output_filename):
    global pc, registers, memory
    
    
    pc = 0
    registers = [0] * 32
    memory = {}
    
    with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
        while (pc<len(pc_map)):
            instruction = pc_map[pc].strip()
            if len(instruction) != 32 :
                output_file.write(f"Invalid instruction format at PC={pc}: {instruction}\n")
                break
            execute_instruction(instruction, output_file)
            if (get_bits(instruction, 6, 0)==0b1101111):
                imm = sign_extend(
                (get_bits(instruction, 31, 31) << 20) | 
                (get_bits(instruction, 19, 12) << 12) | 
                (get_bits(instruction, 20, 20) << 11) |
                (get_bits(instruction, 30, 21) << 1), 21)
                if (imm==0):
                    break
            # if (get_bits==) write for b type instruction if imm == 0 then break
        output_file.write("\n")
        
        base_addr = 0x00010000
        for i in range(32): 
            addr = base_addr + (i * 4)
            value = memory.get(addr, 0)
            output_file.write(f"0x{addr:08x}:{value}\n")




simulate_riscv(input_file, output_file)