def bonus_instruction(instruction):
    """Executes bonus instructions: rst (reset), halt (stop execution), and rvrs."""
    global registers, halt_flag

    instruction = instruction.strip().lower()
    
    if instruction == "rst":
        # Reset all registers except PC
        registers = {reg: "00000000000000000000000000000000" for reg in REGISTERS}
        print("All registers reset (except PC).")

    elif instruction == "halt":
        halt_flag = True
        print("Execution Halted.")

    elif instruction == "rvrs":
        # Reverse register values (example behavior)
        registers = {reg: bin(int(val, 2))[2:].zfill(32)[::-1] for reg, val in registers.items()}
        print("All registers reversed.")

    else:
        print(f"Error: Unknown bonus instruction '{instruction}'")

# Sample dictionary for register values (default initialized)
registers = {reg: "00000000000000000000000000000000" for reg in [
    "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0", "s1", "a0", "a1", "a2", "a3",
    "a4", "a5", "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
    "t3", "t4", "t5", "t6"
]}

halt_flag = False  # Global halt flag

bonus_instruction("rst")   # Resets all registers
bonus_instruction("halt")  # Halts execution
bonus_instruction("rvrs")  # Reverses all register values
