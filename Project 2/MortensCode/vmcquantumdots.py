#VMC for electrons in harmonic oscillator potentials with oscillator
#frequency = 1
#"Computational Physics", Morten Hjorth-Jensen

import numpy
import math
import sys
from random import random

#Read name of output file from command line
if len(sys.argv) == 2:
    outfilename = sys.argv[1]
else:
    outfilename = "outfile_m.txt"
    print('\nError: Name of output file must be given as command line argument.\n')

#Initialisation function
def initialize():
    number_particles = eval(input('Number of particles: '))
    dimension = eval(input('Dimensionality: '))
    max_variations = eval(input('Number of variational parameter values: '))
    number_cycles = eval(input('Number of MC cycles: '))
    step_length = eval(input('Step length: '))

    return number_particles,dimension,max_variations,number_cycles,step_length

#Trial wave function
def wave_function(r):
    argument = 0.0
    for i in range(number_particles):
        r_single_particle = 0.0
        for j in range(dimension):
            r_single_particle += r[i,j]**2
        argument += r_single_particle
    wf = math.exp(-argument*alpha*0.5) 
    #Jastrow factor
    for i1 in range(number_particles-1):
        for i2 in range(i1+1,number_particles):
            r_12 = 0.0
            for k in range(dimension):
                r_12 += (r[i1,k] - r[i2,k])**2
            argument = math.sqrt(r_12)
#            wf *= math.exp(0.5*argument/(1.0+0.3*argument))

    return wf

#Local energy (numerical derivative)
#the argument wf is the wave function value at r (so we don't need to calculate it again)
def local_energy(r,wf):
    #Kinetic energy
    r_plus = r.copy()
    r_minus = r.copy()
    e_kinetic = 0.0
    for i in range(number_particles):
        for j in range(dimension):
            r_plus[i,j] = r[i,j] + h
            r_minus[i,j] = r[i,j] - h
            wf_minus = wave_function(r_minus)
            wf_plus = wave_function(r_plus)
            e_kinetic -= wf_minus+wf_plus-2*wf;
            r_plus[i,j] = r[i,j]
            r_minus[i,j] = r[i,j]
    e_kinetic = .5*h2*e_kinetic/wf
    #Potential energy
    e_potential = 0.0
    
    #harmonic oscillator  contribution
    for i in range(number_particles):
        r_single_particle = 0.0
        for j in range(dimension):
            r_single_particle += r[i,j]**2
        e_potential += 0.5*r_single_particle

    #Electron-electron contribution
    for i1 in range(number_particles-1):
        for i2 in range(i1+1,number_particles):
            r_12 = 0.0
            for j in range(dimension):
                r_12 += (r[i1,j] - r[i2,j])**2
#            e_potential += 1/math.sqrt(r_12)
    
    return e_potential + e_kinetic


#Here starts the main program

number_particles,dimension,max_variations,number_cycles,step_length = initialize()

outfile = open(outfilename,'w')

alpha = 0.5  #variational parameter

#Step length for numerical differentiation and its inverse squared
h = .001
h2 = 1/(h**2)

r_old = numpy.zeros((number_particles,dimension), numpy.double)
r_new = numpy.zeros((number_particles,dimension), numpy.double)

#Loop over alpha values
for variate in range(max_variations):
    
    alpha += .1
    energy = energy2 = 0.0
    accept = 0.0
    delta_e = 0.0

    #Initial position
    for i in range(number_particles):
        for j in range(dimension):
            r_old[i,j] = step_length * (random() - .5)
    
    wfold = wave_function(r_old)

    #Loop over MC cycles
    for cycle in range(number_cycles):

        #Trial position
        for i in range(number_particles):
            for j in range(dimension):
                r_new[i,j] = r_old[i,j] + step_length * (random() - .5)

        wfnew = wave_function(r_new)

        #Metropolis test to see whether we accept the move
        if random() < wfnew**2 / wfold**2:
            r_old = r_new.copy()
            wfold = wfnew
            accept += 1
        #update expectation values
        delta_e = local_energy(r_old,wfold)
        energy += delta_e
        energy2 += delta_e**2

    #We calculate mean, variance and error ...
    energy /= number_cycles
    energy2 /= number_cycles
    variance = energy2 - energy**2
    #print(energy, energy2, variance)
    error = math.sqrt(variance/number_cycles)
        
    #...and write them to file
    outfile.write('%f %f %f %f %f\n' %(alpha,energy,variance,error,accept*1.0/(number_cycles)))

outfile.close()

print('\nDone. Results are in the file "%s", formatted as:\n\
alpha, <energy>, variance, error, acceptance ratio' %(outfilename))


