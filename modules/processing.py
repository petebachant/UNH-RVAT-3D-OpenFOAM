#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processing for UNH-RVAT 3D OpenFOAM simulation.
"""

from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np
import os
from pxl import fdiff
import sys
import foampy
import pandas as pd


# Some constants
R = 0.5
U = 1.0
U_infty = 1.0
H = 1.0
D = 1.0
A = H*D
area = A
rho = 1000.0

ylabels = {"meanu" : r"$U/U_\infty$",
           "stdu" : r"$\sigma_u/U_\infty$",
           "meanv" : r"$V/U_\infty$",
           "meanw" : r"$W/U_\infty$",
           "meanuv" : r"$\overline{u'v'}/U_\infty^2$"}
           
def calc_perf(theta_0=360, plot=False, verbose=True, inertial=False):
    t, torque, drag = foampy.load_all_torque_drag()
    _t, theta, omega = foampy.load_theta_omega(t_interp=t)
    reached_theta_0 = True
    if theta.max() < theta_0:
        theta_0 = 1
        reached_theta_0 = False
    # Compute tip speed ratio
    tsr = omega*R/U_infty
    # Compute mean TSR
    meantsr = np.mean(tsr[theta >= theta_0])
    if inertial:
        inertia = 3 # guess from SolidWorks model
        inertial_torque = inertia*fdiff.second_order_diff(omega, t)
        torque -= inertial_torque
    # Compute power coefficient
    power = torque*omega
    cp = power/(0.5*rho*area*U_infty**3)
    meancp = np.mean(cp[theta >= theta_0])
    # Compute drag coefficient
    cd = drag/(0.5*rho*area*U_infty**2)
    meancd = np.mean(cd[theta >= theta_0])
    if verbose:
        print("Performance from {:.1f}--{:.1f} degrees:".format(theta_0, 
                                                                theta.max()))
        print("Mean TSR = {:.3f}".format(meantsr))
        print("Mean C_P = {:.3f}".format(meancp))
        print("Mean C_D = {:.3f}".format(meancd))
    if plot:
        plt.close('all')
        plt.plot(theta[5:], cp[5:])
        plt.title(r"$\lambda = %1.1f$" %meantsr)
        plt.xlabel(r"$\theta$ (degrees)")
        plt.ylabel(r"$C_P$")
        #plt.ylim((0, 1.0))
        plt.tight_layout()
        plt.show()
    if reached_theta_0:
        return {"C_P" : meancp, 
                "C_D" : meancd, 
                "TSR" : meantsr}
    else:
        return {"C_P" : "nan", 
                "C_D" : "nan", 
                "TSR" : "nan"}

def plot_perf():
    calc_perf(plot=True)
    
def loadwake(time):
    """Loads wake data and returns y/R and statistics."""
    # Figure out if time is an int or float
    if not isinstance(time, str):
        if time % 1 == 0:
            folder = str(int(time))
        else:
            folder = str(time)
    else:
        folder = time
    flist = os.listdir("postProcessing/sets/"+folder)
    data = {}
    for fname in flist:
        fpath = "postProcessing/sets/"+folder+"/"+fname
        z_H = float(fname.split("_")[1])
        data[z_H] = np.loadtxt(fpath, unpack=True)
    return data
    
def calcwake(t1=0.0, save=False):
    times = os.listdir("postProcessing/sets")
    times = [float(time) for time in times]
    times.sort()
    times = np.asarray(times)
    data = loadwake(times[0])
    z_H = np.asarray(sorted(data.keys()))
    y_R = data[z_H[0]][0]/R
    # Find first timestep from which to average over
    t = times[times >= t1]
    # Assemble 3-D arrays, with time as first index
    u = np.zeros((len(t), len(z_H), len(y_R)))
    v = np.zeros((len(t), len(z_H), len(y_R)))
    w = np.zeros((len(t), len(z_H), len(y_R)))
    xvorticity = np.zeros((len(t), len(z_H), len(y_R)))
    # Loop through all times
    for n, t_i in enumerate(t):
        print("Loading sampled velocity data for t = {}".format(t_i))
        data = loadwake(t[n])
        for m, z_H_i in enumerate(z_H):
            u[n,m,:] = data[z_H_i][1]
            v[n,m,:] = data[z_H_i][2]
            w[n,m,:] = data[z_H_i][3]
            try:
                xvorticity[n,m,:] = data[z_H_i][4]
            except IndexError:
                pass
    meanu = u.mean(axis=0)
    meanv = v.mean(axis=0)
    meanw = w.mean(axis=0)
    xvorticity = xvorticity.mean(axis=0)
    if save:
        df = pd.DataFrame(meanu, index=z_H, columns=y_R)
        df.to_csv("processed/mean_u.csv")
        df = pd.DataFrame(meanv, index=z_H, columns=y_R)
        df.to_csv("processed/mean_v.csv")
        df = pd.DataFrame(meanw, index=z_H, columns=y_R)
        df.to_csv("processed/mean_w.csv")
        df = pd.DataFrame(xvorticity, index=z_H, columns=y_R)
        df.to_csv("processed/xvorticity.csv")
    return {"meanu" : meanu,
            "meanv" : meanv,
            "meanw" : meanw,
            "xvorticity" : xvorticity,
            "y/R" : y_R, 
            "z/H" : z_H}

def plot_wake_profile(quantity="meanu", z_H=0.0, t1=3.0, save=False, savepath="",
                      savetype=".pdf"):
    """Plots a 2-D wake profile for a given quantity"""
    data = calcwake(t1=t1)
    y_R = data["y/R"]
    z_H = data["z/H"]
    df = pd.DataFrame(data[quantity], index=z_H, columns=y_R)
    d = df.loc[0, :]
    plt.figure()
    plt.plot(y_R, d.values)
    plt.xlabel("$y/R$")
    plt.ylabel("$U/U_\infty$")
    plt.show()
    
def plotwake(plotlist=["meancontquiv"], t1=3.0, save=False, savepath="", 
             savetype=".pdf", show=False):
    data = calcwake(t1=t1)
    y_R = data["y/R"]
    z_H = data["z/H"]
    u = data["meanu"]
    v = data["meanv"]
    w = data["meanw"]
    xvorticity = data["xvorticity"]
    if "meanu" in plotlist or "all" in plotlist:
        plt.figure(figsize=(9,8))
        cs = plt.contourf(y_R, z_H, u, 20, cmap=plt.cm.coolwarm)
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.12)
        cb.set_label(r'$U/U_{\infty}$')
        plot_turb_lines()
        ax = plt.axes()
        ax.set_aspect(2)
    if "meanv" in plotlist or "all" in plotlist:
        plt.figure(figsize=(10,5))
        cs = plt.contourf(y/0.5, z, v, 20, cmap=plt.cm.coolwarm)
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.22)
        cb.set_label(r'$V/U_{\infty}$')
        #plot_turb_lines()
        ax = plt.axes()
        ax.set_aspect(2)
        plt.grid(True)
        plt.yticks([0,0.13,0.25,0.38,0.5,0.63])
    if "v-wquiver" in plotlist or "all" in plotlist:
        # Make quiver plot of v and w velocities
        plt.figure(figsize=(10,5))
        Q = plt.quiver(y_R, z_H, v, w, angles='xy')
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        plt.ylim(-0.2, 0.78)
        plt.xlim(-3.2, 3.2)
        plt.quiverkey(Q, 0.75, 0.2, 0.1, r'$0.1$ m/s',
                   labelpos='E',
                   coordinates='figure',
                   fontproperties={'size': 'small'})
        plt.tight_layout()
        plt.hlines(0.5, -1, 1, linestyles='solid', colors='r',
                   linewidth=2)
        plt.vlines(-1, -0.2, 0.5, linestyles='solid', colors='r',
                   linewidth=2)
        plt.vlines(1, -0.2, 0.5, linestyles='solid', colors='r',
                   linewidth=2)
        ax = plt.axes()
        ax.set_aspect(2)
        plt.yticks([0,0.13,0.25,0.38,0.5,0.63])
        if save:
            plt.savefig(savepath+'v-wquiver'+savetype)
    if "xvorticity" in plotlist or "all" in plotlist:
        plt.figure(figsize=(9,8))
        cs = plt.contourf(y_R, z_H, xvorticity, 10, cmap=plt.cm.coolwarm,
                          levels=np.linspace(-2.5,2.5,21))
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.12)
        cb.set_ticks(np.linspace(-2.5,2.5,11), update_ticks=True)
        cb.set_label(r"$\Omega_x$")
        plot_turb_lines()
        ax = plt.axes()
        ax.set_aspect(2)
        plt.tight_layout()
        if save:
            plt.savefig(savepath+'/xvorticity_3drans'+savetype)
    if "meancontquiv" in plotlist or "all" in plotlist:
        plt.figure(figsize=(9, 5))
        # Add contours of mean velocity
        cs = plt.contourf(y_R, z_H, u, 20, cmap=plt.cm.coolwarm)
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.16)
        cb.set_label(r'$U/U_{\infty}$')
        plt.hold(True)
        # Make quiver plot of v and w velocities
        Q = plt.quiver(y_R, z_H, v, w, angles='xy', width=0.0022)
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        plt.xlim(-3.66, 3.66)
        plt.ylim(0, 1.22)
        plt.quiverkey(Q, 0.8, 0.28, 0.1, r'$0.1 U_\infty$',
                      labelpos='E',
                      coordinates='figure',
                      fontproperties={'size': 'small'})
        plt.hlines(0.5, -1, 1, linestyles='solid', colors='gray',
                   linewidth=3)
        plt.hlines(-0.5, -1, 1, linestyles='solid', colors='gray',
                   linewidth=3)
        plt.vlines(-1, -0.5, 0.5, linestyles='solid', colors='gray',
                   linewidth=3)
        plt.vlines(1, -0.5, 0.5, linestyles='solid', colors='gray',
                   linewidth=3)
        ax = plt.axes()
        ax.set_aspect(2.0)
#        plt.yticks([0.0, 0.13, 0.25, 0.38, 0.5, 0.63, 0.75, 0.88, 1.0, 1.13])
        plt.tight_layout()
        if save:
            plt.savefig(savepath+"/meancontquiv"+savetype)
    if show:
        plt.show()

def plot_turb_lines(half=False):
    if half:
        plt.hlines(0.5, -1, 1, linestyles="solid", linewidth=2)
        plt.vlines(-1, 0, 0.5, linestyles="solid", linewidth=2)
        plt.vlines(1, 0, 0.5, linestyles="solid", linewidth=2)
    else:
        plt.hlines(0.5, -1, 1, linestyles="solid", colors="gray",
                   linewidth=3)
        plt.hlines(-0.5, -1, 1, linestyles="solid", colors="gray",
                   linewidth=3)
        plt.vlines(-1, -0.5, 0.5, linestyles="solid", colors="gray",
                   linewidth=3)
        plt.vlines(1, -0.5, 0.5, linestyles="solid", colors="gray",
                   linewidth=3)
                   
def plot_exp_lines():
    color = "gray"
    linewidth = 2
    """Plots the outline of the experimental y-z measurement plane"""
    plt.hlines(0.625, -3, 3, linestyles="dashed", colors=color,
               linewidth=linewidth)
    plt.hlines(0.0, -3, 3, linestyles="dashed", colors=color,
               linewidth=linewidth)
    plt.vlines(-3.0, 0.0, 0.625, linestyles="dashed", colors=color,
               linewidth=linewidth)
    plt.vlines(3.0, 0.0, 0.625, linestyles="dashed", colors=color,
               linewidth=linewidth)    
    
    
def plot_meancontquiv(save=False, show=False, savetype=".pdf", 
                      cb_orientation="vertical"):
    """Plot mean contours/quivers of velocity."""
    if not os.path.isfile("processed/mean_u.csv"):
        calcwake(t1=3.0, save=True)
    mean_u = pd.read_csv("processed/mean_u.csv", index_col=0)
    mean_v = pd.read_csv("processed/mean_v.csv", index_col=0)
    mean_w = pd.read_csv("processed/mean_w.csv", index_col=0)
    y_R = np.round(np.asarray(mean_u.columns.values, dtype=float), decimals=4)
    z_H = np.asarray(mean_u.index.values, dtype=float)
    plt.figure(figsize=(10,6))
    # Add contours of mean velocity
    cs = plt.contourf(y_R, z_H, mean_u,
                      np.arange(0.15, 1.25, 0.05), cmap=plt.cm.coolwarm)
    if cb_orientation == "horizontal":
        cb = plt.colorbar(cs, shrink=1, extend="both",
                          orientation="horizontal", pad=0.14)
    elif cb_orientation == "vertical":
        cb = plt.colorbar(cs, shrink=1, extend="both", 
                          orientation="vertical", pad=0.02)
    cb.set_label(r"$U/U_{\infty}$")
    plt.hold(True)
    # Make quiver plot of v and w velocities
    Q = plt.quiver(y_R, z_H, mean_v, mean_w, width=0.0022,
                   edgecolor="none")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$z/H$")
#    plt.ylim(-0.2, 0.78)
#    plt.xlim(-3.2, 3.2)
    if cb_orientation == "horizontal":
        plt.quiverkey(Q, 0.65, 0.26, 0.1, r"$0.1 U_\infty$",
                      labelpos="E",
                      coordinates="figure",
                      fontproperties={"size": "small"})
    elif cb_orientation == "vertical":
        plt.quiverkey(Q, 0.65, 0.055, 0.1, r"$0.1 U_\infty$",
                      labelpos="E",
                      coordinates="figure",
                      fontproperties={"size": "small"})
    plot_turb_lines()
    plot_exp_lines()
    ax = plt.axes()
    ax.set_aspect(2.0)
    plt.yticks(np.around(np.arange(-1.125, 1.126, 0.125), decimals=2))
    plt.tight_layout()
    if show:
        plt.show()
    if save:
        plt.savefig("figures/meancontquiv"+savetype)
    
def get_ncells(logname="log.checkMesh", keyword="cells"):
    if keyword == "cells":
        keyword = "cells:"
    with open(logname) as f:
        for line in f.readlines():
            ls = line.split()
            if ls and ls[0] == keyword:
                value = ls[1]
                return int(value)
                
def get_yplus(logname="log.yPlus"):
    with open(logname) as f:
        lines = f.readlines()
        for n in range(len(lines)):
            ls = lines[n].split()
            if ls and ls[-1] == "blades":
                nstart = n
                break
    line = lines[n+3]
    line = line.split()
    return {"min" : float(line[3]),
            "max" : float(line[5]),
            "mean" : float(line[7])}
            
def get_nx_nz():
    blocks = foampy.dictionaries.read_text("constant/polyMesh/blockMeshDict", 
                                           "blocks")
    nx = int(blocks[3].replace("(", "").split()[0])
    nz = int(blocks[3].replace(")", "").split()[2])
    return nx, nz

def get_nlayers_expratio():
    nlayers = foampy.dictionaries.read_single_line_value("snappyHexMeshDict",
            "nSurfaceLayers", valtype=int)
    expratio = foampy.dictionaries.read_single_line_value("snappyHexMeshDict",
            "expansionRatio")
    return nlayers, expratio
    
def get_ddt_scheme():
    block = foampy.dictionaries.read_text("system/fvSchemes", "ddtSchemes")
    val = block[2].replace(";", "").split()[1]
    return val
    
def get_max_courant_no():
    if foampy.dictionaries.read_single_line_value("controlDict", 
            "adjustTimeStep", valtype=str) == "yes":
        return foampy.dictionaries.read_single_line_value("controlDict", 
                                                          "maxCo")
    else:
        return "nan"
        
def get_deltat():
    if foampy.dictionaries.read_single_line_value("controlDict", 
                                                  "adjustTimeStep",
                                                  valtype=str) == "no":
        return foampy.dictionaries.read_single_line_value("controlDict", 
                                                          "deltaT")
    else:
        return "nan"

def log_perf(logname="all_perf.csv", mode="a", verbose=True):
    """Logs mean performance calculations to CSV file. If file exists, data
    is appended."""
    if not os.path.isdir("processed"):
        os.mkdir("processed")
    with open("processed/" + logname, mode) as f:
        if os.stat("processed/" + logname).st_size == 0:
            f.write("dt,maxco,nx,nz,ncells,nlayers,expratio,tsr,cp,cd,"\
                    + "yplus_min,yplus_max,yplus_mean,ddt_scheme\n")
        data = calc_perf(verbose=verbose)
        ncells = get_ncells()
        yplus = get_yplus()
        nx, nz = get_nx_nz()
        nlayers, expratio = get_nlayers_expratio()
        maxco = get_max_courant_no()
        dt = get_deltat()
        ddt_scheme = get_ddt_scheme()
        val_string = "{dt},{maxco},{nx},{nz},{ncells},{nlayers},{expratio},{tsr},"\
                + "{cp},{cd},{ypmin},{ypmax},{ypmean},{ddt_scheme}\n" 
        f.write(val_string.format(dt=dt,
                                  maxco=maxco,
                                  nx=nx,
                                  nz=nz,
                                  ncells=ncells,
                                  nlayers=nlayers,
                                  expratio=expratio,
                                  tsr=data["TSR"],
                                  cp=data["C_P"],
                                  cd=data["C_D"],
                                  ypmin=yplus["min"],
                                  ypmax=yplus["max"],
                                  ypmean=yplus["mean"],
                                  ddt_scheme=ddt_scheme))


if __name__ == "__main__":
    pass
