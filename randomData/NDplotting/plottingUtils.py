####
#
#   Utilities for plotting random evaluations of nuclear data
#
#                   Ander Gray
####


import os
import sys

import h5py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import openmc.data


######
#   Random plots
######
def plotRandom(nuc, Nfiles = 10, MT = 1, Temp = 294, Dir = None):

    ###
    #   Validate inputs
    ###
    if Dir is None:
        Dir = os.path.abspath(os.chdir())
    filepath = Dir + '/' + 'hdf5' +  '/' + nuc

    if not os.path.exists(filepath):
        print(filepath + ' does not exist')
        sys.exit(None)

    REACTION = openmc.data.reaction.REACTION_NAME

    if not MT in REACTION:
        print('{} is not a valid MT number'.format(MT))
        sys.exit(None)

    reaction = REACTION[MT]


    for i in range(1,Nfiles+1):
        file = "{}-{}.h5".format(nuc, i)
        if not os.path.isfile( filepath + '/' + file ):
            print("{} file does not exits".format(file))
            sys.exit(None)


    ###
    #   Print and create plot dir
    ###
    message = "####\nCreating plot for nuclide {} {} at {}K with {} random evaluations\n####\n".format(nuc, reaction, Temp, Nfiles)
    print(message)

    if not os.path.exists(Dir + '/plots'):
        os.mkdir(Dir + '/plots')

    plotPath = Dir + '/plots' + '/' + nuc

    if not os.path.exists(plotPath):
        os.mkdir(plotPath)

    ###
    #   Extract cross-section data
    ###
    XS = [None]*Nfiles

    Temp = "{}K".format(Temp)
    file = filepath + "/{}-1.h5".format(nuc)
    NUC = openmc.data.IncidentNeutron.from_hdf5(file)

    energy = NUC.energy[Temp]
    XS_type = NUC[MT]
    XS[0] = XS_type.xs[Temp](energy)
    
    for i in range(1,Nfiles):

        file =  filepath + "/{}-{}.h5".format(nuc, i+1)
        NUC = openmc.data.IncidentNeutron.from_hdf5(file)
        XS_type = NUC[MT]
        XS[i] = XS_type.xs[Temp](energy)

    ###
    #   Process and plot
    ###
    meanXS = np.mean(XS, axis=0)

    title = "{} for {}".format(reaction, nuc, Nfiles)
    plt.title(title)

    for i in range(0, Nfiles):
        plt.loglog(energy, XS[i],'red', alpha = 0.1,linewidth = 0.2)

    plt.loglog(energy, meanXS, 'blue', linewidth = 0.5)
    plt.xlabel('Energy (eV)')
    plt.ylabel('Cross section (b)')
    PlotName = plotPath + "/{}_{}_{}_{}.png".format(nuc, reaction, Temp, Nfiles)

    plt.savefig(PlotName, dpi=1200)


######===================================================
#   Slice plots
######

def plotRandomSlice(nuc, Nfiles = 10, MT1 = 1, MT2 = 1, E1 = 3.8e5 , E2 = 4.8e5, Temp = 294, Dir = None):
        
    ###
    #   Validate inputs
    ###
    if Dir is None:
        Dir = os.path.abspath(os.chdir())
    filepath = Dir + '/' + 'hdf5' +  '/' + nuc

    if not os.path.exists(filepath):
        print(filepath + ' does not exist')
        sys.exit(None)

    REACTION = openmc.data.reaction.REACTION_NAME

    if not MT1 in REACTION:
        print('{} is not a valid MT number'.format(MT1))
        sys.exit(None)

    reaction1 = REACTION[MT1]

    if not MT2 in REACTION:
        print('{} is not a valid MT number'.format(MT2))
        sys.exit(None)

    reaction2 = REACTION[MT2]

    if not E1 < E2:
        print('E1 must be less than E2, provided: {} !< {}'.format(E1,E2))
        sys.exit()


    for i in range(1,Nfiles+1):
        file = "{}-{}.h5".format(nuc, i)
        if not os.path.isfile( filepath + '/' + file ):
            print("{} file does not exits".format(file))
            sys.exit(None)


    isSame = MT1 == MT2

    ###
    #   Print and create plot dir
    ###
    message = "####\nCreating slice plot for nuclide {}, {} at {}ev and {} at {}ev.\n{}K with {} random evaluations\n####\n".format(nuc, reaction1,E1, reaction2, E2, Temp, Nfiles)
    if isSame:
        message = "####\nCreating slice plot for nuclide {}, {} at {}ev and {}ev.\n{}K with {} random evaluations\n####\n".format(nuc, reaction1,E1, E2, Temp, Nfiles)
    print(message)

    if not os.path.exists(Dir + '/plots'):
        os.mkdir(Dir + '/plots')

    plotPath = Dir + '/plots' + '/' + nuc

    if not os.path.exists(plotPath):
        os.mkdir(plotPath)

    plotPath = plotPath + '/slice'

    if not os.path.exists(plotPath):
        os.mkdir(plotPath)
    else:
        i = 0
        isTrue = True
        while isTrue:
            i = i+1
            isTrue = os.path.exists(plotPath + '-%d'%i)
        plotPath = plotPath + '-%d'%i
        os.mkdir(plotPath)

    ###
    #   Extract cross-section data
    ###

    XS1 = [None]*Nfiles
    XS2 = [None]*Nfiles

    Samples1 = [None] * Nfiles
    Samples2 = [None] * Nfiles

    Temp = "{}K".format(Temp)
    file = filepath + "/{}-1.h5".format(nuc)
    NUC = openmc.data.IncidentNeutron.from_hdf5(file)

    energy = NUC.energy[Temp]

    XS_type1 = NUC[MT1]
    XS_type2 = NUC[MT2]

    XS1[0] = XS_type1.xs[Temp](energy)
    XS2[0] = XS_type1.xs[Temp](energy)

    Samples1[0] = XS_type1.xs[Temp](E1)
    Samples2[0] = XS_type1.xs[Temp](E2)

    print("Loading Data")

    for i in range(1,Nfiles):

        file =  filepath + "/{}-{}.h5".format(nuc, i+1)
        NUC = openmc.data.IncidentNeutron.from_hdf5(file)

        XS_type1 = NUC[MT1]
        XS_type2 = NUC[MT1]

        XS1[i] = XS_type1.xs[Temp](energy)
        XS2[i] = XS_type2.xs[Temp](energy)

        Samples1[i] = XS_type1.xs[Temp](E1)
        Samples2[i] = XS_type1.xs[Temp](E2)

    ###
    #   Process and plot
    ###
    meanXS1 = np.mean(XS1, axis=0)
    meanXS2 = np.mean(XS2, axis=0)

    # Joint Plot
    JointPlotName = "Joint_{}_{}_{}_({}_{})ev.png".format(nuc,MT1,MT2,E1,E2)

    if isSame:
        JointPlotName = "Joint_{}_{}_({}_{})ev.png".format(nuc,reaction1,E1,E2)

    g = sns.jointplot(Samples1,Samples2,kind="kde", height=7, space=0)
    g.plot_joint(plt.scatter, c="red", s=30, linewidth=1.5, marker="+", alpha = 0.4)

    xlab = "Distribution at {}ev".format(E1)
    ylab = "Distribution at {}ev".format(E2)

    g.set_axis_labels(xlab,ylab)
    g.savefig(plotPath+'/'+JointPlotName, dpi = 1200)


    print("Saving plots to {}".format(plotPath))

    # Cross sections
    plt.figure()

    title = "{} for {}".format(reaction1, nuc)
    plt.title(title)

    for i in range(0, Nfiles):
        plt.loglog(energy, XS1[i],'red', alpha = 0.1,linewidth = 0.2)

    plt.loglog(energy, meanXS1, 'blue', linewidth = 0.5)
    plt.xlabel('Energy (eV)')
    plt.ylabel('Cross section (b)')

    plt.axvline(x=E1, color = 'black')
    if isSame:
        plt.axvline(x=E2, color='black')
    PlotName = plotPath + "/{}_{}_{}_{}.png".format(nuc, reaction1, Temp, Nfiles)

    plt.savefig(PlotName, dpi=1200)
    

    if isSame:
        plt.figure()
        title = "{} for {}".format(reaction1, nuc)
        for i in range(0, Nfiles):
            plt.plot(energy, XS1[i],'red', alpha = 0.1,linewidth = 0.2)

        plt.plot(energy, meanXS1, 'blue', linewidth = 0.5)

        plt.yscale('log')

        bot, top = plt.ylim()   

        plt.xlabel('Energy (eV)')
        plt.ylabel('Cross section (b)')
        plt.axvline(x=E1, color = 'black')
        plt.axvline(x=E2, color = 'black')

        plt.ylim((bot,top))
        plt.xlim((E1 - E1 * 0.05, E2 + E2 * 0.05))

        PlotName = plotPath + "/{}_{}_{}_{}ZOOMED.png".format(nuc, reaction1, Temp, Nfiles)
        plt.savefig(PlotName, dpi = 1200)

    else:

        plt.figure()

        title = "{} for {}".format(reaction2, nuc)
        plt.title(title)

        for i in range(0, Nfiles):
            plt.loglog(energy, XS2[i],'red', alpha = 0.1,linewidth = 0.2)

        plt.loglog(energy, meanXS2, 'blue', linewidth = 0.5)
        plt.xlabel('Energy (eV)')
        plt.ylabel('Cross section (b)')

        plt.axvline(x=E2, color = 'black')
        PlotName = plotPath + "/{}_{}_{}_{}.png".format(nuc, reaction2, Temp, Nfiles)

        plt.savefig(PlotName, dpi=1200)

        
        ###
        #   Zoomed React1
        ###

        plt.figure()
        title = "{} for {}".format(reaction1, nuc)
        for i in range(0, Nfiles):
            plt.plot(energy, XS1[i],'red', alpha = 0.1,linewidth = 0.2)

        plt.plot(energy, meanXS1, 'blue', linewidth = 0.5)

        plt.yscale('log')

        bot, top = plt.ylim()   

        plt.xlabel('Energy (eV)')
        plt.ylabel('Cross section (b)')
        plt.axvline(x=E1, color = 'black')

        plt.ylim((bot,top))
        plt.xlim((E1 - E1 * 0.05, E2 + E2 * 0.05))

        PlotName = plotPath + "/{}_{}_{}_{}ZOOMED.png".format(nuc, reaction1, Temp, Nfiles)
        plt.savefig(PlotName, dpi = 1200)


        ###
        #   Zoomed React1
        ###

        plt.figure()
        title = "{} for {}".format(reaction2, nuc)
        for i in range(0, Nfiles):
            plt.plot(energy, XS2[i],'red', alpha = 0.1,linewidth = 0.2)

        plt.plot(energy, meanXS1, 'blue', linewidth = 0.5)

        plt.yscale('log')

        bot, top = plt.ylim()   

        plt.xlabel('Energy (eV)')
        plt.ylabel('Cross section (b)')
        plt.axvline(x=E2, color = 'black')

        plt.ylim((bot,top))
        plt.xlim((E1 - E1 * 0.05, E2 + E2 * 0.05))

        PlotName = plotPath + "/{}_{}_{}_{}ZOOMED.png".format(nuc, reaction2, Temp, Nfiles)
        plt.savefig(PlotName, dpi = 1200)


#def plotRandomCovariance()