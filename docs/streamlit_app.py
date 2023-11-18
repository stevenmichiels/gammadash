# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 19:18:55 2023

@author: steven.michiels
"""

import streamlit as st
import streamlit.components.v1 as components

st.header("test html import")

# add a button that switches between 1 and 2 
if st.button("Switch"):
    if state == 1:
        state = 2
    else:
        state = 1

st.write("state:", state)


HtmlFile = open("test.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 
print(source_code)
components.html(source_code, height = 600)

