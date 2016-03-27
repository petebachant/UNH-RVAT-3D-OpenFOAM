#!/usr/bin/env python
"""Plotting for UNH-RVAT 3-D OpenFOAM simulation."""

from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np
import os
from pxl import fdiff
import sys
import foampy
import pandas as pd
from .processing import *

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


def plot_turb_lines(color="gray"):
    plt.hlines(0.5, -1, 1, linestyles="solid", colors=color, linewidth=2)
    plt.hlines(-0.5, -1, 1, linestyles="solid", colors=color, linewidth=2)
    plt.vlines(-1, -0.5, 0.5, linestyles="solid", colors=color, linewidth=2)
    plt.vlines(1, -0.5, 0.5, linestyles="solid", colors=color, linewidth=2)


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
    mean_u = load_vel_map("u")
    mean_v = load_vel_map("v")
    mean_w = load_vel_map("w")
    y_R = np.round(np.asarray(mean_u.columns.values, dtype=float), decimals=4)
    z_H = np.asarray(mean_u.index.values, dtype=float)
    plt.figure(figsize=(7.5, 4.8))
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
                   edgecolor="none", scale=3.0)
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$z/H$")
    # plt.ylim(-0.2, 0.78)
    # plt.xlim(-3.2, 3.2)
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

def plot_kcont(cb_orientation="vertical", newfig=True):
    """Plot contours of TKE."""
    k = load_k_map()
    y_R = np.round(np.asarray(k.columns.values, dtype=float), decimals=4)
    z_H = np.asarray(k.index.values, dtype=float)
    if newfig:
        plt.figure(figsize=(7.5, 2.0))
    cs = plt.contourf(y_R, z_H, k, 20, cmap=plt.cm.coolwarm,
                      levels=np.linspace(0, 0.09, num=19))
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$z/H$")
    if cb_orientation == "horizontal":
        cb = plt.colorbar(cs, shrink=1, extend="both",
                          orientation="horizontal", pad=0.3)
    elif cb_orientation == "vertical":
        cb = plt.colorbar(cs, shrink=1, extend="both",
                          orientation="vertical", pad=0.02)
    cb.set_label(r"$k/U_\infty^2$")
    plot_turb_lines(color="black")
    plt.ylim((0, 0.63))
    ax = plt.axes()
    ax.set_aspect(2)
    plt.yticks([0,0.13,0.25,0.38,0.5,0.63])
    plt.tight_layout()


def plot_spanwise_pressure(ax=None):
    """Plot spanwise pressure distribution."""
    df = pd.read_csv("processed/pressure_slice_9s.csv")
    df = df[df["Points:0"] > -0.31]
    df["z"] = df["Points:2"]
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(df.z/H, -df.p, "o")
    ax.set_xlabel("$z/H$")
    ax.set_ylabel("$-p$")
    try:
        fig.tight_layout
    except UnboundLocalError:
        pass


if __name__ == "__main__":
    pass
