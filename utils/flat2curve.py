import numpy as np
from scipy import ndimage


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (phi, rho)


def pol2cart(phi, rho):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def sub2ind(array_shape, rows, cols):
    return rows * array_shape[1] + cols


def flat2curve(I, dist, mon_size, **kwargs):
    params = dict({'center_x': 0, 'center_y': 0, 'method': 'index'},
                  **kwargs)  # center_x, center_y points in normalized x coordinates from center

    # Shift the origin to the closest point of the image.
    nrows, ncols = np.shape(I)
    [yi, xi] = np.meshgrid(np.linspace(1, ncols, ncols),np.linspace(1, nrows, nrows))
    yt = yi - ncols/2 + params['center_y']*nrows - 0.5
    xt = xi - nrows/2 - params['center_x']*nrows - 0.5

    # Convert the Cartesian x- and y-coordinates to cylindrical angle (theta) and radius (r) coordinates
    [theta, r] = cart2pol(yt, xt)

    # Compute spherical radius
    diag = np.sqrt(sum(np.array(np.shape(I)) ** 2))  # diagonal in px
    dist_px = dist / 2.54 / mon_size * diag  # closest distance from the monitor in px
    phi = np.arctan(r / dist_px)

    h = np.cos(phi / 2) * dist_px
    r_new = 2 * np.sqrt(dist_px ** 2 - h ** 2)

    # Convert back to the Cartesian coordinate system. Shift the origin back to the upper-right corner of the image.
    [ut, vt] = pol2cart(theta, r_new)
    ui = ut + ncols / 2 - params['center_y'] * nrows
    vi = vt + nrows / 2 + params['center_x'] * nrows

    # Tranform image
    if params['method'] == 'index':
        idx = (vi.astype(int), ui.astype(int))
        transform = lambda x: x[idx]
    elif params['method'] == 'interp':
        transform = lambda x: ndimage.map_coordinates(x, [vi.ravel() - 0.5, ui.ravel() - 0.5], order=1,
                                                      mode='nearest').reshape(x.shape)
    return (transform(I), transform)
