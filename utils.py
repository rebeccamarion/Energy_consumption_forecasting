#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic custom functions
"""

import pickle as pkl

def load_data (file) : 
    
    with open(file, "br") as f:
         data = pkl.load(f)
    return data

def save_data (file, element) : 
    
    with open(file, "bw") as f:
         pkl.dump(element, f)