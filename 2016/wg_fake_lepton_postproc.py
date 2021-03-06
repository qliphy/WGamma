#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from  wgFakeLeptonModule import *

from PhysicsTools.NanoAODTools.postprocessing.modules.common.countHistogramsModule import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *

from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

#p=PostProcessor(".",inputFiles(),None,"wg_fake_lepton_keep_and_drop.txt",[countHistogramsModule(),wgFakeLeptonModule()],provenance=True,justcount=False,noOut=False,fwkJobReport=True, jsonInput=runsAndLumis(), outputbranchsel = "wg_fake_lepton_output_branch_selection.txt")

p=PostProcessor(".",inputFiles(),None,"wg_fake_lepton_keep_and_drop.txt",[countHistogramsModule(),wgFakeLeptonModule(),puWeight_2016(),PrefCorr()],provenance=True,justcount=False,noOut=False,fwkJobReport=True, jsonInput=runsAndLumis(), outputbranchsel = "wg_fake_lepton_output_branch_selection.txt")

p.run()

print "DONE"
