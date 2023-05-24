from django.shortcuts import render
from tethys_sdk.gizmos import TextInput
from tethys_sdk.gizmos import SelectInput
from django.http import JsonResponse
from tethys_sdk.routing import controller

import json
import os
import glob

import pandas as pd
import numpy as np

from .app import Lfhazard as App


@controller(name='home')
def index(request):
    """
    Controller for map page.
    """
    workspace = App.get_custom_setting('data_path')
    state_geojsons = glob.glob(os.path.join(workspace, 'state_geojson', '*.geojson'))
    state_geojsons = sorted([os.path.basename(f).replace('.geojson', '').title() for f in state_geojsons])
    state_geojsons = [(s.replace('_', ' '), s) for s in state_geojsons]
    state_geojsons = [('', '')] + state_geojsons

    # Define Gizmo Options
    select_model = SelectInput(
        display_text='Model Type:',
        name='select_model',
        multiple=False,
        options=(('CPT (Cone Penetration Test)', 'cpt'),
                 ('SPT (Standard Penetration Test)', 'spt')),
        initial=('CPT (Cone Penetration Test)', 'cpt'),
    )
    select_return_period = SelectInput(
        display_text='Return Period (years):',
        name='select_return_period',
        multiple=False,
        options=[('475', 475), ('1033', 1033), ('2475', 2475)],
        initial=['475', 475]
    )
    select_state = SelectInput(
        display_text='State:',
        name='select_state',
        multiple=False,
        options=state_geojsons,
        initial=['', '']
    )

    text_input_lat = TextInput(
        display_text='Latitude',
        name='lat-input'
    )
    text_input_lon = TextInput(
        display_text='Longitude',
        name='lon-input'
    )

    context = {
        'select_model': select_model,
        'select_return_period': select_return_period,
        'select_state': select_state,
        'text_input_lat': text_input_lat,
        'text_input_lon': text_input_lon,
    }

    return render(request, 'lfhazard/home.html', context)


@controller(name='getgeojson', url='getgeojson')
def get_geojson(request):
    state = str(request.GET.get('state', 'utah')).lower().replace(' ', '')
    with open(os.path.join(App.get_custom_setting('data_path'), 'state_geojson', f'{state}.geojson'), 'r') as gj:
        return JsonResponse(json.loads(gj.read()))


@controller(name='querycsv', url='querycsv')
def query_csv(request):
    """
    From the lon and lat interpolates from 4 of the closest points from a csv files,
    the LD, LS and SSD values.
    """
    lon = float(request.GET['lon'])
    lat = float(request.GET['lat'])
    state = request.GET['state']
    return_period = request.GET['returnPeriod']
    model = request.GET['model']
    csv_base_path = os.path.join(App.get_custom_setting("data_path"), model)
    print(csv_base_path)

    point = (float(lon), float(lat))


    if model == 'cpt':
        # get CSR from the BI_LT_returnperiod csvs
        try:
            df = pd.read_csv(
                os.path.join(csv_base_path, f'BI_LT_{return_period}_{state}.csv'))
            csr = interpolate_idw(df[['Longitude', 'Latitude', 'CSR']].values, point, bound=1)
        except Exception as e:
            print(e)
            print('fail 1')
            csr = ''

        # get Qreq from the KU_LT_returnperiod csv files
        try:
            df = pd.read_csv(
                os.path.join(csv_base_path, f'KU_LT_{return_period}_{state}.csv'))
            qreq = interpolate_idw(df[['Longitude', 'Latitude', 'Qreq']].values, point, bound=1)
        except Exception as e:
            qreq = ''

        # get Ev_ku and Ev_bi from the LS-returnperiod csv files
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS_{return_period}_{state}.csv'))
            ku_strain_ref = interpolate_idw(df[['Longitude', 'Latitude', 'Ku Strain(%)']].values, point, bound=1)
            bi_strain_ref = interpolate_idw(df[['Longitude', 'Latitude', 'B&I Strain(%)']].values, point, bound=1)
        except Exception as e:
            ku_strain_ref = ''
            bi_strain_ref = ''

        # get gamma_ku_max and gamma_bi_max from the Set_returnperiod csv files
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'Set_{return_period}_{state}.csv'))
            ku_strain_max = interpolate_idw(df[['Longitude', 'Latitude', 'Ku Strain(%)']].values, point, bound=1)
            bi_strain_max = interpolate_idw(df[['Longitude', 'Latitude', 'B&I Strain(%)']].values, point, bound=1)
        except Exception as e:
            ku_strain_max = ''
            bi_strain_max = ''

        return JsonResponse({
            "csr": csr,
            "qReq": qreq,
            "kuStrainRef": ku_strain_ref,
            "biStrainRef": bi_strain_ref,
            "kuStrainMax": ku_strain_max,
            "biStrainMax": bi_strain_max
        })

    elif model == 'spt':
        # Javascript expects return order: logDvalue, Nvalue, CSRvalue, Cetinvalue, InYvalue, RnSvalue, BnTvalue
        # read the LS file and get the Log Dh ref value
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            log_D = interpolate_idw(df[['Longitude', 'Latitude', 'logD']].values, point, bound=1)
        except Exception as e:
            log_D = ''
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            N = interpolate_idw(df[['Longitude', 'Latitude', 'N']].values, point, bound=1)
        except Exception as e:
            N = ''
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            CSR = interpolate_idw(df[['Longitude', 'Latitude', 'CSR']].values, point, bound=1)
        except Exception as e:
            CSR = ''
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            Cetin = interpolate_idw(df[['Longitude', 'Latitude', 'Cetin']].values, point, bound=1)
        except Exception as e:
            Cetin = ''
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            InY = interpolate_idw(df[['Longitude', 'Latitude', 'InY']].values, point, bound=1)
        except Exception as e:
            InY = ''
        #try:
            #df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            #RnS = interpolate_idw(df[['Longitude', 'Latitude', 'RnS']].values, point, bound=1)
        #except Exception as e:
            #RnS = ''
        try:
            df = pd.read_csv(os.path.join(csv_base_path, f'LS-{return_period}_{state}.csv'))
            BnT = interpolate_idw(df[['Longitude', 'Latitude', 'BnT']].values, point, bound=1)
        except Exception as e:
            BnT = ''


        return JsonResponse({
            "logD": log_D,
            "N": N,
            "CSR": CSR,
            "Cetin": Cetin,
            "InY": InY,
            #"RnS": RnS,
            "BnT": BnT,
        })


def interpolate_idw(a: np.array, loc: tuple, p: int = 1, r: int or float = None, nearest: int = None,
                    bound: int = None) -> float:
    """
    Copyright (c) Riley Hales, 2020. BSD 3 Clause Clear License. All rights reserved.

    Computes the interpolated value at a specified location (loc) from an array of measured values (a). There are 3
    ways to limit the interpolation points considered.

    1. Use a search radius: only points within a certain radius of the location to be interpolated will be considered
    2. Choose a number of nearest neighbors to use.
    3. Use a number of points that bound the interpolation location. That is, take the n nearest points

    All 3 may be applied but the most restrictive option will govern. For example, suppose you choose a radius of 10
    and to use the 5 nearest neighbors. If there are 100 points within the radius of 10, 95 of them will be ignored
    since you limited the interpolation to the nearest 5 points. Similarly, If you choose to take 5 points from each of
    the bounding quadrants and also the nearest 5 neighbors, then 15 of the points chosen because they bound the
    location will get ignored. This behavior could be intentional so the all 3 options can still be applied.

    Args:
        a (np.array): a numpy array with 3 columns (x, y, value) and a row for each measurement
        loc (tuple): a tuple of (x, y) coordinates representing the location to get the interpolated values at
        p (int): an integer representing the power factor applied to the distances before inverting (usually 1, 2, 3)
        r (int or float): the radius, same length units as x & y values, to limit the value pairs in a. only points <=
            r distance away are used for the interpolation
        nearest (int): number of nearest points to include in the interpolation, if that many are available.
        bound (int): number of nearest points to include from the 4 bounding quadrants, if that many are available.

    Returns:
        float, the IDW interpolated value for the loc specified
    """
    # identify the x distance from location to the measurement points
    x = np.subtract(a[:, 0], loc[0])
    # identify the y distance from location to the measurement points
    y = np.subtract(a[:, 1], loc[1])
    # select the values column of the data
    val = a[:, 2]
    # compute the pythagorean distance (square root sum of the squares)
    dist = np.sqrt(np.add(np.multiply(x, x), np.multiply(y, y)))
    # filter the nearest number of points, limit by radius, and/or use bounding points (all use df sorted by distance)
    if r is not None or nearest is not None or bound is not None:
        b = pd.DataFrame({'dist': dist, 'val': val, 'x': x, 'y': y})
        b.sort_values('dist', inplace=True)
        if bound is not None:
            b = pd.concat((b.loc[(b['x'] >= 0) & (b['y'] > 0)].head(bound),
                           b.loc[(b['x'] >= 0) & (b['y'] < 0)].head(bound),
                           b.loc[(b['x'] < 0) & (b['y'] > 0)].head(bound),
                           b.loc[(b['x'] < 0) & (b['y'] < 0)].head(bound),))
        if nearest is not None:
            b = b.head(nearest)
        if r is not None:
            b = b[b['dist'] <= r]
        dist = b['dist'].values
        val = b['val'].values

    # raise distances to power (usually 1 or 2)
    dist = np.power(dist, p)
    # inverse the distances
    dist = np.divide(1, dist)

    return float(np.divide(np.sum(np.multiply(dist, val)), np.sum(dist)))
