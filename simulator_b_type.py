import os

registers = [0] * 32  # 32 registers initialized to 0
pc = 0  # Program Counter


def get_bits(instruction, start, end):
    """Extract bits from the given instruction."""
    return (instruction >> end) & ((1 << (start - end + 1)) - 1)


def sign_extend(value, bits):
    """Perform sign extension for a given bit length."""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def decode_b_instruction(funct3):
    """Decode the B-type (branch) instruction based on funct3 value."""
    b_instructions = {
        0b000: "beq",
        0b001: "bne",
        0b100: "blt",
        0b101: "bge",
        0b110: "bltu",
        0b111: "bgeu"
    }
    return b_instructions.get(funct3, "UNKNOWN INSTRUCTION")


def execute_instruction(instruction_bin, output_file):
    """Decode and execute the given instruction."""
    global pc
    try:
        instruction = int(instruction_bin, 2)
        opcode = get_bits(instruction, 6, 0)

        if opcode == 0b1100011:  
            rs1 = get_bits(instruction, 19, 15)
            rs2 = get_bits(instruction, 24, 20)
            funct3 = get_bits(instruction, 14, 12)

            imm = sign_extend(
                (get_bits(instruction, 31, 31) << 12) |
                (get_bits(instruction, 7, 7) << 11) |
                (get_bits(instruction, 30, 25) << 5) |
                (get_bits(instruction, 11, 8) << 1), 13
            )

            operation = decode_b_instruction(funct3)

            should_branch = False
            if operation == "beq":
                should_branch = registers[rs1] == registers[rs2]
            elif operation == "bne":
                should_branch = registers[rs1] != registers[rs2]
            elif operation == "blt":
                should_branch = registers[rs1] < registers[rs2]
            elif operation == "bge":
                should_branch = registers[rs1] >= registers[rs2]
            elif operation == "bltu":
                should_branch = (registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF)
            elif operation == "bgeu":
                should_branch = (registers[rs1] & 0xFFFFFFFF) >= (registers[rs2] & 0xFFFFFFFF)
            else:
                raise ValueError(f"Unsupported B-type funct3={funct3}")

            if should_branch:
                pc += imm  
            else:
                pc += 4  

            output_file.write(f"{pc} {' '.join(map(str, registers))}\n")

        else:
            raise ValueError(f"Unsupported opcode: {bin(opcode)}")

    except Exception as e:
        output_file.write(f"Exception at PC={pc}: {str(e)}\n")


def simulate_riscv(input_filename):
    """Simulate execution of RISC-V instructions from a file."""
    global pc, registers

    pc = 0
    registers = [0] * 32

    if not os.path.exists(input_filename):
        print(f"Error: File '{input_filename}' not found.")
        return

    output_filename = "output.txt"

    with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
        for line in input_file:
            instruction = line.strip()
            if len(instruction) != 32:
                output_file.write(f"Invalid instruction format at PC={pc}: {instruction}\n")
                break
            execute_instruction(instruction, output_file)

        print(f"Execution completed. Output saved to '{output_filename}'.")


if __name__ == "__main__":
    input_filename = input("Enter the input file name (e.g., input.txt): ").strip()
    simulate_riscv(input_filename)