import sys

# Here I will be building a CPU that is capable of the following functions
# Instruction|  Opcode|  Function | Meaning
#--------------------------------
# ADD        | 000001 |    00000  |Rd <- Rs + Rt
# SUB        | 000010 |    00000  | Rd <- Rs - Rt
# MULT       | 000011 |    00000  | Rd <- Rs * Rt
# DIV        | 000100 |    00000  | Rd <- Rs / Rt
# SLT        | 000101 |    00000  | If (Rs < Rt) Then Rd <- 1 Else Rd <- 0
# J          | 000111 |    00000  | PC <- target 
# JAL        | 001000 |    00000  | R7 <- PC + 4; PC <- target *4
# LW         | 001001 |    00000  | Rt <- MEM[Rs + offset]
# SW         | 001010 |    00000  | MEM[Rs + offset] <- Rt
# CACHE      |        |    000--  | If Code = 0 (Cache Off), Code = 1 (Cache On), Code = 11 (Flush Cache)
# HALT       |        |    10000  | Terminate Execution

# 000000 00000 00000 0000000000 000000 
# opcode  rs    rt       rd      func
"""
So I will be building a CPU, So we will parse machine code, perform operations on the information provided,
and return the output.

-Can only operation on numbers stored in registers
-processor receives binary data as 32 bits strings
-returns results to the terminal
-can operate on 0-1023
-32 registers
    - 0-21 for number storgae
    - 0 is constant 0
    - 22-31 available for history storage

I am going to simulate using RISC (Reduced Instruction Set Computer) Type instructions to make the parsing 
simpler (although we could just use len operation in conjugtion if using CISC (Comples Instruction Set Computer)).

Up top, I have listed the operations that this CPU will be designed to perform. Below I will define the terms

opcode = the operation code, tells the cpu where to send the information after it.
shamt = 
func = additional bits for various opertations like CACHE and HALT
Rd = Destination Register
Rs, Rt = Source Operand Registers
PC = Program Counter
Offset = Still trying to figure that out. lol

ADD is an addition operation on two registers and stores the result in the destination register 
SUB is a subtraction operation between two registers and stores the result in the destination register
MULT is a multiplication operation between two registers and stores the reult in the destination register
DIV is a division operation between two registers and stores the result in the destination register
SLT is a logical operation for Set On Less Than.
BNE is a branching operation and stands for Branch on Not Equal
J is a Jump Operation- used to jump to a specific instruction, such as in a loop
JAL stands for Jump and Link
LW stands for Load Word
SW stands for Store Word
CACHE is a means to shorten retrieval of information
HALT Terminates the execution of the current instruction set
"""

class Codecademy_CPU():
    #Initializing Parameters used for CPU operations
    def __init__ (self, name):
        self.name = name
        #Imagine that each of these positions in the number registers is a string of 10 bits.
        #Instead of bits, we are storing the actual numbers in deci form and will be using
        # int() and bin() to transform back and forth.
        self.number_registers = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.history_registers = [0,0,0,0,0,0,0,0,0,0]

        #now we need a way to keep track of which register to use. Also we are going to be using
        #the Fifo method for our registers
        #since our 0th position in numbers_registers is always 0, we will start at the 1st position
        self.numbers_index = 1
        self.history_index = 0
        self.temp_history_index = 0
        self.cache_index = 0
        self.main_memory_index = 0
        self.pc = 0

        #We want to print the process and final result of what is going on
        self.user_display = ''
        self.update_display(f"Hello, I am the {self.name} CPU. Let's start crunching!")

        #mm_loc tells us the main_memory location and data is the value temp stored in cache
        self.cache = [
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None},
            {'mm_loc': None, 'data': None}
        ]

        #simulating main_memory. We will have a thousand locations to store 32 bits. 32000 bits if you will.
        self.main_memory = [{x : x} for x in range(1024)]

    #Method for changing output.
    def update_display(self, to_update):
        self.user_display = to_update
        print(self.user_display)

    #Method to store a value to a register
    def store_value_to_register(self, value_to_store, location = None):
        if location and location <= 21:
            self.number_registers[location] = int(value_to_store,2)
        else:
            if self.numbers_index > 21:
                self.numbers_index = 1
            self.number_registers[self.numbers_index] = int(value_to_store, 2)
            print(f"Value: {int(value_to_store,2)} was stored in Register: {self.numbers_index}")
            self.numbers_index += 1

    #Method to load a value from a register
    def load_value_from_register(self, register_address):
        index = int(register_address, 2)
        int_value = int(self.number_registers[index])
        return int_value
    
    #Method to store to history_register
    def store_to_history_register(self, result_to_store):
        if self.history_index > 9:
            self.history_index = 0
        self.history_registers[self.history_index] = bin(result_to_store)
        self.history_index += 1
        self.temp_history_index = self.history_index

    def store_main_memory(self, value_to_store, location_to_store = None):
        if location_to_store:
            self.main_memory[location_to_store][location_to_store] = value_to_store
            self.update_display(f"Storing the value: {value_to_store} in main memory location {location_to_store}\n")
        else:
            self.main_memory[self.main_memory_index][self.main_memory_index] = value_to_store
            self.main_memory_index += 1
            self.update_display(f"Storing the value: {value_to_store} in main memory location {self.main_memory_index - 1}\n")
        return
    
    def retrieve_main_memory(self, location):
        value = self.main_memory[location][location]
        return value

    def reset_main_memory_location(self, location):
        self.main_memory[location][location] = location
        return

    def store_to_cache(self, mm_loc, value):
        if self.cache_index > 9:
            self.cache_index = 0
        self.cache[self.cache_index]['mm_loc'] = mm_loc
        self.cache[self.cache_index]['data'] = value
        self.cache_index += 1
        return

    def is_in_cache(self, location):
        is_in = False
        position = 0
        counter = 0
        for dict_ in self.cache:
            if dict_['mm_loc'] == location:
                is_in = True
                position = counter
            else:
                counter += 1
                continue
        return is_in, position

    def check_cache(self, loc):
        if self.is_in_cache == True:
            for dict_ in self.cache:
                if dict_['mm_loc'] == loc:
                     return dict_['data']
                else:
                    continue
        else:
            self.store_to_cache(loc, self.retrieve_main_memory(loc))

    def store_instruction(self, instruction):
        if len(instruction) != 32:
            self.update_display('Instruction is not 32 bits long.\n')
        self.store_main_memory(instruction)
        self.pc += 1
        return

    def get_current_instruction(self, location = None):
        if location:
            instruction = self.retrieve_main_memory(location)
            opcode = instruction[0:6]
            Rs = instruction[6:11]
            Rt = instruction[11:16]
            Rd = instruction[16:26]
            func = instruction[26:]
            return opcode, Rs, Rt, Rd, func
        else:
            if self.pc == 0:
                self.update_display('CPU has executed current batch of insturctions\n')
            else:
                instruction = self.retrieve_main_memory(self.pc - 1)
                opcode = instruction[0:6]
                Rs = instruction[6:11]
                Rt = instruction[11:16]
                Rd = instruction[16:26]
                func = instruction[26:]
                self.pc -= 1
                return opcode, Rs, Rt, Rd, func


    def add(self, Rs, Rt):
        num1 = self.load_value_from_register(Rs)
        num2 = self.load_value_from_register(Rt)
        calculated_num = num1 + num2
        self.update_display(f"Adding {num1} and {num2} together\n")
        return calculated_num

    def sub(self, Rs, Rt):
        num1 = self.load_value_from_register(Rs)
        num2 = self.load_value_from_register(Rt)
        calculated_num = num1 - num2
        self.update_display(f"Subtracting {num1} and {num2}\n")
        return calculated_num

    def mult(self, Rs, Rt):
        num1 = self.load_value_from_register(Rs)
        num2 = self.load_value_from_register(Rt)
        calculated_num = num1 * num2
        self.update_display(f"Multiplying {num1} and {num2}\n")
        return calculated_num

    def div(self, Rs, Rt):
        num1 = self.load_value_from_register(Rs)
        num2 = self.load_value_from_register(Rt)
        calculated_num = num1 / num2
        self.update_display(f"Divinding {num1} and {num2}\n")
        return calculated_num

    def slt(self, Rs, Rt):
        num1 = self.load_value_from_register(Rs)
        num2 = self.load_value_from_register(Rt)
        self.update_display(f"Checking to see if {num1} is less than {num2}\n")
        if num1 < num2:
            return 1
        else:
            return 0

    def J_(self, target):
        self.pc = int(target)
        self.update_display(f'Jumping Program counter to {target} in main memory')
        return

    def JAL(self, target):
        self.store_value_to_register(self.pc+4, 7)
        self.pc = target * 4

    def LW(self, Rs):
        word = self.retrieve_main_memory(int(Rs, 2))
        self.update_display(f"Loading {word} from main memory location {int(Rs, 2)}")
        return word

    def SW(self, Rs, word):
        self.store_main_memory(word, int(Rs, 2))
        self.update_display(f"Storing {word} into main memory location {int(Rs, 2)}")

    def HALT(self):
        sys.exit('Terminate Execution Completed.\n')

    def parse_and_execute_instructions(self, instructions):
        instructions = instructions.split('\n')
        print(instructions)
        for n,instruction in enumerate(reversed(instructions)):
            self.update_display(f'Instruction {n}')
            self.store_instruction(instruction)
            self.update_display(f'Is {self.retrieve_main_memory(self.pc - 1)} and is stored at location {self.pc - 1}\n')
        self.update_display(f'We have a total of {self.pc} instructions.\n')
        for instruction in range(self.pc):
            opcode, Rs, Rt, Rd, func = self.get_current_instruction()
            print(f"Opcode: {opcode}\n    Rs: {Rs}\n    Rt: {Rt}\n    Rd: {Rd}\n  func: {func}\n")
            if func == '000011':
                self.store_value_to_register(Rs)
                self.store_value_to_register(Rt)
            if opcode == '000001':
                value = self.add(Rs, Rt)
                loc = int(Rd, 2)
                self.store_main_memory(value, loc)
            if opcode == '000010':
                value = self.sub(Rs, Rt)
                loc = int(Rd, 2)
                self.store_main_memory(value, loc)
            if opcode == '000011':
                value = self.mult(Rs, Rt)
                loc = int(Rd, 2)
                self.store_main_memory(value, loc)
            if opcode == '000100':
                value = self.div(Rs, Rt)
                loc = int(Rd, 2)
                self.store_main_memory(value, loc)


my_cpu = Codecademy_CPU('Alex')
instructions = '00000000100010000000000000000011\n00000100001000100000001000000000\n00001000001000100000001001000000\n00001100001000100000001010000000\n00010000010000010000001011000000'
my_cpu.parse_and_execute_instructions(instructions)