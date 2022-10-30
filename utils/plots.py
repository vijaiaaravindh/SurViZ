import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from astropy.io import fits
import streamlit as st

def plot_bands(info, telescopes, instruments, bands):
    plt.rcParams.update({"font.size": 22})

    fig, ax = plt.subplots(figsize=(15, 10))
    for i, telescope in enumerate(telescopes):
        j = i+1
        k = 0
        for instrument in instruments[telescope]:
            ax.plot([], [], ls=info[telescope]['instruments'][instrument]['ls'], color=info[telescope]['color'], label=f'{telescope} {instrument}')
            for i, band in enumerate(bands[telescope][instrument]):                
                k += 1
                band_info = info[telescope]['instruments'][instrument]['bands'][band]
                min_, max_ = band_info["min_max"]
                
                steep = (max_ - min_) / 15

                plt.plot([min_-steep, min_+steep], [0, 10-j-k/10], color=info[telescope]['color'], ls=info[telescope]['instruments'][instrument]['ls'], alpha=0.7)
                plt.plot([max_-steep, max_+steep], [10-j-k/10, 0], color=info[telescope]['color'], ls=info[telescope]['instruments'][instrument]['ls'], alpha=0.7)
                ax.hlines(10-j-k/10, min_+steep, max_-steep, color=info[telescope]['color'], ls=info[telescope]['instruments'][instrument]['ls'], alpha=0.7)

                plt.text((max_+min_)/2, 10-j+((10-j)/30)-k/30, band, c=info[telescope]['color'], rotation=90, size=10)
    ax.set_ylim([-1, 10])
    min_ = ax.get_xticks()[0]
    max_ = ax.get_xticks()[-1]
    # ax.set_xticks(list(ax.get_xticklabels()))
    # ax.set_xticklabels(list(ax.get_xticklabels()), fontsize=15)
    ax.set_yticks([])
    ax.set_xlabel('Wavelength (nm)', fontsize=20)
    plt.legend(bbox_to_anchor = (1, -0.1), ncol=len(instruments), fontsize=20)

    return fig

def plot_mirrors(info, telescopes):

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ds = []
    for telescope in telescopes:
        d = info[telescope]["mirror"]
        if d in ds:
            ls = "--"
        else:
            ls = "-"
        mirror = plt.Circle(
            (0, 0),
            d / 2,
            fill=False,
            lw=2,
            ec=info[telescope]["color"],
            label=telescope,
            alpha=0.8,
            ls=ls,
        )
        ax.add_patch(mirror)
        ds.append(d)
        plt.legend()

    dmax = np.max(ds) + 1
    ax.set_xlim(-dmax / 2, dmax / 2)
    ax.set_ylim(-dmax / 2, dmax / 2)
    ax.set_xticks([])
    ax.set_yticks([])
    human_axes = ax.inset_axes(
        [-1.8 / 2, -1.8 / 2, 1.8, 1.8], transform=ax.transData, zorder=0
    )
    human_axes.imshow(mpimg.imread("./data/human.png"), alpha=0.3, aspect="auto")
    human_axes.axis("off")
    human_axes.set_xticks([])
    human_axes.set_yticks([])
    plt.title("Primary Mirror Size")
    return fig

# @st.cache
def plot_fovs(info, telescope):
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")

    if "Rubin" in telescope:
        lims = 120
    else:
        lims = 30

    ax.set_xlim(-lims, lims)
    ax.set_ylim(-lims, lims)
    ax.add_patch(
        plt.Rectangle(
            (-lims, -lims), 2 * lims, 2 * lims, fc="black", ec="red", zorder=0
        )
    )

    for survey in telescope:
        x, y = info[survey]["fov"]
        fov = plt.Rectangle(
            (-x / 2, -y / 2),
            x,
            y,
            fc=info[survey]["color"],
            ec="white",
            lw=2,
            label=survey,
            alpha=0.3,
        )
        ax.add_patch(fov)
        plt.legend()
    moon_axes = ax.inset_axes(
        [-31 / 2, -31 / 2, 31, 31], transform=ax.transData, zorder=0
    )
    moon_axes.imshow(mpimg.imread("./data/moon.png"), aspect="auto")

    moon_axes.set_xticks([])
    moon_axes.set_yticks([])
    ax.set_xticks([])
    ax.set_yticks([])

    plt.title("Field Of View")

    return fig

from astropy.visualization import ZScaleInterval

def plot_fields(telescopes, surveys, instruments, nb_to_plot, bands=None):
    plt.rcParams.update({"font.size": 10})

    nb_lines = int(np.ceil(nb_to_plot / 2))
    fig, ax  = plt.subplots(nb_lines, 2, figsize=(10, nb_lines * 5))
    ax = ax.flatten()
    k = 0
    # contrast = st.slider('Constrast', 0., 3., 0.7, 0.05)
    images = {}
    mins = []
    maxs = []
    for telescope in telescopes:
        images[telescope] = {}
        for survey in surveys[telescope]:
            images[telescope][survey] = {}
            for instrument in instruments[telescope][survey]:
                try:
                    images[telescope][survey] = fits.open(f'./data/{telescope}_{instrument}_{survey}.fits')[0].data
                    interval = ZScaleInterval()
                    a = interval.get_limits(images[telescope][survey])
                    mins.append(a[0])
                    maxs.append(a[1])
                except OSError:
                    images[telescope][survey] = np.diag(np.ones(128))
                    images[telescope][survey] += np.fliplr(images[telescope][survey])

                    st.write(f'Sorry, {telescope} {survey} {instrument} is not implemented yet!')

    min_v, max_v = np.min(mins), np.max(maxs)
    for telescope in telescopes:
        for survey in surveys[telescope]:
            for instrument in instruments[telescope][survey]:
                # img = fits.open(f'./data/{telescope}_{instrument}_{survey}.fits')[0].data
                ax[k].imshow(images[telescope][survey], cmap='bone', vmin=min_v, vmax=max_v)
                ax[k].set_title(f'{telescope}, {survey} {instrument}', fontsize=10)
                k += 1
    if nb_to_plot % 2 != 0:
        ax[-1].set_visible(False)
    return fig


def plot_galaxies(info, telescopes, surveys, instruments, nb_to_plot, bands=None):
    same_size = st.checkbox('Same size image')
    plt.rcParams.update({"font.size": 10})

    nb_lines = int(np.ceil(nb_to_plot / 2))
    fig, ax  = plt.subplots(nb_lines, 2, figsize=(10, nb_lines * 5))
    ax = ax.flatten()
    k = 0
    # contrast = st.slider('Constrast', 0., 3., 0.7, 0.05)
    sizes = []
    images = {}
    for telescope in telescopes:
        images[telescope] = {}
        for survey in surveys[telescope]:
            images[telescope][survey] = {}
            for instrument in instruments[telescope][survey]:
                try:
                    images[telescope][survey][instrument] = np.load(f'./data/gal_{telescope}_{instrument}_{survey}.npy', allow_pickle=True)
                    sizes.append(237 * 0.03/info[telescope]['surveys'][survey]['instruments'][instrument]['pix_scale'])
                except OSError:
                    st.write(f'Sorry, {telescope} {survey} {instrument} is not implemented yet!')
                    images[telescope][survey][instrument] = np.diag(np.ones(128))
                    images[telescope][survey][instrument] += np.fliplr(images[telescope][survey][instrument])
                    # st.write(np.max(images[telescope][survey][instrument]))
                
    max_size = np.max(sizes)
    for telescope in telescopes:
        for survey in surveys[telescope]:
            for instrument in instruments[telescope][survey]:
                img = images[telescope][survey][instrument]
                # st.write(f'./data/gal_{telescope}_{instrument}_{survey}.npy')
                if same_size:
                    padding = int((max_size - np.shape(img)[0])/2)
                    img = np.pad(img, ((padding, padding), (padding, padding)), constant_values=0)

                ax[k].imshow(img, cmap='bone')
                ax[k].set_title(f'{telescope}, {survey}, {instrument}', fontsize=10)
                k += 1
    if nb_to_plot % 2 != 0:
        ax[-1].set_visible(False)
    return fig