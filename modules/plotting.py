#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plotting for UNH-RVAT 3D OpenFOAM simulation.
"""

from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np
import os
from pxl import fdiff
import sys
import foampy
import pandas as pd
from modules.processing import *

ylabels = {"meanu" : r"$U/U_\infty$",
           "stdu" : r"$\sigma_u/U_\infty$",
           "meanv" : r"$V/U_\infty$",
           "meanw" : r"$W/U_\infty$",
           "meanuv" : r"$\overline{u'v'}/U_\infty^2$"}

def plot_perf():
    calc_perf(plot=True)

def plot_u_profile(z_H=0.0, newfig=True, save=False, savedir="figures", 
                   savetype=".pdf"):
    """Plot mean streamwise velocity profile."""
    df = load_u_profile(z_H)
    if newfig:
        plt.figure()
    plt.plot(df.y_R, df.u/U_infty, "k", label="SA (3-D)")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$U/U_\infty$")
    plt.grid(True)
    plt.tight_layout()
    if save:
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
        plt.savefig(os.path.join(savedir, 
                    "u_profile_{}_SA".format(z_H) + savetype))
                    
def plot_k_profile(z_H=0.0, amount="total", newfig=True, save=False):
    """Plot turbulence kinetic energy profile."""
    df = load_k_profile(z_H)
    if newfig:
        plt.figure()
    k = df["k_{}".format(amount)]
    plt.plot(df.y_R, k/U_infty**2, "k", label="SA (2-D)")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$k/U_\infty^2$")
    plt.grid(True)
    plt.tight_layout()
    if save:
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
        plt.savefig(os.path.join(savedir, "k_{}_profile_{}_SA{}".format(
                amount, z_H, savetype)))

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


if __name__ == "__main__":
    pass
