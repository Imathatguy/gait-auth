#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Benjamin Zhao
"""

from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
import pickle

verify_data = True

data = 'user_defence_results'

vary_dir = {0.00: join('./', data),
            }

arches = {'linsvm': 'linsvm_probaresults',
          'rbfsvm': 'rbfsvm_probaresults',
          'rndf': 'rndf_probaresults',
          'tfdnn': 'dnn_probaresults',
          }

data_holder = {}

# Convert user_id string to int
user_mapping = {}

for vary_key, data_path in vary_dir.items():
    for arch, arch_path in arches.items():
        arch_holder = data_holder.get(arch, {})
        run_path = join(data_path, arch_path)
        onlyfiles = [join(run_path, f) for f in listdir(run_path) if
                     isfile(join(run_path, f)) & f.endswith('.pickle')]

        # Extract data from directory
        data_arr = []
        for n, file_path in enumerate(onlyfiles):
            print(n, file_path)
            with open(file_path, 'rb') as open_file:
                lines = pickle.load(open_file)
                # if len(lines) == 10:
                print(len(lines))

                lines[0] = (lines[0][0], lines[0][1], lines[0][2])

                data_arr.extend(lines)

        # Check there are a correct number of test runs in each extraction
        print(arch, len(data_arr))
        if verify_data:
            assert len(data_arr) == 50

        arch_holder[vary_key] = data_arr
        data_holder[arch] = arch_holder


arch_order = ['linsvm', 'rbfsvm', 'rndf', 'tfdnn']

markers = {'linsvm': 'o',
           'rbfsvm': 'D',
           'rndf': 's',
           'tfdnn': '^',
           }

plot_labels = {'linsvm': 'LinSVM',
               'rbfsvm': 'RBFSVM',
               'rndf': 'RNDF',
               'tfdnn': 'DNN',
               }

fig = plt.figure(figsize=(3, 2))
axe = plt.gca()
axes = [axe, axe, axe, axe]

n_thresh = 101
n_users = 30

for n, (ax, clasif) in enumerate(zip(axes, arch_order)):
    print(clasif)
    # print(data_df[data_df['classifier'] == clasif].mean())
    data = data_holder[clasif]
    labels, values = zip(*[(d, data[d]) for d in sorted(data.keys())])

    a = np.asarray(values)

    FRR = 1 - np.array([np.average(a[0, :, 0, b, :], axis=0) for b in range(n_users)])
    assert FRR.shape == (n_users, n_thresh)

    FPR = np.array([np.average(a[0, :, 1, b, :], axis=0) for b in range(n_users)])
    assert FRR.shape == (n_users, n_thresh)

    AR = np.array([np.average(a[0, :, 2, b, :], axis=0) for b in range(n_users)])
    assert FRR.shape == (n_users, n_thresh)

    x_ref = np.arange(0, 1.01, 0.01)

    linked_res = []

    for user in range(n_users):
        u_FRR = FRR[user]
        u_FPR = FPR[user]
        u_AR = AR[user]
        idx = np.argwhere(np.diff(np.sign(u_FRR - u_FPR))).flatten()
        print(u_FPR[idx[0]])
        print(u_AR[idx[0]])
        print(u_AR[idx[0]])
        linked_res.append((u_FPR[idx[0]], u_AR[idx[0]]))

    [scatter_x, scatter_y] = list(zip(*linked_res))
    ax.scatter(scatter_x, scatter_y, label='{}'.format(plot_labels[clasif]),
               alpha=0.5, marker=markers[clasif], s=15)

    # ax.set_title(clasif)
    ax.set_xlabel('EER')
    # ax.set_ylim(0, 1)
    # ax.set_xlim(0, 1)
    if n == 0:
        ax.set_ylabel('AR')
    # ax.legend(fontsize=10, framealpha=0.5)

# # Plot x=y line, but bound figure to the limits of where points exist.
# x_lims = ax.get_xlim()
# y_lims = ax.get_ylim()
# # now plot both limits against each other
# lims = [
#     np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
#     np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
# ]
# ax.plot(lims, lims, alpha=0.75, zorder=0, color='k', linestyle='--')
# #ax.set_aspect('equal')
# ax.set_xlim(x_lims)
# ax.set_ylim(y_lims)

ax.plot((-0.05, 1.05), (-0.05, 1.05), alpha=0.75, zorder=0,
        color='k', linestyle='--')

ax.set_ylim(-0.05, 1.05)
ax.set_xlim(-0.05, 1.05)

plt.savefig('gait_defencerand_arind.pdf', bbox_inches='tight')
plt.show()
