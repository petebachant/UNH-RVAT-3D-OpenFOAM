#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processing for UNH-RVAT 3D OpenFOAM simulation.

by Pete Bachant (petebachant@gmail.com)

"""
from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np
import os
from pxl import styleplot, fdiff
import sys
import foampy
import pandas as pd

#import seaborn
styleplot.setpltparams(latex=False)
    
exp_path = "/media/pete/External 2/Research/Experiments/2014 Spring RVAT Re dep"

# Some constants
R = 0.5
U = 1.0
U_infty = 1.0
H = 0.5
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
        print("Performance from {} degrees onward:".format(theta_0))
        print("Mean TSR =", meantsr)
        print("Mean C_P =", meancp)
        print("Mean C_D =", meancd)
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
    
def calcwake(t1=0.0):
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
    for n in range(len(t)):
        data = loadwake(t[n])
        for m in range(len(z_H)):
            u[n,m,:] = data[z_H[m]][1]
            v[n,m,:] = data[z_H[m]][2]
            w[n,m,:] = data[z_H[m]][3]
            xvorticity[n,m,:] = data[z_H[m]][4]
    meanu = u.mean(axis=0)
    meanv = v.mean(axis=0)
    meanw = w.mean(axis=0)
    xvorticity = xvorticity.mean(axis=0)
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
    
def plotwake(plotlist=["meanu"], t1=3.0, save=False, savepath="", 
             savetype=".pdf"):
    data = calcwake(t1=t1)
    y_R = data["y/R"]
    z_H = data["z/H"]
    u = data["meanu"]
    v = data["meanv"]
    w = data["meanw"]
    xvorticity = data["xvorticity"]
    def turb_lines(half=False):
        if half:
            plt.hlines(0.5, -1, 1, linestyles='solid', linewidth=2)
            plt.vlines(-1, 0, 0.5, linestyles='solid', linewidth=2)
            plt.vlines(1, 0, 0.5, linestyles='solid', linewidth=2)
        else:
            plt.hlines(0.5, -1, 1, linestyles='solid', colors='gray',
                       linewidth=3)
            plt.hlines(-0.5, -1, 1, linestyles='solid', colors='gray',
                       linewidth=3)
            plt.vlines(-1, -0.5, 0.5, linestyles='solid', colors='gray',
                       linewidth=3)
            plt.vlines(1, -0.5, 0.5, linestyles='solid', colors='gray',
                       linewidth=3)
    if "meanu" in plotlist or "all" in plotlist:
        plt.figure(figsize=(9,8))
        cs = plt.contourf(y_R, z_H, u, 20, cmap=plt.cm.coolwarm)
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.12)
        cb.set_label(r'$U/U_{\infty}$')
        turb_lines()
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
        #turb_lines()
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
        turb_lines()
        ax = plt.axes()
        ax.set_aspect(2)
        plt.tight_layout()
        if save:
            plt.savefig(savepath+'/xvorticity_3drans'+savetype)
    if "meancomboquiv" in plotlist or "all" in plotlist:
        plt.figure(figsize=(9, 8))
        # Add contours of mean velocity
        cs = plt.contourf(y_R, z_H, u, 20, cmap=plt.cm.coolwarm)
        cb = plt.colorbar(cs, shrink=1, extend='both', 
                          orientation='horizontal', pad=0.12)
        cb.set_label(r'$U/U_{\infty}$')
        plt.hold(True)
        # Make quiver plot of v and w velocities
        Q = plt.quiver(y_R, z_H, v, w, angles='xy', width=0.0022)
        plt.xlabel(r'$y/R$')
        plt.ylabel(r'$z/H$')
        #plt.ylim(-0.2, 0.78)
        #plt.xlim(-3.2, 3.2)
        plt.xlim(-3.66, 3.66)
        plt.ylim(-1.22, 1.22)
        plt.quiverkey(Q, 0.8, 0.22, 0.1, r'$0.1 U_\infty$',
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
        plt.tight_layout()
        if save:
            plt.savefig(savepath+"\\meancomboquiv_AD"+savetype)
    plt.show()
        
def plotexpwake(Re_D, quantity, z_H=0.0, save=False, savepath="", 
                savetype=".pdf", newfig=True, marker="--ok",
                fill="none", figsize=(10, 5)):
    """Plots the transverse wake profile of some quantity. These can be
      * meanu
      * meanv
      * meanw
      * stdu
    """
    U = Re_D/1e6
    label = "Exp."
    folder = exp_path + "/Wake/U_" + str(U) + "/Processed/"
    z_H_arr = np.load(folder + "z_H.npy")
    i = np.where(z_H_arr==z_H)
    q = np.load(folder + quantity + ".npy")[i]
    y_R = np.load(folder + "y_R.npy")[i]
    if newfig:
        plt.figure(figsize=figsize)
    plt.plot(y_R, q/U, marker, markerfacecolor=fill, label=label)
    plt.xlabel(r"$y/R$")
    plt.ylabel(ylabels[quantity])
    plt.grid(True)

def main():
    p = "Google Drive/Research/Papers/JOT CFT near-wake/Figures"
    if "linux" in sys.platform:
        p = "/home/pete/" + p
    elif "win" in sys.platform:
        p = "C:/Users/Pete/" + p
    plt.close("all")
    
#    plotwake(plotlist=["xvorticity", "meancomboquiv"], t1=3.0, 
#             save=False, savepath=p)
#    calcwake()
#    plot_wake_profile()
    calc_perf(plot=True, inertial=True)

if __name__ == "__main__":
    main()
