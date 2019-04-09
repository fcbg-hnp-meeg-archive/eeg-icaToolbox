import numpy as np
import scipy
import pandas as pd
import mne
import seaborn as sns
import matplotlib.pyplot as plt
from mne.channels import Montage


def xyz_to_montage(path):
    """Convert xyz positions to a mne montage type"""
    n = int(open(path).readline().split(' ')[0])
    coord = np.loadtxt(path, skiprows=1, usecols=(0, 1, 2), max_rows=n)
    names = np.loadtxt(path, skiprows=1, usecols=3, max_rows=n, dtype=np.dtype(str)).tolist()
    return Montage(coord, names, 'standard_1005', selection=[i for i in range(n)])


def compute_gfp(raw):
    return(np.mean(raw.get_data()**2, axis=0)**0.5)


def plot_overlay(raw, ica):
    """Custom plot overlay given fitted ica and raw"""
    raw_copy = raw.copy()
    ica.apply(raw_copy)
    gfp_raw_signal = compute_gfp(raw)
    gfp_raw_applied_signal = compute_gfp(raw_copy)
    sfreq = raw.info["sfreq"]
    ch_types = ['eeg', 'eeg']
    ch_names = ['before', 'after']
    data = [gfp_raw_signal, gfp_raw_applied_signal]
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)
    raw.info['bads'] = ["before"]
    raw.plot(scalings="auto", n_channels=2, butterfly=True, block=True, bad_color=(1, 0, 0))
    return()


def find_chnames_in_template(ch_names, template_names):
    """Find ch_names in template and return index and names not found in template"""
    ch_names = [name.lower() for name in ch_names]
    template_names = [name.lower() for name in template_names]
    Index = []
    NotFound = []
    for name in ch_names:
        try:
            idx = template_names.index(name)
            Index.append(idx)
        except Exception:
            NotFound.append(name)
    return(Index, NotFound)


def construct__template_from_montage(Index, template_values):
    """Extract a template corresponding to the given indexes"""
    match_template = template_values[Index]
    match_template = match_template / np.linalg.norm(match_template)
    return(match_template)


def compute_correlation(match_templates, ics):
    Templates_names = []
    Ics_names = []
    Correlation = []
    for t, temp in enumerate(match_templates):
        for i, ic in enumerate(ics):
            Templates_names.append("template " + str(t))
            Ics_names.append("ic " + str(i))
            pearson = scipy.stats.pearsonr(temp, ic)[0]
            Correlation.append(pearson)
    data = {'Templates_names': Templates_names, 'Ics_names': Ics_names, 'correlation': Correlation}
    df = pd.DataFrame(data)
    return(df)


def plot_correlation(df):
    df = df.pivot("Templates_names", "Ics_names", "correlation")
    ax = sns.heatmap(df, linewidths=.5,  annot=True)
    plt.show()
    return()


"""match_templates = np.random.randint(0, 10, (3, 100))
ics = np.random.randint(0, 10, (12, 100))
df = compute_correlation(match_templates, ics)
plot_correlation_matrix(df)"""
