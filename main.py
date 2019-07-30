# H. Hadipour
# May 30, 2019
# 1398/03/09

from craft import Craft

if __name__ == "__main__":
    rounds = int(input("Input the target round number: "))
    while not (rounds > 0):
        print("Input a round number greater than 0.")
        rounds = int(input("Input the target round number again: "))    
    craft = Craft(rounds)
    brute_force_flag = input("Brute force : 1  Probing an especial case : 0 ?\n")
    while (brute_force_flag not in ['0', '1']):
        print("Enter 0 or 1!")
        brute_force_flag = input("Brute force : 1  Probing an especial case : 0 ?\n")
    craft.set_brute_force_flag(brute_force_flag)
    if brute_force_flag == '0':
        temp = input("Enter the list of constant bits separated by space:\n")
        temp = temp.split()
        constant_bits = []
        for element in temp:
            constant_bits.append(int(element))
        craft.set_constant_bits(constant_bits)
        craft.make_model()
        craft.solve_model()
    else:
        number_of_total_states = 64
        for i in range(0, 64):
            print("%d / %d" % (i, number_of_total_states))
            constant_bits = [i]
            craft.set_constant_bits(constant_bits)
            craft.make_model()
            craft.solve_model()