import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.axes_grid1 import make_axes_locatable

# to do
# gui plotting
# physical parameters
# - threshold
# power delivered to surface

ZERO_THRESH = (1E-3)  # mm
SQ_ZERO_THRESH = (1E-1)**2 # mm^2


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


class world_data:
    def __init__(self, world_grid, origin=None, normal=None):
        self.world_grid = world_grid
        self.origin = self.world_grid.point(origin)
        self.normal = normal
        self.data = None

    def get_cross_section(self, x=None, y=None, z=None):
        # specify two coordinates to determine the slice
        # this relies on 0,0,0 being inside the grid. might not be ideal
        if x is not None:
            nx, _, _ = self.world_grid.iloc((x, 0.0, 0.0))
            return self.data[nx, :, :]
        elif y is not None:
            _, ny, _ = self.world_grid.iloc((0.0, y, 0.0))
            return self.data[:, ny, :]
        elif z is not None:
            _, _, nz = self.world_grid.iloc((0.0, 0.0, z))
            return self.data[:, :, nz]


class spherical(world_data):
    def __init__(self, world_grid, origin=None, normal=None, total_power=1.0):
        super().__init__(world_grid, origin, normal)
        self.total_power = total_power
        self.create_intensity_distribution()
        self.data = self.create_intensity_distribution()

    def create_intensity_distribution(self):
        intensity = np.zeros(self.world_grid.shape)
        for x in self.world_grid.axis[0]:
            for y in self.world_grid.axis[1]:
                for z in self.world_grid.axis[2]:
                    nx, ny, nz = self.world_grid.iloc((x, y, z))
                    x0, y0, z0 = self.origin
                    r_squared = ((x-x0)**2 + (y-y0)**2 + (z-z0)**2)
                    if r_squared > SQ_ZERO_THRESH:
                        intensity[nx][ny][nz] = self.total_power*1/r_squared
                    else:
                        intensity[nx][ny][nz] = self.total_power/SQ_ZERO_THRESH
        return intensity


class surface(world_data):
    def __init__(self, world_grid, origin=None, normal=None):
        super().__init__(world_grid, origin, normal)
        self.data = self.create_surface()

    def create_surface(self):
        surface = np.zeros(self.world_grid.shape)
        x0, y0, z0 = self.origin
        A, B, C = self.normal
        for x in self.world_grid.axis[0]:
            for y in self.world_grid.axis[1]:
                for z in self.world_grid.axis[2]:
                    if np.abs(A*(x-x0) + B*(y-y0) + C*(z-z0)) < ZERO_THRESH:
                        nx, ny, nz = self.world_grid.iloc((x, y, z))
                        surface[nx][ny][nz] = 1
        return surface

class plot_gui:
    def __init__(self, intensity_distribution, plane):
        self.intensity_distribution = intensity_distribution
        self.plane = plane
        plot_array = self.intensity_distribution.get_cross_section(x=0)+self.plane.get_cross_section(x=0)

        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(plot_array, origin='lower')
        self.im.set_clim(0, 5.0)

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(self.im, ax=self.ax, cax=cax, label="Amplitude")
        plt.subplots_adjust(left=0.25, bottom=0.25)

        axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
        sfreq = Slider(axfreq, 'x', -.9, .9, valinit=-.9, valstep=.1)
        sfreq.on_changed(self.update_x)

        plt.show()

    def update_x(self, val):
        self.im.set_data(self.intensity_distribution.get_cross_section(x=val)+self.plane.get_cross_section(x=val))
        self.fig.canvas.draw_idle()

    def update_y(self, val):
        self.im.set_data(self.intensity_distribution.get_cross_section(y=val))
        self.fig.canvas.draw_idle()

    def update_z(self, val):
        self.im.set_data(self.intensity_distribution.get_cross_section(z=val))
        self.fig.canvas.draw_idle()

grid_shape = (1, 1, 1)  # mm
grid_resolution = .05  # mm

world = world_grid(grid_shape, grid_resolution)

point_source = spherical(world, origin=(0, 0, 0), normal=np.array([0, 0, 0, ]), total_power=5.0)
detector_plane = surface(world, origin=(0, .5, .5), normal=np.array([0, 1, 1])/np.sqrt(2))

plot_it = plot_gui(point_source, detector_plane)
