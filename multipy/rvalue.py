# -*- encoding: utf-8 -*-
"""Functions for computing reproducibility values.

Author: Tuomas Puoliväli
Email: tuomas.puolivali@helsinki.fi
License: Revised 3-clause BSD
Last modified: 12th April 2019

References:

[1] Heller R, Bogomolov M, Benjamini Y (2014): Deciding whether follow-up
studies have replicated findings in a preliminary large-scale omics study.
The Proceedings of the National Academy of Sciences of the United States
of America 111(46):16262-16267.
"""

import numpy as np

from scipy.optimize import root
from scipy.stats import rankdata

def _fdr_rvalue_f(x, m, p1, p2, c2=0.5, l00=0.8):
    """Function for computing the FDR r-value of a given feature.

    Input arguments:
    ================
    c2 : float in range (0, 1)
        The emphasis given to the follow-up study.

    l00 : float in range [0, 1)
        The lower bound on f00, which is "the fraction of features, of the
        m features examined in the primary study, that are null in both
        studies".
    """

    # TODO: initially named to match the reference R code
    R1 = len(p1)
    c1 = (1.-c2) / (1.-l00*(1.-c2*x))

    e = np.max([m*p1 / c1, R1*p2 / c2], axis=0)
    e = e / rankdata(e, method='max')

    oe = np.argsort(e)[::-1]
    oer = np.argsort(oe)

    r = np.minimum.accumulate(e[oe])[oer]
    r = np.min([r, np.ones(np.shape(r))], axis=0)
    return r

def _fdr_rvalue_f_aux(x, i, m, p1, p2, c2, l00):
    """Auxiliary function used to enable solving f(x) = x."""
    return _fdr_rvalue_f(x, m, p1, p2, c2, l00)[i] - x

def fdr_rvalue(p1, p2, m, c2=0.5, l00=0.8):
    """Function for computing FDR r-values using the method suggested by
    Heller et al.

    Input arguments:
    ================
    p1, p2 : ndarray [n_tests, ]
        The p-values that were selected for follow-up from the primary
        study (p1) and the corresponding p-values observed in the
        follow-up study (p2).

    m : int
        The number of tests considered in the primary study.

    c2 : float in range (0, 1)
        The emphasis given to the follow-up study.

    l00 : float in range [0, 1)
        The lower bound on f00, which is "the fraction of features, of the
        m features examined in the primary study, that are null in both
        studies".
    """

    # TODO: Consider implementing the other variations of computing c1.

    tol = np.min([np.min([p1, p2]), 0.0001])

    """Compute the r-values."""
    rvalue = np.zeros(np.shape(p2), dtype='float')
    for i, _ in enumerate(p2):
        if (_fdr_rvalue_f_aux(1, i, m, p1, p2, c2, l00) >= 0):
            rvalue[i] = 1
        else:
            sol = root(_fdr_rvalue_f_aux, x0=0.5,
                       args=(i, m, p1, p2, c2, l00), tol=tol)['x']
            rvalue[i] = sol

    return rvalue
