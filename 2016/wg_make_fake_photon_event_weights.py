#there is a bug which causes a crash inside of the TFractionFitter destructor: https://sft.its.cern.ch/jira/browse/ROOT-9414
#I think this makes it necessary to create the tfractionfitters only once for each set of input files that are used, and then reuse the tfractionfitters

import sys
import random
import ROOT
import numpy as np
import json

from pprint import pprint

ROOT.gStyle.SetOptStat(0)

fake_fractions = {}

fake_event_weights = {}

fake_fractions["muon_barrel"] = []

fake_fractions["muon_endcap"] = []

fake_fractions["electron_barrel"] = []

fake_fractions["electron_endcap"] = []

fake_event_weights["muon_barrel"] = []

fake_event_weights["muon_endcap"] = []

fake_event_weights["electron_barrel"] = []

fake_event_weights["electron_endcap"] = []

#lepton_names =["muon","electron"]
lepton_names =["electron","muon"]
#lepton_names =["muon"]


photon1_eta_ranges = ["abs(photon1_eta) < 1.4442","abs(photon1_eta) > 1.566 && abs(photon1_eta) < 2.5"]
photon2_eta_ranges = ["abs(photon2_eta) < 1.4442","abs(photon2_eta) > 1.566 && abs(photon2_eta) < 2.5"]

photon1_pt_range_cutstrings = ["photon1_pt > 20 && photon1_pt < 25","photon1_pt > 25 && photon1_pt < 30","photon1_pt > 30 && photon1_pt < 40","photon1_pt > 40 && photon1_pt < 50","photon1_pt > 50 && photon1_pt < 70","photon1_pt > 70 && photon1_pt < 100","photon1_pt > 100 && photon1_pt < 135","photon1_pt > 135 && photon1_pt < 400"]

photon2_pt_range_cutstrings = ["photon2_pt > 20 && photon2_pt < 25","photon2_pt > 25 && photon2_pt < 30","photon2_pt > 30 && photon2_pt < 40","photon2_pt > 40 && photon2_pt < 50","photon2_pt > 50 && photon2_pt < 70","photon2_pt > 70 && photon2_pt < 100","photon2_pt > 100 && photon2_pt < 135","photon2_pt > 135 && photon2_pt < 400"]

assert(len(photon1_pt_range_cutstrings) == len(photon2_pt_range_cutstrings))
assert(len(photon2_eta_ranges) == len(photon2_eta_ranges))

veto_signal_selection_cutstring = "!((met > 70 && mt > 30 && lepton_pt > 30 && photon_pt > 25 && lepton_pdg_id == 11) || (met > 70 && mt > 30 && lepton_pt > 25 && photon_pt > 25 && lepton_pdg_id == 13))" #need to fix this such that it uses photon1 and photon2 branches

#veto_signal_selection_cutstring = "1"

index = 0

muon_fake_photon_file = ROOT.TFile.Open("/afs/cern.ch/work/a/amlevin/data/wg/2016/14Dec2018/single_muon_fake_photon.root")
electron_fake_photon_file = ROOT.TFile.Open("/afs/cern.ch/work/a/amlevin/data/wg/2016/14Dec2018/single_electron_fake_photon.root")
real_photon_template_file = ROOT.TFile.Open("/afs/cern.ch/work/a/amlevin/data/wg/2016/14Dec2018/real_photon_template.root")

created_muon_fitter = False
created_electron_fitter = False


for lepton_name in lepton_names:

    if lepton_name == "muon":
        lepton_pdg_id = "13"
    else:
        lepton_pdg_id = "11"

    if lepton_name == "muon":
        fake_photon_file = muon_fake_photon_file
    else:
        fake_photon_file = electron_fake_photon_file

    for i in range(len(photon1_eta_ranges)):
        for j in range(len(photon1_pt_range_cutstrings)):

            photon1_eta_range = photon1_eta_ranges[i]
            photon2_eta_range = photon2_eta_ranges[i]
            photon1_pt_range_cutstring = photon1_pt_range_cutstrings[j]
            photon2_pt_range_cutstring = photon2_pt_range_cutstrings[j]

            if photon1_eta_range == "abs(photon1_eta) < 1.4442":
                sieie_cut = 0.01022
                n_bins = 128
                sieie_lower = 0.00
                sieie_upper = 0.04
            else:
                sieie_cut = 0.03001
                #n_bins = 160                                                                                                                                                             
                #n_bins = 80                                                                                                                                                              
                n_bins = 20
                sieie_lower = 0.01
                sieie_upper = 0.06


            fake_photon_tree = fake_photon_file.Get("Events")
            total_hist = ROOT.TH1F("total_sieie_for_fake_photon_fraction_hist","total_sieie_for_fake_photon_fraction_hist",n_bins,sieie_lower,sieie_upper)
            total_hist.Sumw2()
            fake_photon_tree.Draw("photon1_sieie >> total_sieie_for_fake_photon_fraction_hist",photon1_eta_range+" && (photon1_selection == 1 || photon1_selection == 2) && "+photon1_pt_range_cutstring + " && pass_selection1 && "+str(veto_signal_selection_cutstring))

            fake_photon_template_hist = ROOT.TH1F("fake_photon_template_hist","fake_photon_template_hist",n_bins,sieie_lower,sieie_upper)
            fake_photon_template_hist.Sumw2()
            fake_photon_tree.Draw("photon2_sieie >> fake_photon_template_hist",photon2_eta_range + " && lepton_pdg_id == "+lepton_pdg_id+" && "+photon2_pt_range_cutstring + " && pass_selection2 && "+str(veto_signal_selection_cutstring))

            real_photon_template_tree = real_photon_template_file.Get("Events")
            real_photon_template_hist = ROOT.TH1F("real_photon_template_hist","real_photon_template_hist",n_bins,sieie_lower,sieie_upper)
            real_photon_template_hist.Sumw2()
            for k in range(real_photon_template_tree.GetEntries()):
                real_photon_template_tree.GetEntry(k)

                pass_eta_range = False

                if photon1_eta_range == "abs(photon1_eta) < 1.4442":
                    if abs(real_photon_template_tree.photon_eta) < 1.4442:
                        pass_eta_range = True
                elif photon1_eta_range == "abs(photon1_eta) > 1.566 && abs(photon1_eta) < 2.5":
                    if 1.4442 < abs(real_photon_template_tree.photon_eta) and abs(real_photon_template_tree.photon_eta) < 2.5:
                        pass_eta_range = True
                else:
                    assert(0)

                pass_lepton_pdg_id = False

                if str(real_photon_template_tree.lepton_pdg_id) == lepton_pdg_id:
                    pass_lepton_pdg_id = True

                pass_photon_pt_range = False

                if photon1_pt_range_cutstring == "photon1_pt > 20 && photon1_pt < 25":
                    if real_photon_template_tree.photon_pt > 20 and real_photon_template_tree.photon_pt < 25:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 25 && photon1_pt < 30":
                    if real_photon_template_tree.photon_pt > 25 and real_photon_template_tree.photon_pt < 30:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 30 && photon1_pt < 40":
                    if real_photon_template_tree.photon_pt > 30 and real_photon_template_tree.photon_pt < 40:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 40 && photon1_pt < 50":
                    if real_photon_template_tree.photon_pt > 40 and real_photon_template_tree.photon_pt < 50:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 50 && photon1_pt < 70":
                    if real_photon_template_tree.photon_pt > 50 and real_photon_template_tree.photon_pt < 70:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 70 && photon1_pt < 100":
                    if real_photon_template_tree.photon_pt > 70 and real_photon_template_tree.photon_pt < 100:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 100 && photon1_pt < 135":
                    if real_photon_template_tree.photon_pt > 100 and real_photon_template_tree.photon_pt < 135:
                        pass_photon_pt_range = True
                elif photon1_pt_range_cutstring == "photon1_pt > 135 && photon1_pt < 400":
                    if real_photon_template_tree.photon_pt > 135 and real_photon_template_tree.photon_pt < 400:
                        pass_photon_pt_range = True
                else:
                    assert(0)


                pass_signal_selection_veto = not ((real_photon_template_tree.met > 70 and real_photon_template_tree.mt > 30 and real_photon_template_tree.lepton_pt > 30 and real_photon_template_tree.photon_pt > 25 and real_photon_template_tree.lepton_pdg_id == 11) or (real_photon_template_tree.met > 70 and real_photon_template_tree.mt > 30 and real_photon_template_tree.lepton_pt > 25 and real_photon_template_tree.photon_pt > 25 and real_photon_template_tree.lepton_pdg_id == 13))

                if pass_photon_pt_range and pass_lepton_pdg_id and pass_eta_range and pass_signal_selection_veto:

                    if real_photon_template_tree.gen_weight > 0:
                        real_photon_template_hist.Fill(real_photon_template_tree.photon_sieie)
                    else:
                        real_photon_template_hist.Fill(real_photon_template_tree.photon_sieie,-1)

            for k in range(real_photon_template_hist.GetNbinsX()+2):
                if real_photon_template_hist.GetBinContent(k) < 0:
                    real_photon_template_hist.SetBinContent(k,0)

            mc = ROOT.TObjArray(2)

            mc.Add(fake_photon_template_hist)
            mc.Add(real_photon_template_hist)

            ffitter = ROOT.TFractionFitter(total_hist,mc)


            c1 = ROOT.TCanvas("c1", "c1",5,50,500,500);

            real_photon_template_hist.GetXaxis().SetTitle("\sigma_{i \eta i \eta}")
            real_photon_template_hist.SetLineWidth(2)
#            real_photon_template_hist.Draw("hist")
            real_photon_template_hist.Draw()


            if photon1_eta_range == "abs(photon1_eta) < 1.4442":
                eta_range_no_spaces = "barrel"
            elif photon1_eta_range == "abs(photon1_eta) > 1.566 && abs(photon1_eta) < 2.5":
                eta_range_no_spaces = "endcap"
            else:
                assert(0)

            if photon1_pt_range_cutstring == "photon1_pt > 20 && photon1_pt < 25":
                photon_pt_range_cutstring_no_spaces = "20to25"
            elif photon1_pt_range_cutstring == "photon1_pt > 25 && photon1_pt < 30":
                photon_pt_range_cutstring_no_spaces = "25to30"
            elif photon1_pt_range_cutstring == "photon1_pt > 30 && photon1_pt < 40":
                photon_pt_range_cutstring_no_spaces = "30to40"
            elif photon1_pt_range_cutstring == "photon1_pt > 40 && photon1_pt < 50":
                photon_pt_range_cutstring_no_spaces = "40to50"
            elif photon1_pt_range_cutstring == "photon1_pt > 50 && photon1_pt < 70":
                photon_pt_range_cutstring_no_spaces = "50to70"
            elif photon1_pt_range_cutstring == "photon1_pt > 70 && photon1_pt < 100":
                photon_pt_range_cutstring_no_spaces = "70to100"
            elif photon1_pt_range_cutstring == "photon1_pt > 100 && photon1_pt < 135":
                photon_pt_range_cutstring_no_spaces = "100to135"
            elif photon1_pt_range_cutstring == "photon1_pt > 135 && photon1_pt < 400":
                photon_pt_range_cutstring_no_spaces = "135to400"
            else:
                   assert(0)


            c1.SaveAs("/eos/user/a/amlevin/www/wg/2016/fake-photon/"+lepton_name+"/"+eta_range_no_spaces+"/real_photon_template_"+photon_pt_range_cutstring_no_spaces+".png")

            fake_photon_template_hist.GetXaxis().SetTitle("\sigma_{i \eta i \eta}")
            fake_photon_template_hist.SetLineWidth(2)
            fake_photon_template_hist.Draw()

            c1.SaveAs("/eos/user/a/amlevin/www/wg/2016/fake-photon/"+lepton_name+"/"+eta_range_no_spaces+"/fake_photon_template_"+photon_pt_range_cutstring_no_spaces+".png")

            #raw_input()                                                                                                                                                                  

            ffitter.Fit()

            total_hist.GetXaxis().SetTitle("\sigma_{i \eta i \eta}")            
            total_hist.SetLineWidth(2)            
            total_hist.Draw()

            c1.SaveAs("/eos/user/a/amlevin/www/wg/2016/fake-photon/"+lepton_name+"/"+eta_range_no_spaces+"/total_"+photon_pt_range_cutstring_no_spaces+".png")

            total_hist.SetLineColor(ROOT.kBlack)
            total_hist.SetMarkerColor(ROOT.kBlack)
            total_hist.Draw()

            ffitter.GetPlot().SetLineColor(ROOT.kRed)

            ffitter.GetPlot().SetOption("")
            ffitter.GetPlot().Draw("hist same l")

            black_th1f=ROOT.TH1F("black_th1f","black_th1f",1,0,1)
            black_th1f.SetLineColor(ROOT.kBlack)
            black_th1f.SetLineWidth(2)
#            black_th1f.SetLineStyle(ROOT.kDashed)
            red_th1f=ROOT.TH1F("red_th1f","red_th1f",1,0,1)
            red_th1f.SetLineColor(ROOT.kRed)
            red_th1f.SetLineWidth(2)
#            red_th1f.SetLineStyle(ROOT.kDashed)
            blue_th1f=ROOT.TH1F("blue_th1f","blue_th1f",1,0,1)
            blue_th1f.SetLineColor(ROOT.kBlue)
            blue_th1f.SetLineWidth(2)
#            blue_th1f.SetLineStyle(ROOT.kDashed)
            blue_dashed_th1f=ROOT.TH1F("blue_th1f","blue_th1f",1,0,1)
            blue_dashed_th1f.SetLineColor(ROOT.kBlue)
            blue_dashed_th1f.SetLineWidth(2)
            blue_dashed_th1f.SetLineStyle(ROOT.kDashed)
            
            legend1 = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
            legend1.SetBorderSize(0)  # no border
            legend1.SetFillStyle(0)  # make transparent
            legend1.AddEntry(black_th1f,"data fitted to","lp")
            legend1.AddEntry(red_th1f,"fit result","lp")
            legend1.Draw("same")

            c1.SaveAs("/eos/user/a/amlevin/www/wg/2016/fake-photon/"+lepton_name+"/"+eta_range_no_spaces+"/fit_"+photon_pt_range_cutstring_no_spaces+".png")


            c1.ForceUpdate()
            c1.Modified()

            value = ROOT.Double(-1)
            error = ROOT.Double(-1)

            ffitter.GetResult(0,value,error)

            print str(value) + "+/-" + str(error)

            ffitter.GetPlot().SetOption("")
            ffitter.GetPlot().SetLineColor(ROOT.kRed)
#            ffitter.GetPlot().SetLineWidth(2)
            ffitter.GetPlot().Draw("hist l")
            real_component = real_photon_template_hist.Clone("real component")
            fake_component = fake_photon_template_hist.Clone("fake component")
            
            real_component.SetLineColor(ROOT.kBlue)
            fake_component.SetLineColor(ROOT.kBlue)
            fake_component.SetLineStyle(ROOT.kDashed)

            real_component.Scale((1-value)*ffitter.GetPlot().Integral()/real_component.Integral())
            fake_component.Scale(value*ffitter.GetPlot().Integral()/fake_component.Integral())
            
            real_component.Draw("hist same l")
            fake_component.Draw("hist same l")
            ffitter.GetPlot().Draw("hist same l")

            legend1 = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
            legend1.SetBorderSize(0)  # no border
            legend1.SetFillStyle(0)  # make transparent
            legend1.AddEntry(red_th1f,"fit result","lp")
            legend1.AddEntry(blue_th1f,"true component","lp")
            legend1.AddEntry(blue_dashed_th1f,"fake component","lp")
            legend1.Draw("same")

            c1.ForceUpdate()
            c1.Modified()

            c1.SaveAs("/eos/user/a/amlevin/www/wg/2016/fake-photon/"+lepton_name+"/"+eta_range_no_spaces+"/components_"+photon_pt_range_cutstring_no_spaces+".png")


            print total_hist.GetXaxis().FindFixBin( sieie_cut )

            print value*fake_photon_template_hist.Integral()/total_hist.Integral()

#            print total_sieie_for_fake_photon_fraction_tree.GetEntries(eta_range+" && lepton_pdg_id == "+lepton_pdg_id+" && (photon_selection == 0 || photon_selection == 1) && "+ photon_pt_range_cutstring)                                                                                                                                                                     
            print fake_photon_tree.GetEntries(photon1_eta_range+" && (photon1_selection == 0 || photon1_selection == 1) && "+ photon1_pt_range_cutstring+ " && pass_selection1")

            print value*fake_photon_template_hist.Integral(1,fake_photon_template_hist.GetXaxis().FindFixBin( sieie_cut ))*total_hist.Integral()/total_hist.Integral(1,total_hist.GetXaxis().FindFixBin( sieie_cut ))/fake_photon_template_hist.Integral()


            array_fitted_fraction = np.array([value,error])

            array_fake_fraction = array_fitted_fraction * fake_photon_template_hist.Integral(1,fake_photon_template_hist.GetXaxis().FindFixBin( sieie_cut ))*total_hist.Integral()/total_hist.Integral(1,total_hist.GetXaxis().FindFixBin( sieie_cut ))/fake_photon_template_hist.Integral()
            array_fake_event_weight = array_fitted_fraction * fake_photon_template_hist.Integral(1,fake_photon_template_hist.GetXaxis().FindFixBin( sieie_cut ))*total_hist.Integral()/fake_photon_template_hist.Integral()/fake_photon_tree.GetEntries(photon1_eta_range + " && (photon1_selection == 0 || photon1_selection == 1) && "+ photon1_pt_range_cutstring + " && pass_selection1")

            if photon1_eta_range == "abs(photon1_eta) < 1.4442":
                fake_fractions[lepton_name+ "_barrel"].append(list(array_fake_fraction))
            else:
                fake_fractions[lepton_name+ "_endcap"].append(list(array_fake_fraction))

            if photon1_eta_range == "abs(photon1_eta) < 1.4442":
                fake_event_weights[lepton_name+"_barrel"].append(list(array_fake_event_weight))
            else:
                fake_event_weights[lepton_name+"_endcap"].append(list(array_fake_event_weight))


pprint(fake_fractions)

pprint(fake_event_weights)

json.dump(fake_event_weights,open("fake_photon_event_weights_data.txt","w"))

json.dump(fake_fractions,open("fake_photon_fractions_data.txt","w"))

