import openmc
import os



##
#   Replaces the nuclides in mat.xml with the random nuclides of NuclideStream
#   Returns openmc materials object with changed nuclides
##
def replaceNuclideMaterial(nuc, materials, newNuc):
    for mat in materials:
        if nuc not in mat.get_nuclides():
            continue
        dens = mat.get_nuclide_densities()
        NuclideTuple = dens[nuc]
        mat.remove_nuclide(nuc)
        mat.add_nuclide(newNuc, NuclideTuple[1], NuclideTuple[2])
    return materials


def replaceNuclideTally(nuc, newNuc):
    fin = open("tallies.xml", "rt")
    fout = open("tallies1.xml", "wt")

    for line in fin:
	#read replace the string and write to output file
	    fout.write(line.replace(nuc, newNuc))
    
    fin.close()
    fout.close()
    os.system("mv tallies1.xml tallies.xml")