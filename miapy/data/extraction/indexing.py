import abc
import typing as t

import numpy as np

import miapy.data.indexexpression as expr


class IndexingStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, shape) -> t.List[expr.IndexExpression]:
        # return list of indexes by giving shape
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__


class EmptyIndexing(IndexingStrategy):

    def __call__(self, shape) -> t.List[expr.IndexExpression]:
        return [expr.IndexExpression()]


class SliceIndexing(IndexingStrategy):

    def __init__(self, slice_axis: t.Union[int, tuple]=0) -> None:
        if isinstance(slice_axis, int):
            slice_axis = (slice_axis, )
        self.slice_axis = slice_axis

    def __call__(self, shape) -> t.List[expr.IndexExpression]:
        indexing = []
        for axis in self.slice_axis:
            indexing.extend(expr.IndexExpression(i, axis) for i in range(shape[axis]))
        return indexing

    def __repr__(self) -> str:
        return '{} ({})'.format(self.__class__.__name__, self.slice_axis)


class VoxelWiseIndexing(IndexingStrategy):

    def __init__(self, image_dimension: int=3):
        """Initializes a new instance of the VoxelWiseIndexing class.

        Args:
            image_dimension (int): The image dimension without the dimension of the voxels itself.
        """
        self.shape = None
        self.indexing = None
        self.image_dimension = image_dimension

    def __call__(self, shape) -> t.List[expr.IndexExpression]:
        if self.shape == shape:
            return self.indexing

        self.shape = shape  # save for later comparison to avoid calculating indices if the shape is equal
        shape_without_voxel = shape[0:self.image_dimension]
        indices = np.indices(shape_without_voxel)
        indices = indices.reshape((indices.shape[0], np.prod(indices.shape[1:])))
        indices = indices.transpose()
        self.indexing = [expr.IndexExpression(idx.tolist()) for idx in indices]
        return self.indexing
