# H. Hadipour
# May 30, 2019
# 1398/03/09

import time
from gurobipy import *
"""
x_roundNumber_nibbleNumber_bitNumber
x_roundNumber_nibbleNumber_0: msb
x_roundNumber_nibbleNumber_3: lsb

x_i_0_0,x_i_0_1,x_i_0_2,x_i_0_3,......x_i_16_0,x_i_16_1,x_i_16_2,x_i_16_3 denote the input of the (i+1)-th round
y_i_0_0,y_i_0_1,y_i_0_2,y_i_0_3,......y_i_16_0,y_i_16_1,y_i_16_2,y_i_16_3 denote the output of MixColumns in the (i+1)-th round

Temporary 4-bit variables used in the mixing layer:
t0_0, t0_1, t0_2, t0_3,
t1_0, t1_1, t1_2, t1_3,
t2_0, t2_1, t2_2, t2_3
"""


class Craft:
    def __init__(self, rounds):
        self.rounds = rounds
        self.brute_force_flag = '0'
        self.block_size = 64
        self.p_permute_nibbles = [
            0xf, 0xc, 0xd, 0xe, 0xa, 0x9, 0x8, 0xb, 0x6, 0x5, 0x4, 0x7, 0x1, 0x2, 0x3, 0x0]
        self.model_file_name = "CRAFT%d.lp" % self.rounds
        self.result_file_name = "result%d.txt" % self.rounds
        fileobj = open(self.model_file_name, "w")
        fileobj.close()
        fileobj = open(self.result_file_name, "w")
        fileobj.close()

    def set_constant_bits(self, constant_bits):
        self.constant_bits = constant_bits

    def set_brute_force_flag(self, brute_force_flag):
        self.brute_force_flag = brute_force_flag

    # Number of coefficients
    NUMBER = 9
    # Linear inequalities for the  Sbox used in CRAFT round function
    sb = [[1, 1, 4, 1, -2, -2, -2, -2, 1],
          [0, 0, -3, 0, 1, 1, -2, 1, 2],
          [0, 0, 0, 0, -1, -1, 2, -1, 1],
          [-1, -1, 0, -1, 2, 2, 2, 2, 0],
          [0, -1, 0, -1, 0, 1, 1, 1, 1]]

    def create_objective_function(self):
        """
        Create objective function of the MILP model.
        """
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Minimize\n")
        eqn = []
        for i in range(0, 16):
            for j in range(0, 4):
                eqn.append("x_%d_%d_%d" % (self.rounds, i, j))
        temp = " + ".join(eqn)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    @staticmethod
    def create_variables(n, s):
        """
        Generate the variables used in the model.
        """
        array = [["%s_%d_%d_%d" % (s, n, i, j)
                  for j in range(4)] for i in range(16)]
        return array

    def flatten(self, state):
        return [state[i][j] for i in range(16) for j in range(4)]

    def constraints_by_sbox(self, variable1, variable2):
        """
        Generate the constraints by Sbox layer.
        """
        fileobj = open(self.model_file_name, "a")
        for k in range(0, 16):
            for coff in Craft.sb:
                temp = []
                for u in range(0, 4):
                    temp.append(str(coff[u]) + " " + variable1[k][u])
                for v in range(0, 4):
                    temp.append(str(coff[4 + v]) + " " + variable2[k][v])
                temp1 = " + ".join(temp)
                temp1 = temp1.replace("+ -", "- ")
                s = str(-coff[Craft.NUMBER - 1])
                s = s.replace("--", "")
                temp1 += " >= " + s
                fileobj.write(temp1)
                fileobj.write("\n")
        fileobj.close()

    def constraints_by_4bit_copy(self, x, x1, x2):
        """
        Generate the constraints by 4-bit copy operation.
        x -> (x1, x2)
        """
        fileobj = open(self.model_file_name, "a")
        for j in range(0, 4):
            temp = []
            temp.append(x[j])
            temp.append(x1[j])
            temp.append(x2[j])
            s = " - ".join(temp) + " = 0\n"
            fileobj.write(s)
        fileobj.close()

    def constraints_by_4bit_xor(self, x, y, z):
        """
        Generate the constraints by 4-bit Xor operation.
        x + y = z
        """
        fileobj = open(self.model_file_name, "a")
        for j in range(0, 4):
            temp = []
            temp.append(z[j])
            temp.append(y[j])
            temp.append(x[j])
            s = " - ".join(temp) + " = 0\n"
            fileobj.write(s)
        fileobj.close()

    def constraints_by_4bit_threeway_fork(self, x, x1, x2, x3):
        """
        Generate the constraints by 4-bit threeway fork
        x ---> (x1, x2, x3)
        """
        fileobj = open(self.model_file_name, "a")
        for i in range(0, 4):
            temp = [x[i], x1[i], x2[i], x3[i]]
            s = " - ".join(temp) + " = 0\n"
            fileobj.write(s)
        fileobj.close()

    def constraints_by_4bit_threeway_xor(self, x1, x2, x3, x):
        """
        Generate the constraints by 4-bit threeway xor
        x1 + x2 + x3 = x
        """
        fileobj = open(self.model_file_name, "a")
        for i in range(0, 4):
            temp = [x[i], x1[i], x2[i], x3[i]]
            s = " - ".join(temp) + " = 0\n"
            fileobj.write(s)
        fileobj.close()

    def PermuteNibbles(self, inputs):
        return [inputs[i] for i in self.p_permute_nibbles]

    def constraints_by_mixing_layer(self, variables_in, variables_out, round_number):
        """
        Generate constraints related to mixing layer
        """
        t0 = [["t0_%d_%d_%d" % (round_number, i, j)
               for j in range(4)] for i in range(4)]
        t1 = [["t1_%d_%d_%d" % (round_number, i, j)
               for j in range(4)] for i in range(4)]
        t2 = [["t2_%d_%d_%d" % (round_number, i, j)
               for j in range(4)] for i in range(4)]
        for j in range(4):
            # Constraints by 4-bit copies:
            self.constraints_by_4bit_copy(
                variables_in[8 + j], t0[j], variables_out[8 + j])
            self.constraints_by_4bit_threeway_fork(
                variables_in[12 + j], t1[j], t2[j], variables_out[12 + j])
            # Constraints by 4-it xors:
            self.constraints_by_4bit_threeway_xor(
                variables_in[j], t0[j], t2[j], variables_out[j])
            self.constraints_by_4bit_xor(
                variables_in[4 + j], t1[j], variables_out[4 + j])

    def constraint(self):
        """
        Generate the constraints used in the MILP model.
        """
        assert(self.rounds >= 1)
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        x_in = Craft.create_variables(0, "x")
        y = Craft.create_variables(0, "y")
        x_out = Craft.create_variables(1, "x")
        if self.rounds == 1:
            self.constraints_by_mixing_layer(x_in, y, 0)
            y_temp = self.PermuteNibbles(y)
            self.constraints_by_sbox(y_temp, x_out)
        else:
            self.constraints_by_mixing_layer(x_in, y, 0)
            y_temp = self.PermuteNibbles(y)
            self.constraints_by_sbox(y_temp, x_out)
            for i in range(1, self.rounds):
                x_in = x_out
                y = self.create_variables(i, "y")
                x_out = self.create_variables(i + 1, "x")
                self.constraints_by_mixing_layer(x_in, y, i)
                y_temp = self.PermuteNibbles(y)
                self.constraints_by_sbox(y_temp, x_out)

    # Variables declaration
    def variable_binary(self):
        """
        Specify the variables type.
        """
        fileobj = open(self.model_file_name, "a")
        fileobj.write("Binary\n")
        for i in range(self.rounds + 1):
            for j in range(16):
                for k in range(4):
                    fileobj.write("x_%d_%d_%d\n" % (i, j, k))
        for i in range(self.rounds):
            for j in range(16):
                for k in range(4):
                    fileobj.write("y_%d_%d_%d\n" % (i, j, k))
        for i in range(self.rounds):
            for j in range(4):
                for k in range(4):
                    for ind in range(3):
                        fileobj.write("t%d_%d_%d_%d\n" % (ind, i, j, k))
        fileobj.write("END")
        fileobj.close()

    def init(self):
        """
        Generate the initial constraints introduced by the initial division property.
        """
        input_state = Craft.create_variables(0, "x")
        input_state = self.flatten(input_state)
        fileobj = open(self.model_file_name, "a")
        eqn = []
        for i in range(64):
            if i in self.constant_bits:
                fileobj.write("%s = 0\n" % input_state[i])
            else:
                fileobj.write("%s = 1\n" % input_state[i])

        fileobj.close()

    def make_model(self):
        """
        Generate the MILP model of CRAFT
        """
        fileobj = open(self.model_file_name, "w")
        fileobj.close()
        self.create_objective_function()
        self.constraint()
        self.init()
        self.variable_binary()

    def write_objective(self, obj):
        """
        Write the objective value into filename_result.
        """
        fileobj = open(self.result_file_name, "a")
        fileobj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.block_size):
            u = obj.getVar(i)
            if u.getAttr("x") != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            fileobj.write(s)
            fileobj.write("\n")
        fileobj.close()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher of CRAFT.
        """
        time_start = time.time()
        balanced_bits = ["?" for i in range(64)]
        balanced_flag = False
        m = read(self.model_file_name)
        if (self.brute_force_flag == '1'):
            m.setParam("OutputFlag", 0)
        obj = m.getObjective()
        for i in range(0, self.block_size):            
            mask = [0 for j in range(64)]
            mask[i] = 1
            temporary_constraints = m.addConstrs(
                (obj.getVar(j) == mask[j] for j in range(64)), name='temp_constraints')            
            m.optimize()
            if m.Status == 3:
                balanced_flag = True
                balanced_bits[i] = "b"
            m.remove(temporary_constraints)
            m.update()
        fileobj = open(self.result_file_name, "a")
        if balanced_flag:
            fileobj.write("Indices of constant bits : %s\n" %
                          ",".join(map(str, self.constant_bits)))
            fileobj.write("Integral distinguisher found :)\n")
            print("\nIndices of constant bits : %s" %
                  ",".join(map(str, self.constant_bits)))
            print("Integral distinguisher found :)")
        else:
            fileobj.write("Indices of constant bits : %s\n" %
                          ",".join(map(str, self.constant_bits)))
            fileobj.write("Integral distinguisher doesn't exist :(\n")
            print("\nIndices of constant bits : %s" %
                  ",".join(map(str, self.constant_bits)))
            print("Integral distinguisher doesn't exist :(")
        output_state = ["".join(balanced_bits[4*i: 4*i + 4])
                        for i in range(16)]
        fileobj.write("output state : %s" % " ".join(output_state))
        print(" ".join(output_state))
        time_end = time.time()
        elapsed_time = time_end - time_start
        fileobj.write("\nTime used = %.2f\n\n" % elapsed_time)
        print("Time used = %.2f\n" % elapsed_time)
        fileobj.close()
