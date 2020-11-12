include("/cosma/home/dp163/dc-gray2/opt/juliaStuff/ProbabilityBoundsAnalysis.jl/src/ProbabilityBoundsAnalysis.jl")
using Main.ProbabilityBoundsAnalysis

using HDF5, Statistics, PyPlot, XLSX, JLD2

simDir = pwd()

loadData = true

SIMNAME1 = "endfNi"
SIMNAME2 = "tendlNi"
statePointDirSandy = "$(simDir)/statepoints-$(SIMNAME1)"
statePointDirTendl = "$(simDir)/statepoints-$(SIMNAME2)"

useLeth = false
useSurf = true

r = 0.16
##
#   Plotting stuff
##

index = 1

h1 = h5open("$(statePointDirSandy)/statepoint.$(index).h5", "r")
h2 = h5open("$(statePointDirTendl)/statepoint.$(index).h5", "r")


NouterS = 500
NouterT = 500


enEndf = read(h1,"tallies/filters/filter 1/bins")
endfTendl = read(h2,"tallies/filters/filter 1/bins")

if !(enEndf == endfTendl); throw(ArgumentError("Energy grid of Sandy and Tendl simulations are different")); end

enHi = enEndf[2:end]
enLo = enEndf[1:end-1]

nBins = length(enHi)

valuesE    = read(h1,"tallies/tally 1/results")
meansEndf  = valuesE[1,1,:]
stdEndf    = valuesE[2,1,:]

global Spbox = N.(meansEndf, stdEndf)

global meansS = meansEndf

valuesT    = read(h2,"tallies/tally 1/results")
meansTendl  = valuesT[1,1,:]
stdTendl    = valuesT[2,1,:]

global meansT = meansTendl

global Tpbox = N.(meansTendl, stdTendl)

println("Loading Sandy Data...")
for i = 2:NouterS
    
    valuesE = h5read("$(statePointDirSandy)/statepoint.$(i).h5","tallies/tally 1/results")
    meansEndf  = valuesE[1,1,:]
    stdEndf    = valuesE[2,1,:]
    thisBox    = N.(meansEndf, stdEndf)
    global Spbox = env.(Spbox, thisBox)
    global meansS = meansS + meansEndf
end

meansS = meansS / NouterS

println("Loading Tendl Data...")
for i = 1:NouterT

    valuesT = h5read("$(statePointDirTendl)/statepoint.$(i).h5","tallies/tally 1/results")
    meansTendl  = valuesT[1,1,:]
    stdTendl    = valuesT[2,1,:]
    thisBox     = N.(meansTendl, stdTendl)
    global Tpbox = env.(Tpbox, thisBox)
    global meansT = meansT + meansTendl
end

meansT = meansT /NouterT

if loadData

    @save "compareSave.jld2" Spbox Tpbox meansS meansT

else

    @load "compareSave.jld2" Spbox Tpbox meansS meansT

    diff = convPerfect.(Spbox, Tpbox, op=-)
    diff = (diff ./meansT) *100

    LI= 50
    dif = diff[LI:end]
    enPlot = enHi[LI:end]

    divMeans = (meansS .- meansT) ./meansT
    divMeans = divMeans[LI:end] * 100

    lower5 = left.(cut.(dif,0.05))
    upper95 = right.(cut.(dif,0.95))

    fontsize = 22
    fig = figure(figsize=(19, 15))
    ax = fig.add_subplot()

    PyPlot.step(enPlot, lower5, where = "post", color = "blue")
    PyPlot.step(enPlot, upper95, where = "post", color = "blue")

    ax.fill_between(enPlot, lower5, upper95, alpha=0.3, color ="grey", step = "post", label = "95%")

    PyPlot.step(enPlot, divMeans, color ="red", where = "post", label = "ratio of means")
    PyPlot.plot([enPlot[1],enPlot[end]],[0,0], color = "black", label = "agreement")

    PyPlot.xticks(fontsize=fontsize); PyPlot.yticks(fontsize=fontsize)
    PyPlot.legend(fontsize=fontsize)
    PyPlot.xscale("log")
    PyPlot.xlim([10^3, 1.5*10^7])
    PyPlot.xlabel("Energy [eV]", fontsize =fontsize)
    PyPlot.ylabel("\$ J_{Sandy}(E) ÷ J_{Tendl}(E) \$", fontsize=fontsize)

    PyPlot.savefig("ratioDifference.png", dpi = 1200)


    highdf = XLSX.readxlsx("$(simDir)/exp_data/OKTAV_high.xlsx")["Sheet1"][:]
    lowdf = XLSX.readxlsx("$(simDir)/exp_data/OKTAV_low.xlsx")["Sheet1"][:]
    lowdf = lowdf[1:130,:]

    leth = 1
    surf = 1
    widths = enHi - enLo

    if useLeth; leth=log.(widths) .* (widths .> 1);end
    if useSurf; surf = π * 4 * r^2; end


    lowEns = lowdf[2:end,1]  * 10e5
    highEns = highdf[2:end,1]  * 10e5

    meanLow = lowdf[2:end,2]; 
    stdLow = meanLow .* lowdf[2:end,2] / 100;

    meanHigh = highdf[2:end,2]; 
    stdHigh = meanHigh .* highdf[2:end,2] / 100;

    enIndexHigh = [searchsortedfirst(enHi,e) for e in highEns if e < enHi[end]]
    enIndexLow = [searchsortedfirst(enHi,e) for e in lowEns if e > enLo[1]]

    meanLow = meanLow[lowEns .> enLo[1]]
    stdLow = stdLow[lowEns .> enLo[1]]

    lowPb = N.(meanLow, stdLow)
    highPb = N.(meanHigh, stdHigh)

    Spbox = Spbox .* leth/surf
    Tpbox = Tpbox .* leth/surf

    meansS = meansS .* leth/surf
    meansT = meansT .* leth/surf
    #=
    diffMeansLowS = ((meansS[enIndexLow] .- meanLow) ./ meanLow ) * 100
    diffMeansHighS = ((meansS[enIndexHigh] .- meanHigh) ./ meanHigh) * 100

    diffMeansLowT = ((meansT[enIndexLow] .- meanLow) ./meanLow) * 100
    diffMeansHighT = ((meansT[enIndexHigh] .- meanHigh) ./ meanHigh) * 100

    diffLowS = (convPerfect.(Spbox[enIndexLow], lowPb, op=-) ./ meanLow) * 100
    diffHighS = (convPerfect.(Spbox[enIndexHigh], highPb, op=-) ./ meanHigh) * 100

    diffLowT = (convPerfect.(Tpbox[enIndexLow], lowPb, op=-) ./ meanLow) *100
    diffHighT = (convPerfect.(Tpbox[enIndexHigh], highPb, op=-) ./ meanHigh) *100
    =#

    diffMeansLowS = ((meansS[enIndexLow] .- meanLow) ./ meansS[enIndexLow] ) * 100
    diffMeansHighS = ((meansS[enIndexHigh] .- meanHigh) ./ meansS[enIndexHigh]) * 100

    diffMeansLowT = ((meansT[enIndexLow] .- meanLow) ./meansT[enIndexLow]) * 100
    diffMeansHighT = ((meansT[enIndexHigh] .- meanHigh) ./ meansT[enIndexHigh] ) * 100

    diffLowS = (convPerfect.(Spbox[enIndexLow], lowPb, op=-) ./ meansS[enIndexLow]) * 100
    diffHighS = (convPerfect.(Spbox[enIndexHigh], highPb, op=-) ./ meansS[enIndexHigh]) * 100

    diffLowT = (convPerfect.(Tpbox[enIndexLow], lowPb, op=-) ./ meansT[enIndexLow]) *100
    diffHighT = (convPerfect.(Tpbox[enIndexHigh], highPb, op=-) ./ meansT[enIndexHigh]) *100

    lower5LS = left.(cut.(diffLowS,0.05))
    upper95LS = right.(cut.(diffLowS,0.95))

    lower5HS = left.(cut.(diffHighS,0.05))
    upper95HS = right.(cut.(diffHighS,0.95))

    lower5LT = left.(cut.(diffLowT,0.05))
    upper95LT = right.(cut.(diffLowT,0.95))

    lower5HT = left.(cut.(diffHighT,0.05))
    upper95HT = right.(cut.(diffHighT,0.95))


    fig = figure(figsize=(19, 15))
    ax = fig.add_subplot()

    [PyPlot.plot([lowEns[i], lowEns[i]], [lower5LS[i], upper95LS[i]], alpha = 0.5, color = "red", linewidth = 1.6) for i = 1:length(lowEns)]
    [PyPlot.plot([highEns[i], highEns[i]], [lower5HS[i], upper95HS[i]], alpha = 0.5, color= "red", linewidth = 1.6) for i = 1:length(highEns)]

    [PyPlot.plot([lowEns[i], lowEns[i]], [lower5LT[i], upper95LT[i]], alpha = 0.5, color = "blue", linewidth = 1.6) for i = 1:length(lowEns)]
    [PyPlot.plot([highEns[i], highEns[i]], [lower5HT[i], upper95HT[i]], alpha = 0.5, color= "blue", linewidth = 1.6) for i = 1:length(highEns)]

    PyPlot.scatter(lowEns, diffMeansLowS, color = "red")
    PyPlot.scatter(highEns, diffMeansHighS, color = "red", label = "endf - exp")

    PyPlot.scatter(lowEns, diffMeansLowT, color = "blue")
    PyPlot.scatter(highEns, diffMeansHighT, color = "blue", label = "tendl - exp")

    #PyPlot.plot([enPlot[1],enPlot[end]],[0,0], color = "black", label = "agreement")

    PyPlot.xticks(fontsize=fontsize); PyPlot.yticks(fontsize=fontsize)

    PyPlot.xticks(fontsize=fontsize); PyPlot.yticks(fontsize=fontsize)
    PyPlot.legend(fontsize=fontsize)

    PyPlot.legend(fontsize=fontsize)
    PyPlot.xscale("log")
    #PyPlot.yscale("log")
    PyPlot.xlim([5*10^3, 5*10^7])
    PyPlot.plot([5*10^3, 5*10^7], [1,1], "black")
    PyPlot.xlabel("Energy [eV]", fontsize =fontsize)
    PyPlot.ylabel("% difference", fontsize=fontsize)

    PyPlot.savefig("ratioDifferenceToExp.png", dpi = 1200)
end