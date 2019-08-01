# CRAFT-Integral-Distinguisher
Using an MILP method to find integral distinguisher based on division property for CRAFT

This tool is used to find an integral distinguisher based on division property for CRAFT. 

# What is CRAFT?
CRAFT is a lightweight tweakable block cipher for which efficient protection against DFA attacks has been considered in its design phase. Here's the link of a dedicated web-page which 
is created for CRAFT by it's designers: 
https://sites.google.com/view/craftcipher/home

# What this tool is used for?
This repository contains two main files called `main.py` and `craft.py`. The `craft.py` contains a python class named `Craft` which is used to convert the problem 
of searching integral distinguisher to an MILP problem. The `Craft` class has also a method called `Solve`, which is used to solve the obtained MILP model via Gurobi. 
the `main.py` shows how to use the `Craft` class to find an integral distinguisher for CRAFT. To run this tool, just run the following command: 

    python3 main.py

The following figure shows one round of CRAFT, which in `AddTweakey` layer has been removed for simplicity, because adding a constant doesn't change the integral properties.


![Round Function of CRAFT)](https://github.com/hadipourh/CRAFT-Integral-Distinguisher/blob/master/Images/CRAFT-Round-Function.svg)


