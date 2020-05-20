import numpy as np

# to do
# gui plotting
# physical parameters
# - threshold 


class world_grid:
    def __init__(self, grid_shape, grid_resolution):
        self.extent = grid_shape
        self.resolution = grid_resolution
        self.axis = [np.arange(-grid_range, grid_range+self.resolution, self.resolution) for grid_range in self.extent]
        self.shape = tuple([len(ax) for ax in self.axis])
        self._grids = np.meshgrid(self.axis[0], self.axis[1], self.axis[2], indexing='ij')

    def point(self, point):
        x, y, z = point
        nx = [index for index, value in enumerate(self.axis[0]) if np.abs(value - x) < .9*self.resolution][0]
        ny = [index for index, value in enumerate(self.axis[1]) if np.abs(value - y) < .9*self.resolution][0]
        nz = [index for index, value in enumerate(self.axis[2]) if np.abs(value - z) < .9*self.resolution][0]
        return tuple([self._grids[i][nx][ny][nz] for i in range(3)])

    def iloc(self, point):
        x, y, z = point
        nx = [index for index, value in enumerate(self.axis[0]) if np.abs(value - x) < .9*self.resolution][0]
        ny = [index for index, value in enumerate(self.axis[1]) if np.abs(value - y) < .9*self.resolution][0]
        nz = [index for index, value in enumerate(self.axis[2]) if np.abs(value - z) < .9*self.resolution][0]
        return (nx, ny, nz)


class distribution:
    def __init__(self, world_grid, origin=None, orientation=None):
        self.world_grid = world_grid
        self.intensity = np.zeros(self.world_grid.shape)
        self.origin = origin
        self.orientation = orientation

    def get_cross_section(self, x=None, y=None, z=None):
        # specify two coordinates to determine the slice
        # this relies on 0,0,0 being inside the grid. might not be ideal
        if x is not None:
            nx, _, _ = self.world_grid.iloc((x, 0.0, 0.0))
            return self.intensity[nx, :, :]
        elif y is not None:
            _, ny, _ = self.world_grid.iloc((0.0, y, 0.0))
            return self.intensity[:, ny, :]
        elif z is not None:
            _, _, nz = self.world_grid.iloc((0.0, 0.0, z))
            return self.intensity[:, :, nz]


class spherical(distribution):
    def __init__(self, world_grid, origin=None, orientation=None):
        super().__init__(world_grid, origin, orientation)
        self.create_intensity_distribution()

    def create_intensity_distribution(self):
        for x in self.world_grid.axis[0]:
            for y in self.world_grid.axis[1]:
                for z in self.world_grid.axis[2]:
                    nx, ny, nz = self.world_grid.iloc((x, y, z))
                    x0, y0, z0 = self.origin
                    r_squared = ((x-x0)**2 + (y-y0)**2 + (z-z0)**2)
                    self.intensity[nx][ny][nz] = 1/r_squared


grid_shape = (1, 1, 1)  # mm
grid_resolution = .1  # mm
world = world_grid(grid_shape, grid_resolution)
# test = spherical(world, origin=(1.1, 1.1, 1.1), orientation=np.array([0, 0, 0, ]))
