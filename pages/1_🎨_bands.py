import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from telescopes.main_info import info
from utils.plots import plot_bands

st.markdown('# 🎨 Filters visualisation \n You can see here the filters of the different instruments. Note that for now, the shape and sensitivity are not correct: the y-axis is arbitrary, and the differences are just here for a better visualisation ')
telescopes = st.sidebar.multiselect(
        "Select telescopes to display",
        ["Euclid", "JWST", "HST", "Rubin"],
        default=["Euclid"]#, "HST"]
    )

selected_bands = {}
selected_instruments = {}

for telescope in telescopes:
    selected_bands[telescope] = {}
    # SELECTION OF THE INSTRUMENT
    st.sidebar.markdown(f'# {telescope}')
    telescope_instrument = st.sidebar.multiselect(
                "Select the instruments",
                list(info[telescope]['instruments'].keys()),
                default=[list(info[telescope]['instruments'].keys())[0]])
    selected_instruments[telescope] = telescope_instrument

    for instrument in selected_instruments[telescope]:
        instrument_bands =  st.sidebar.multiselect(
                f" Select Bands to display ({instrument})",
                list(info[telescope]['instruments'][instrument]['bands'].keys()),
                default=list(info[telescope]['instruments'][instrument]['bands'].keys()))
        selected_bands[telescope][instrument] = instrument_bands

fig = plot_bands(info, telescopes, selected_instruments, selected_bands)
st.pyplot(fig)