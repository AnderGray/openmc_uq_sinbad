import openmc




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


