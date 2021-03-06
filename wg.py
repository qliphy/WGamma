data_driven = True
data_driven_correction = True

import json

import sys
import style

import optparse

from math import hypot, pi, sqrt, acos, cos, sin, atan2

from pprint import pprint

def deltaPhi(phi1,phi2):
    ## Catch if being called with two objects                                                                                                                        
    if type(phi1) != float and type(phi1) != int:
        phi1 = phi1.phi
    if type(phi2) != float and type(phi2) != int:
        phi2 = phi2.phi
    ## Otherwise                                                                                                                                                     
    dphi = (phi1-phi2)
    while dphi >  pi: dphi -= 2*pi
    while dphi < -pi: dphi += 2*pi
    return abs(dphi)

def deltaR(eta1,phi1,eta2=None,phi2=None):
    ## catch if called with objects                                                                                                                                  
    if eta2 == None:
        return deltaR(eta1.eta,eta1.phi,phi1.eta,phi1.phi)
    ## otherwise                                                                                                                                                     
    return hypot(eta1-eta2, deltaPhi(phi1,phi2))


dict_lumi = {"2016" : 35.9, "2017" : 41.5, "2018" : 59.6}

parser = optparse.OptionParser()


parser.add_option('--lep',dest='lep',default='both')
parser.add_option('--year',dest='year',default='all')
parser.add_option('--zveto',dest='zveto',action='store_true',default=False)
parser.add_option('--phoeta',dest='phoeta',default='both')
parser.add_option('--overflow',dest='overflow',action='store_true',default=False)
parser.add_option('--fit',dest='fit',action='store_true',default=False)
parser.add_option('--closure_test',dest='closure_test',action='store_true',default=False)
parser.add_option('--no_pdf_var_for_2017_and_2018',dest='no_pdf_var_for_2017_and_2018',action='store_true',default=False)
parser.add_option('--no_wjets_for_2017_and_2018',dest='no_wjets_for_2017_and_2018',action='store_true',default=False)
parser.add_option('--ewdim6',dest='ewdim6',action='store_true',default=False)
parser.add_option('--use_wjets_for_fake_photon',dest='use_wjets_for_fake_photon',action='store_true',default=False)
parser.add_option('--float_fake_sig_cont',dest='float_fake_sig_cont',action='store_true',default=False)
parser.add_option('--draw_ewdim6',dest='draw_ewdim6',action='store_true',default=False)
parser.add_option('--ewdim6_scaling_only',dest='ewdim6_scaling_only',action='store_true',default=False)
parser.add_option('--make_plots',dest='make_plots',action='store_true',default=False)
parser.add_option('--blind',dest='blind',action='store_true',default=False)

parser.add_option('-i',dest='inputfile')
parser.add_option('-o',dest='outputdir',default="/eos/user/a/amlevin/www/tmp/")

(options,args) = parser.parse_args()

if options.ewdim6_scaling_only and not options.ewdim6:
    assert(0)

if options.fit and not options.lep == "electron":
    assert(0)

if options.year == "2016":
    years = ["2016"]
    totallumi=dict_lumi["2016"]
elif options.year == "2017":
    years=["2017"]
    totallumi=dict_lumi["2017"]
elif options.year == "2018":
    years=["2018"]
    totallumi=dict_lumi["2018"]
elif options.year == "run2":
    years=["2016","2017","2018"]
    totallumi=dict_lumi["2016"]+dict_lumi["2017"]+dict_lumi["2018"]
else:
    assert(0)

den_pho_sel = 4

sieie_cut_2016_barrel = 0.01022
sieie_cut_2016_endcap = 0.03001
sieie_cut_2017_barrel = 0.01015
sieie_cut_2017_endcap = 0.0272
sieie_cut_2018_barrel = 0.01015
sieie_cut_2018_endcap = 0.0272

chiso_cut_2016_barrel = 1.416
chiso_cut_2016_endcap = 1.012
chiso_cut_2017_barrel = 1.141
chiso_cut_2017_endcap = 1.051
chiso_cut_2018_barrel = 1.141
chiso_cut_2018_endcap = 1.051

if options.lep == "muon":
    lepton_name = "muon"
elif options.lep == "electron":
    lepton_name = "electron"
elif options.lep == "both":
    lepton_name = "both"
else:
    assert(0)

if options.phoeta == "barrel":
    photon_eta_min = 0
    photon_eta_max = 1.5
elif options.phoeta == "endcap":
    photon_eta_min = 1.5
    photon_eta_max = 2.5
elif options.phoeta == "both":
    photon_eta_min = 0
    photon_eta_max = 2.5
else:
    assert(0)

photon_eta_cutstring = "((abs(photon_eta) < "+str(photon_eta_max)+") && (abs(photon_eta) > "+str(photon_eta_min)+"))"

f_json=open("/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt")
#f_json=open("delete_this_JSON.txt")

good_run_lumis=json.loads(f_json.read())

def get_postfilter_selection_string(syst="nominal"):
    assert(syst == "nominal" or syst == "JESUp" or syst == "JERUp")

    if syst == "nominal":
        return "(puppimet > 40)"
    elif syst == "JESUp":
        return "(puppimetJESUp > 40)"
    elif syst == "JERUp":
        return "(puppimetJERUp > 40)"
    else:
        assert(0)

def get_filter_string(year,isdata=True):
    if not isdata:
        puppimet_cutstring = "(puppimet > 40 || puppimetJESUp > 40 || puppimetJERUp > 40)"
    else:    
        puppimet_cutstring = "(puppimet > 40)"

    if options.zveto:
        zveto_cutstring = "(mlg < 60 || mlg > 120)"
    else:
        zveto_cutstring = "1"

    if options.lep == "muon":
        if year == "2016":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 25)"
        elif year == "2017":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 30)"
        elif year == "2018":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 25)"
        else:
            assert(0)
    elif options.lep == "electron":                
        if year == "2016":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 30)"
        elif year == "2017":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 35)"
        elif year == "2018":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 35)"
        else:
            assert(0)
    elif options.lep == "both":    
        if year == "2016":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && ((abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 25) || (abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 30)))"
        elif year == "2017":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && ((abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 30) || (abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 35)))"
        elif year == "2018":
            return "(" + photon_eta_cutstring+" && " + zveto_cutstring + " && " + puppimet_cutstring + " && ((abs(lepton_pdg_id) == 13 && photon_pt > 25 && lepton_pt > 25) || (abs(lepton_pdg_id) == 11 && photon_pt > 25 && lepton_pt > 35)))"
        else:
            assert(0)
    else:
        assert(0)

def pass_json(run,lumi):

    if str(run) not in good_run_lumis.keys():
        return False

    for lumi_pair in good_run_lumis[str(run)]:
        if lumi < lumi_pair[1] and lumi > lumi_pair[0]:
            return True

    return False    

import eff_scale_factor

import ROOT

ROOT.gROOT.cd()

ROOT.ROOT.EnableImplicitMT()

#when the TMinuit object is reused, the random seed is not reset after each fit, so the fit result can change when it is run on the same input 
ROOT.TMinuitMinimizer.UseStaticMinuit(False)

if options.closure_test:
    from wg_labels_closuretest import labels
else:
    from wg_labels import labels
#    from wg_labels_wjets import labels
#from wg_labels_recoil_tree import labels

mlg_fit_upper_bound = 400

#the first variable is for the ewdim6 analysis
#variables = ["photon_pt","dphilg","met","lepton_pt","lepton_eta","photon_pt","photon_eta","mlg","lepton_phi","photon_phi","njets40","mt","npvs","drlg"]
#variables_labels = ["ewdim6_photon_pt","dphilg","met","lepton_pt","lepton_eta","photon_pt","photon_eta","mlg","lepton_phi","photon_phi","njets40","mt","npvs","drlg"]

variables = ["photon_pt_overflow","detalg","dphilmet","dphilg","puppimet","lepton_pt","lepton_eta","photon_pt","photon_eta","mlg","mlg","lepton_phi","photon_phi","njets40","mt","puppimt","npvs","drlg","photon_pt","met","photon_recoil"]
variables_labels = ["ewdim6_photon_pt","detalg","dphilmet","dphilg","puppimet","lepton_pt","lepton_eta","photon_pt","photon_eta","fit_mlg","mlg","lepton_phi","photon_phi","njets40","mt","puppimt","npvs","drlg","photon_pt_20to180","met","photon_recoil"]


assert(len(variables) == len(variables_labels))

from array import array

binning_photon_pt = array('f',[400,500,600,900,1500])
#binning_photon_pt = array('f',[300,500,750,1000,1500])
#binning_photon_pt = array('f',[100,200,300,400,500,600])

n_photon_pt_bins = len(binning_photon_pt)-1

variable_definitions = [
["detalg" , "abs(lepton_eta-photon_eta)"],
["dphilmet" , "abs(lepton_phi - metphi) > TMath::Pi() ? abs(abs(lepton_phi - metphi) - 2*TMath::Pi()) : abs(lepton_phi - metphi)"],
["dphilg" , "abs(lepton_phi - photon_phi) > TMath::Pi() ? abs(abs(lepton_phi - photon_phi) - 2*TMath::Pi()) : abs(lepton_phi - photon_phi)"],
["drlg" , "sqrt(dphilg*dphilg+detalg*detalg)" ],
["photon_recoil","cos(photon_phi)*(-lepton_pt*cos(lepton_phi)-puppimet*cos(puppimetphi)) + sin(photon_phi)*(-lepton_pt*sin(lepton_phi) -puppimet*sin(puppimetphi))"],
["photon_pt_overflow","TMath::Min(float(photon_pt),float("+str(   (binning_photon_pt[n_photon_pt_bins] + binning_photon_pt[n_photon_pt_bins-1])/2) +"))"  ]
]


histogram_models = [ROOT.RDF.TH1DModel('', '', n_photon_pt_bins, binning_photon_pt ),ROOT.RDF.TH1DModel('','',16,0,6),ROOT.RDF.TH1DModel('','',16,0,pi),ROOT.RDF.TH1DModel('','',16,0,pi), ROOT.RDF.TH1DModel("met", "", 15 , 0., 300 ), ROOT.RDF.TH1DModel('lepton_pt', '', 8, 20., 180 ), ROOT.RDF.TH1DModel('lepton_eta', '', 10, -2.5, 2.5 ), ROOT.RDF.TH1DModel('', '', n_photon_pt_bins, binning_photon_pt ), ROOT.RDF.TH1DModel('photon_eta', '', 10, -2.5, 2.5 ), ROOT.RDF.TH1DModel("mlg","",mlg_fit_upper_bound/2,0,mlg_fit_upper_bound), ROOT.RDF.TH1DModel("mlg","",100,0,200),ROOT.RDF.TH1DModel("lepton_phi","",14,-3.5,3.5), ROOT.RDF.TH1DModel("photon_phi","",14,-3.5,3.5), ROOT.RDF.TH1DModel("njets40","",7,-0.5,6.5), ROOT.RDF.TH1DModel("mt","",10,0,200), ROOT.RDF.TH1DModel("puppimt","",10,0,200), ROOT.RDF.TH1DModel("npvs","",51,-0.5,50.5), ROOT.RDF.TH1DModel("drlg","",16,0,5), ROOT.RDF.TH1DModel('photon_pt', '', 8, 20., 180 ),ROOT.RDF.TH1DModel("met", "", 15 , 0., 300 ),ROOT.RDF.TH1DModel('photon_recoil', '', 20, -70., 130 )] 

assert(len(variables) == len(histogram_models))



mlg_index = 9

#ewdim6_filename = "/afs/cern.ch/work/a/amlevin/data/wg/2016/wgjetsewdim6.root.bak"
ewdim6_samples = {
"2016" : [{"xs" : 4.318, "filename" : "/afs/cern.ch/work/a/amlevin/tmp/wgjetsewdim6.root"}],
"2017" : [{"xs" : 4.318, "filename" : "/afs/cern.ch/work/a/amlevin/tmp/wgjetsewdim6.root"}],
"2018" : [{"xs" : 4.318, "filename" : "/afs/cern.ch/work/a/amlevin/tmp/wgjetsewdim6.root"}]
}

for year in years:
    for sample in ewdim6_samples[year]:
        sample["file"] = ROOT.TFile(sample["filename"])
        sample["nweightedevents"] = sample["file"].Get("nEventsGenWeighted").GetBinContent(1)

def getXaxisLabel(varname):
    if varname == "njets40":
        return "number of jets"
    elif varname == "detalg":
        return "#Delta #eta(l,g)"
    elif varname == "dphilmet":
        return "#Delta#phi(l,MET)"
    elif varname == "corrdphilmet":
        return "corrected #Delta#phi(l,MET)"
    elif varname == "drlg":
        return "#Delta R(l,g)"
    elif varname == "dphilg":
        return "#Delta#phi(l,g)"
    elif varname == "npvs":
        return "number of PVs"
    elif varname == "mt":
        return "m_{t} (GeV)"
    elif varname == "puppimt":
        return "m_{t} (GeV)"
    elif varname == "corrmt":
        return "corrected m_{t} (GeV)"
    elif varname == "mlg":
        return "m_{lg} (GeV)"
    elif varname == "puppimet":
        return "MET (GeV)"
    elif varname == "met":
        return "MET (GeV)"
    elif varname == "corrmet":
        return "corrected MET (GeV)"
    elif varname == "lepton_pt":
        return "lepton p_{T} (GeV)"
    elif varname == "lepton_eta":
        return "lepton #eta"
    elif varname == "lepton_phi":
        return "lepton #phi"
    elif varname == "photon_pt":
        return "photon p_{T} (GeV)"
    elif varname == "photon_pt_overflow":
        return "photon p_{T} (GeV)"
    elif varname == "photon_eta":
        return "photon #eta"    
    elif varname == "photon_phi":
        return "photon #phi"
    elif varname == "photon_recoil":
        return "photon recoil (GeV)"

    else:
        assert(0)

xoffsetstart = 0.0;
yoffsetstart = 0.0;
xoffset = 0.20;
yoffset = 0.05;

xpositions = [0.68,0.68,0.68,0.68,0.4,0.4,0.4,0.4,0.21,0.21,0.21,0.21]
ypositions = [0,1,2,3,0,1,2,3,0,1,2,3]

#xpositions = [0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.445,0.445,0.445,0.445,0.445,0.445,0.445,0.21,0.21,0.21,0.21,0.21,0.21,0.21]
#ypositions = [0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6]

style.GoodStyle().cd()

def set_axis_fonts(thstack, coordinate, title):

    if coordinate == "x":
        axis = thstack.GetXaxis();
    elif coordinate == "y":
        axis = thstack.GetYaxis();
    else:
        assert(0)
    
    axis.SetLabelFont  (   42)
    axis.SetLabelOffset(0.015)
    axis.SetLabelSize  (0.050)
    axis.SetNdivisions (  505)
    axis.SetTitleFont  (   42)
    axis.SetTitleOffset(  1.5)
    axis.SetTitleSize  (0.050)
    if (coordinate == "y"):
        axis.SetTitleOffset(1.6)
    axis.SetTitle(title)    

def draw_legend(x1,y1,hist,label,options):

    legend = ROOT.TLegend(x1+xoffsetstart,y1+yoffsetstart,x1+xoffsetstart + xoffset,y1+yoffsetstart + yoffset)

    legend.SetBorderSize(     0)
    legend.SetFillColor (     0)
    legend.SetTextAlign (    12)
    legend.SetTextFont  (    42)
    legend.SetTextSize  ( 0.040)

    legend.AddEntry(hist,label,options)

    legend.Draw("same")

    #otherwise the legend goes out of scope and is deleted once the function finishes
    hist.label = legend

for label in labels.keys():



    labels[label]["hists"] = {}

    labels[label]["hists-electron-id-sf-up"] = {}
    labels[label]["hists-electron-reco-sf-up"] = {}
    labels[label]["hists-muon-id-sf-up"] = {}
    labels[label]["hists-muon-iso-sf-up"] = {}
    labels[label]["hists-photon-id-sf-up"] = {}
    labels[label]["hists-pileup-up"] = {}
    labels[label]["hists-prefire-up"] = {}
    labels[label]["hists-jes-up"] = {}
    labels[label]["hists-jer-up"] = {}

    if labels[label]["syst-pdf"]:
        for i in range(0,32):
            labels[label]["hists-pdf-variation"+str(i)] = {}

    if labels[label]["syst-scale"]:
        for i in range(0,8):
            labels[label]["hists-scale-variation"+str(i)] = {}

    for i in range(len(variables)):    
        if labels[label]["color"] == None:
            continue

        labels[label]["hists"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists"][i].SetName(label+" "+variables[i])
        labels[label]["hists"][i].Sumw2()

        labels[label]["hists-pileup-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-prefire-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-jes-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-jer-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-electron-id-sf-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-electron-reco-sf-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-muon-id-sf-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-muon-iso-sf-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-photon-id-sf-up"][i] = histogram_models[i].GetHistogram()
        labels[label]["hists-pileup-up"][i].Sumw2()
        labels[label]["hists-prefire-up"][i].Sumw2()
        labels[label]["hists-electron-id-sf-up"][i].Sumw2()
        labels[label]["hists-electron-reco-sf-up"][i].Sumw2()
        labels[label]["hists-muon-id-sf-up"][i].Sumw2()
        labels[label]["hists-muon-iso-sf-up"][i].Sumw2()
        labels[label]["hists-photon-id-sf-up"][i].Sumw2()
        

        if labels[label]["syst-pdf"]:
            for j in range(0,32):
                labels[label]["hists-pdf-variation"+str(j)][i] = histogram_models[i].GetHistogram()
                labels[label]["hists-pdf-variation"+str(j)][i].Sumw2()

        if labels[label]["syst-scale"]:
            for j in range(0,8):
                labels[label]["hists-scale-variation"+str(j)][i] = histogram_models[i].GetHistogram()
                labels[label]["hists-scale-variation"+str(j)][i].Sumw2()


    for year in years:            
        for sample in labels[label]["samples"][year]:
            sample["file"] = ROOT.TFile.Open(sample["filename"])
            sample["tree"] = sample["file"].Get("Events")
            sample["nweightedevents"] = sample["file"].Get("nEventsGenWeighted").GetBinContent(1)



if "wg+jets" in labels:

    labels["wg+jets"]["hists-pass-fiducial"] = {}

    for i in range(len(variables)):    
        labels["wg+jets"]["hists-pass-fiducial"][i] = histogram_models[i].GetHistogram()
        labels["wg+jets"]["hists-pass-fiducial"][i].Sumw2()

    for year in years:            
        for sample in labels["wg+jets"]["samples"][year]:
            sample["nweightedevents_passfiducial"] = sample["file"].Get("nEventsGenWeighted_PassFidSelection").GetBinContent(1)

        if labels["wg+jets"]["syst-scale"]:
            for i in range(0,8):
                labels["wg+jets"]["samples"][year][0]["nweightedevents_qcdscaleweight"+str(i)]=labels["wg+jets"]["samples"][year][0]["file"].Get("nEventsGenWeighted_PassFidSelection_QCDScaleWeight"+str(i)).GetBinContent(1)

                if labels["wg+jets"]["samples"][year][0]["filename"] == "/afs/cern.ch/work/a/amlevin/data/wg/2016/1June2019/wgjets.root":
                    labels["wg+jets"]["samples"][year][0]["nweightedevents_qcdscaleweight"+str(i)] *= 2
                    
        if labels["wg+jets"]["syst-pdf"]:
            for i in range(1,32):
                if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                    continue
                labels["wg+jets"]["samples"][year][0]["nweightedevents_pdfweight"+str(i)]=labels["wg+jets"]["samples"][year][0]["file"].Get("nEventsGenWeighted_PassFidSelection_PDFWeight"+str(i)).GetBinContent(1)

                if labels["wg+jets"]["samples"][year][0]["filename"] == "/afs/cern.ch/work/a/amlevin/data/wg/2016/1June2019/wgjets.root":
                    labels["wg+jets"]["samples"][year][0]["nweightedevents_pdfweight"+str(i)] *= 2


#    for year in years:
#        labels["wg+jets"]["samples"][year][0]["nweightedeventspassgenselection"]=labels["wg+jets"]["samples"][year][0]["file"].Get("nWeightedEventsPassGenSelection").GetBinContent(1)
    #labels["wg+jets"]["samples"][year][0]["nweightedeventspassgenselection"]=1

    nweightedeventspassgenselection=0
    nweightedevents = 0
    for year in years:

        lumi = dict_lumi[year]

        nweightedeventspassgenselection+=labels["wg+jets"]["samples"][year][0]["nweightedevents_passfiducial"]*lumi
        nweightedevents+=labels["wg+jets"]["samples"][year][0]["nweightedevents"]*lumi

    fiducial_region_cuts_efficiency = nweightedeventspassgenselection/nweightedevents

data = {}
fake_signal_contamination = {}
fake_photon = {}
fake_photon_2016 = {}
fake_photon_alt = {}
fake_photon_stat_up = {}
fake_lepton = {}
fake_lepton_stat_down = {}
fake_lepton_stat_up = {}
double_fake = {}
double_fake_alt = {}
double_fake_stat_up = {}
e_to_p = {}
e_to_p_non_res = {}
ewdim6 = {}

data["hists"] = []
fake_signal_contamination["hists"] = []
fake_photon["hists"] = []
fake_photon_2016["hists"] = []
fake_photon_alt["hists"] = []
fake_photon_stat_up["hists"] = []
fake_lepton["hists"] = []
fake_lepton_stat_down["hists"] = []
fake_lepton_stat_up["hists"] = []
double_fake["hists"] = []
double_fake_alt["hists"] = []
double_fake_stat_up["hists"] = []
e_to_p_non_res["hists"] = []
e_to_p["hists"] = []
ewdim6["hists"] = []

for i in range(len(variables)):
    data["hists"].append(histogram_models[i].GetHistogram())
    fake_photon["hists"].append(histogram_models[i].GetHistogram())
    fake_photon_2016["hists"].append(histogram_models[i].GetHistogram())
    fake_photon_alt["hists"].append(histogram_models[i].GetHistogram())
    fake_photon_stat_up["hists"].append(histogram_models[i].GetHistogram())
    fake_lepton["hists"].append(histogram_models[i].GetHistogram())
    fake_lepton_stat_up["hists"].append(histogram_models[i].GetHistogram())
    fake_lepton_stat_down["hists"].append(histogram_models[i].GetHistogram())
    double_fake["hists"].append(histogram_models[i].GetHistogram())
    double_fake_alt["hists"].append(histogram_models[i].GetHistogram())
    double_fake_stat_up["hists"].append(histogram_models[i].GetHistogram())
    e_to_p_non_res["hists"].append(histogram_models[i].GetHistogram())
    e_to_p["hists"].append(histogram_models[i].GetHistogram())
    fake_signal_contamination["hists"].append(histogram_models[i].GetHistogram())
    ewdim6["hists"].append(histogram_models[i].GetHistogram())


for i in range(len(variables)):
    data["hists"][i].Sumw2()
    data["hists"][i].SetName("data "+variables[i])
    fake_photon["hists"][i].Sumw2()
    fake_photon_2016["hists"][i].Sumw2()
    fake_photon["hists"][i].SetName("fake photon "+variables[i])
    fake_photon_2016["hists"][i].SetName("fake photon 2016 "+variables[i])
    fake_lepton["hists"][i].Sumw2()
    fake_lepton_stat_up["hists"][i].Sumw2()
    fake_lepton_stat_down["hists"][i].Sumw2()
    fake_photon_alt["hists"][i].Sumw2()
    fake_photon_stat_up["hists"][i].Sumw2()
    double_fake["hists"][i].Sumw2()
    double_fake_alt["hists"][i].Sumw2()
    double_fake_stat_up["hists"][i].Sumw2()
    e_to_p_non_res["hists"][i].Sumw2()
    e_to_p["hists"][i].Sumw2()
    ewdim6["hists"][i].Sumw2()
    fake_signal_contamination["hists"][i].Sumw2()

c1 = ROOT.TCanvas("c1", "c1",5,50,500,500)

ROOT.gROOT.cd()

eff_scale_factor_cpp = '''

TFile photon_id_2016_sf_file("eff_scale_factors/2016/Fall17V2_2016_Medium_photons.root");
TH2F * photon_id_2016_sf = (TH2F*) photon_id_2016_sf_file.Get("EGamma_SF2D");

TFile photon_id_2017_sf_file("eff_scale_factors/2017/2017_PhotonsMedium.root");
TH2F * photon_id_2017_sf = (TH2F*) photon_id_2017_sf_file.Get("EGamma_SF2D");

TFile photon_id_2018_sf_file("eff_scale_factors/2018/2018_PhotonsMedium.root","read");
TH2F * photon_id_2018_sf = (TH2F*) photon_id_2018_sf_file.Get("EGamma_SF2D");

TFile electron_id_2016_sf_file("eff_scale_factors/2016/2016LegacyReReco_ElectronMedium_Fall17V2.root","read");
TH2F * electron_id_2016_sf = (TH2F*) electron_id_2016_sf_file.Get("EGamma_SF2D");

TFile electron_id_2017_sf_file("eff_scale_factors/2017/2017_ElectronMedium.root","read");
TH2F * electron_id_2017_sf = (TH2F*)electron_id_2017_sf_file.Get("EGamma_SF2D");

TFile electron_id_2018_sf_file("eff_scale_factors/2018/2018_ElectronMedium.root","read");
TH2F * electron_id_2018_sf = (TH2F*)electron_id_2018_sf_file.Get("EGamma_SF2D");

TFile electron_reco_2016_sf_file("eff_scale_factors/2016/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root","read");
TH2F * electron_reco_2016_sf = (TH2F*) electron_reco_2016_sf_file.Get("EGamma_SF2D");

TFile electron_reco_2017_sf_file("eff_scale_factors/2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root","read");
TH2F * electron_reco_2017_sf = (TH2F*)electron_reco_2017_sf_file.Get("EGamma_SF2D");

TFile electron_reco_2018_sf_file("eff_scale_factors/2018/egammaEffi.txt_EGM2D_updatedAll.root" ,"read");
TH2F * electron_reco_2018_sf = (TH2F*)electron_reco_2018_sf_file.Get("EGamma_SF2D");

TFile muon_iso_2016_sf_file("eff_scale_factors/2016/RunBCDEF_SF_ISO.root","read");
TH2D * muon_iso_2016_sf = (TH2D*) muon_iso_2016_sf_file.Get("NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt");

TFile muon_id_2016_sf_file("eff_scale_factors/2016/RunBCDEF_SF_ID.root","read");
TH2D * muon_id_2016_sf = (TH2D*) muon_id_2016_sf_file.Get("NUM_TightID_DEN_genTracks_eta_pt");

TFile muon_iso_2017_sf_file("eff_scale_factors/2017/RunBCDEF_SF_ISO.root","read");
TH2D * muon_iso_2017_sf = (TH2D*) muon_iso_2017_sf_file.Get("NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta");

TFile muon_id_2017_sf_file("eff_scale_factors/2017/RunBCDEF_SF_ID.root","read");
TH2D * muon_id_2017_sf = (TH2D*) muon_id_2017_sf_file.Get("NUM_TightID_DEN_genTracks_pt_abseta");

TFile muon_iso_2018_sf_file("eff_scale_factors/2018/RunABCD_SF_ISO.root","read");
TH2D * muon_iso_2018_sf = (TH2D*) muon_iso_2018_sf_file.Get("NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta");

TFile muon_id_2018_sf_file("eff_scale_factors/2018/RunABCD_SF_ID.root","read");
TH2D * muon_id_2018_sf = (TH2D*)muon_id_2018_sf_file.Get("NUM_TightID_DEN_TrackerMuons_pt_abseta");

float electron_efficiency_scale_factor(float pt, float eta, string year,bool id_err_up=false, bool reco_err_up=false) {

    TH2F * electron_reco_sf = 0;
    TH2F * electron_id_sf = 0;

    if (year == "2016") {
        electron_reco_sf = electron_reco_2016_sf;
        electron_id_sf = electron_id_2016_sf;
    }
    else if (year == "2017"){
        electron_reco_sf = electron_reco_2017_sf;
        electron_id_sf = electron_id_2017_sf;
    }
    else if (year == "2018") {
        electron_reco_sf = electron_reco_2018_sf;
        electron_id_sf = electron_id_2018_sf;
    }
    else
        assert(0);


    //the reco 2D histogram is really a 1D histogram
    float sf_id=electron_id_sf->GetBinContent(electron_id_sf->GetXaxis()->FindFixBin(eta),electron_id_sf->GetYaxis()->FindFixBin(pt));
    if (id_err_up) sf_id+=electron_id_sf->GetBinError(electron_id_sf->GetXaxis()->FindFixBin(eta),electron_id_sf->GetYaxis()->FindFixBin(pt));

    float sf_reco=electron_reco_sf->GetBinContent(electron_reco_sf->GetXaxis()->FindFixBin(eta),1);

    if (reco_err_up) sf_reco+=electron_reco_sf->GetBinError(electron_reco_sf->GetXaxis()->FindFixBin(eta),1);
    
    return sf_id*sf_reco;
}

float photon_efficiency_scale_factor(float pt,float eta,string year,bool err_up=false){

    TH2F * photon_id_sf = 0;

    if (year == "2016") photon_id_sf = photon_id_2016_sf;
    else if (year == "2017") photon_id_sf = photon_id_2017_sf;
    else if (year == "2018") photon_id_sf = photon_id_2018_sf;
    else assert(0);

    float mypt = TMath::Min(pt,float(photon_id_sf->GetYaxis()->GetBinCenter(photon_id_sf->GetNbinsY())));
    float myeta = TMath::Max(TMath::Min(eta,float(photon_id_sf->GetXaxis()->GetBinCenter(photon_id_sf->GetNbinsX()))),float(photon_id_sf->GetXaxis()->GetBinCenter(1)));

    float sf = photon_id_sf->GetBinContent(photon_id_sf->GetXaxis()->FindFixBin(myeta),photon_id_sf->GetYaxis()->FindFixBin(mypt));

    if (err_up) sf += photon_id_sf->GetBinError(photon_id_sf->GetXaxis()->FindFixBin(myeta),photon_id_sf->GetYaxis()->FindFixBin(mypt));

    return sf;
}

float muon_efficiency_scale_factor(float pt,float eta,string year,bool iso_err_up=false,bool id_err_up=false) {

    TH2D * muon_iso_sf = 0;
    TH2D * muon_id_sf = 0;

    if (year == "2016") {
        muon_iso_sf = muon_iso_2016_sf;
        muon_id_sf = muon_id_2016_sf;
    }
    else if (year == "2017") {
        muon_iso_sf = muon_iso_2017_sf;
        muon_id_sf = muon_id_2017_sf;
    }
    else if (year == "2018"){
        muon_iso_sf = muon_iso_2018_sf;
        muon_id_sf = muon_id_2018_sf;
    }
    else assert(0);

    int muon_iso_sf_xaxisbin = -1;
    int muon_iso_sf_yaxisbin = -1;

    if (year == "2016") {   
        muon_iso_sf_xaxisbin = muon_iso_sf->GetXaxis()->FindFixBin(eta);
        muon_iso_sf_yaxisbin = muon_iso_sf->GetYaxis()->FindFixBin(TMath::Min(pt,float(muon_iso_sf->GetYaxis()->GetBinCenter(muon_iso_sf->GetNbinsY()))));
    }
    else if (year == "2017") {
        muon_iso_sf_yaxisbin = muon_iso_sf->GetYaxis()->FindFixBin(abs(eta));
        muon_iso_sf_xaxisbin = muon_iso_sf->GetXaxis()->FindFixBin(TMath::Min(pt,float(muon_iso_sf->GetXaxis()->GetBinCenter(muon_iso_sf->GetNbinsX()))));
    }
    else if (year == "2018") {
        muon_iso_sf_yaxisbin = muon_iso_sf->GetYaxis()->FindFixBin(abs(eta));
        muon_iso_sf_xaxisbin = muon_iso_sf->GetXaxis()->FindFixBin(TMath::Min(pt,float(muon_iso_sf->GetXaxis()->GetBinCenter(muon_iso_sf->GetNbinsX()))));
    }
    else assert(0);

    int muon_id_sf_xaxisbin = -1;
    int muon_id_sf_yaxisbin = -1;

    if (year == "2016") {    
        muon_id_sf_xaxisbin = muon_id_sf->GetXaxis()->FindFixBin(eta);
        muon_id_sf_yaxisbin = muon_id_sf->GetYaxis()->FindFixBin(TMath::Min(pt,float(muon_id_sf->GetYaxis()->GetBinCenter(muon_id_sf->GetNbinsY()))));
    }
    else if (year == "2017") {
        muon_id_sf_yaxisbin = muon_id_sf->GetYaxis()->FindFixBin(abs(eta));
        muon_id_sf_xaxisbin = muon_id_sf->GetXaxis()->FindFixBin(TMath::Min(pt,float(muon_id_sf->GetXaxis()->GetBinCenter(muon_id_sf->GetNbinsX()))));
    }
    else if (year == "2018") {
        muon_id_sf_yaxisbin = muon_id_sf->GetYaxis()->FindFixBin(abs(eta));
        muon_id_sf_xaxisbin = muon_id_sf->GetXaxis()->FindFixBin(TMath::Min(pt,float(muon_id_sf->GetXaxis()->GetBinCenter(muon_id_sf->GetNbinsX()))));
    }
    else assert(0);

    float iso_sf = muon_iso_sf->GetBinContent(muon_iso_sf_xaxisbin,muon_iso_sf_yaxisbin);

    if (iso_err_up) iso_sf += muon_iso_sf->GetBinError(muon_iso_sf_xaxisbin,muon_iso_sf_yaxisbin);

    float id_sf = muon_id_sf->GetBinContent(muon_id_sf_xaxisbin,muon_id_sf_yaxisbin); 
    
    if (id_err_up) id_sf += muon_id_sf->GetBinError(muon_id_sf_xaxisbin,muon_id_sf_yaxisbin) ;

    return iso_sf * id_sf;

}

'''

fake_lepton_weight_cpp = '''

TFile muon_2016_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/muon_2016_frs.root");
TFile electron_2016_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/electron_2016_frs.root");

TFile muon_2017_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/muon_2017_frs.root");
TFile electron_2017_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/electron_2017_frs.root");

TFile muon_2018_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/muon_2018_frs.root");
TFile electron_2018_file("/afs/cern.ch/user/a/amlevin/wg/fake_lepton_weights/electron_2018_frs.root");

TH2D * muon_2016_fr_hist = (TH2D*)muon_2016_file.Get("muon_frs");
TH2D * electron_2016_fr_hist = (TH2D*)electron_2016_file.Get("electron_frs");
TH2D * muon_2017_fr_hist = (TH2D*)muon_2017_file.Get("muon_frs");
TH2D * electron_2017_fr_hist = (TH2D*)electron_2017_file.Get("electron_frs");
TH2D * muon_2018_fr_hist = (TH2D*)muon_2018_file.Get("muon_frs");
TH2D * electron_2018_fr_hist = (TH2D*)electron_2018_file.Get("electron_frs");

float get_fake_lepton_weight(float eta, float pt, string year, int lepton_pdg_id, string syst = "nominal")
{
    TH2D * fr_hist = 0;

    if (year == "2016" && abs(lepton_pdg_id) == 13) fr_hist = muon_2016_fr_hist;
    else if (year == "2016" && abs(lepton_pdg_id) == 11) fr_hist = electron_2016_fr_hist;
    else if (year == "2017" && abs(lepton_pdg_id) == 13) fr_hist = muon_2017_fr_hist;
    else if (year == "2017" && abs(lepton_pdg_id) == 11) fr_hist = electron_2017_fr_hist;
    else if (year == "2018" && abs(lepton_pdg_id) == 13) fr_hist = muon_2018_fr_hist;
    else if (year == "2018" && abs(lepton_pdg_id) == 11) fr_hist = electron_2018_fr_hist;
    else assert(0);

    float myeta  = TMath::Min(abs(eta),float(2.4999));
    float mypt  = TMath::Min(pt,float(44.999));

    int etabin = fr_hist->GetXaxis()->FindFixBin(myeta);
    int ptbin = fr_hist->GetYaxis()->FindFixBin(mypt);

    float prob = fr_hist->GetBinContent(etabin,ptbin);

    if (syst == "up") prob += fr_hist->GetBinError(etabin,ptbin);
    else if (syst == "down") prob -= fr_hist->GetBinError(etabin,ptbin);
    else assert(syst == "nominal");

    return prob/(1-prob);
}
'''

fake_photon_weight_cpp = '''

float get_fake_photon_weight(float eta, float pt, string year, int lepton_pdg_id, bool use_alt = false, bool stat_err_up = false)
{

    float fr = 0;
    if (year == "2016") {
       if (abs(eta) < 1.4442) {
          if (pt < 25 and pt > 20) fr = 0.7003077299250816;
          else if (pt < 30 and pt > 25) fr = 0.7491921116866056;
          else if (pt < 40 and pt > 30) fr = 0.6923424340462188;
          else if (pt < 50 and pt > 40) fr = 0.5924400615098443;
          else if (pt > 50) fr = 0.41487112738225757;
          else assert(0); 
    
       }
       else if (1.566 < abs(eta) && abs(eta) < 2.5) {
          if (pt < 25 and pt > 20) fr = 0.9250582944492323;
          else if (pt < 30 and pt > 25) fr = 0.9801218809625295;
          else if (pt < 40 and pt > 30) fr = 0.9737000530879558;
          else if (pt < 50 and pt > 40) fr = 0.931277245690856;
          else if (pt > 50) fr = 0.9554568420958437;
          else assert(0); 
       }
    }
    else if (year == "2017") {
       if (abs(eta) < 1.4442) {
          if (pt < 25 and pt > 20) fr = 0.6919941128926052;
          else if (pt < 30 and pt > 25) fr = 0.7642612688144812;
          else if (pt < 40 and pt > 30) fr = 0.7319714597093456;
          else if (pt < 50 and pt > 40) fr = 0.6565046379834663;
          else if (pt > 50) fr = 0.5082509744944883;
          else assert(0); 
    
       }
       else if (1.566 < abs(eta) && abs(eta) < 2.5) {
          if (pt < 25 and pt > 20) fr = 0.3156163737594128;
          else if (pt < 30 and pt > 25) fr = 0.34359058295934536;
          else if (pt < 40 and pt > 30) fr = 0.35025195124946745;
          else if (pt < 50 and pt > 40) fr = 0.40439061453627173;
          else if (pt > 50) fr = 0.5124493109053964;
          else assert(0); 
       }
    }
    else if (year == "2018") {
       if (abs(eta) < 1.4442) {
          if (pt < 25 and pt > 20) fr =  0.6825421960990049;
          else if (pt < 30 and pt > 25) fr = 0.7747729112544205;
          else if (pt < 40 and pt > 30) fr = 0.7527219268802551;
          else if (pt < 50 and pt > 40) fr = 0.6961865786204705;
          else if (pt > 50) fr = 0.5052867803309009;
          else assert(0); 
    
       }
       else if (1.566 < abs(eta) && abs(eta) < 2.5) {
          if (pt < 25 and pt > 20) fr =  0.2759815128517819;
          else if (pt < 30 and pt > 25) fr = 0.31879868070069095;
          else if (pt < 40 and pt > 30) fr = 0.3314147255351294;
          else if (pt < 50 and pt > 40) fr = 0.3590191199263839;
          else if (pt > 50) fr = 0.4941625832443751;
          else assert(0); 
       }
    }



    if (use_alt) {
       if (year == "2016") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.6190870499337138-0.6814886579951697;
             else if (pt < 30 and pt > 25) fr += 0.712091760366602-0.7606516857597383;
             else if (pt < 40 and pt > 30) fr += 0.8430015704496387-0.7450406087708085;
             else if (pt < 50 and pt > 40) fr += 0.6846064051376111-0.649268052437818;
             else if (pt > 50) fr += 0.4952101391384845-0.4003105171422588;
             else assert(0); 
    
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.9591923682905277-0.9592504449053858;
             else if (pt < 30 and pt > 25) fr += 1.0971187360948766-0.9282955655701293;
             else if (pt < 40 and pt > 30) fr += 1.0456798210055638-0.7828376615562467;
             else if (pt < 50 and pt > 40) fr += 1.2819914667917254-1.2397186217161777;
             else if (pt > 50) fr += 1.2637351371285357-0.9640670849112092;
             else assert(0); 
          }
       }
       else if (year == "2017") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.5430681940767117-0.7186263506266279;
             else if (pt < 30 and pt > 25) fr += 0.6053293250021909-0.8462067803611018;
             else if (pt < 40 and pt > 30) fr += 0.7996362012953444-0.7835289599562423; 
             else if (pt < 50 and pt > 40) fr += 0.816318680573053-0.6597575100160821;
             else if (pt > 50) fr += 0.5854042526160212-0.3559537538193207;
             else assert(0); 
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.4870463540350601-0.304201721544001;
             else if (pt < 30 and pt > 25) fr += 0.669910419310825-0.34921030538500225;
             else if (pt < 40 and pt > 30) fr += 0.7648489297053381-0.369744857512926;
             else if (pt < 50 and pt > 40) fr += 0.5562241273284817-0.458784939518758;
             else if (pt > 50) fr += 0.6310856585443262-0.9692844596772306;
             else assert(0); 
          }
       }
       else if (year == "2018") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.5953328151710774-0.7537195591739787;
             else if (pt < 30 and pt > 25) fr += 0.6340529159096009-0.8283002385161902;
             else if (pt < 40 and pt > 30) fr += 0.7928619828007212-0.8491210330539455;
             else if (pt < 50 and pt > 40) fr += 0.8482110690222703-0.7430790194561276;
             else if (pt > 50) fr += 0.5856752553538738-0.4673413804309628;
             else assert(0); 
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.5184638060548978-0.3441605362569155;
             else if (pt < 30 and pt > 25) fr += 0.7473648332250271-0.3466002004607558;
             else if (pt < 40 and pt > 30) fr += 0.6989525748508031-0.40835850112040833;
             else if (pt < 50 and pt > 40) fr += 0.5318051822376055-0.42837695820993127;
             else if (pt > 50) fr += 0.7985385075798461-0.4685590510894559;
             else assert(0); 
          }
       }
    }



    if (stat_err_up) {
       if (year == "2016") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.003726696434316919;
             else if (pt < 30 and pt > 25) fr += 0.008007838249636558;
             else if (pt < 40 and pt > 30) fr += 0.008433979158612695;
             else if (pt < 50 and pt > 40) fr += 0.010859005689809001;
             else if (pt > 50) fr += 0.006921188984346714;
             else assert(0); 
    
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.008385538724853942;
             else if (pt < 30 and pt > 25) fr += 0.01644968136974182;
             else if (pt < 40 and pt > 30) fr += 0.01802650090283417;
             else if (pt < 50 and pt > 40) fr += 0.029514264317711723;
             else if (pt > 50) fr += 0.03290098149767282;
             else assert(0); 
          }
       }
       else if (year == "2017") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.003385092552323846;
             else if (pt < 30 and pt > 25) fr += 0.007066861293194911;
             else if (pt < 40 and pt > 30) fr += 0.008210431530362772;
             else if (pt < 50 and pt > 40) fr += 0.011112675359727656;
             else if (pt > 50) fr += 0.008149800513402552;
             else assert(0); 
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.003526768130379223;
             else if (pt < 30 and pt > 25) fr += 0.006543586882338852;
             else if (pt < 40 and pt > 30) fr += 0.007742888937472314;
             else if (pt < 50 and pt > 40) fr += 0.014797541119452121;
             else if (pt > 50) fr += 0.01889769251249905;
             else assert(0); 
          }
       }
       else if (year == "2018") {
          if (abs(eta) < 1.4442) {
             if (pt < 25 and pt > 20) fr += 0.003045437293190333;
             else if (pt < 30 and pt > 25) fr += 0.006371299316978814;
             else if (pt < 40 and pt > 30) fr += 0.0072871968596617325;
             else if (pt < 50 and pt > 40) fr += 0.010243263327547105;
             else if (pt > 50) fr += 0.007432642816465921;
             else assert(0); 
          }
          else if (1.566 < abs(eta) && abs(eta) < 2.5) {
             if (pt < 25 and pt > 20) fr += 0.0025408616349431017;
             else if (pt < 30 and pt > 25) fr += 0.004803076104518955;
             else if (pt < 40 and pt > 30) fr += 0.0058370202697056684;
             else if (pt < 50 and pt > 40) fr += 0.010347864628364374;
             else if (pt > 50) fr += 0.014355530744851597;
             else assert(0); 
          }
       }
    }


    return fr;

}
'''

ROOT.gInterpreter.Declare(fake_lepton_weight_cpp)
ROOT.gInterpreter.Declare(fake_photon_weight_cpp)
ROOT.gInterpreter.Declare(eff_scale_factor_cpp)

if options.ewdim6:

    sm_lhe_weight = 372

    sm_lhe_weight_hist = ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt )

    sm_hist = ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt )

    cwww_reweights = [372,0,1,2,3,4,5]

    cwww_coefficients = [0.0, 10.0,-10.0,20.0,-20.0,-30.0,30.0]

    #cwww_coefficients = [0.0, 1.0,-1.0,2.0,-2.0,-3.0,3.0]

    cwww_hists = []

    cw_reweights = [372,6,7,8,9,10,11]

    cw_coefficients = [0.0, 80.0,-80.0,160.0,-160.0,240.0,-240.0]

    #cw_coefficients = [0.0, 17.0,-17.0,34.0,-34.0,51.0,-51.0]

    cw_hists = []

    cb_reweights = [372,12,13,14,15,16,17]

    cb_coefficients = [0.0, 80.0,-80.0,160.0,-160.0,240.0,-240.0]

    #cb_coefficients = [0.0, 17.0,-17.0,34.0,-34.0,51.0,-51.0]

    cb_hists = []

    cpwww_reweights = [372,18,19,20,21,22,23]

    cpwww_coefficients = [0.0, 4.0,-4.0,8.0,-8.0,12.0,-12.0]

    #cpwww_coefficients = [0.0, 0.5,-0.5,1.0,-1.0,1.5,-1.5]

    cpwww_hists = []

    cpw_reweights = [372,24,25,26,27,28,29]

    cpw_coefficients = [0.0, 40.0,-40.0,80.0,-80.0,120.0,-120.0]

    #cpw_coefficients = [0.0, 8.0,-8.0,16.0,-16.0,24.0,-24.0]

    cpw_hists = []

    for i in range(0,len(cwww_reweights)):
        cwww_hists.append(ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt ))

    for i in range(0,len(cw_reweights)):
        cw_hists.append(ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt ))

    for i in range(0,len(cb_reweights)):
        cb_hists.append(ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt ))

    for i in range(0,len(cpwww_reweights)):
        cpwww_hists.append(ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt ))

    for i in range(0,len(cpw_reweights)):
        cpw_hists.append(ROOT.TH1D('', '', n_photon_pt_bins, binning_photon_pt ))

    gen_matching_string = "(is_lepton_real == 1 && (photon_gen_matching == 4 || photon_gen_matching == 5 || photon_gen_matching == 6))"

    for year in years:    

        lumi = dict_lumi[year]

        rdf=ROOT.RDataFrame("Events",labels["wg+jets"]["samples"][year][0]["filename"])

        rinterface = rdf.Filter(get_filter_string(year) + " && " + gen_matching_string)

        rinterface = rinterface.Define("xs_weight",str(labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi/labels["wg+jets"]["samples"][year][0]["nweightedevents"]) + "*gen_weight/abs(gen_weight)")  

        rinterface = rinterface.Define("weight","xs_weight*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")    

        for variable_definition in variable_definitions:
            rinterface = rinterface.Define(variable_definition[0],variable_definition[1])

        rresultptr = rinterface.Histo1D(histogram_models[0],variables[0],"weight")

        sm_hist.Add(rresultptr.GetValue())

    sm_hist.Print("all")

    for year in years:

        lumi = dict_lumi[year]

        rdf=ROOT.RDataFrame("Events",ewdim6_samples[year][0]["filename"])

        rinterface = rdf.Filter(get_filter_string(year) + " && " + gen_matching_string)

        rinterface = rinterface.Define("xs_weight",str(ewdim6_samples[year][0]["xs"]*1000*lumi/ewdim6_samples[year][0]["nweightedevents"]) + "*gen_weight/abs(gen_weight)")  

        rinterface = rinterface.Define("weight","xs_weight*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")    

        for variable_definition in variable_definitions:
            rinterface = rinterface.Define(variable_definition[0],variable_definition[1])

        rresultptrs_cwww = []
        rresultptrs_cw = []
        rresultptrs_cb = []
        rresultptrs_cpwww = []
        rresultptrs_cpw = []

        for i in range(len(cwww_reweights)):
            rinterface = rinterface.Define("cwww_weight_"+str(i),"weight*LHEReweightingWeight["+str(cwww_reweights[i])+"]")
            rresultptrs_cwww.append(rinterface.Histo1D(histogram_models[0],variables[0],"cwww_weight_"+str(i)))
            
        for i in range(len(cw_reweights)):
            rinterface = rinterface.Define("cw_weight_"+str(i),"weight*LHEReweightingWeight["+str(cw_reweights[i])+"]")
            rresultptrs_cw.append(rinterface.Histo1D(histogram_models[0],variables[0],"cw_weight_"+str(i)))

        for i in range(len(cb_reweights)):
            rinterface = rinterface.Define("cb_weight_"+str(i),"weight*LHEReweightingWeight["+str(cb_reweights[i])+"]")
            rresultptrs_cb.append(rinterface.Histo1D(histogram_models[0],variables[0],"cb_weight_"+str(i)))

        for i in range(len(cpwww_reweights)):
            rinterface = rinterface.Define("cpwww_weight_"+str(i),"weight*LHEReweightingWeight["+str(cpwww_reweights[i])+"]")
            rresultptrs_cpwww.append(rinterface.Histo1D(histogram_models[0],variables[0],"cpwww_weight_"+str(i)))

        for i in range(len(cpw_reweights)):
            rinterface = rinterface.Define("cpw_weight_"+str(i),"weight*LHEReweightingWeight["+str(cpw_reweights[i])+"]")
            rresultptrs_cpw.append(rinterface.Histo1D(histogram_models[0],variables[0],"cpw_weight_"+str(i)))

        rinterface = rinterface.Define("sm_weight","weight*LHEReweightingWeight["+str(sm_lhe_weight)+"]")
        rresultptr_sm = rinterface.Histo1D(histogram_models[0],variables[0],"sm_weight")



        for i in range(len(cwww_reweights)):
            cwww_hists[i].Add(rresultptrs_cwww[i].GetValue())

        for i in range(len(cw_reweights)):
            cw_hists[i].Add(rresultptrs_cw[i].GetValue())

        for i in range(len(cb_reweights)):
            cb_hists[i].Add(rresultptrs_cb[i].GetValue())

        for i in range(len(cpwww_reweights)):
            cpwww_hists[i].Add(rresultptrs_cpwww[i].GetValue())

        for i in range(len(cpw_reweights)):
            cpw_hists[i].Add(rresultptrs_cpw[i].GetValue())

        sm_lhe_weight_hist.Add(rresultptr_sm.GetValue())

    cwww_scaling_outfile = ROOT.TFile("cwww_scaling.root",'recreate')
    cw_scaling_outfile = ROOT.TFile("cw_scaling.root",'recreate')
    cb_scaling_outfile = ROOT.TFile("cb_scaling.root",'recreate')
    cpwww_scaling_outfile = ROOT.TFile("cpwww_scaling.root",'recreate')
    cpw_scaling_outfile = ROOT.TFile("cpw_scaling.root",'recreate')

    cwww_hist_max = max(cwww_coefficients) + (max(cwww_coefficients) - min(cwww_coefficients))/(len(cwww_coefficients)-1)/2
    cwww_hist_min = min(cwww_coefficients) - (max(cwww_coefficients) - min(cwww_coefficients))/(len(cwww_coefficients)-1)/2

    cw_hist_max = max(cw_coefficients) + (max(cw_coefficients) - min(cw_coefficients))/(len(cw_coefficients)-1)/2
    cw_hist_min = min(cw_coefficients) - (max(cw_coefficients) - min(cw_coefficients))/(len(cw_coefficients)-1)/2

    cb_hist_max = max(cb_coefficients) + (max(cb_coefficients) - min(cb_coefficients))/(len(cb_coefficients)-1)/2
    cb_hist_min = min(cb_coefficients) - (max(cb_coefficients) - min(cb_coefficients))/(len(cb_coefficients)-1)/2

    cpwww_hist_max = max(cpwww_coefficients) + (max(cpwww_coefficients) - min(cpwww_coefficients))/(len(cpwww_coefficients)-1)/2
    cpwww_hist_min = min(cpwww_coefficients) - (max(cpwww_coefficients) - min(cpwww_coefficients))/(len(cpwww_coefficients)-1)/2

    cpw_hist_max = max(cpw_coefficients) + (max(cpw_coefficients) - min(cpw_coefficients))/(len(cpw_coefficients)-1)/2
    cpw_hist_min = min(cpw_coefficients) - (max(cpw_coefficients) - min(cpw_coefficients))/(len(cpw_coefficients)-1)/2

    sm_lhe_weight_hist.Print("all")

    cwww_scaling_hists = {}
    cw_scaling_hists = {}
    cb_scaling_hists = {}
    cpw_scaling_hists = {}
    cpwww_scaling_hists = {}

    for i in range(1,cwww_hists[0].GetNbinsX()+1):
        ROOT.gROOT.cd() #so that the histogram created in the next line is not put in a file that is closed
        cwww_scaling_hists[i]=ROOT.TH1D("ewdim6_scaling_bin_"+str(i),"ewdim6_scaling_bin_"+str(i),len(cwww_coefficients),cwww_hist_min,cwww_hist_max)

        for j in range(0,len(cwww_hists)):
            assert(sm_lhe_weight_hist.GetBinContent(i) > 0)

            cwww_scaling_hists[i].SetBinContent(cwww_scaling_hists[i].GetXaxis().FindFixBin(cwww_coefficients[j]), cwww_hists[j].GetBinContent(i)/sm_lhe_weight_hist.GetBinContent(i))
        
        cwww_scaling_outfile.cd()
        cwww_scaling_hists[i].Write()

    cwww_scaling_outfile.Close()

    for i in range(1,cw_hists[0].GetNbinsX()+1):
        cw_scaling_hists[i]=ROOT.TH1D("ewdim6_scaling_bin_"+str(i),"ewdim6_scaling_bin_"+str(i),len(cw_coefficients),cw_hist_min,cw_hist_max)

        for j in range(0,len(cw_hists)):
            assert(sm_lhe_weight_hist.GetBinContent(i) > 0)

            cw_scaling_hists[i].SetBinContent(cw_scaling_hists[i].GetXaxis().FindFixBin(cw_coefficients[j]), cw_hists[j].GetBinContent(i)/sm_lhe_weight_hist.GetBinContent(i))
            
        cw_scaling_outfile.cd()
        cw_scaling_hists[i].Write()

    cw_scaling_outfile.Close()

    for i in range(1,cb_hists[0].GetNbinsX()+1):
        ROOT.gROOT.cd() #so that the histogram created in the next line is not put in a file that is closed
        cb_scaling_hists[i]=ROOT.TH1D("ewdim6_scaling_bin_"+str(i),"ewdim6_scaling_bin_"+str(i),len(cb_coefficients),cb_hist_min,cb_hist_max);

        for j in range(0,len(cb_hists)):
            assert(sm_lhe_weight_hist.GetBinContent(i) > 0)

            cb_scaling_hists[i].SetBinContent(cb_scaling_hists[i].GetXaxis().FindFixBin(cb_coefficients[j]), cb_hists[j].GetBinContent(i)/sm_lhe_weight_hist.GetBinContent(i))
        
        cb_scaling_outfile.cd()
        cb_scaling_hists[i].Write()

    cb_scaling_outfile.Close()

    for i in range(1,cpwww_hists[0].GetNbinsX()+1):
        cpwww_scaling_hists[i]=ROOT.TH1D("ewdim6_scaling_bin_"+str(i),"ewdim6_scaling_bin_"+str(i),len(cpwww_coefficients),cpwww_hist_min,cpwww_hist_max);

        for j in range(0,len(cpwww_hists)):
            assert(sm_lhe_weight_hist.GetBinContent(i) > 0)

            cpwww_scaling_hists[i].SetBinContent(cpwww_scaling_hists[i].GetXaxis().FindFixBin(cpwww_coefficients[j]), cpwww_hists[j].GetBinContent(i)/sm_lhe_weight_hist.GetBinContent(i))
        
        cpwww_scaling_outfile.cd()
        cpwww_scaling_hists[i].Write()

    cpwww_scaling_outfile.Close()

    for i in range(1,cpw_hists[0].GetNbinsX()+1):
        cpw_scaling_hists[i]=ROOT.TH1D("ewdim6_scaling_bin_"+str(i),"ewdim6_scaling_bin_"+str(i),len(cpw_coefficients),cpw_hist_min,cpw_hist_max);

        for j in range(0,len(cpw_hists)):
            assert(sm_lhe_weight_hist.GetBinContent(i) > 0)

            cpw_scaling_hists[i].SetBinContent(cpw_scaling_hists[i].GetXaxis().FindFixBin(cpw_coefficients[j]), cpw_hists[j].GetBinContent(i)/sm_lhe_weight_hist.GetBinContent(i))
        
        cpw_scaling_outfile.cd()
        cpw_scaling_hists[i].Write()

    cpw_scaling_outfile.Close()

if options.ewdim6_scaling_only:
    sys.exit(1)

data_mlg_tree = ROOT.TTree()

array_data_mlg=array('f',[0])

data_mlg_tree.Branch('m',array_data_mlg,'m/F')

for year in years:

    if year == "2016":
        lumi=35.9
    elif year == "2017":
        lumi=41.5
    elif year == "2018":
        lumi=59.6
    else:
        assert(0)

    if lepton_name == "muon":
        if not options.closure_test:
            data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/single_muon.root"
        else:
            data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/wjets.root"
    elif lepton_name == "electron":
        if not options.closure_test:
            if year != "2018":
                data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/single_electron.root"
            else:    
                data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/egamma.root"
        else:
            data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/wjets.root"
    elif lepton_name == "both":
        if not options.closure_test:
            if year != "2018":
                data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/data.root"
            else:
                data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/data.root"
        else:
            data_filename = "/afs/cern.ch/work/a/amlevin/data/wg/"+year+"/1June2019/wjets.root"
    else:
        assert(0)

    if year == "2016":
        sieie_cut_barrel = sieie_cut_2016_barrel
        sieie_cut_endcap = sieie_cut_2016_endcap
        chiso_cut_barrel = chiso_cut_2016_barrel
        chiso_cut_endcap = chiso_cut_2016_endcap
    elif year == "2017":
        sieie_cut_barrel = sieie_cut_2017_barrel
        sieie_cut_endcap = sieie_cut_2017_endcap
        chiso_cut_barrel = chiso_cut_2017_barrel
        chiso_cut_endcap = chiso_cut_2017_endcap
    elif year == "2018":
        sieie_cut_barrel = sieie_cut_2018_barrel
        sieie_cut_endcap = sieie_cut_2018_endcap
        chiso_cut_barrel = chiso_cut_2018_barrel
        chiso_cut_endcap = chiso_cut_2018_endcap
    else:
        assert(0)

    fake_photon_sieie_cut_barrel = sieie_cut_barrel*1.75
    fake_photon_sieie_cut_endcap = sieie_cut_endcap*1.75
    fake_photon_chiso_cut_barrel = chiso_cut_barrel*1000
    fake_photon_chiso_cut_endcap = chiso_cut_endcap*1000    

    print "Running over "+year+" data"

    rdf=ROOT.RDataFrame("Events",data_filename)

    rinterface = rdf.Filter(get_filter_string(year))

    fake_photon_sieie_cut_cutstring = "((abs(photon_eta) < 1.5 && photon_sieie < "+str(fake_photon_sieie_cut_barrel)+ ") || (abs(photon_eta) > 1.5 && photon_sieie < "+str(fake_photon_sieie_cut_endcap)+ "))" 

    fake_photon_chiso_cut_cutstring = "((abs(photon_eta) < 1.5 && photon_pfRelIso03_chg*photon_pt < "+str(fake_photon_chiso_cut_barrel)+ ") || (abs(photon_eta) > 1.5 && photon_pfRelIso03_chg*photon_pt < "+str(fake_photon_chiso_cut_endcap)+ "))" 

    rinterface = rinterface.Define("weight","photon_selection == 0 && is_lepton_tight == 1")
    rinterface = rinterface.Define("fake_lepton_weight","photon_selection == 0 && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id) : 0")
    rinterface = rinterface.Define("fake_lepton_stat_up_weight","photon_selection == 0 && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id,\"up\") : 0")
    rinterface = rinterface.Define("fake_lepton_stat_down_weight","photon_selection == 0 && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id,\"down\") : 0")
    rinterface = rinterface.Define("fake_photon_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id) : 0")
    rinterface = rinterface.Define("fake_photon_alt_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,true) : 0")
    rinterface = rinterface.Define("fake_photon_stat_up_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,false,true) : 0")
    rinterface = rinterface.Define("double_fake_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id) : 0") 
    rinterface = rinterface.Define("double_fake_alt_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,true) : 0") 
    rinterface = rinterface.Define("double_fake_stat_up_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,false,true) : 0") 

    if options.closure_test:
        if year == "2016" or year == "2017":    
            prefire_weight_string = "PrefireWeight"
        else:    
            prefire_weight_string = "1"

        data_file = ROOT.TFile.Open(data_filename)
        data_nweightedevents = data_file.Get("nEventsGenWeighted").GetBinContent(1)
        rinterface = rinterface.Define("closure_test_fake_photon_weight","fake_photon_weight*"+prefire_weight_string+"*puWeight*(!(photon_gen_matching == 1|| photon_gen_matching == 4 || photon_gen_matching == 5 || photon_gen_matching == 6) && is_lepton_real == 1)*gen_weight/abs(gen_weight)*60430.0*1000*"+str(lumi)+"/"+str(data_nweightedevents)+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")
        rinterface = rinterface.Define("closure_test_weight","weight*"+prefire_weight_string+"*puWeight*(!(photon_gen_matching == 1 || photon_gen_matching == 4 || photon_gen_matching == 5 || photon_gen_matching == 6) && is_lepton_real == 1)*gen_weight/abs(gen_weight)*60430.0*1000*"+str(lumi)+"/"+str(data_nweightedevents)+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")

    for variable_definition in variable_definitions:
            rinterface = rinterface.Define(variable_definition[0],variable_definition[1])

    rresultptrs = []    
    rresultptrs_fake_photon = []    
    rresultptrs_fake_photon_alt = []    
    rresultptrs_fake_photon_stat_up = []    
    rresultptrs_fake_lepton = []    
    rresultptrs_fake_lepton_stat_up = []    
    rresultptrs_fake_lepton_stat_down = []    
    rresultptrs_double_fake = []    
    rresultptrs_double_fake_alt = []    
    rresultptrs_double_fake_stat_up = []    

    for i in range(len(variables)):
        if options.closure_test:
            rresultptrs.append(rinterface.Histo1D(histogram_models[i],variables[i],"closure_test_weight"))
            rresultptrs_fake_photon.append(rinterface.Histo1D(histogram_models[i],variables[i],"closure_test_fake_photon_weight"))
        else:    
            rresultptrs_fake_photon.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_weight"))
            rresultptrs.append(rinterface.Histo1D(histogram_models[i],variables[i],"weight"))
        rresultptrs_fake_photon_alt.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_alt_weight"))
        rresultptrs_fake_photon_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_stat_up_weight"))
        rresultptrs_fake_lepton.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_weight"))
        rresultptrs_fake_lepton_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_stat_up_weight"))
        rresultptrs_fake_lepton_stat_down.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_stat_down_weight"))
        rresultptrs_double_fake.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_weight"))
        rresultptrs_double_fake_alt.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_alt_weight"))
        rresultptrs_double_fake_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_stat_up_weight"))

    for i in range(len(variables)):
        data["hists"][i].Add(rresultptrs[i].GetValue())
        if year == "2016":    
            fake_photon_2016["hists"][i].Add(rresultptrs_fake_photon[i].GetValue())
        fake_photon["hists"][i].Add(rresultptrs_fake_photon[i].GetValue())

        if options.closure_test:
            continue

        fake_photon_alt["hists"][i].Add(rresultptrs_fake_photon_alt[i].GetValue())
        fake_photon_stat_up["hists"][i].Add(rresultptrs_fake_photon_stat_up[i].GetValue())
        fake_lepton["hists"][i].Add(rresultptrs_fake_lepton[i].GetValue())
        fake_lepton_stat_up["hists"][i].Add(rresultptrs_fake_lepton_stat_up[i].GetValue())
        fake_lepton_stat_down["hists"][i].Add(rresultptrs_fake_lepton_stat_down[i].GetValue())
        double_fake["hists"][i].Add(rresultptrs_double_fake[i].GetValue())
        double_fake_alt["hists"][i].Add(rresultptrs_double_fake_alt[i].GetValue())
        double_fake_stat_up["hists"][i].Add(rresultptrs_double_fake_stat_up[i].GetValue())
        rresultptrs_double_fake[i].GetPtr().Scale(-1)
        rresultptrs_double_fake_alt[i].GetPtr().Scale(-1)
        if year == "2016":    
            fake_photon_2016["hists"][i].Add(rresultptrs_double_fake[i].GetValue())
        fake_photon["hists"][i].Add(rresultptrs_double_fake[i].GetValue())
        fake_photon_alt["hists"][i].Add(rresultptrs_double_fake_alt[i].GetValue())
        fake_lepton["hists"][i].Add(rresultptrs_double_fake[i].GetValue())


hists = []

for year in years:
    for label in labels.keys():

        if label == "w+jets" and (year == "2017" or year == "2018") and options.no_wjets_for_2017_and_2018:
            continue

        if year == "2016":
            lumi=35.9
        elif year == "2017":
            lumi=41.5
        elif year == "2018":
            lumi=59.6
        else:
            assert(0)

        if year == "2016":
            sieie_cut_barrel = sieie_cut_2016_barrel
            sieie_cut_endcap = sieie_cut_2016_endcap
            chiso_cut_barrel = chiso_cut_2016_barrel
            chiso_cut_endcap = chiso_cut_2016_endcap
        elif year == "2017":
            sieie_cut_barrel = sieie_cut_2017_barrel
            sieie_cut_endcap = sieie_cut_2017_endcap
            chiso_cut_barrel = chiso_cut_2017_barrel
            chiso_cut_endcap = chiso_cut_2017_endcap
        elif year == "2018":
            sieie_cut_barrel = sieie_cut_2018_barrel
            sieie_cut_endcap = sieie_cut_2018_endcap
            chiso_cut_barrel = chiso_cut_2018_barrel
            chiso_cut_endcap = chiso_cut_2018_endcap
        else:
            assert(0)

        fake_photon_sieie_cut_barrel = sieie_cut_barrel*1.75
        fake_photon_sieie_cut_endcap = sieie_cut_endcap*1.75
        fake_photon_chiso_cut_barrel = chiso_cut_barrel*1000
        fake_photon_chiso_cut_endcap = chiso_cut_endcap*1000    

        for sample in labels[label]["samples"][year]:
            print "Running over sample " + str(sample["filename"])

            photon_gen_matching_for_fake_cutstring = "("
            photon_gen_matching_cutstring = "("

            if sample["fsr"]:
                photon_gen_matching_for_fake_cutstring+="photon_gen_matching == 4"
                photon_gen_matching_cutstring+="photon_gen_matching == 4"
            if sample["non_fsr"]:  
                if photon_gen_matching_for_fake_cutstring != "(":
                    photon_gen_matching_for_fake_cutstring += " || "
                if photon_gen_matching_cutstring != "(":
                    photon_gen_matching_cutstring += " || "
                photon_gen_matching_for_fake_cutstring+="photon_gen_matching == 5 || photon_gen_matching == 6"
                photon_gen_matching_cutstring+="photon_gen_matching == 5 || photon_gen_matching == 6"
            if sample["e_to_p_for_fake"]:
                if photon_gen_matching_for_fake_cutstring != "(":
                    photon_gen_matching_for_fake_cutstring += " || "
                photon_gen_matching_for_fake_cutstring+="photon_gen_matching == 1"
            if sample["non-prompt"]:
                pass
                if photon_gen_matching_cutstring != "(":
                    photon_gen_matching_cutstring += " || "
                photon_gen_matching_cutstring+="!(photon_gen_matching == 1 || photon_gen_matching == 4 || photon_gen_matching == 5 || photon_gen_matching == 6)"
                
            if photon_gen_matching_for_fake_cutstring != "(":    
                photon_gen_matching_for_fake_cutstring+= ")"    
            else:
                photon_gen_matching_for_fake_cutstring= "0"    

            if photon_gen_matching_cutstring != "(":    
                photon_gen_matching_cutstring+= ")"    
            else:
                photon_gen_matching_cutstring= "0"    

            rdf = ROOT.RDataFrame("Events",sample["filename"])

            #the JERUp and JESUp information was not added to the w+jets sample
            if  label != "w+jets":
                rinterface = rdf.Filter(get_filter_string(year,isdata=False))
            else:    
                rinterface = rdf.Filter(get_filter_string(year,isdata=True))

            rinterface = rinterface.Define("xs_weight",str(sample["xs"]*1000*lumi/sample["nweightedevents"]) + "*gen_weight/abs(gen_weight)") 

            if year == "2016" or year == "2017":    
                prefire_weight_string = "PrefireWeight"
                prefire_up_weight_string = "PrefireWeight_Up"
            else:    
                prefire_weight_string = "1"
                prefire_up_weight_string = "1"

            rinterface = rinterface.Define("base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")      
            rinterface = rinterface.Define("prefire_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_up_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")    
            rinterface = rinterface.Define("pileup_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeightUp*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")    
            rinterface = rinterface.Define("electron_id_sf_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\",true))")                  
            rinterface = rinterface.Define("electron_reco_sf_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\",false,true))")    
            rinterface = rinterface.Define("muon_id_sf_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\",false,true) : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")                  
            rinterface = rinterface.Define("muon_iso_sf_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\")*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\",true) : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))")    
            rinterface = rinterface.Define("photon_id_sf_up_base_weight",get_postfilter_selection_string()+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\",true)*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))") 
            if label != "w+jets":
                rinterface = rinterface.Define("jes_up_base_weight",get_postfilter_selection_string("JESUp")+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\",true)*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))") 
                rinterface = rinterface.Define("jer_up_base_weight",get_postfilter_selection_string("JERUp")+"*xs_weight*puWeight*"+prefire_weight_string+"*photon_efficiency_scale_factor(photon_pt,photon_eta,\""+year+"\",true)*(abs(lepton_pdg_id) == 13 ? muon_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\") : electron_efficiency_scale_factor(lepton_pt,lepton_eta,\""+year+"\"))") 

            rinterface = rinterface.Define("weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*base_weight")

            if label == "wg+jets":
                rinterface = rinterface.Define("weight_pass_fiducial","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + " && pass_fiducial)*base_weight")


            rinterface = rinterface.Define("pileup_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*pileup_up_base_weight")
            rinterface = rinterface.Define("prefire_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*prefire_up_base_weight")
            rinterface = rinterface.Define("electron_id_sf_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*electron_id_sf_up_base_weight")
            rinterface = rinterface.Define("electron_reco_sf_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*electron_reco_sf_up_base_weight")
            rinterface = rinterface.Define("muon_id_sf_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*muon_id_sf_up_base_weight")
            rinterface = rinterface.Define("muon_iso_sf_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*muon_iso_sf_up_base_weight")
            rinterface = rinterface.Define("photon_id_sf_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*photon_id_sf_up_base_weight")

            if label != "w+jets":
                rinterface = rinterface.Define("jes_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*jes_up_base_weight")
                rinterface = rinterface.Define("jer_up_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*jer_up_base_weight")

            if labels[label]["syst-scale"]:
                for i in range(0,8):
                     #this sample has a bug that causes the scale weight to be 1/2 the correct value
                    if sample["filename"] == "/afs/cern.ch/work/a/amlevin/data/wg/2016/1June2019/wgjets.root":
                        rinterface = rinterface.Define("scale"+str(i)+"_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*base_weight*LHEScaleWeight["+str(i)+"]*2")
                    else:    
                        rinterface = rinterface.Define("scale"+str(i)+"_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*base_weight*LHEScaleWeight["+str(i)+"]")

            if labels[label]["syst-pdf"]:
                for i in range(0,32):
                    if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                        continue
                    #this sample has a bug that causes the scale weight to be 1/2 the correct value
                    if sample["filename"] == "/afs/cern.ch/work/a/amlevin/data/wg/2016/1June2019/wgjets.root":
                        rinterface = rinterface.Define("pdf"+str(i)+"_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*base_weight*LHEPdfWeight["+str(i+1)+"]*2")
                    else:    
                        rinterface = rinterface.Define("pdf"+str(i)+"_weight","(photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_cutstring + ")*base_weight*LHEPdfWeight["+str(i+1)+"]")

            fake_photon_sieie_cut_cutstring = "((abs(photon_eta) < 1.5 && photon_sieie < "+str(fake_photon_sieie_cut_barrel)+ ") || (abs(photon_eta) > 1.5 && photon_sieie < "+str(fake_photon_sieie_cut_endcap)+ "))" 

            fake_photon_chiso_cut_cutstring = "((abs(photon_eta) < 1.5 && photon_pfRelIso03_chg*photon_pt < "+str(fake_photon_chiso_cut_barrel)+ ") || (abs(photon_eta) > 1.5 && photon_pfRelIso03_chg*photon_pt < "+str(fake_photon_chiso_cut_endcap)+ "))" 

#            rinterface = rinterface.Define("fake_lepton_weight","photon_selection == 0 && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*base_weight : 0")
#            rinterface = rinterface.Define("fake_photon_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id)*base_weight : 0")
#            rinterface = rinterface.Define("double_fake_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id)*base_weight : 0") 

            rinterface = rinterface.Define("fake_lepton_weight","photon_selection == 0 && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("fake_lepton_stat_up_weight","photon_selection == 0 && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id,\"up\")*xs_weight*puWeight*"+prefire_weight_string + "*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("fake_lepton_stat_down_weight","photon_selection == 0 && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id,\"down\")*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("fake_photon_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("fake_photon_alt_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,true)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("fake_photon_stat_up_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 1 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,false,true)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0")
            rinterface = rinterface.Define("double_fake_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0") 
            rinterface = rinterface.Define("double_fake_alt_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,true)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0") 
            rinterface = rinterface.Define("double_fake_stat_up_weight","photon_selection == 4 && "+fake_photon_sieie_cut_cutstring + " && " + fake_photon_chiso_cut_cutstring+" && is_lepton_tight == 0 && is_lepton_real == 1 && "+photon_gen_matching_for_fake_cutstring+" ? get_fake_lepton_weight(lepton_eta,lepton_pt,\""+year+"\",lepton_pdg_id)*get_fake_photon_weight(photon_eta,photon_pt,\""+year+"\",lepton_pdg_id,false,true)*xs_weight*puWeight*"+prefire_weight_string+"*" + get_postfilter_selection_string()+" : 0") 

            if sample["e_to_p"]:
                rinterface = rinterface.Define("e_to_p_weight","photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && photon_gen_matching == 1 ? base_weight : 0")
                
            if sample["e_to_p_non_res"]:
                rinterface = rinterface.Define("e_to_p_non_res_weight","photon_selection == 0 && is_lepton_tight == 1 && is_lepton_real == 1 && photon_gen_matching == 1 ? base_weight : 0") 

            for variable_definition in variable_definitions:
                rinterface = rinterface.Define(variable_definition[0],variable_definition[1])


            if labels[label]["syst-scale"]:
                rresultptrs_scale = []    
                for i in range(0,8):
                    rresultptrs_scale.append([])    
                    
            if labels[label]["syst-pdf"]:
                rresultptrs_pdf = []    
                for i in range(0,32):
                    if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                        continue
                    rresultptrs_pdf.append([])    

            rresultptrs = []    
            rresultptrs_fake_photon = []    
            rresultptrs_fake_photon_alt = []    
            rresultptrs_fake_photon_stat_up = []    
            rresultptrs_fake_lepton = []    
            rresultptrs_fake_lepton_stat_up = []    
            rresultptrs_fake_lepton_stat_down = []    
            rresultptrs_double_fake = []    
            rresultptrs_double_fake_alt = []    
            rresultptrs_double_fake_stat_up = []    
            rresultptrs_pileup_up = []
            rresultptrs_prefire_up = []    
            if label != "w+jets":
                rresultptrs_jes_up = []    
                rresultptrs_jer_up = []    
            rresultptrs_electron_id_sf_up = []    
            rresultptrs_electron_reco_sf_up = []    
            rresultptrs_muon_id_sf_up = []    
            rresultptrs_muon_iso_sf_up = []    
            rresultptrs_photon_id_sf_up = []    
            if sample["e_to_p"]:
                rresultptrs_e_to_p = []    
            if sample["e_to_p_non_res"]:
                rresultptrs_e_to_p_non_res = []    
            if label == "wg+jets":
                rresultptrs_pass_fiducial = []    


            for i in range(len(variables)):
                if labels[label]["color"] != None:
                    rresultptrs.append(rinterface.Histo1D(histogram_models[i],variables[i],"weight"))
                    rresultptrs_pileup_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"pileup_up_weight"))
                    rresultptrs_prefire_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"prefire_up_weight"))
                    rresultptrs_electron_id_sf_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"electron_id_sf_up_weight"))
                    rresultptrs_electron_reco_sf_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"electron_reco_sf_up_weight"))
                    rresultptrs_muon_id_sf_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"muon_id_sf_up_weight"))
                    rresultptrs_muon_iso_sf_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"muon_iso_sf_up_weight"))
                    rresultptrs_photon_id_sf_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"photon_id_sf_up_weight"))
                    if label == "wg+jets":
                        rresultptrs_pass_fiducial.append(rinterface.Histo1D(histogram_models[i],variables[i],"weight_pass_fiducial"))
                    if label != "w+jets":
                        rresultptrs_jes_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"jes_up_weight"))
                        rresultptrs_jer_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"jer_up_weight"))

                rresultptrs_fake_photon.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_weight"))
                rresultptrs_fake_photon_alt.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_alt_weight"))
                rresultptrs_fake_photon_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_photon_stat_up_weight"))
                rresultptrs_fake_lepton.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_weight"))
                rresultptrs_fake_lepton_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_stat_up_weight"))
                rresultptrs_fake_lepton_stat_down.append(rinterface.Histo1D(histogram_models[i],variables[i],"fake_lepton_stat_down_weight"))
                rresultptrs_double_fake.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_weight"))
                rresultptrs_double_fake_alt.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_alt_weight"))
                rresultptrs_double_fake_stat_up.append(rinterface.Histo1D(histogram_models[i],variables[i],"double_fake_stat_up_weight"))

                if labels[label]["syst-scale"]:
                    for j in range(0,8):
                        rresultptrs_scale[j].append(rinterface.Histo1D(histogram_models[i],variables[i],"scale"+str(j)+"_weight"))
                if labels[label]["syst-pdf"]:
                    for j in range(0,32):
                        if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                            continue
                        rresultptrs_pdf[j].append(rinterface.Histo1D(histogram_models[i],variables[i],"pdf"+str(j)+"_weight"))

                if sample["e_to_p"]:
                    rresultptrs_e_to_p.append(rinterface.Histo1D(histogram_models[i],variables[i],"e_to_p_weight"))
                if sample["e_to_p_non_res"]:
                    rresultptrs_e_to_p_non_res.append(rinterface.Histo1D(histogram_models[i],variables[i],"e_to_p_non_res_weight"))

            for i in range(len(variables)):
                if labels[label]["color"] != None:
                    labels[label]["hists"][i].Add(rresultptrs[i].GetValue())
                    labels[label]["hists-pileup-up"][i].Add(rresultptrs_pileup_up[i].GetValue())
                    labels[label]["hists-prefire-up"][i].Add(rresultptrs_prefire_up[i].GetValue())
                    labels[label]["hists-electron-id-sf-up"][i].Add(rresultptrs_electron_id_sf_up[i].GetValue())
                    labels[label]["hists-electron-reco-sf-up"][i].Add(rresultptrs_electron_reco_sf_up[i].GetValue())
                    labels[label]["hists-muon-id-sf-up"][i].Add(rresultptrs_muon_id_sf_up[i].GetValue())
                    labels[label]["hists-muon-iso-sf-up"][i].Add(rresultptrs_muon_iso_sf_up[i].GetValue())
                    labels[label]["hists-photon-id-sf-up"][i].Add(rresultptrs_photon_id_sf_up[i].GetValue())
                    if label == "wg+jets":
                        labels[label]["hists-pass-fiducial"][i].Add(rresultptrs_pass_fiducial[i].GetValue())
                    if label != "w+jets":
                        labels[label]["hists-jes-up"][i].Add(rresultptrs_jes_up[i].GetValue())
                        labels[label]["hists-jer-up"][i].Add(rresultptrs_jer_up[i].GetValue())
                        

            for i in range(len(variables)):
                rresultptrs_fake_photon[i].Scale(-1)
                rresultptrs_fake_lepton[i].Scale(-1)
                rresultptrs_fake_photon_alt[i].Scale(-1)
                rresultptrs_fake_photon_stat_up[i].Scale(-1)

                if labels[label]["syst-scale"]:
                    for j in range(0,8):
                         labels[label]["hists-scale-variation"+str(j)][i].Add(rresultptrs_scale[j][i].GetValue())

                if labels[label]["syst-pdf"]:
                    for j in range(0,32):
                        if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                            continue
                        labels[label]["hists-pdf-variation"+str(j)][i].Add(rresultptrs_pdf[j][i].GetValue())

                if label == "wg+jets":
                    fake_signal_contamination["hists"][i].Add(rresultptrs_fake_lepton[i].GetValue())
                    fake_signal_contamination["hists"][i].Add(rresultptrs_fake_photon[i].GetValue())
                    fake_signal_contamination["hists"][i].Add(rresultptrs_double_fake[i].GetValue())

                    
                if year == "2016":    
                    fake_photon_2016["hists"][i].Add(rresultptrs_fake_photon[i].GetValue())
                fake_photon["hists"][i].Add(rresultptrs_fake_photon[i].GetValue())
                fake_photon_alt["hists"][i].Add(rresultptrs_fake_photon_alt[i].GetValue())
                fake_photon_stat_up["hists"][i].Add(rresultptrs_fake_photon_stat_up[i].GetValue())
                fake_lepton["hists"][i].Add(rresultptrs_fake_lepton[i].GetValue())
                fake_lepton_stat_up["hists"][i].Add(rresultptrs_fake_lepton_stat_up[i].GetValue())
                fake_lepton_stat_down["hists"][i].Add(rresultptrs_fake_lepton_stat_down[i].GetValue())
                double_fake["hists"][i].Add(rresultptrs_double_fake[i].GetValue())
                double_fake_alt["hists"][i].Add(rresultptrs_double_fake_alt[i].GetValue())
                double_fake_stat_up["hists"][i].Add(rresultptrs_double_fake_stat_up[i].GetValue())
                if sample["e_to_p"]:
                    e_to_p["hists"][i].Add(rresultptrs_e_to_p[i].GetValue())

                if sample["e_to_p_non_res"]:
                    e_to_p_non_res["hists"][i].Add(rresultptrs_e_to_p_non_res[i].GetValue())
                
        for i in range(len(variables)):    

            if labels[label]["color"] == None:
                continue

            labels[label]["hists"][i].SetFillColor(labels[label]["color"])
            labels[label]["hists"][i].SetFillStyle(1001)
            labels[label]["hists"][i].SetLineColor(labels[label]["color"])

for hist in hists:
    hists.Print("all")

def mlg_fit(inputs):

    print "inputs[\"label\"] = "+str(inputs["label"])

    m= ROOT.RooRealVar("m","m",0,mlg_fit_upper_bound)
    m0=ROOT.RooRealVar("m0",    "m0",2.48320,-4,4)
    sigma=ROOT.RooRealVar("sigma",  "sigma",1.75029,0.1,3)
    alpha=ROOT.RooRealVar("alpha",  "alpha",2.48320,0,10)
#    alpha=ROOT.RooRealVar("alpha",  "alpha",4.45779,4.45779-2,4.45779+2)
#    alpha=ROOT.RooRealVar("alpha",  "alpha",,0,10)
#    alpha=ROOT.RooRealVar("alpha",  "alpha",4.27560,4.27560,4.27560)
#    n=ROOT.RooRealVar("n",          "n",2.11960,1,3)
    n=ROOT.RooRealVar("n",          "n",2.11960,2.11960,2.11960)
    cb = ROOT.RooCBShape("cb", "Crystal Ball", m, m0, sigma, alpha, n)

    mass = ROOT.RooRealVar("mass","mass",91.9311,89.855-5,89.855+5)
    width = ROOT.RooRealVar("width","width",3.3244,0.5*3.3244/4.0,10*3.3244/3.0);
    bw = ROOT.RooBreitWigner("bw","Breit Wigner",m,mass,width)

    RooFFTConvPdf_bwcb = ROOT.RooFFTConvPdf("bwcb","Breit Wigner convolved with a Crystal Ball",m,bw,cb)

    RooDataSet_mlg_data = ROOT.RooDataSet("data","dataset",data_mlg_tree,ROOT.RooArgSet(m))
    RooDataHist_mlg_data = ROOT.RooDataHist("data","dataset",ROOT.RooArgList(m),inputs["data"])

    RooDataHist_mlg_wg = ROOT.RooDataHist("wg data hist","wg data hist",ROOT.RooArgList(m),inputs["wg"])
    RooHistPdf_wg = ROOT.RooHistPdf("wg","wg",ROOT.RooArgSet(m),RooDataHist_mlg_wg)

    wg_plus_fake_wg_contamination_hist = inputs["wg"].Clone("wg plus fake wg contamination hist")
    wg_plus_fake_wg_contamination_hist.Add(inputs["fake-wg-contamination"])

    RooDataHist_mlg_wg_plus_fake_wg_contamination = ROOT.RooDataHist("wg plus fake wg contamination","wg plus fake wg contamination",ROOT.RooArgList(m),wg_plus_fake_wg_contamination_hist)
    RooHistPdf_wg_plus_fake_wg_contamination = ROOT.RooHistPdf("wg plus fake wg contamination","wg plus fake wg contamination",ROOT.RooArgSet(m),RooDataHist_mlg_wg_plus_fake_wg_contamination)

    RooDataHist_mlg_vv = ROOT.RooDataHist("vv data hist","vv data hist",ROOT.RooArgList(m),inputs["vv"])
    RooHistPdf_vv = ROOT.RooHistPdf("vv","vv",ROOT.RooArgSet(m),RooDataHist_mlg_vv)

    RooDataHist_mlg_top = ROOT.RooDataHist("top data hist","top data hist",ROOT.RooArgList(m),inputs["top"])
    RooHistPdf_top = ROOT.RooHistPdf("top","top",ROOT.RooArgSet(m),RooDataHist_mlg_top)

    RooDataHist_mlg_zg = ROOT.RooDataHist("zg data hist","zg data hist",ROOT.RooArgList(m),inputs["zg"])
    RooHistPdf_zg = ROOT.RooHistPdf("zg","zg",ROOT.RooArgSet(m),RooDataHist_mlg_zg)

    RooDataHist_mlg_fake_lepton = ROOT.RooDataHist("fake lepton","fake lepton",ROOT.RooArgList(m),inputs["fake_lepton"])
    RooHistPdf_fake_lepton = ROOT.RooHistPdf("fake lepton","fake lepton",ROOT.RooArgSet(m),RooDataHist_mlg_fake_lepton)

    RooDataHist_mlg_fake_photon = ROOT.RooDataHist("fake photon","fake photon",ROOT.RooArgList(m),inputs["fake_photon"])
    RooHistPdf_fake_photon = ROOT.RooHistPdf("fake photon","fake photon",ROOT.RooArgSet(m),RooDataHist_mlg_fake_photon)

    RooDataHist_mlg_double_fake = ROOT.RooDataHist("double fake","double fake",ROOT.RooArgList(m),inputs["double_fake"])
    RooHistPdf_double_fake = ROOT.RooHistPdf("double fake","double fake",ROOT.RooArgSet(m),RooDataHist_mlg_double_fake)

    if inputs["lepton"] == "electron":
        RooDataHist_mlg_etog = ROOT.RooDataHist("etog data hist","etog data hist",ROOT.RooArgList(m),inputs["e_to_p_non_res"])
        RooHistPdf_etog = ROOT.RooHistPdf("etog","etog",ROOT.RooArgSet(m),RooDataHist_mlg_etog)

    top_norm = ROOT.RooRealVar("top_norm","top_norm",inputs["top"].Integral(),inputs["top"].Integral())    
    wg_norm = ROOT.RooRealVar("wg_norm","wg_norm",125594.,75000,200000);    
    wg_plus_fake_wg_contamination_norm = ROOT.RooRealVar("wg_plus_fake_wg_contamination_norm","wg_plus_fake_wg_contamination_norm",13234.2,0.5*13234.2,2*13234.2);    
#    zg_norm = ROOT.RooRealVar("zg_norm","zg_norm",0,1000000);    
    zg_norm = ROOT.RooRealVar("zg_norm","zg_norm",inputs["zg"].Integral(),inputs["zg"].Integral());    
    vv_norm = ROOT.RooRealVar("vv_norm","vv_norm",inputs["vv"].Integral(),inputs["vv"].Integral());    
    bwcb_norm = ROOT.RooRealVar("bwcb_norm","bwcb_norm",152671.0,0,1000000);    
    fake_lepton_norm = ROOT.RooRealVar("fake_lepton_norm","fake_lepton_norm",inputs["fake_lepton"].Integral(),inputs["fake_lepton"].Integral());    
    fake_photon_norm = ROOT.RooRealVar("fake_photon_norm","fake_photon_norm",inputs["fake_photon"].Integral(),inputs["fake_photon"].Integral());    
    double_fake_norm = ROOT.RooRealVar("double_fake_norm","double_fake_norm",inputs["double_fake"].Integral(),inputs["double_fake"].Integral());    
    if inputs["lepton"] == "electron":
        etog_norm = ROOT.RooRealVar("etog_norm","etog_norm",inputs["e_to_p_non_res"].Integral(),inputs["e_to_p_non_res"].Integral())

    n1=ROOT.RooRealVar("n1","n1",0.1,0.01,100000)
    n2=ROOT.RooRealVar("n2","n2",0.1,0.01,100000)

    f= ROOT.RooRealVar("f","f",0.5,0.,1.) ;

    if inputs["lepton"] == "electron" or inputs["lepton"] == "both":
        if options.float_fake_sig_cont:
            sum=ROOT.RooAddPdf("sum","sum",ROOT.RooArgList(RooHistPdf_wg_plus_fake_wg_contamination,RooHistPdf_zg,RooHistPdf_vv,RooFFTConvPdf_bwcb,RooHistPdf_fake_lepton,RooHistPdf_fake_photon,RooHistPdf_double_fake,RooHistPdf_top,RooHistPdf_etog),ROOT.RooArgList(wg_plus_fake_wg_contamination_norm,zg_norm,vv_norm,bwcb_norm,fake_lepton_norm,fake_photon_norm,double_fake_norm,top_norm,etog_norm))
        else:    
            sum=ROOT.RooAddPdf("sum","sum",ROOT.RooArgList(RooHistPdf_wg,RooHistPdf_zg,RooHistPdf_vv,RooFFTConvPdf_bwcb,RooHistPdf_fake_lepton,RooHistPdf_fake_photon,RooHistPdf_double_fake,RooHistPdf_top,RooHistPdf_etog),ROOT.RooArgList(wg_norm,zg_norm,vv_norm,bwcb_norm,fake_lepton_norm,fake_photon_norm,double_fake_norm,top_norm,etog_norm))        
    elif inputs["lepton"] == "muon":
        if options.float_fake_sig_cont:
            sum=ROOT.RooAddPdf("sum","sum",ROOT.RooArgList(RooHistPdf_wg_plus_fake_wg_contamination,RooHistPdf_zg,RooHistPdf_vv,RooHistPdf_fake_lepton,RooHistPdf_fake_photon,RooHistPdf_double_fake,RooHistPdf_top),ROOT.RooArgList(wg_plus_fake_wg_contamination_norm,zg_norm,vv_norm,fake_lepton_norm,fake_photon_norm,double_fake_norm,top_norm))
        else:    
            sum=ROOT.RooAddPdf("sum","sum",ROOT.RooArgList(RooHistPdf_wg,RooHistPdf_zg,RooHistPdf_vv,RooHistPdf_fake_lepton,RooHistPdf_fake_photon,RooHistPdf_double_fake,RooHistPdf_top),ROOT.RooArgList(wg_norm,zg_norm,vv_norm,fake_lepton_norm,fake_photon_norm,double_fake_norm,top_norm))
    else:
        assert(0)

    print "nfits = "+str(0)

    roofitresult=sum.fitTo(RooDataHist_mlg_data,ROOT.RooFit.Extended(),ROOT.RooFit.Strategy(2),ROOT.RooFit.Save())
    #roofitresult=sum.fitTo(RooDataHist_mlg_data,ROOT.RooFit.Extended(),ROOT.RooFit.Strategy(2))
    #sum.fitTo(RooDataSet_mlg_data,ROOT.RooFit.Extended())


    print "roofitresult.status() = "+str(roofitresult.status())

    nfits=1

    while roofitresult.status() != 0 and nfits < 10:     

        width.setVal(ROOT.TRandom(0).Uniform(3,4))
        bwcb_norm.setVal(ROOT.TRandom(0).Uniform(140000,160000))
        m0.setVal(ROOT.TRandom(0).Uniform(-2,2))
        mass.setVal(ROOT.TRandom(0).Uniform(88,92))

        print "nfits = "+str(nfits)
        roofitresult=sum.fitTo(RooDataHist_mlg_data,ROOT.RooFit.Extended(),ROOT.RooFit.Strategy(2),ROOT.RooFit.Save())
        print "roofitresult.status() = "+str(roofitresult.status())
        nfits+=1

    frame1 = m.frame()
    frame2 = m.frame(ROOT.RooFit.Range(0,200))

    RooDataHist_mlg_data.plotOn(frame1)
    RooDataHist_mlg_data.plotOn(frame2)
    #RooDataSet_mlg_data.plotOn(frame1)
    #RooDataSet_mlg_data.plotOn(frame2)
    sum.plotOn(frame1)
    sum.plotOn(frame2)
    #sum.plotOn(frame, ROOT.RooFit.Components(ROOT.RooArgSet(sum.getComponents()["zg"])),ROOT.RooFit.LineStyle(ROOT.kDashed)) 
    #sum.plotOn(frame, ROOT.RooFit.Components("zg,wg,bwcb"),ROOT.RooFit.LineStyle(ROOT.kDashed)) 

    red_th1f=ROOT.TH1D("red_th1f","red_th1f",1,0,1)
    red_th1f.SetLineColor(ROOT.kRed)
    red_th1f.SetLineWidth(3)
    red_th1f.SetLineStyle(ROOT.kDashed)
    green_th1f=ROOT.TH1D("green_th1f","green_th1f",1,0,1)
    green_th1f.SetLineColor(ROOT.kGreen)
    green_th1f.SetLineWidth(3)
    green_th1f.SetLineStyle(ROOT.kDashed)
    magenta_th1f=ROOT.TH1D("magenta_th1f","magenta_th1f",1,0,1)
    magenta_th1f.SetLineColor(ROOT.kMagenta)
    magenta_th1f.SetLineWidth(3)
    magenta_th1f.SetLineStyle(ROOT.kDashed)
    orangeminus1_th1f=ROOT.TH1D("orangeminus1_th1f","orangeminus_th1f",1,0,1)
    orangeminus1_th1f.SetLineColor(ROOT.kOrange-1)
    orangeminus1_th1f.SetLineWidth(3)
    orangeminus1_th1f.SetLineStyle(ROOT.kDashed)

    if inputs["lepton"] == "both" or inputs["lepton"] == "electron":
        sum.plotOn(frame1, ROOT.RooFit.Components("wg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
        sum.plotOn(frame1, ROOT.RooFit.Components("zg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 
        sum.plotOn(frame1, ROOT.RooFit.Components("bwcb"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kMagenta)) 
        sum.plotOn(frame2, ROOT.RooFit.Components("wg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
        sum.plotOn(frame2, ROOT.RooFit.Components("zg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 
        sum.plotOn(frame2, ROOT.RooFit.Components("bwcb"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kMagenta)) 

        legend1 = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
        legend1.SetBorderSize(0)  # no border
        legend1.SetFillStyle(0)  # make transparent
        legend1.AddEntry(red_th1f,"wg","lp")
        legend1.AddEntry(green_th1f,"zg","lp")
        legend1.AddEntry(magenta_th1f,"bwcb","lp")
    elif lepton_name == "muon":
        sum.plotOn(frame1, ROOT.RooFit.Components("wg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
        sum.plotOn(frame1, ROOT.RooFit.Components("zg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 
        sum.plotOn(frame2, ROOT.RooFit.Components("wg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
        sum.plotOn(frame2, ROOT.RooFit.Components("zg"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 

        legend1 = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
        legend1.SetBorderSize(0)  # no border
        legend1.SetFillStyle(0)  # make transparent
        legend1.AddEntry(red_th1f,"wg","lp")
        legend1.AddEntry(green_th1f,"zg","lp")
    else:
        assert(0)

    frame1.SetTitle("")
    frame1.GetYaxis().SetTitle("")
    frame1.GetXaxis().SetTitle("m_{lg} (GeV)")
    frame2.SetTitle("")
    frame2.GetYaxis().SetTitle("")
    frame2.GetXaxis().SetTitle("m_{lg} (GeV)")
    
    c2 = ROOT.TCanvas("c2", "c2",5,50,500,500)
    
    frame1.Draw()
    
    legend1.Draw("same")
    
    c2.Update()
    c2.ForceUpdate()
    c2.Modified()

    if inputs["label"] == None:
        prefix = ""
    else:
        prefix = inputs["label"] + "_"

    c2.SaveAs(options.outputdir + "/" +prefix+"frame1.png")

    c2.Close()

    c3 = ROOT.TCanvas("c3", "c3",5,50,500,500)

    frame2.Draw()

    legend1.Draw("same")

    c3.Update()
    c3.ForceUpdate()
    c3.Modified()

    c3.SaveAs(options.outputdir + "/" +prefix + "frame2.png")

    c3.Close()

    frame3 = m.frame()
    frame4 = m.frame(ROOT.RooFit.Range(0,200))

    RooDataHist_mlg_data.plotOn(frame3)
    RooDataHist_mlg_data.plotOn(frame4)
    #RooDataSet_mlg_data.plotOn(frame3)
    #RooDataSet_mlg_data.plotOn(frame4)
    sum.plotOn(frame3)
    sum.plotOn(frame4)
    
    sum.plotOn(frame3, ROOT.RooFit.Components("fake photon"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
    sum.plotOn(frame3, ROOT.RooFit.Components("fake lepton"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 
    sum.plotOn(frame3, ROOT.RooFit.Components("double fake"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kMagenta)) 
    sum.plotOn(frame4, ROOT.RooFit.Components("fake photon"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kRed)) 
    sum.plotOn(frame4, ROOT.RooFit.Components("fake lepton"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kGreen)) 
    sum.plotOn(frame4, ROOT.RooFit.Components("double fake"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kMagenta)) 
    
    if inputs["lepton"] == "electron" or inputs["lepton"] == "both":
        sum.plotOn(frame3, ROOT.RooFit.Components("etog"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kOrange-1)) 
        sum.plotOn(frame4, ROOT.RooFit.Components("etog"),ROOT.RooFit.LineStyle(ROOT.kDashed),ROOT.RooFit.LineColor(ROOT.kOrange-1)) 

    frame3.SetTitle("")
    frame3.GetYaxis().SetTitle("")
    frame3.GetXaxis().SetTitle("m_{lg} (GeV)")
    frame4.SetTitle("")
    frame4.GetYaxis().SetTitle("")
    frame4.GetXaxis().SetTitle("m_{lg} (GeV)")

    legend2 = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
    legend2.SetBorderSize(0)  # no border
    legend2.SetFillStyle(0)  # make transparent
    legend2.AddEntry(red_th1f,"fake photon","lp")
    legend2.AddEntry(green_th1f,"fake lepton","lp")
    legend2.AddEntry(magenta_th1f,"double fake","lp")
    if inputs["lepton"] == "electron" or inputs["lepton"] == "both":
        legend2.AddEntry(orangeminus1_th1f,"e->g non-res","lp")

    c4 = ROOT.TCanvas("c4", "c4",5,50,500,500)

    frame3.Draw()
    
    legend2.Draw("same")
    
    c4.Update()
    c4.ForceUpdate()
    c4.Modified()
    
    c4.SaveAs(options.outputdir + "/" +prefix + "frame3.png")
    
    c4.Close()
    

    c5 = ROOT.TCanvas("c5", "c5",5,50,500,500)
    
    frame4.Draw()
    
    legend2.Draw("same")

    c5.Update()
    c5.ForceUpdate()
    c5.Modified()
    
    c5.SaveAs(options.outputdir + "/" +prefix + "frame4.png")
    
    c5.Close()

    mlg_fit_results = {}

    print "wg_plus_fake_wg_contamination_norm.getVal() = "+str(wg_plus_fake_wg_contamination_norm.getVal())
    print "wg_plus_fake_wg_contamination_norm.getVal()*inputs[\"wg\"].Integral()/(inputs[\"wg\"].Integral() + inputs[\"fake-wg-contamination\"]) = "+str(wg_plus_fake_wg_contamination_norm.getVal()*inputs["wg"].Integral()/(inputs["wg"].Integral() + inputs["fake-wg-contamination"].Integral()))

    mlg_fit_results["bwcb_norm"] = bwcb_norm.getVal()
    if options.float_fake_sig_cont:
        mlg_fit_results["wg_norm"] = wg_plus_fake_wg_contamination_norm.getVal()*inputs["wg"].Integral()/(inputs["wg"].Integral() + inputs["fake-wg-contamination"].Integral())
        mlg_fit_results["wg_norm_err"] = wg_plus_fake_wg_contamination_norm.getError()*inputs["wg"].Integral()/(inputs["wg"].Integral() + inputs["fake-wg-contamination"].Integral())
    else:
        mlg_fit_results["wg_norm"] = wg_norm.getVal()
        mlg_fit_results["wg_norm_err"] = wg_norm.getError()

    return mlg_fit_results

if lepton_name == "electron" and options.fit:
#if False:

    fit_inputs = {
        "label" : None,
        "lepton" : "electron",
        "data" : data["hists"][mlg_index],
        "top" : labels["top+jets"]["hists"][mlg_index],
        "zg" : labels["zg+jets"]["hists"][mlg_index],
        "vv" : labels["vv+jets"]["hists"][mlg_index],
        "wg" : labels["wg+jets"]["hists"][mlg_index],
        "fake-wg-contamination" : fake_signal_contamination["hists"][mlg_index],
        "e_to_p_non_res" : e_to_p_non_res["hists"][mlg_index],
        "fake_photon" : fake_photon["hists"][mlg_index],
        "fake_lepton" : fake_lepton["hists"][mlg_index],
        "double_fake" : double_fake["hists"][mlg_index]
        }

    fit_results = mlg_fit(fit_inputs)
    
    fit_inputs_fake_lepton_syst = dict(fit_inputs)
    fake_lepton_mlg_syst = fake_lepton["hists"][mlg_index].Clone("fake lepton syst")
    fake_lepton_mlg_syst.Scale(1.4)
    fit_inputs_fake_lepton_syst["label"] = "fake_lepton_syst"
    fit_inputs_fake_lepton_syst["fake_lepton"] = fake_lepton_mlg_syst
    fit_results_fake_lepton_syst = mlg_fit(fit_inputs_fake_lepton_syst)
    
    fit_inputs_fake_lepton_stat_up = dict(fit_inputs)
    fit_inputs_fake_lepton_stat_up["label"] = "fake_lepton_stat_up"
    fit_inputs_fake_lepton_stat_up["fake_lepton"] = fake_lepton_stat_up["hists"][mlg_index]
    fit_results_fake_lepton_stat_up = mlg_fit(fit_inputs_fake_lepton_stat_up)

    fit_inputs_pileup_up = dict(fit_inputs)
    fit_inputs_pileup_up["label"] = "pileup_up"
    fit_inputs_pileup_up["zg"] = labels["zg+jets"]["hists-pileup-up"][mlg_index]
    fit_inputs_pileup_up["wg"] = labels["wg+jets"]["hists-pileup-up"][mlg_index]
    fit_inputs_pileup_up["top"] = labels["top+jets"]["hists-pileup-up"][mlg_index]
    fit_inputs_pileup_up["vv"] = labels["vv+jets"]["hists-pileup-up"][mlg_index]
    fit_results_pileup_up = mlg_fit(fit_inputs_pileup_up)

    fit_inputs_prefire_up = dict(fit_inputs)
    fit_inputs_prefire_up["label"] = "prefire_up"
    fit_inputs_prefire_up["zg"] = labels["zg+jets"]["hists-prefire-up"][mlg_index]
    fit_inputs_prefire_up["wg"] = labels["wg+jets"]["hists-prefire-up"][mlg_index]
    fit_inputs_prefire_up["top"] = labels["top+jets"]["hists-prefire-up"][mlg_index]
    fit_inputs_prefire_up["vv"] = labels["vv+jets"]["hists-prefire-up"][mlg_index]
    fit_results_prefire_up = mlg_fit(fit_inputs_prefire_up)

    fit_inputs_jes_up = dict(fit_inputs)
    fit_inputs_jes_up["label"] = "jes_up"
    fit_inputs_jes_up["zg"] = labels["zg+jets"]["hists-jes-up"][mlg_index]
    fit_inputs_jes_up["wg"] = labels["wg+jets"]["hists-jes-up"][mlg_index]
    fit_inputs_jes_up["top"] = labels["top+jets"]["hists-jes-up"][mlg_index]
    fit_inputs_jes_up["vv"] = labels["vv+jets"]["hists-jes-up"][mlg_index]
    fit_results_jes_up = mlg_fit(fit_inputs_jes_up)

    fit_inputs_jer_up = dict(fit_inputs)
    fit_inputs_jer_up["label"] = "jer_up"
    fit_inputs_jer_up["zg"] = labels["zg+jets"]["hists-jer-up"][mlg_index]
    fit_inputs_jer_up["wg"] = labels["wg+jets"]["hists-jer-up"][mlg_index]
    fit_inputs_jer_up["top"] = labels["top+jets"]["hists-jer-up"][mlg_index]
    fit_inputs_jer_up["vv"] = labels["vv+jets"]["hists-jer-up"][mlg_index]
    fit_results_jer_up = mlg_fit(fit_inputs_jer_up)

    fit_inputs_fake_lepton_stat_down = dict(fit_inputs)
    fit_inputs_fake_lepton_stat_down["label"] = "fake_lepton_stat_down"
    fit_inputs_fake_lepton_stat_down["fake_lepton"] = fake_lepton_stat_down["hists"][mlg_index]
    fit_results_fake_lepton_stat_down = mlg_fit(fit_inputs_fake_lepton_stat_down)

    fit_inputs_fake_photon_alt = dict(fit_inputs)
    fit_inputs_fake_photon_alt["fake_photon"] = fake_photon_alt["hists"][mlg_index]
    fit_inputs_fake_photon_alt["label"] = "fake_photon_alt"
    fit_results_fake_photon_alt = mlg_fit(fit_inputs_fake_photon_alt)

    fit_inputs_fake_photon_wjets = dict(fit_inputs)
    fit_inputs_fake_photon_wjets["fake_photon"] = labels["w+jets"]["hists"][mlg_index].Clone("fake photon wjets")
    if options.no_wjets_for_2017_and_2018:
        fit_inputs_fake_photon_wjets["fake_photon"].Scale(fake_photon["hists"][mlg_index].Integral()/fake_photon_2016["hists"][mlg_index].Integral())
    fit_inputs_fake_photon_wjets["label"] = "fake_photon_wjets"
    fit_results_fake_photon_wjets = mlg_fit(fit_inputs_fake_photon_wjets)

    fit_inputs_lumi_up= dict(fit_inputs)
    fit_inputs_lumi_up["zg"] = labels["zg+jets"]["hists"][mlg_index].Clone("zg+jets lumi up")
    fit_inputs_lumi_up["zg"].Scale(1.025)
    fit_inputs_lumi_up["top"] = labels["top+jets"]["hists"][mlg_index].Clone("top+jets lumi up")
    fit_inputs_lumi_up["top"].Scale(1.025)
    fit_inputs_lumi_up["vv"] = labels["vv+jets"]["hists"][mlg_index].Clone("vv+jets lumi up")
    fit_inputs_lumi_up["vv"].Scale(1.025)
    fit_inputs_lumi_up["label"] = "lumi_up"
    fit_results_lumi_up = mlg_fit(fit_inputs_lumi_up)

    fit_results_fake_photon_stat_up = []

    for i in range(1,fake_photon["hists"][mlg_index].GetNbinsX()+1):
        fake_photon_mlg_stat_up = fake_photon["hists"][mlg_index].Clone("fake photon stat up bin "+ str(i))
        print str(fake_photon_mlg_stat_up.GetBinContent(i)) + " --> " + str(fake_photon_mlg_stat_up.GetBinContent(i)+fake_photon_mlg_stat_up.GetBinError(i))
        fake_photon_mlg_stat_up.SetBinContent(i,fake_photon_mlg_stat_up.GetBinContent(i)+fake_photon_mlg_stat_up.GetBinError(i))
        fit_inputs_fake_photon_stat_up = dict(fit_inputs)
        fit_inputs_fake_photon_stat_up["label"] = "fake_photon_stat_up_bin_"+str(i)
        fit_inputs_fake_photon_stat_up["fake_photon"] = fake_photon_mlg_stat_up
        fit_results_fake_photon_stat_up.append(mlg_fit(fit_inputs_fake_photon_stat_up))

    fit_results_fake_lepton_stat_up = []

    for i in range(1,fake_lepton["hists"][mlg_index].GetNbinsX()+1):
        fake_lepton_mlg_stat_up = fake_lepton["hists"][mlg_index].Clone("fake lepton stat up bin "+ str(i))
        print str(fake_lepton_mlg_stat_up.GetBinContent(i)) + " --> " + str(fake_lepton_mlg_stat_up.GetBinContent(i)+fake_lepton_mlg_stat_up.GetBinError(i))
        fake_lepton_mlg_stat_up.SetBinContent(i,fake_lepton_mlg_stat_up.GetBinContent(i)+fake_lepton_mlg_stat_up.GetBinError(i))
        fit_inputs_fake_lepton_stat_up = dict(fit_inputs)
        fit_inputs_fake_lepton_stat_up["label"] = "fake_lepton_stat_up_bin_"+str(i)
        fit_inputs_fake_lepton_stat_up["fake_lepton"] = fake_lepton_mlg_stat_up
        fit_results_fake_lepton_stat_up.append(mlg_fit(fit_inputs_fake_lepton_stat_up))

    fit_results_double_fake_stat_up = []

    for i in range(1,double_fake["hists"][mlg_index].GetNbinsX()+1):
        double_fake_mlg_stat_up = double_fake["hists"][mlg_index].Clone("fake lepton stat up bin "+ str(i))
        print str(double_fake_mlg_stat_up.GetBinContent(i)) + " --> " + str(double_fake_mlg_stat_up.GetBinContent(i)+double_fake_mlg_stat_up.GetBinError(i))
        double_fake_mlg_stat_up.SetBinContent(i,double_fake_mlg_stat_up.GetBinContent(i)+double_fake_mlg_stat_up.GetBinError(i))
        fit_inputs_double_fake_stat_up = dict(fit_inputs)
        fit_inputs_double_fake_stat_up["label"] = "double_fake_stat_up_bin_"+str(i)
        fit_inputs_double_fake_stat_up["double_fake"] = double_fake_mlg_stat_up
        fit_results_double_fake_stat_up.append(mlg_fit(fit_inputs_double_fake_stat_up))

    fit_results_zg_stat_up = []

    for i in range(1,labels["zg+jets"]["hists"][mlg_index].GetNbinsX()+1):
        zg_mlg_stat_up = labels["zg+jets"]["hists"][mlg_index].Clone("zg stat up bin "+ str(i))
        print str(zg_mlg_stat_up.GetBinContent(i)) + " --> " + str(zg_mlg_stat_up.GetBinContent(i)+zg_mlg_stat_up.GetBinError(i))
        zg_mlg_stat_up.SetBinContent(i,zg_mlg_stat_up.GetBinContent(i)+zg_mlg_stat_up.GetBinError(i))
        fit_inputs_zg_stat_up = dict(fit_inputs)
        fit_inputs_zg_stat_up["label"] = "zg_stat_up_bin_"+str(i)
        fit_inputs_zg_stat_up["zg"] = zg_mlg_stat_up
        fit_results_zg_stat_up.append(mlg_fit(fit_inputs_zg_stat_up))

    fit_results_vv_stat_up = []

    for i in range(1,labels["vv+jets"]["hists"][mlg_index].GetNbinsX()+1):
        vv_mlg_stat_up = labels["vv+jets"]["hists"][mlg_index].Clone("vv stat up bin "+ str(i))
        print str(vv_mlg_stat_up.GetBinContent(i)) + " --> " + str(vv_mlg_stat_up.GetBinContent(i)+vv_mlg_stat_up.GetBinError(i))
        vv_mlg_stat_up.SetBinContent(i,vv_mlg_stat_up.GetBinContent(i)+vv_mlg_stat_up.GetBinError(i))
        fit_inputs_vv_stat_up = dict(fit_inputs)
        fit_inputs_vv_stat_up["label"] = "vv_stat_up_bin_"+str(i)
        fit_inputs_vv_stat_up["vv"] = vv_mlg_stat_up
        fit_results_vv_stat_up.append(mlg_fit(fit_inputs_vv_stat_up))

    fit_results_top_stat_up = []

    for i in range(1,labels["top+jets"]["hists"][mlg_index].GetNbinsX()+1):
        top_mlg_stat_up = labels["top+jets"]["hists"][mlg_index].Clone("top stat up bin "+ str(i))
        print str(top_mlg_stat_up.GetBinContent(i)) + " --> " + str(top_mlg_stat_up.GetBinContent(i)+top_mlg_stat_up.GetBinError(i))
        top_mlg_stat_up.SetBinContent(i,top_mlg_stat_up.GetBinContent(i)+top_mlg_stat_up.GetBinError(i))
        fit_inputs_top_stat_up = dict(fit_inputs)
        fit_inputs_top_stat_up["label"] = "top_stat_up_bin_"+str(i)
        fit_inputs_top_stat_up["top"] = top_mlg_stat_up
        fit_results_top_stat_up.append(mlg_fit(fit_inputs_top_stat_up))


    if labels["zg+jets"]["syst-scale"]:    
        fit_results_zg_scale_variation = []

        for i in range(0,8): 
            fit_inputs_zg_scale_variation = dict(fit_inputs)
            fit_inputs_zg_scale_variation["label"] = "zg_scale_variation_"+str(i)
            fit_inputs_zg_scale_variation["zg"] = labels["zg+jets"]["hists-scale-variation"+str(i)][mlg_index]
            fit_results_zg_scale_variation.append(mlg_fit(fit_inputs_zg_scale_variation))


    if labels["zg+jets"]["syst-pdf"]:    
        fit_results_zg_pdf_variation = []
        
        for i in range(1,32): 
            fit_inputs_zg_pdf_variation = dict(fit_inputs)
            fit_inputs_zg_pdf_variation["label"] = "zg_pdf_variation_"+str(i)
            fit_inputs_zg_pdf_variation["zg"] = labels["zg+jets"]["hists-pdf-variation"+str(i)][mlg_index]
            fit_results_zg_pdf_variation.append(mlg_fit(fit_inputs_zg_pdf_variation))


if "wg+jets" in labels:
    prefire_unc = abs(labels["wg+jets"]["hists-prefire-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral())
    pileup_unc = abs(labels["wg+jets"]["hists-pileup-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral())
    jes_unc = abs(labels["wg+jets"]["hists-jes-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral())
    jer_unc = abs(labels["wg+jets"]["hists-jer-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral())
    electron_id_sf_unc = labels["wg+jets"]["hists-electron-id-sf-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral()
    electron_reco_sf_unc = labels["wg+jets"]["hists-electron-reco-sf-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral()
    muon_id_sf_unc = labels["wg+jets"]["hists-muon-id-sf-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral()
    muon_iso_sf_unc = labels["wg+jets"]["hists-muon-iso-sf-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral()
    photon_id_sf_unc = labels["wg+jets"]["hists-photon-id-sf-up"][mlg_index].Integral() - labels["wg+jets"]["hists"][mlg_index].Integral()

    print labels["wg+jets"]["hists-muon-iso-sf-up"][mlg_index].Integral()
    print labels["wg+jets"]["hists"][mlg_index].Integral()

    print "(number of wg+jets events run over) = "+str(labels["wg+jets"]["samples"][year][0]["nweightedevents"])

    print "fiducial_region_cuts_efficiency = "+str(fiducial_region_cuts_efficiency)

if options.draw_ewdim6:
    for i in range(1,n_photon_pt_bins+1):
        #hardcoded to use bin 6 of the scaling histogram for now 
        ewdim6["hists"][0].SetBinContent(i,cb_scaling_hists[i].GetBinContent(4)*labels["wg+jets"]["hists"][0].GetBinContent(i))

for i in range(len(variables)):

    if options.blind:
        data["hists"][i].Scale(0)

#    fake_lepton["hists"][i].Scale(2)

    fake_photon["hists"][i].Scale(1.0)

    data["hists"][i].Print("all")
    fake_photon["hists"][i].Print("all")
    fake_lepton["hists"][i].Print("all")
    if "wg+jets" in labels:
        labels["wg+jets"]["hists"][i].Print("all")
    if "w+jets" in labels:
        labels["w+jets"]["hists"][i].Print("all")

    data["hists"][i].SetMarkerStyle(ROOT.kFullCircle)
    data["hists"][i].SetLineWidth(3)
    data["hists"][i].SetLineColor(ROOT.kBlack)

    ewdim6["hists"][i].SetLineWidth(3)
    ewdim6["hists"][i].SetLineColor(ROOT.kOrange+3)

    fake_photon["hists"][i].SetFillColor(ROOT.kGray+1)
    fake_lepton["hists"][i].SetFillColor(ROOT.kAzure-1)
    double_fake["hists"][i].SetFillColor(ROOT.kMagenta)
    e_to_p["hists"][i].SetFillColor(ROOT.kSpring)
    e_to_p_non_res["hists"][i].SetFillColor(ROOT.kYellow)


    fake_photon["hists"][i].SetLineColor(ROOT.kGray+1)
    fake_lepton["hists"][i].SetLineColor(ROOT.kAzure-1)
    double_fake["hists"][i].SetLineColor(ROOT.kMagenta)
    e_to_p["hists"][i].SetLineColor(ROOT.kSpring)
    e_to_p_non_res["hists"][i].SetLineColor(ROOT.kYellow)


    fake_photon["hists"][i].SetFillStyle(1001)
    fake_lepton["hists"][i].SetFillStyle(1001)
    double_fake["hists"][i].SetFillStyle(1001)
    e_to_p["hists"][i].SetFillStyle(1001)
    e_to_p_non_res["hists"][i].SetFillStyle(1001)

    s=str(totallumi)+" fb^{-1} (13 TeV)"
    lumilabel = ROOT.TLatex (0.95, 0.93, s)
    lumilabel.SetNDC ()
    lumilabel.SetTextAlign (30)
    lumilabel.SetTextFont (42)
    lumilabel.SetTextSize (0.040)

#
    hsum = data["hists"][i].Clone()
    hsum.Scale(0.0)

    hstack = ROOT.THStack()

    for label in labels.keys():
        if labels[label]["color"] == None:
            continue
        if options.closure_test and label == "wg+jets":
            continue

        if not options.use_wjets_for_fake_photon and label == "w+jets":
            continue

        hsum.Add(labels[label]["hists"][i])
        hstack.Add(labels[label]["hists"][i])

    if not options.closure_test and (lepton_name == "electron" or lepton_name == "both"): 
        if options.closure_test and label == "wg+jets":
            continue
        hsum.Add(e_to_p["hists"][i])
        hstack.Add(e_to_p["hists"][i])

    if not options.closure_test:    
        hsum.Add(e_to_p_non_res["hists"][i])
        hstack.Add(e_to_p_non_res["hists"][i])

    if data_driven:
        if not options.use_wjets_for_fake_photon:
            hsum.Add(fake_photon["hists"][i])
        if not options.closure_test:
            hsum.Add(fake_lepton["hists"][i])
            hsum.Add(double_fake["hists"][i])


    if data_driven:
        if not options.use_wjets_for_fake_photon:
            hstack.Add(fake_photon["hists"][i])
        if not options.closure_test:
            hstack.Add(fake_lepton["hists"][i])
            hstack.Add(double_fake["hists"][i])


    if data["hists"][i].GetMaximum() < hsum.GetMaximum():
        data["hists"][i].SetMaximum(hsum.GetMaximum()*1.55)
#        data["hists"][i].SetMaximum(hsum.GetMaximum()*2.55)
    else:
        data["hists"][i].SetMaximum(data["hists"][i].GetMaximum()*1.55)
#        data["hists"][i].SetMaximum(data["hists"][i].GetMaximum()*2.55)
        

    data["hists"][i].SetMinimum(0)
    hstack.SetMinimum(0)
    hsum.SetMinimum(0)

    data["hists"][i].Draw("")

    hstack.Draw("hist same")

    if options.draw_ewdim6:
        ewdim6["hists"][i].Print("all")
        ewdim6["hists"][i].Draw("same")
#wg_qcd.Draw("hist same")
#fake_lepton_hist.Draw("hist same")
#fake_photon_hist.Draw("hist same")

#wg_ewk_hist.Print("all")

#cmslabel = TLatex (0.18, 0.93, "#bf{CMS} (Unpublished)")
    cmslabel = ROOT.TLatex (0.18, 0.93, "")
    cmslabel.SetNDC ()
    cmslabel.SetTextAlign (10)
    cmslabel.SetTextFont (42)
    cmslabel.SetTextSize (0.040)
    cmslabel.Draw ("same") 
    
    lumilabel.Draw("same")

#wpwpjjewk.Draw("same")

    j=0
    if options.closure_test:
        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,data["hists"][i],"w+jets","lp")
    else:    
        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,data["hists"][i],"data","lp")

    if data_driven :
        if not options.use_wjets_for_fake_photon:
            j=j+1
            draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,fake_photon["hists"][i],"fake photon","f")
        if not options.closure_test:
            j=j+1
            if lepton_name == "muon":
                draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,fake_lepton["hists"][i],"fake muon","f")
            elif lepton_name == "electron":
                draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,fake_lepton["hists"][i],"fake electron","f")
            elif lepton_name == "both":
                draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,fake_lepton["hists"][i],"fake lepton","f")
            else:
                assert(0)
            j=j+1
            draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,double_fake["hists"][i],"double fake","f")

    if (lepton_name == "electron" or lepton_name == "both") and not options.closure_test: 
        j=j+1
        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,e_to_p["hists"][i],"e->#gamma","f")

    if not options.closure_test:
        j=j+1
        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,e_to_p_non_res["hists"][i],"e->#gamma non-res","f")

    for label in labels.keys():
        if labels[label]["color"] == None:
            continue

        if options.closure_test and label == "wg+jets":
            continue

        if not options.use_wjets_for_fake_photon and label == "w+jets":
            continue

        j=j+1    
#        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,labels[label]["hists"][i],label,"f")
        if len(label) > 10:
            print "Warning: truncating the legend label "+str(label) + " to "+str(label[0:10]) 
            draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,labels[label]["hists"][i],label[0:10],"f")
        else:    
            draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,labels[label]["hists"][i],label,"f")

    if options.draw_ewdim6:
        j=j+1
        draw_legend(xpositions[j],0.84 - ypositions[j]*yoffset,ewdim6["hists"][i],"C_{WWW} = 2.0","l")

#set_axis_fonts(hstack,"x","m_{ll} (GeV)")
#set_axis_fonts(hstack,"x","|\Delta \eta_{jj}|")
    set_axis_fonts(data["hists"][i],"x",getXaxisLabel(variables[i]))
#set_axis_fonts(hstack,"x","pt_{l}^{max} (GeV)")
#set_axis_fonts(data_hist,"y","Events / bin")
#set_axis_fonts(hstack,"y","Events / bin")

    gstat = ROOT.TGraphAsymmErrors(hsum);

    for j in range(0,gstat.GetN()):
        gstat.SetPointEYlow (j, hsum.GetBinError(j+1));
        gstat.SetPointEYhigh(j, hsum.GetBinError(j+1));

    gstat.SetFillColor(12);
    gstat.SetFillStyle(3345);
    gstat.SetMarkerSize(0);
    gstat.SetLineWidth(0);
    gstat.SetLineColor(ROOT.kWhite);
    gstat.Draw("E2same");

    data["hists"][i].Draw("same")

    c1.Update()
    c1.ForceUpdate()
    c1.Modified()

    c1.SaveAs(options.outputdir + "/" + variables_labels[i] + ".png")

c1.Close()

if options.closure_test:
    sys.exit(0)


wg_jets_integral_error = ROOT.Double()
wg_jets_integral = labels["wg+jets"]["hists"][mlg_index].IntegralAndError(1,labels["wg+jets"]["hists"][mlg_index].GetXaxis().GetNbins(),wg_jets_integral_error)

zg_jets_integral_error = ROOT.Double()
zg_jets_integral = labels["zg+jets"]["hists"][mlg_index].IntegralAndError(1,labels["zg+jets"]["hists"][mlg_index].GetXaxis().GetNbins(),zg_jets_integral_error)

vv_jets_integral_error = ROOT.Double()
vv_jets_integral = labels["vv+jets"]["hists"][mlg_index].IntegralAndError(1,labels["vv+jets"]["hists"][mlg_index].GetXaxis().GetNbins(),vv_jets_integral_error)

top_jets_integral_error = ROOT.Double()
top_jets_integral = labels["top+jets"]["hists"][mlg_index].IntegralAndError(1,labels["top+jets"]["hists"][mlg_index].GetXaxis().GetNbins(),top_jets_integral_error)

fake_lepton_integral_error = ROOT.Double()
fake_lepton_integral = fake_lepton["hists"][mlg_index].IntegralAndError(1,fake_lepton["hists"][mlg_index].GetXaxis().GetNbins(),fake_lepton_integral_error)

fake_photon_integral_error = ROOT.Double()
fake_photon_integral = fake_photon["hists"][mlg_index].IntegralAndError(1,fake_photon["hists"][mlg_index].GetXaxis().GetNbins(),fake_photon_integral_error)

double_fake_integral_error = ROOT.Double()
double_fake_integral = double_fake["hists"][mlg_index].IntegralAndError(1,double_fake["hists"][mlg_index].GetXaxis().GetNbins(),double_fake_integral_error)

data_integral_error = ROOT.Double()
data_integral = data["hists"][mlg_index].IntegralAndError(1,data["hists"][mlg_index].GetXaxis().GetNbins(),data_integral_error)

e_to_p_integral_error = ROOT.Double()
e_to_p_integral = e_to_p["hists"][mlg_index].IntegralAndError(1,e_to_p["hists"][mlg_index].GetXaxis().GetNbins(),e_to_p_integral_error)

e_to_p_non_res_integral_error = ROOT.Double()
e_to_p_non_res_integral = e_to_p_non_res["hists"][mlg_index].IntegralAndError(1,e_to_p_non_res["hists"][mlg_index].GetXaxis().GetNbins(),e_to_p_non_res_integral_error)

fake_signal_contamination_integral_error = ROOT.Double()
fake_signal_contamination_integral = fake_signal_contamination["hists"][mlg_index].IntegralAndError(1,fake_signal_contamination["hists"][mlg_index].GetXaxis().GetNbins(),fake_signal_contamination_integral_error)

print "fake signal contamination = "+str(fake_signal_contamination_integral) + " +/- " +str(fake_signal_contamination_integral_error)

print "wg+jets = "+str(wg_jets_integral)+" +/- "+str(wg_jets_integral_error)
print "zg+jets = "+str(zg_jets_integral)+" +/- "+str(zg_jets_integral_error)
print "vv+jets = "+str(vv_jets_integral)+" +/- "+str(vv_jets_integral_error)
print "top+jets = "+str(top_jets_integral)+" +/- "+str(top_jets_integral_error)
print "fake photon = "+str(fake_photon_integral)+" +/- "+str(fake_photon_integral_error)
print "fake lepton = "+str(fake_lepton_integral)+" +/- "+str(fake_lepton_integral_error)
print "double fake = "+str(double_fake_integral)+" +/- "+str(double_fake_integral_error)
print "data = "+str(data_integral)+" +/- "+str(data_integral_error)
print "e_to_p = "+str(e_to_p_integral)+" +/- "+str(e_to_p_integral_error)
print "e_to_p_non_res = "+str(e_to_p_non_res_integral)+" +/- "+str(e_to_p_non_res_integral_error)

if options.fit:
    print "fit_results[\"bwcb_norm\"] = "+str(fit_results["bwcb_norm"])

n_signal = data_integral - double_fake_integral - fake_photon_integral - fake_lepton_integral - top_jets_integral - vv_jets_integral - zg_jets_integral - e_to_p_non_res_integral

n_signal_error = sqrt(pow(data_integral_error,2) + pow(double_fake_integral_error,2) + pow(fake_lepton_integral_error,2)+ pow(fake_photon_integral_error,2)+pow(top_jets_integral_error,2)+ pow(vv_jets_integral_error,2)+ pow(zg_jets_integral_error,2)+pow(e_to_p_non_res_integral_error,2))

print "n_signal = "+str(n_signal) + " +/- " + str(n_signal_error)

#labels["wg+jets"]["hists"]["photon_pt"].Print("all")

double_fake["hists"][mlg_index].Print("all")
fake_lepton["hists"][mlg_index].Print("all")
fake_photon["hists"][mlg_index].Print("all")
fake_photon_alt["hists"][mlg_index].Print("all")
fake_photon_stat_up["hists"][mlg_index].Print("all")



if lepton_name == "muon":

    xs_times_lumi = 0
    fiducial_xs_times_lumi = 0
    for year in years:
        if year == "2016":
            lumi=35.9
        elif year == "2017":
            lumi=41.5
        elif year == "2018":
            lumi=59.6
        else:
            assert(0)
        xs_times_lumi += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi
        fiducial_xs_times_lumi += labels["wg+jets"]["samples"][year][0]["nweightedevents_passfiducial"]*labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

    xs_inputs_muon = {
        "lumi" : totallumi,
        "fiducial" : fiducial_xs_times_lumi,
        "fiducial_pass" : labels["wg+jets"]["hists-pass-fiducial"][mlg_index].Integral(),
        "xs_times_lumi" : xs_times_lumi,
        "signal_data_muon" : n_signal,
        "signal_mc_xs_data_mc" : labels["wg+jets"]["hists"][mlg_index].Integral(),
        "signal_syst_unc_due_to_pileup" : abs(labels["top+jets"]["hists-pileup-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-pileup-up"][mlg_index].Integral()+labels["vv+jets"]["hists-pileup-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
        "signal_syst_unc_due_to_prefire" : abs(labels["top+jets"]["hists-prefire-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-prefire-up"][mlg_index].Integral()+labels["vv+jets"]["hists-prefire-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
        "signal_syst_unc_due_to_jes" : abs(labels["top+jets"]["hists-jes-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-jes-up"][mlg_index].Integral()+labels["vv+jets"]["hists-jes-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
        "signal_syst_unc_due_to_jer" : abs(labels["top+jets"]["hists-jer-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-jer-up"][mlg_index].Integral()+labels["vv+jets"]["hists-jer-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
        "signal_syst_unc_due_to_fake_photon_alt_muon" : abs(fake_photon_alt["hists"][mlg_index].Integral() - fake_photon["hists"][mlg_index].Integral()),

        "signal_syst_unc_due_to_fake_lepton_muon" : abs(fake_lepton["hists"][mlg_index].Integral()*1.3 - fake_lepton["hists"][mlg_index].Integral()),
        "signal_stat_unc_muon" : n_signal_error,
        "signal_mc_xs_data_mc_syst_unc_due_to_prefire" : prefire_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_jes" : jes_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_jer" : jer_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_pileup" : pileup_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_muon_id_sf_muon" : muon_id_sf_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_muon_iso_sf_muon" : muon_iso_sf_unc,
        "signal_mc_xs_data_mc_syst_unc_due_to_photon_id_sf_muon" : photon_id_sf_unc
        }

    if options.no_wjets_for_2017_and_2018:
        xs_inputs_muon["signal_syst_unc_due_to_fake_photon_wjets_muon"] = abs(labels["w+jets"]["hists"][mlg_index].Integral() - fake_photon_2016["hists"][mlg_index].Integral())*fake_photon["hists"][mlg_index].Integral()/fake_photon_2016["hists"][mlg_index].Integral()
    else:    
        xs_inputs_muon["signal_syst_unc_due_to_fake_photon_wjets_muon"] = abs(labels["w+jets"]["hists"][mlg_index].Integral() - fake_photon["hists"][mlg_index].Integral())

    for i in range(1,32):
        xs_inputs_muon["signal_mc_xs_data_mc_pdf_variation"+str(i)] = labels["wg+jets"]["hists-pdf-variation"+str(i)][mlg_index].Integral()
        xs_times_lumi_pdf_variation = 0
        for year in years:
            if year == "2016":
                lumi=35.9
            elif year == "2017":
                lumi=41.5
            elif year == "2018":
                lumi=59.6
            else:
                assert(0)

            if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                continue

            xs_times_lumi_pdf_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_pdfweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

        xs_inputs_muon["xs_times_lumi_pdf_variation"+str(i)] = xs_times_lumi_pdf_variation

    for i in range(0,8):
        xs_inputs_muon["signal_mc_xs_data_mc_scale_variation"+str(i)] = labels["wg+jets"]["hists-scale-variation"+str(i)][mlg_index].Integral() 
        xs_times_lumi_scale_variation = 0
        for year in years:
            if year == "2016":
                lumi=35.9
            elif year == "2017":
                lumi=41.5
            elif year == "2018":
                lumi=59.6
            else:
                assert(0)
            
            xs_times_lumi_scale_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_qcdscaleweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

        xs_inputs_muon["xs_times_lumi_scale_variation"+str(i)] = xs_times_lumi_scale_variation        


    for i in range(1,fake_photon["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_fake_photon_stat_up_bin"+str(i)] = fake_photon["hists"][mlg_index].GetBinError(i)

    for i in range(1,fake_lepton["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_fake_lepton_stat_up_bin"+str(i)] = fake_lepton["hists"][mlg_index].GetBinError(i)

    for i in range(1,double_fake["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_double_fake_stat_up_bin"+str(i)] = double_fake["hists"][mlg_index].GetBinError(i)

    for i in range(1,labels["zg+jets"]["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_zg_stat_up_bin"+str(i)] = labels["zg+jets"]["hists"][mlg_index].GetBinError(i)

    for i in range(1,labels["vv+jets"]["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_vv_stat_up_bin"+str(i)] = labels["vv+jets"]["hists"][mlg_index].GetBinError(i)

    for i in range(1,labels["top+jets"]["hists"][mlg_index].GetNbinsX()+1): 
        xs_inputs_muon["signal_syst_unc_due_to_top_stat_up_bin"+str(i)] = labels["top+jets"]["hists"][mlg_index].GetBinError(i)

    if labels["zg+jets"]["syst-scale"]:    
        for i in range(0,8): 
            xs_inputs_muon["signal_syst_unc_due_to_zg_scale_variation"+str(i)] = labels["zg+jets"]["hists"][mlg_index].Integral() - labels["zg+jets"]["hists-scale-variation"+str(i)][mlg_index].Integral()

    if labels["zg+jets"]["syst-pdf"]:    
        for i in range(1,32): 
            xs_inputs_muon["signal_syst_unc_due_to_zg_pdf_variation"+str(i)] = labels["zg+jets"]["hists"][mlg_index].Integral() - labels["zg+jets"]["hists-pdf-variation"+str(i)][mlg_index].Integral()

    xs_inputs_muon["signal_syst_unc_due_to_lumi_up"] = abs(0.026*(labels["zg+jets"]["hists"][mlg_index].Integral()+labels["top+jets"]["hists"][mlg_index].Integral() + labels["vv+jets"]["hists"][mlg_index].Integral()) )

    pprint(xs_inputs_muon)

    import json

    f_muon = open("xs_inputs_muon.txt","w")

    json.dump(xs_inputs_muon,f_muon)

elif lepton_name == "electron":

    if options.fit:

        xs_times_lumi = 0
        for year in years:
            if year == "2016":
                lumi=35.9
            elif year == "2017":
                lumi=41.5
            elif year == "2018":
                lumi=59.6
            else:
                assert(0)
            xs_times_lumi += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi

        xs_inputs_electron = {
            "lumi" : totallumi,
            "fiducial_region_cuts_efficiency":fiducial_region_cuts_efficiency,
            "xs_times_lumi" : xs_times_lumi,
            "signal_mc_xs_data_mc" : labels["wg+jets"]["hists"][mlg_index].Integral(),
            "signal_data_electron" : fit_results["wg_norm"],
            "signal_syst_unc_due_to_pileup" : abs(fit_results_pileup_up["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_prefire" : abs(fit_results_prefire_up["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_jes" : abs(fit_results_jes_up["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_jer" : abs(fit_results_jer_up["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_fake_photon_alt_electron" : abs(fit_results_fake_photon_alt["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_fake_photon_wjets_electron" : abs(fit_results_fake_photon_wjets["wg_norm"]-fit_results["wg_norm"]),
            "signal_syst_unc_due_to_fake_lepton_electron" : abs(fit_results_fake_lepton_syst["wg_norm"]-fit_results["wg_norm"]),
            "signal_stat_unc_electron" : fit_results["wg_norm_err"],
            "signal_mc_xs_data_mc_electron" : labels["wg+jets"]["hists"][mlg_index].Integral(),
            "signal_mc_xs_data_mc_syst_unc_due_to_electron_id_sf_electron" : electron_id_sf_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_pileup" : pileup_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_prefire" : prefire_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_jer" : jer_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_jes" : jes_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_electron_reco_sf_electron" : electron_reco_sf_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_photon_id_sf_electron" : photon_id_sf_unc
            }

        for i in range(1,32):
            xs_inputs_electron["signal_mc_xs_data_mc_pdf_variation"+str(i)] = labels["wg+jets"]["hists-pdf-variation"+str(i)][mlg_index].Integral()
            xs_times_lumi_pdf_variation = 0
            for year in years:
                if year == "2016":
                    lumi=35.9
                elif year == "2017":
                    lumi=41.5
                elif year == "2018":
                    lumi=59.6
                else:
                    assert(0)

                if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                    continue

                xs_times_lumi_pdf_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_pdfweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

            xs_inputs_electron["xs_times_lumi_pdf_variation"+str(i)] = xs_times_lumi_pdf_variation

        for i in range(0,8):
            xs_inputs_electron["signal_mc_xs_data_mc_scale_variation"+str(i)] = labels["wg+jets"]["hists-scale-variation"+str(i)][mlg_index].Integral()
            xs_times_lumi_scale_variation = 0
            for year in years:
                if year == "2016":
                    lumi=35.9
                elif year == "2017":
                    lumi=41.5
                elif year == "2018":
                    lumi=59.6
                else:
                    assert(0)

                xs_times_lumi_scale_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_qcdscaleweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

            xs_inputs_electron["xs_times_lumi_scale_variation"+str(i)] = xs_times_lumi_scale_variation        

        for i in range(1,fake_photon["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_fake_photon_stat_up_bin"+str(i)] = abs(fit_results_fake_photon_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        for i in range(1,fake_lepton["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_fake_lepton_stat_up_bin"+str(i)] = abs(fit_results_fake_lepton_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        for i in range(1,double_fake["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_double_fake_stat_up_bin"+str(i)] = abs(fit_results_double_fake_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        for i in range(1,labels["zg+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_zg_stat_up_bin"+str(i)] = abs(fit_results_zg_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        for i in range(1,labels["vv+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_vv_stat_up_bin"+str(i)] = abs(fit_results_vv_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        for i in range(1,labels["top+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_top_stat_up_bin"+str(i)] = abs(fit_results_top_stat_up[i-1]["wg_norm"] - fit_results["wg_norm"])

        if labels["zg+jets"]["syst-scale"]:    
            for i in range(0,8): 
                xs_inputs_electron["signal_syst_unc_due_to_zg_scale_variation"+str(i)] = fit_results_zg_scale_variation[i]["wg_norm"] - fit_results["wg_norm"]

        if labels["zg+jets"]["syst-pdf"]:    
            for i in range(1,32): 
                xs_inputs_electron["signal_syst_unc_due_to_zg_pdf_variation"+str(i)] = fit_results_zg_pdf_variation[i-1]["wg_norm"] - fit_results["wg_norm"]

        xs_inputs_electron["signal_syst_unc_due_to_lumi_up"] = abs(fit_results_lumi_up["wg_norm"] - fit_results["wg_norm"])

    else:

        xs_times_lumi = 0
        fiducial_xs_times_lumi = 0
        for year in years:
            if year == "2016":
                lumi=35.9
            elif year == "2017":
                lumi=41.5
            elif year == "2018":
                lumi=59.6
            else:
                assert(0)
            xs_times_lumi += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi
            fiducial_xs_times_lumi += labels["wg+jets"]["samples"][year][0]["nweightedevents_passfiducial"]*labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

        xs_inputs_electron = {
            "lumi" : totallumi,
            "fiducial" : fiducial_xs_times_lumi,
            "fiducial_pass" : labels["wg+jets"]["hists-pass-fiducial"][mlg_index].Integral(),
            "xs_times_lumi" : xs_times_lumi,
            "signal_data_electron" : n_signal,
            "signal_mc_xs_data_mc" : labels["wg+jets"]["hists"][mlg_index].Integral(),
            "signal_syst_unc_due_to_pileup" : abs(labels["top+jets"]["hists-pileup-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-pileup-up"][mlg_index].Integral()+labels["vv+jets"]["hists-pileup-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
            "signal_syst_unc_due_to_prefire" : abs(labels["top+jets"]["hists-prefire-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-prefire-up"][mlg_index].Integral()+labels["vv+jets"]["hists-prefire-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
            "signal_syst_unc_due_to_jes" : abs(labels["top+jets"]["hists-jes-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-jes-up"][mlg_index].Integral()+labels["vv+jets"]["hists-jes-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
            "signal_syst_unc_due_to_jer" : abs(labels["top+jets"]["hists-jer-up"][mlg_index].Integral()+ labels["zg+jets"]["hists-jer-up"][mlg_index].Integral()+labels["vv+jets"]["hists-jer-up"][mlg_index].Integral()-labels["top+jets"]["hists"][mlg_index].Integral()- labels["zg+jets"]["hists"][mlg_index].Integral()-labels["vv+jets"]["hists"][mlg_index].Integral()),
            "signal_syst_unc_due_to_fake_photon_electron" : abs(fake_photon_alt["hists"][mlg_index].Integral() - fake_photon["hists"][mlg_index].Integral()),
            "signal_syst_unc_due_to_fake_lepton_electron" : abs(fake_lepton["hists"][mlg_index].Integral()*1.3 - fake_lepton["hists"][mlg_index].Integral()),
            "signal_stat_unc_electron" : n_signal_error,
            "signal_mc_xs_data_mc_syst_unc_due_to_pileup" : pileup_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_pileup" : prefire_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_jes" : jes_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_jer" : jer_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_electron_id_sf_electron" : electron_id_sf_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_electron_reco_sf_electron" : electron_reco_sf_unc,
            "signal_mc_xs_data_mc_syst_unc_due_to_photon_id_sf_electron" : photon_id_sf_unc
            }

        if options.no_wjets_for_2017_and_2018:
            xs_inputs_electron["signal_syst_unc_due_to_fake_photon_wjets_electron"] = abs(labels["w+jets"]["hists"][mlg_index].Integral() - fake_photon_2016["hists"][mlg_index].Integral())*fake_photon["hists"][mlg_index].Integral()/fake_photon_2016["hists"][mlg_index].Integral()
        else:    
            xs_inputs_electron["signal_syst_unc_due_to_fake_photon_wjets_electron"] = abs(labels["w+jets"]["hists"][mlg_index].Integral() - fake_photon["hists"][mlg_index].Integral())
        
        for i in range(1,32):
            xs_inputs_electron["signal_mc_xs_data_mc_pdf_variation"+str(i)] = labels["wg+jets"]["hists-pdf-variation"+str(i)][mlg_index].Integral()
            xs_times_lumi_pdf_variation = 0
            for year in years:
                if year == "2016":
                    lumi=35.9
                elif year == "2017":
                    lumi=41.5
                elif year == "2018":
                    lumi=59.6
                else:
                    assert(0)

                if (year == "2017" or year == "2018") and options.no_pdf_var_for_2017_and_2018:
                    continue

                xs_times_lumi_pdf_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_pdfweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

            xs_inputs_electron["xs_times_lumi_pdf_variation"+str(i)] = xs_times_lumi_pdf_variation

        for i in range(0,8):
            xs_inputs_electron["signal_mc_xs_data_mc_scale_variation"+str(i)] = labels["wg+jets"]["hists-scale-variation"+str(i)][mlg_index].Integral() 
            xs_times_lumi_scale_variation = 0
            for year in years:
                if year == "2016":
                    lumi=35.9
                elif year == "2017":
                    lumi=41.5
                elif year == "2018":
                    lumi=59.6
                else:
                    assert(0)
            
                xs_times_lumi_scale_variation += labels["wg+jets"]["samples"][year][0]["xs"]*1000*lumi*labels["wg+jets"]["samples"][year][0]["nweightedevents_qcdscaleweight"+str(i)]/labels["wg+jets"]["samples"][year][0]["nweightedevents"]

            xs_inputs_electron["xs_times_lumi_scale_variation"+str(i)] = xs_times_lumi_scale_variation        

        for i in range(1,fake_photon["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_fake_photon_stat_up_bin"+str(i)] = fake_photon["hists"][mlg_index].GetBinError(i)

        for i in range(1,fake_lepton["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_fake_lepton_stat_up_bin"+str(i)] = fake_lepton["hists"][mlg_index].GetBinError(i)

        for i in range(1,double_fake["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_double_fake_stat_up_bin"+str(i)] = double_fake["hists"][mlg_index].GetBinError(i)

        for i in range(1,labels["zg+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_zg_stat_up_bin"+str(i)] = labels["zg+jets"]["hists"][mlg_index].GetBinError(i)

        for i in range(1,labels["vv+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_vv_stat_up_bin"+str(i)] = labels["vv+jets"]["hists"][mlg_index].GetBinError(i)

        for i in range(1,labels["top+jets"]["hists"][mlg_index].GetNbinsX()+1): 
            xs_inputs_electron["signal_syst_unc_due_to_top_stat_up_bin"+str(i)] = labels["top+jets"]["hists"][mlg_index].GetBinError(i)

        if labels["zg+jets"]["syst-scale"]:    
            for i in range(0,8): 
                xs_inputs_electron["signal_syst_unc_due_to_zg_scale_variation"+str(i)] = labels["zg+jets"]["hists"][mlg_index].Integral() - labels["zg+jets"]["hists-scale-variation"+str(i)][mlg_index].Integral()

        if labels["zg+jets"]["syst-pdf"]:    
            for i in range(1,32): 
                xs_inputs_electron["signal_syst_unc_due_to_zg_pdf_variation"+str(i)] = labels["zg+jets"]["hists"][mlg_index].Integral() - labels["zg+jets"]["hists-pdf-variation"+str(i)][mlg_index].Integral()

        xs_inputs_electron["signal_syst_unc_due_to_lumi_up"] = abs(0.026*(labels["zg+jets"]["hists"][mlg_index].Integral()+labels["top+jets"]["hists"][mlg_index].Integral() + labels["vv+jets"]["hists"][mlg_index].Integral()) )

    pprint(xs_inputs_electron)

    import json

    f_electron = open("xs_inputs_electron.txt","w")

    json.dump(xs_inputs_electron,f_electron)

if not options.ewdim6:
    sys.exit(0)

for i in range(1,sm_lhe_weight_hist.GetNbinsX()+1):

    dcard = open("photon_pt_bin"+str(i)+".txt",'w')

    print >> dcard, "imax 1 number of channels"
    print >> dcard, "jmax * number of background"
    print >> dcard, "kmax * number of nuisance parameters"
    print >> dcard, "Observation "+str(data["hists"][0].GetBinContent(i))
    dcard.write("bin")
    dcard.write(" bin1")
    
    for label in labels.keys():
        if label == "no label" or label == "wg+jets":
            continue
        dcard.write(" bin1")

    dcard.write(" bin1")    
    dcard.write(" bin1")    
    dcard.write(" bin1")    
    dcard.write(" bin1")    
    dcard.write('\n')    
    
    dcard.write("process")
    dcard.write(" Wg")
        
    for label in labels.keys():
        if label == "no label" or label == "wg+jets":
            continue
        dcard.write(" " + label)

    dcard.write(" fake_photon")
    dcard.write(" fake_lepton")
    dcard.write(" double_fake")
    dcard.write(" e_to_p_non_res")
    dcard.write('\n')    
    dcard.write("process")
    dcard.write(" 0")
    
    for j in range(1,len(labels.keys())+3):
        dcard.write(" " + str(j))
    dcard.write('\n')    
    dcard.write('rate')
    dcard.write(' '+str(sm_lhe_weight_hist.GetBinContent(i)))
#    dcard.write(' '+str(labels["wg+jets"]["hists"][0].GetBinContent(i)))
    for label in labels.keys():
        if label == "no label" or label == "wg+jets":
            continue
        if labels[label]["hists"][0].GetBinContent(i) > 0:
            dcard.write(" "+ str(labels[label]["hists"][0].GetBinContent(i)))
        else:
            dcard.write(" 0.0001") 



    if fake_photon["hists"][0].GetBinContent(i) > 0:        
        dcard.write(" "+str(fake_photon["hists"][0].GetBinContent(i))) 
    else:
        if fake_photon["hists"][0].GetBinContent(i) < 0:
            print "Warning: fake photon estimate is "+str(fake_photon["hists"][0].GetBinContent(i))+ " for bin " + str(i) + ". It will be replaced with 0.0001"
        dcard.write(" 0.0001") 

    if fake_lepton["hists"][0].GetBinContent(i) > 0:        
        dcard.write(" "+str(fake_lepton["hists"][0].GetBinContent(i))) 
    else:
        if fake_lepton["hists"][0].GetBinContent(i) < 0:
            print "Warning: fake lepton estimate is "+str(fake_lepton["hists"][0].GetBinContent(i))+ " for bin " + str(i) + ". It will be replaced with 0.0001"
        dcard.write(" 0.0001") 

    if double_fake["hists"][0].GetBinContent(i) > 0:        
        dcard.write(" "+str(double_fake["hists"][0].GetBinContent(i))) 
    else:
        if double_fake["hists"][0].GetBinContent(i) < 0:
            print "Warning: double fake estimate is "+str(double_fake["hists"][0].GetBinContent(i))+ " for bin " + str(i) + ". It will be replaced with 0.0001"
        dcard.write(" 0.0001") 

    if e_to_p["hists"][0].GetBinContent(i) > 0:        
        dcard.write(" "+str(e_to_p["hists"][0].GetBinContent(i))) 
    else:
        dcard.write(" 0.0001") 
   
    dcard.write('\n')    

    dcard.write("lumi_13tev lnN")
    dcard.write(" 1.027")

    for label in labels.keys():
        if label == "no label" or label == "wg+jets":
            continue
        dcard.write(" 1.027")

    dcard.write(" -")
    dcard.write(" -")
    dcard.write(" -")
    dcard.write(" 1.027")

    dcard.write('\n')    

    if sm_lhe_weight_hist.GetBinContent(i) > 0:
        dcard.write("mcstat_ewdim6_bin"+str(i)+" lnN "+str(1+sm_lhe_weight_hist.GetBinError(i)/sm_lhe_weight_hist.GetBinContent(i)))
        
#        dcard.write("mcstat_ewdim6_bin"+str(i)+" lnN "+str(1+labels["wg+jets"]["hists"][0].GetBinError(i)/labels["wg+jets"]["hists"][0].GetBinContent(i)))
        for label in labels.keys():
            if label == "no label" or label == "wg+jets":
                continue
            dcard.write(" -")

        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write("\n")  

    for label in labels.keys():
        if label == "no label" or label == "wg+jets":
            continue

        if labels[label]["hists"][0].GetBinContent(i) > 0:
            dcard.write("mcstat_"+str(label)+"_bin"+str(i)+" lnN ")
            dcard.write(" -")

            for l in labels.keys():
                if l == "no label" or l == "wg+jets":
                    continue
                if l == label:
                    dcard.write(" "+str(1+labels[label]["hists"][0].GetBinError(i)/labels[label]["hists"][0].GetBinContent(i)))
                else:    
                    dcard.write(" -")

            dcard.write(" -")                
            dcard.write(" -")                
            dcard.write(" -")                
            dcard.write(" -")                
            dcard.write("\n")  

    if fake_lepton["hists"][0].GetBinContent(i) > 0:        
        dcard.write("fake_lepton_syst lnN -")
        for label in labels.keys():
            if label == "no label" or label == "wg+jets":
                continue
            dcard.write(" -")

        dcard.write(" -")                
        dcard.write(" 1.3")                
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write("\n")  

    if fake_lepton["hists"][0].GetBinContent(i) > 0:        
        dcard.write("fake_lepton_stat lnN -")
        for label in labels.keys():
            if label == "no label" or label == "wg+jets":
                continue
            dcard.write(" -")

        dcard.write(" -")                
        dcard.write(" "+str(1+fake_lepton["hists"][0].GetBinError(i)/fake_lepton["hists"][0].GetBinContent(i)))
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write("\n")  

    if fake_photon["hists"][0].GetBinContent(i) > 0:        
        dcard.write("fake_photon_stat lnN -")
        for label in labels.keys():
            if label == "no label" or label == "wg+jets":
                continue
            dcard.write(" -")

        dcard.write(" "+str(1+fake_photon["hists"][0].GetBinError(i)/fake_photon["hists"][0].GetBinContent(i)))
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write(" -")                
        dcard.write("\n")  
