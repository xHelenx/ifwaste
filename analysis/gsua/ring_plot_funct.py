import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os


def intercalate_lists(a, b):
    """
    Intercalate items from two lists
    :param a: first list
    :param b: second list
    :return: list of intercalated items
    """
    c = list(zip(a, b))
    return [elt for sublist in c for elt in sublist]
    

def ring_plot(data, det_sto, color_dic=0):
    """
    Produces ring plots for deterministic or stochastic sensitivity indices
    :param data: DataFrame containing first-order ('Si') and total-order effects ('STi'), def the
    fraction of total variance caused by deterministic effects ('S_exp'), input names ('input')
    and output names ('output')
    :param det_sto: string indicating whether the sensitivity indices are deterministic ('det')
    or stochastic ('sto')
    :param color_dic: dictionary with the names of the inputs ('input') and colors for the
    total-order sensitivity indices ('color') as keys
    :return: ring plots. They are also saved to the '/results' folder
    """
    outpath = 'results/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    font = {'family': 'serif', 'weight': 'normal', 'size': 14}
    matplotlib.rc('font', **font)
    patterns = ['/', '\\']

    file_name = '{}_S_ind.csv'.format(det_sto)
    indices = pd.read_csv(file_name)

    pies = pd.DataFrame()
    for i in indices['output'].unique():
        tmp = indices[(indices['output'] == i)]
        group = tmp.groupby('input')
        tmp = group.mean()
        tmp['output'] = i
        pies = pd.concat([pies, tmp])

    pies['Interactions'] = pies['ST'] - pies['Si']
    pies['input'] = pies.index
    pies['oInt'] = pies['oST'] - pies['oSi']
    pies['Interactions'] = pies['Interactions'].clip(lower=0)

    if det_sto == 'sto': 
        pies['S_exp'] = 1

    # Fixes
    pies.reset_index(drop=True, inplace=True)

    # Change dictionary below if another model is used
    if color_dic == 0:
        color_dic = pd.DataFrame(
            {'input': ['MutMxSz', 'MutSSz', 'MutSpP', 'GlutMnSz', 'GlutSSz', 'GlutFzP', 'GlutFzA', 'GlutIniPop', 'others'],
             'color': [[31/255, 119/255, 180/255], [255/255, 127/255, 14/255], [44/255, 160/255, 44/255], 
                       [214/255, 39/255, 40/255], [148/255, 103/255, 189/255], [140/255, 86/255, 75/255],
                       [227/255, 119/255, 194/255], [127/255, 127/255, 127/255], [31/255, 119/255, 180/255], ]
                     })
#        color_dic = pd.DataFrame(
#            {'input': ['wolf_gain_from_food', 'initial_number_wolves', 'wolf_reproduce', 'initial_number_sheep', 
#               'sheep_gain_from_food', 'grass_regrowth_time', 'sheep_reproduce', 'others'],
#             'color': [[31/255, 119/255, 180/255], [255/255, 127/255, 14/255], [44/255, 160/255, 44/255], 
#                       [214/255, 39/255, 40/255], [148/255, 103/255, 189/255], [140/255, 86/255, 75/255],
#                       [227/255, 119/255, 194/255], [127/255, 127/255, 127/255]]
#                     })

    for out in pies['output'].unique():
        df = pd.DataFrame(pies[pies['output'] == out])
        df = df.groupby(['input'], sort=False).mean()  # do not input change order here
        df['input'] = df.index

        if det_sto == 'det':
            group_names = ['Deterministic', 'Stochastic']        
            group_size = [df['S_exp'].mean()*100, (1-df['S_exp'].mean())*100]
            a, b = [plt.cm.Blues, plt.cm.Reds]
        elif det_sto == 'sto':
            group_names = [' ', ' ']
            group_size = [100, 0]    
            b, a = [plt.cm.Blues, plt.cm.Reds]
        # External ring
        fig, ax = plt.subplots(figsize=[9, 6])
        plt.title('ST ' + out)
        ax.axis('equal')
        # ring1, _ = ax.pie(group_size, radius=1, labels=group_names, colors=[a(0.8), b(0.8)])  # det
        ring1, _ = ax.pie(group_size, radius=1, colors=[a(0.8), b(0.8)], labels=group_names)  # det
        # ring1, _ = ax.pie(group_size, radius=1, labels=group_names, colors=[b(0.8), a(0.8)])  # sto
        # ring1, _ = ax.pie(group_size, radius=1, colors=[b(0.8), a(0.8)])  # sto
        ring1[0].set_hatch(patterns[0])
        ring1[1].set_hatch(patterns[1])
        plt.setp(ring1, width=0.15, edgecolor='white')

        # Second Ring
        det_values = df[df['ST'] > 0.03]['ST']
        other = (np.sum(df['ST']) - np.sum(det_values))*df['S_exp'].mean()*100/np.sum(df['ST'])
        det_values = list(df[df['ST'] > 0.03]['ST']*df['S_exp'].mean()*100/np.sum(df['ST']))
        det_values.append(other)
        sto_values = [group_size[1]]
        subgroup_size = det_values + sto_values

        det_names = list(df[df['ST'] > 0.03]['input'])
        det_names.append('others')
        sto_names = list(' ')

        subgroup_names = det_names + sto_names

        count_det = len(det_names)
        count_sto = len(sto_names)

        col = []
        for i in subgroup_names:
            if i != ' ':
                col.append(list(color_dic[color_dic['input'] == i]['color'])[0])
            else:
                col.append(b(0.8))  # det
                # col.append(a(0.8))  # sto
        if out == 'pop3':
            subgroup_names[0] = 'all'

        ring2, _ = ax.pie(subgroup_size, radius=1-0.15, labeldistance=0.8, colors=col, labels=subgroup_names)
        # ring2, _ = ax.pie(subgroup_size, radius=1 - 0.15, labeldistance=0.8, colors=col)
        ring2[-1].set_hatch(patterns[1])
        plt.setp(ring2, width=0.3, edgecolor='white')
        plt.margins(0, 0)

        # Third ring
        # Interactions
        df['Interactions'] = df['ST'] - df['Si']
        det_int = list(df[df['ST'] > 0.03]['Interactions'])
        other_int = (np.sum(df['Interactions']) - np.sum(det_int))*df['S_exp'].mean()*100/np.sum(df['ST'])
        det_int = list(df[df['ST'] > 0.03]['Interactions']*df['S_exp'].mean()*100/np.sum(df['ST']))
        det_int.append(other_int)
        # Direct effects
        det_direct = list(df[df['ST'] > 0.03]['Si'])
        other_direct = (np.sum(df['Si']) - np.sum(det_direct))*df['S_exp'].mean()*100/np.sum(df['ST'])
        det_direct = list(df[df['ST'] > 0.03]['Si']*df['S_exp'].mean()*100/np.sum(df['ST']))
        det_direct.append(other_direct)

        third_group = intercalate_lists(det_direct, det_int)
        df['Sto interactions'] = group_size[1]
        sto_int = [group_size[1]]

        third_group_sto = sto_int
        third_group = third_group + third_group_sto

        a, b = [plt.cm.Greys, plt.cm.Greys]
        col = []
        for i in range(len(third_group)-1):
            if i % 2 == 0:
                col.append(a(0.8))
            else:
                col.append(b(0.2))
        col.append(b(0))
        cheat = [' ']*len(third_group)
        third_group = [x if x >= 0 else 0 for x in third_group]
        ring3, _ = ax.pie(third_group, radius=1-0.45, colors=col, labels=cheat)
        handles, labels = ax.get_legend_handles_labels()
        legs = ['Direct effects', 'Interactions']
        ax.legend(handles[-3:], legs, loc=(0.9, 0.1))
        plt.setp(ring3, width=0.06, edgecolor='white')
        plt.tight_layout()
        plt.savefig('{}{}_{}_piechart.png'.format(outpath, out, det_sto), dpi=300)