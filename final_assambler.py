# assuming that input will be in formate of add x1,x2,x3
# assuming that input will not be like add, x1 , x2, x3

def type_of_inst(key):
    INSTRUCTION_TYPES = {
    "add": "R", "sub": "R", "and": "R", "or": "R", "slt": "R","srl":"R",
    "addi": "I", 
    "lw": "I", "jalr": "I",
    "sw": "S", 
    "beq": "B", "bne": "B",
    "jal": "J"
    }
    return INSTRUCTION_TYPES.get(key.strip().lower(),'error')

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
    "add":  "000", "sub":  "000",
    "slt":  "010", "srl":  "101", 
    "or":   "110", "and":  "111",
    "addi": "000", 
    "lw":   "010", "jalr": "000",
    "sw":   "010", 
    "beq":  "000", "bne": "001",
    }
    return FUNCT3.get(operation,'imm')

def op_code(operation):
    INSTRUCTIONS = {
    "add":  "0110011", "sub":  "0110011",
    "slt":  "0110011", "srl":  "0110011", 
    "or":   "0110011", "and":  "0110011",
    "addi": "0010011", "lw":   "0000011", "jalr": "1100111",
    "sw":   "0100011",
    "beq":  "1100011", "bne": "1100011",
    "jal":  "1101111"
    }
    return INSTRUCTIONS.get(operation.strip().lower(),'error')

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
    num = int(hex_num, 16)
    # Convert to binary and remove '0b' prefix
    return bin(num)[2:]

file_name = input()
label_match= {}
index=0
with open(file_name,'r') as f:
    for instruction in f.readlines():
        if len(instruction.split(':'))==2:
            label = instruction.split(':')[0].strip()
            label_match[label] = (instruction.split(':')[1].strip(),index) # { label : ( instruction , idx )}
        index+=1

index=0
with open("result",'w') as f_write:
    with open(file_name,"r") as f:

        for instruction in f.readlines():
            instruction = instruction.replace('\n','')
            
            if len(instruction.split(':')) > 2:
                f_write.write("wrong instruction1")
                continue
            elif len(instruction.split(':'))==2:

                operation = instruction.split(":")[1].strip().split(' ')[0].strip() # operation --> add,beq
                instruction = instruction.split(':')[1].strip() # add x1,x2,x3

            else :
                operation = instruction.split(' ')[0].strip() # operation --> add,beq
            
            data = instruction.split(' ')[1].strip().split(',')# x1,x2,x3
            opcode = op_code(operation)

            if op_code(operation) == 'error':
                f_write.write("wrong instruction2\n")
            
            if type_of_inst(operation) == 'B': # beq
                rs1 = data[0]
                rs2 = data[1]
                if data[2].isdigit(): # beq x1,x2,3
                    offset = int(data[2])
                    immidiate = to_twos_complement(offset,12) 
                else : # beq x1,x2,label
                    new_idx = label_match[data[2]][1]
                    curr_idx = index
                    offset = (new_idx-curr_idx)*4
                    immidiate = to_twos_complement((new_idx-curr_idx)*4,13)
                imm_12 = immidiate[0]               
                imm_10_5 = immidiate[2:8]           
                imm_4_1 = immidiate[8:12]           
                imm_11 = immidiate[1]   
                binary_instruction = imm_12 + imm_10_5 + registor_binary(rs2) + registor_binary(rs1) + function_f3(operation) + imm_4_1 + imm_11 + opcode
                if  -2**11 <= offset <= 2**11 - 1 :
                    f_write.write(binary_instruction+'\n')  
                else :
                    f_write.write("Error: wrong immidiate value3\n")

            elif type_of_inst(operation) == 'S':
                parts = instruction.split(' ')
                if len(parts) != 2:
                    f_write.write("Error: Incorrect format4\n")
                    continue
                
                func3 = function_f3(operation)  
                if len(data) != 2:
                    f_write.write("Error: Incorrect format5\n")
                    continue
                
                rs2 = registor_binary(data[0]) 
                if rs2 == 'imm':
                    f_write.write("Error: registor formate is incorrect6\n")
                    continue

                if '(' in data[1] :
                    offset, rs1 = data[1].replace(')','').split('(') # opperand_1 = 4(x3),4 
                    if offset.strip() == '':
                        offset = 0
                else : # sw x1,x2
                    offset = 0
                    rs1 = registor_binary(data[1])
                rs1 = registor_binary(rs1)
                if rs1 == 'imm':
                    f_write.write("Error: rs1 formate is incorrect7")
                    continue
                
                if  -2**11 <= int(offset) <= 2**11 - 1 :
                    pass 
                else :
                    f_write.write("Error: immidiate overflow8")
                    continue

                imm = to_twos_complement(int(offset), 12)
                imm_high = imm[:7]
                imm_low = imm[7:]
            
                binary_instruction = imm_high + rs2 + rs1 + func3 + imm_low + opcode
                f_write.write(binary_instruction+'\n')

            elif type_of_inst(operation) == 'R':
                a = instruction.replace(', ',',').split(' ')
                b = a[1].split(',')
                opcode = op_code(operation)
                f3 = function_f3(operation)
                f7 = '0100000' if operation == 'sub' else '0000000'
                rd = registor_binary(b[0])
                rs1 = registor_binary(b[1]) if registor_binary(b[1])!='imm' else to_twos_complement(b[1],5)
                rs2 = registor_binary(b[2]) if registor_binary(b[2])!='imm' else to_twos_complement(b[2],5)
                binary_instruction = f7 + rs2 + rs1 + f3 + rd + opcode
                if len(binary_instruction)>32:
                    f_write.write("wrong instruction9\n")
                else :
                    f_write.write(binary_instruction+'\n')

            elif type_of_inst(operation) == 'J':
                opcode = op_code(operation)
                rd = registor_binary(data[0])
                if '0x' in data[1]:
                    imm = hex_to_binary(data[1])
                    imm = (20-len(imm))*'0' + imm

                else :
                    if data[1].replace('-','').isdigit():
                        offset = int(data[1])
                        imm = to_twos_complement(int(data[1]),21)
                    else :
                        new_idx = label_match[data[1]][1]
                        curr_idx = index
                        offset = (new_idx-curr_idx)*4
                        imm = to_twos_complement(int(offset),21)
                    
                imm_20 = imm[0]                 
                imm_10_1 = imm[10:20]           
                imm_11 = imm[9]
                imm_19_12 = imm[1:9]            
                binary_instruction = imm_20 + imm_10_1 +imm_11 + imm_19_12  + rd + opcode
                if len(binary_instruction)>32:
                    f_write.write("wrong instruction10\n")
                else :
                    if -2**20<=int(offset)<=2**20-2:
                        f_write.write(binary_instruction+'\n') 
                    else :
                        pass                 
            
            elif type_of_inst(operation) =='I':
                f3 = function_f3(operation)
                rd = registor_binary(data[0])
                if len(data)==3:
                    rs1 = registor_binary(data[1])
                    if '0x' in data[2]:
                        imm = hex_to_binary(data[2])
                        imm = (12-len(imm))*'0' + imm
                    else :
                        imm = to_twos_complement(int(data[2]),12)
                else : # cases like --> lb x1, 0(x2)
                    if '[' in data[1]:
                        c = data[1].replace(']','').split('[')
                    elif '(' in data[1]:
                        c = data[1].replace(')','').split('(')

                    rs1 = registor_binary(c[1])
                    
                    imm = to_twos_complement(int(c[0]),12)
                    
                try :
                    offset = int(c[0])
                except :
                    offset = int(data[2])
                binary_instruction = imm + rs1 + f3 + rd + opcode
                if len(binary_instruction)>32:
                    f_write.write("wrong instruction11\n")
                else :
                    if  -2**11 <= offset <= 2**11 - 1 :
                        f_write.write(binary_instruction+'\n')  
                    else :
                        f_write.write("wrong instruction12\n")

            index+=1
