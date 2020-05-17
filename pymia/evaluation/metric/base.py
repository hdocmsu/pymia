import abc

import numpy as np
import scipy.ndimage as ndimage


class NotComputableMetricWarning(RuntimeWarning):
    """Warning class to raise if a metric cannot be computed."""


class ConfusionMatrix:
    """Represents a confusion matrix (or error matrix)."""

    def __init__(self, prediction, label):
        """Initializes a new instance of the ConfusionMatrix class."""

        # true positive (tp): we predict a label of 1 (positive), and the true label is 1
        self.tp = np.sum(np.logical_and(prediction == 1, label == 1))
        # true negative (tn): we predict a label of 0 (negative), and the true label is 0
        self.tn = np.sum(np.logical_and(prediction == 0, label == 0))
        # false positive (fp): we predict a label of 1 (positive), but the true label is 0
        self.fp = np.sum(np.logical_and(prediction == 1, label == 0))
        # false negative (fn): we predict a label of 0 (negative), but the true label is 1
        self.fn = np.sum(np.logical_and(prediction == 0, label == 1))

        self.n = prediction.size


class Distances:
    """Represents distances for distance metrics.

    See Also:
        - Nikolov et al., 2018 Deep learning to achieve clinically applicable segmentation of head and neck anatomy for
        radiotherapy. `arXiv <https://arxiv.org/abs/1809.04430>`_
        - `Original implementation <https://github.com/deepmind/surface-distance>`_
    """
    
    def __init__(self, prediction, label, spacing):
        """Initializes a new instance of the Distances class."""

        self.distances_gt_to_pred = None
        self.distances_pred_to_gt = None
        self.surfel_areas_gt = None
        self.surfel_areas_pred = None

        self._neighbour_code_to_normals = [
            [[0, 0, 0]],
            [[0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [0.25, 0.25, -0.0]],
            [[0.125, -0.125, 0.125]],
            [[-0.25, -0.0, -0.25], [0.25, 0.0, 0.25]],
            [[0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[0.5, 0.0, -0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25]],
            [[0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.5, 0.0, 0.0], [0.25, -0.25, 0.25], [-0.125, 0.125, -0.125]],
            [[-0.5, 0.0, 0.0], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[0.5, 0.0, 0.0], [0.5, 0.0, 0.0]],
            [[0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.5, 0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, 0.0, -0.5], [0.25, 0.25, 0.25], [-0.125, -0.125, -0.125]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25], [0.125, -0.125, -0.125]],
            [[0.125, 0.125, 0.125], [0.375, 0.375, 0.375], [0.0, -0.25, 0.25], [-0.25, 0.0, 0.25]],
            [[0.125, -0.125, -0.125], [0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.375, 0.375, 0.375], [0.0, 0.25, -0.25], [-0.125, -0.125, -0.125], [-0.25, 0.25, 0.0]],
            [[-0.5, 0.0, 0.0], [-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25], [0.125, 0.125, 0.125]],
            [[-0.5, 0.0, 0.0], [-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25]],
            [[0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, 0.25, -0.25]],
            [[0.0, -0.5, 0.0], [0.125, 0.125, -0.125], [0.25, 0.25, -0.25]],
            [[0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125], [-0.25, -0.0, -0.25], [0.25, 0.0, 0.25]],
            [[0.0, -0.25, 0.25], [0.0, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[-0.375, -0.375, 0.375], [-0.0, 0.25, 0.25], [0.125, 0.125, -0.125], [-0.25, -0.0, -0.25]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.25, 0.25, -0.25], [0.25, 0.25, -0.25], [0.125, 0.125, -0.125], [-0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125], [0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.5, 0.0, 0.0], [0.25, -0.25, 0.25], [-0.125, 0.125, -0.125], [0.125, -0.125, 0.125]],
            [[0.0, 0.25, -0.25], [0.375, -0.375, -0.375], [-0.125, 0.125, 0.125], [0.25, 0.25, 0.0]],
            [[-0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.25, -0.25, 0.0], [-0.25, 0.25, 0.0]],
            [[0.0, 0.5, 0.0], [-0.25, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[0.0, 0.5, 0.0], [0.125, -0.125, 0.125], [-0.25, 0.25, -0.25]],
            [[0.0, 0.5, 0.0], [0.0, -0.5, 0.0]],
            [[0.25, -0.25, 0.0], [-0.25, 0.25, 0.0], [0.125, -0.125, 0.125]],
            [[-0.375, -0.375, -0.375], [-0.25, 0.0, 0.25], [-0.125, -0.125, -0.125], [-0.25, 0.25, 0.0]],
            [[0.125, 0.125, 0.125], [0.0, -0.5, 0.0], [-0.25, -0.25, -0.25], [-0.125, -0.125, -0.125]],
            [[0.0, -0.5, 0.0], [-0.25, -0.25, -0.25], [-0.125, -0.125, -0.125]],
            [[-0.125, 0.125, 0.125], [0.25, -0.25, 0.0], [-0.25, 0.25, 0.0]],
            [[0.0, 0.5, 0.0], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.375, 0.375, -0.375], [-0.25, -0.25, 0.0], [-0.125, 0.125, -0.125], [-0.25, 0.0, 0.25]],
            [[0.0, 0.5, 0.0], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[0.25, -0.25, 0.0], [-0.25, 0.25, 0.0], [0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0], [-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0]],
            [[-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0]],
            [[-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.25, -0.25, 0.0], [0.25, 0.25, -0.0]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25]],
            [[0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.375, -0.375, 0.375], [0.0, -0.25, -0.25], [-0.125, 0.125, -0.125], [0.25, 0.25, 0.0]],
            [[-0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25]],
            [[0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.0, 0.5, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[-0.25, 0.25, -0.25], [-0.25, 0.25, -0.25], [-0.125, 0.125, -0.125], [-0.125, 0.125, -0.125]],
            [[-0.25, 0.0, -0.25], [0.375, -0.375, -0.375], [0.0, 0.25, -0.25], [-0.125, 0.125, 0.125]],
            [[0.5, 0.0, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [0.25, 0.0, -0.25]],
            [[-0.0, 0.0, 0.5], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.25, 0.0, 0.25], [0.25, 0.0, -0.25]],
            [[-0.25, -0.0, -0.25], [-0.375, 0.375, 0.375], [-0.25, -0.25, 0.0], [-0.125, 0.125, 0.125]],
            [[0.0, 0.0, -0.5], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [0.0, 0.0, 0.5]],
            [[0.125, 0.125, 0.125], [0.125, 0.125, 0.125], [0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[0.125, 0.125, 0.125], [0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[-0.25, 0.0, 0.25], [0.25, 0.0, -0.25], [-0.125, 0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25], [0.25, 0.0, -0.25]],
            [[0.125, -0.125, 0.125], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[0.25, 0.0, 0.25], [-0.375, -0.375, 0.375], [-0.25, 0.25, 0.0], [-0.125, -0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [0.0, -0.25, 0.25], [0.0, 0.25, -0.25]],
            [[0.0, -0.5, 0.0], [0.125, 0.125, -0.125], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [0.0, 0.25, -0.25]],
            [[0.0, 0.25, 0.25], [0.0, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, 0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[-0.0, 0.5, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.5, 0.0, -0.0], [0.25, -0.25, -0.25], [0.125, -0.125, -0.125]],
            [[-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125], [-0.25, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[0.375, -0.375, 0.375], [0.0, 0.25, 0.25], [-0.125, 0.125, -0.125], [-0.25, 0.0, 0.25]],
            [[0.0, -0.5, 0.0], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[-0.375, -0.375, 0.375], [0.25, -0.25, 0.0], [0.0, 0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [-0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[0.125, 0.125, 0.125], [0.0, 0.25, 0.25], [0.0, 0.25, 0.25]],
            [[0.0, 0.25, 0.25], [0.0, 0.25, 0.25]],
            [[0.5, 0.0, -0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125], [0.125, 0.125, 0.125]],
            [[0.125, -0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, 0.125, 0.125]],
            [[-0.25, -0.0, -0.25], [0.25, 0.0, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [0.25, 0.25, -0.0], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [0.25, 0.25, -0.0], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.25, -0.0, -0.25], [0.25, 0.0, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, -0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, 0.125, 0.125]],
            [[0.5, 0.0, -0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125], [0.125, 0.125, 0.125]],
            [[0.0, 0.25, 0.25], [0.0, 0.25, 0.25]],
            [[0.125, 0.125, 0.125], [0.0, 0.25, 0.25], [0.0, 0.25, 0.25]],
            [[-0.125, 0.125, 0.125], [-0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[-0.375, -0.375, 0.375], [0.25, -0.25, 0.0], [0.0, 0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.0, -0.5, 0.0], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[0.375, -0.375, 0.375], [0.0, 0.25, 0.25], [-0.125, 0.125, -0.125], [-0.25, 0.0, 0.25]],
            [[-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125], [-0.25, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[0.5, 0.0, -0.0], [0.25, -0.25, -0.25], [0.125, -0.125, -0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[-0.0, 0.5, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[-0.0, 0.0, 0.5], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[0.0, 0.25, 0.25], [0.0, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25], [0.0, 0.25, 0.25], [0.0, 0.25, 0.25]],
            [[0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.0, -0.5, 0.0], [0.125, 0.125, -0.125], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [0.0, -0.25, 0.25], [0.0, 0.25, -0.25]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[0.125, 0.125, 0.125], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[-0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.25, 0.0, 0.25], [-0.375, -0.375, 0.375], [-0.25, 0.25, 0.0], [-0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[-0.25, -0.0, -0.25], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25], [0.25, 0.0, 0.25]],
            [[-0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [0.25, 0.0, -0.25], [-0.125, 0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[0.125, 0.125, 0.125], [0.125, 0.125, 0.125], [0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
            [[-0.0, 0.0, 0.5], [0.0, 0.0, 0.5]],
            [[0.0, 0.0, -0.5], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[-0.25, -0.0, -0.25], [-0.375, 0.375, 0.375], [-0.25, -0.25, 0.0], [-0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.25, 0.0, 0.25], [0.25, 0.0, -0.25]],
            [[-0.0, 0.0, 0.5], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [0.25, 0.0, -0.25]],
            [[0.5, 0.0, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[-0.25, 0.0, -0.25], [0.375, -0.375, -0.375], [0.0, 0.25, -0.25], [-0.125, 0.125, 0.125]],
            [[-0.25, 0.25, -0.25], [-0.25, 0.25, -0.25], [-0.125, 0.125, -0.125], [-0.125, 0.125, -0.125]],
            [[-0.0, 0.5, 0.0], [-0.25, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[0.375, -0.375, 0.375], [0.0, -0.25, -0.25], [-0.125, 0.125, -0.125], [0.25, 0.25, 0.0]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.0, 0.0, 0.5], [0.25, -0.25, 0.25], [0.125, -0.125, 0.125]],
            [[0.0, -0.25, 0.25], [0.0, -0.25, 0.25]],
            [[-0.125, -0.125, 0.125], [-0.25, -0.25, 0.0], [0.25, 0.25, -0.0]],
            [[-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0]],
            [[0.125, 0.125, 0.125], [-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0]],
            [[-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0], [-0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0], [-0.25, -0.25, 0.0], [0.25, 0.25, -0.0]],
            [[0.0, 0.5, 0.0], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125]],
            [[-0.375, 0.375, -0.375], [-0.25, -0.25, 0.0], [-0.125, 0.125, -0.125], [-0.25, 0.0, 0.25]],
            [[0.0, 0.5, 0.0], [0.25, 0.25, -0.25], [-0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.25, -0.25, 0.0], [-0.25, 0.25, 0.0]],
            [[0.0, -0.5, 0.0], [-0.25, -0.25, -0.25], [-0.125, -0.125, -0.125]],
            [[0.125, 0.125, 0.125], [0.0, -0.5, 0.0], [-0.25, -0.25, -0.25], [-0.125, -0.125, -0.125]],
            [[-0.375, -0.375, -0.375], [-0.25, 0.0, 0.25], [-0.125, -0.125, -0.125], [-0.25, 0.25, 0.0]],
            [[0.25, -0.25, 0.0], [-0.25, 0.25, 0.0], [0.125, -0.125, 0.125]],
            [[0.0, 0.5, 0.0], [0.0, -0.5, 0.0]],
            [[0.0, 0.5, 0.0], [0.125, -0.125, 0.125], [-0.25, 0.25, -0.25]],
            [[0.0, 0.5, 0.0], [-0.25, 0.25, 0.25], [0.125, -0.125, -0.125]],
            [[0.25, -0.25, 0.0], [-0.25, 0.25, 0.0]],
            [[-0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.0, 0.25, -0.25], [0.375, -0.375, -0.375], [-0.125, 0.125, 0.125], [0.25, 0.25, 0.0]],
            [[0.5, 0.0, 0.0], [0.25, -0.25, 0.25], [-0.125, 0.125, -0.125], [0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125], [0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.25, 0.25, -0.25], [0.25, 0.25, -0.25], [0.125, 0.125, -0.125], [-0.125, -0.125, 0.125]],
            [[-0.0, 0.0, 0.5], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[-0.375, -0.375, 0.375], [-0.0, 0.25, 0.25], [0.125, 0.125, -0.125], [-0.25, -0.0, -0.25]],
            [[0.0, -0.25, 0.25], [0.0, 0.25, -0.25], [0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125], [-0.25, -0.0, -0.25], [0.25, 0.0, 0.25]],
            [[0.125, -0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.0, -0.5, 0.0], [0.125, 0.125, -0.125], [0.25, 0.25, -0.25]],
            [[0.0, -0.25, 0.25], [0.0, 0.25, -0.25]],
            [[0.125, 0.125, 0.125], [0.125, -0.125, 0.125]],
            [[0.125, -0.125, 0.125]],
            [[-0.5, 0.0, 0.0], [-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25]],
            [[-0.5, 0.0, 0.0], [-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25], [0.125, 0.125, 0.125]],
            [[0.375, 0.375, 0.375], [0.0, 0.25, -0.25], [-0.125, -0.125, -0.125], [-0.25, 0.25, 0.0]],
            [[0.125, -0.125, -0.125], [0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.125, 0.125, 0.125], [0.375, 0.375, 0.375], [0.0, -0.25, 0.25], [-0.25, 0.0, 0.25]],
            [[-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125], [0.125, -0.125, -0.125]],
            [[-0.125, -0.125, -0.125], [-0.25, -0.25, -0.25], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, 0.0, -0.5], [0.25, 0.25, 0.25], [-0.125, -0.125, -0.125]],
            [[0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.5, 0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[-0.125, -0.125, 0.125], [0.125, -0.125, -0.125]],
            [[0.0, -0.25, -0.25], [0.0, 0.25, 0.25]],
            [[0.125, -0.125, -0.125]],
            [[0.5, 0.0, 0.0], [0.5, 0.0, 0.0]],
            [[-0.5, 0.0, 0.0], [-0.25, 0.25, 0.25], [-0.125, 0.125, 0.125]],
            [[0.5, 0.0, 0.0], [0.25, -0.25, 0.25], [-0.125, 0.125, -0.125]],
            [[0.25, -0.25, 0.0], [0.25, -0.25, 0.0]],
            [[0.5, 0.0, 0.0], [-0.25, -0.25, 0.25], [-0.125, -0.125, 0.125]],
            [[-0.25, 0.0, 0.25], [-0.25, 0.0, 0.25]],
            [[0.125, 0.125, 0.125], [-0.125, 0.125, 0.125]],
            [[-0.125, 0.125, 0.125]],
            [[0.5, 0.0, -0.0], [0.25, 0.25, 0.25], [0.125, 0.125, 0.125]],
            [[0.125, -0.125, 0.125], [-0.125, -0.125, 0.125]],
            [[-0.25, -0.0, -0.25], [0.25, 0.0, 0.25]],
            [[0.125, -0.125, 0.125]],
            [[-0.25, -0.25, 0.0], [0.25, 0.25, -0.0]],
            [[-0.125, -0.125, 0.125]],
            [[0.125, 0.125, 0.125]],
            [[0, 0, 0]]]

        self._calculate(prediction, label, spacing)

    def _calculate(self, segmentation_arr, ground_truth_arr, spacing):
        if segmentation_arr.ndim == 2 and ground_truth_arr.ndim == 2 and len(spacing) == 2:
            # the implementation works only for 3-D images, therefore, convert 2-D images to 3-D
            # with 3rd dimension being of value 1
            segmentation_arr = np.expand_dims(segmentation_arr, -1)
            ground_truth_arr = np.expand_dims(ground_truth_arr, -1)
            spacing = spacing + (1., )

        # calculate distances
        neighbour_code_to_surface_area = np.zeros([256])
        for code in range(256):
            normals = np.array(self._neighbour_code_to_normals[code])
            sum_area = 0
            for normal_idx in range(normals.shape[0]):
                # normal vector
                n = np.zeros([3])
                n[0] = normals[normal_idx, 0] * spacing[1] * spacing[2]
                n[1] = normals[normal_idx, 1] * spacing[0] * spacing[2]
                n[2] = normals[normal_idx, 2] * spacing[0] * spacing[1]
                area = np.linalg.norm(n)
                sum_area += area
            neighbour_code_to_surface_area[code] = sum_area

        # compute the bounding box of the masks to trim
        # the volume to the smallest possible processing subvolume
        mask_all = ground_truth_arr | segmentation_arr
        bbox_min = np.zeros(3, np.int64)
        bbox_max = np.zeros(3, np.int64)

        # max projection to the x0-axis
        proj_0 = np.max(np.max(mask_all, axis=2), axis=1)
        idx_nonzero_0 = np.nonzero(proj_0)[0]
        if len(idx_nonzero_0) == 0:  # pylint: disable=g-explicit-length-test
            return {"distances_gt_to_pred": np.array([]),
                    "distances_pred_to_gt": np.array([]),
                    "surfel_areas_gt": np.array([]),
                    "surfel_areas_pred": np.array([])}

        bbox_min[0] = np.min(idx_nonzero_0)
        bbox_max[0] = np.max(idx_nonzero_0)

        # max projection to the x1-axis
        proj_1 = np.max(np.max(mask_all, axis=2), axis=0)
        idx_nonzero_1 = np.nonzero(proj_1)[0]
        bbox_min[1] = np.min(idx_nonzero_1)
        bbox_max[1] = np.max(idx_nonzero_1)

        # max projection to the x2-axis
        proj_2 = np.max(np.max(mask_all, axis=1), axis=0)
        idx_nonzero_2 = np.nonzero(proj_2)[0]
        bbox_min[2] = np.min(idx_nonzero_2)
        bbox_max[2] = np.max(idx_nonzero_2)

        # crop the processing subvolume.
        # we need to zeropad the cropped region with 1 voxel at the lower,
        # the right and the back side. This is required to obtain the "full"
        # convolution result with the 2x2x2 kernel
        cropmask_gt = np.zeros((bbox_max - bbox_min) + 2, np.uint8)
        cropmask_pred = np.zeros((bbox_max - bbox_min) + 2, np.uint8)

        cropmask_gt[0:-1, 0:-1, 0:-1] = ground_truth_arr[bbox_min[0]:bbox_max[0] + 1,
                                        bbox_min[1]:bbox_max[1] + 1,
                                        bbox_min[2]:bbox_max[2] + 1]

        cropmask_pred[0:-1, 0:-1, 0:-1] = segmentation_arr[bbox_min[0]:bbox_max[0] + 1,
                                          bbox_min[1]:bbox_max[1] + 1,
                                          bbox_min[2]:bbox_max[2] + 1]

        # compute the neighbour code (local binary pattern) for each voxel
        # the resulting arrays are spacially shifted by minus half a voxel in each
        # axis.
        # i.e. the points are located at the corners of the original voxels
        kernel = np.array([[[128, 64],
                            [32, 16]],
                           [[8, 4],
                            [2, 1]]])
        neighbour_code_map_gt = ndimage.filters.correlate(
            cropmask_gt.astype(np.uint8), kernel, mode="constant", cval=0)
        neighbour_code_map_pred = ndimage.filters.correlate(
            cropmask_pred.astype(np.uint8), kernel, mode="constant", cval=0)

        # create masks with the surface voxels
        borders_gt = ((neighbour_code_map_gt != 0) & (neighbour_code_map_gt != 255))
        borders_pred = ((neighbour_code_map_pred != 0) &
                        (neighbour_code_map_pred != 255))

        # compute the distance transform (closest distance of each voxel to the
        # surface voxels)
        if borders_gt.any():
            distmap_gt = ndimage.morphology.distance_transform_edt(
                ~borders_gt, sampling=spacing)
        else:
            distmap_gt = np.Inf * np.ones(borders_gt.shape)

        if borders_pred.any():
            distmap_pred = ndimage.morphology.distance_transform_edt(
                ~borders_pred, sampling=spacing)
        else:
            distmap_pred = np.Inf * np.ones(borders_pred.shape)

        # compute the area of each surface element
        surface_area_map_gt = neighbour_code_to_surface_area[neighbour_code_map_gt]
        surface_area_map_pred = neighbour_code_to_surface_area[
            neighbour_code_map_pred]

        # create a list of all surface elements with distance and area
        distances_gt_to_pred = distmap_pred[borders_gt]
        distances_pred_to_gt = distmap_gt[borders_pred]
        surfel_areas_gt = surface_area_map_gt[borders_gt]
        surfel_areas_pred = surface_area_map_pred[borders_pred]

        # sort them by distance
        if distances_gt_to_pred.shape != (0,):
            sorted_surfels_gt = np.array(
                sorted(zip(distances_gt_to_pred, surfel_areas_gt)))
            distances_gt_to_pred = sorted_surfels_gt[:, 0]
            surfel_areas_gt = sorted_surfels_gt[:, 1]

        if distances_pred_to_gt.shape != (0,):
            sorted_surfels_pred = np.array(
                sorted(zip(distances_pred_to_gt, surfel_areas_pred)))
            distances_pred_to_gt = sorted_surfels_pred[:, 0]
            surfel_areas_pred = sorted_surfels_pred[:, 1]

        self.distances_gt_to_pred = distances_gt_to_pred
        self.distances_pred_to_gt = distances_pred_to_gt
        self.surfel_areas_gt = surfel_areas_gt
        self.surfel_areas_pred = surfel_areas_pred


class IMetric(abc.ABC):
    """Represents an evaluation metric."""

    def __init__(self, metric: str = 'IMetric'):
        """Initializes a new instance of the IMetric class.

        Args:
            metric (str): The identification string of the metric.
        """
        self.metric = metric

    @abc.abstractmethod
    def calculate(self):
        """Calculates the metric."""

        raise NotImplementedError

    def __str__(self):
        """Gets a printable string representation.

        Returns:
            str: String representation.
        """
        return '{self.metric}'.format(self=self)


class IConfusionMatrixMetric(IMetric):
    """Represents an evaluation metric based on the confusion matrix."""

    def __init__(self, metric: str = 'IConfusionMatrixMetric'):
        """Initializes a new instance of the IConfusionMatrixMetric class.

        Args:
            metric (str): The identification string of the metric.
        """
        super().__init__(metric)
        self.confusion_matrix = None  # ConfusionMatrix

    @abc.abstractmethod
    def calculate(self):
        """Calculates the metric."""

        raise NotImplementedError


class IDistanceMetric(IMetric):
    """Represents an evaluation metric based on distances."""

    def __init__(self, metric: str = 'IDistanceMetric'):
        """Initializes a new instance of the IDistanceMetric class.

        Args:
            metric (str): The identification string of the metric.
        """
        super().__init__(metric)
        self.distances = None  # Distances

    @abc.abstractmethod
    def calculate(self):
        """Calculates the metric."""

        raise NotImplementedError


class ISimpleITKImageMetric(IMetric):
    """Represents an evaluation metric based on SimpleITK images."""

    def __init__(self, metric: str = 'ISimpleITKImageMetric'):
        """Initializes a new instance of the ISimpleITKImageMetric class.

        Args:
            metric (str): The identification string of the metric.
        """
        super().__init__(metric)
        self.ground_truth = None  # SimpleITK.Image
        self.segmentation = None  # SimpleITK.Image

    @abc.abstractmethod
    def calculate(self):
        """Calculates the metric."""

        raise NotImplementedError


class INumpyArrayMetric(IMetric):
    """Represents an evaluation metric based on numpy arrays."""

    def __init__(self, metric: str = 'INumpyArrayMetric'):
        """Initializes a new instance of the INumpyArrayMetric class.

        Args:
            metric (str): The identification string of the metric.
        """
        super().__init__(metric)
        self.ground_truth = None  # np.ndarray
        self.segmentation = None  # np.ndarray

    @abc.abstractmethod
    def calculate(self):
        """Calculates the metric."""

        raise NotImplementedError


class Information(IMetric):
    """Represents an information.

    Can be used to add an additional column of information to an evaluator.
    """

    def __init__(self, column_name: str, value: str):
        """Initializes a new instance of the Information class.

        Args:
            column_name (str): The identification string of the information.
            value (str): The information.
        """
        super().__init__(column_name)
        self.value = value

    def calculate(self):
        """Outputs the value of the information."""
        return self.value
