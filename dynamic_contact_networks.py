##############################################################################
# MDContactNetworks: A Python Library for computing non-covalent contacts
#                    throughout Molecular Dynamics Trajectories. 
# Copyright 2016-2017 Stanford University and the Authors
#
# Authors: Anthony Kai Kwang Ma
# Email: anthony.ma@yale.edu, anthonyma27@gmail.com, akma327@stanford.edu
##############################################################################


##############################################################################
# Imports
##############################################################################

import os
import sys
import datetime
# from contact_calc.compute_contacts_memory_intensive import *
from contact_calc.compute_contacts import *

USAGE_STR = """

# Purpose 
# Computes non-covalent contacts in MD simulation for any protein of study

# Usage
# python DynamicContactNetworks.py <TOP> <TRAJ> <OUTPUT_DIR> <cores> <stride> <solv> <sele> <ligand> <INTERACTION_TYPES>

# Arguments
# <TOP> Absolute path to topology
# <TRAJ> Absolute path to reimaged MD trajectory
# <OUTPUT_DIR> Absolute path to output directory to store contacts data
# <INTERACTION_TYPES> -itypes flag followed by a list of non-covalent interaction types to compute (ie -sb -pc -ps -ts -vdw, etc)
# <optional -cores flag> To denote how many CPU cores to use for parallelization
# <optional -stride flag> To denote a stride value other than default of 1
# <optional -solv flag> To denote a solvent id other than default of TIP3
# <optional -sele flag> To denote a VMD selection query to compute contacts upon
# <optional -ligand flag> To denote the resname of ligand in the simulation.

# Example
TOP=topology.pdb"
TRAJ="trajectory.dcd"
OUTPUT_DIR="output"
python dynamic_contact_networks.py $TOP $TRAJ $OUTPUT_DIR -itype -hb -hlb

"""

K_MIN_ARG = 4

if __name__ == "__main__":
	if(len(sys.argv) < K_MIN_ARG):
		print(USAGE_STR)
		exit(1)

	### Required Arguments
	(TOP, TRAJ, OUTPUT_DIR) = (sys.argv[1], sys.argv[2], sys.argv[3])
	ITYPES = sys.argv[sys.argv.index('-itype') + 1:]
	if("-all" in ITYPES):
		ITYPES = ["-sb", "-pc", "-ps", "-ts", "-vdw", "-hb", "-hlb"]

	print ITYPES

	### Optional Arguments
	cores = 6
	stride = 1 # default
	solvent_resn = "TIP3" # default
	sele_id = None
	ligand = None

	if("-cores" in sys.argv):
		core_index = sys.argv.index("-cores")
		cores = int(sys.argv[core_index + 1])

	if("-stride" in sys.argv):
		stride_index = sys.argv.index("-stride")
		stride = int(sys.argv[stride_index + 1])

	if("-solv" in sys.argv):
		solv_index = sys.argv.index("-solv")
		solvent_resn = sys.argv[solvIndex + 1]

	if("-sele" in sys.argv):
		sele_index = sys.argv.index("-sele")
		sele_id = str(sys.argv[sele_index + 1])

	if("-ligand" in sys.argv):
		ligand_index = sys.argv.index("-ligand")
		ligand = str(sys.argv[ligand_index + 1])

	tic = datetime.datetime.now()
	compute_dynamic_contacts(TOP, TRAJ, OUTPUT_DIR, ITYPES, cores, stride, solvent_resn, sele_id, ligand)
	toc = datetime.datetime.now()
	print("Computation Time: " + str((toc-tic).total_seconds()))

