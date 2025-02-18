#  Copyright (c) 2025 Robert Ball, Joshua Jensen, and Cody Squadroni

import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import matplotlib as mpl
import math
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle


def leave_event(event):
    for patch in reversed(patches):
        _gen = patch.additional_fields['generation']
        try:
            patch.set_facecolor(generationToColorDict[_gen])
            patch.set_zorder(2)
        except ValueError:
            patch.set_facecolor('red')
            patch.set_zorder(2)
        patch.patch_text.set_visible(True)

    for patch in click_patches:
        patch.set_visible(False)
        patch.patch_text.set_visible(False)

    annot.set_visible(False)
    fig.canvas.draw_idle()


def key_press(event):
    global parentViewMode, generationViewMode, individualViewMode, tooltipViewMode, siblingViewMode, childrenViewMode
    if event.key == 'q':
        exit()
    if event.key == '1':
        if parentViewMode:
            parentViewMode = False
            generationViewMode = False
            individualViewMode = True
            viewMode.set_text('(3) Hover: Individual View Mode')
        else:
            parentViewMode = True
            generationViewMode = False
            individualViewMode = False
            viewMode.set_text('(1) Hover: Parents View Mode')
    elif event.key == '2':
        if generationViewMode:
            generationViewMode = False
            parentViewMode = False
            individualViewMode = True
            viewMode.set_text('(3) Hover: Individual View Mode')
        else:
            parentViewMode = False
            generationViewMode = True
            individualViewMode = False
            viewMode.set_text('(2) Hover: Generation View Mode')
    elif event.key == '3':
        parentViewMode = False
        generationViewMode = False
        individualViewMode = True
        viewMode.set_text('(3) Hover: Individual View Mode')
    if event.key == '4':
        if tooltipViewMode:
            tooltipViewMode = False
            tooltipsMode.set_text('(4) Tooltips Off')
            annot.set_visible(False)
        else:
            tooltipViewMode = True
            tooltipsMode.set_text('(4) Tooltips On')
    if event.key == '5':
        siblingViewMode = True
        childrenViewMode = False
        clickViewMode.set_text('(5) Click: Family - Siblings View Mode')
    if event.key == '6':
        childrenViewMode = True
        siblingViewMode = False
        clickViewMode.set_text('(6) Click: Family - Children View Mode')
    fig.canvas.draw_idle()

def onclick(event):
    global clicked
    if event.inaxes == ax:
        foundIt = False
        clicked = False
        for patch in reversed(patches):
            _gen = patch.additional_fields['generation']
            _ind = patch.additional_fields['individualNumber']

            cont, ind = patch.contains(event)
            if cont and _ind == 16 and _gen == 5:
                foundIt = True
                clicked = True
        if not foundIt:
            for patch in reversed(patches):
                _gen = patch.additional_fields['generation']
                _isApproximated = patch.additional_fields['isApproximated']
                patch.set_facecolor(generationToColorDict[_gen])
                if _isApproximated:
                    patch.set_edgecolor('red')
                else:
                    patch.set_edgecolor('black')
                patch.set_zorder(2)
                patch.set_visible(True)
                patch.patch_text.set_visible(True)

            for patch in click_patches:
                patch.set_visible(False)
                patch.patch_text.set_visible(False)

            annot.set_visible(False)
        else:
            for patch in reversed(patches):
                _gen = patch.additional_fields['generation']
                _ind = patch.additional_fields['individualNumber']
                _isApproximated = patch.additional_fields['isApproximated']

                patch.set_facecolor(generationToColorOpacityDict4[_gen])
                if _isApproximated:
                    patch.set_edgecolor((1,0,0,0.5))
                else:
                    patch.set_edgecolor((0,0,0,0.5))
                patch.set_zorder(2)
                patch.patch_text.set_visible(False)

            for patch in click_patches:
                patch.set_visible(True)
                patch.patch_text.set_visible(True)

            annot.set_visible(False)

        fig.canvas.draw_idle()


def hover(event):
    global clicked
    if not clicked:  # Do not do hover if clicked is active
        if event.inaxes == ax:
            foundIt = False
            foundItGen = -1
            foundItIndividual = -1
            for patch in reversed(patches):
                _gen = patch.additional_fields['generation']
                _ind = patch.additional_fields['individualNumber']
                _isApproximated = patch.additional_fields['isApproximated']
                cont, ind = patch.contains(event)
                if cont:
                    _personID = patch.additional_fields['personID']
                    born_text = generationToYears[_gen][_ind][0]
                    if math.isnan(born_text):
                        born_text = 'Not Known\nApproximated to about 1875'
                    # The tooltip:
                    if generationToYears[_gen][_ind][1] == 2025:
                        annot.set_text(f'Name: {_personID}\nBorn: {born_text}\nStill Alive')
                    else:
                        annot.set_text(
                            f'Name: {_personID}\nBorn: {born_text}\nDied: {generationToYears[_gen][_ind][1]}')
                    annot.xy = (event.xdata, event.ydata)
                    if tooltipViewMode:
                        annot.set_visible(True)

                    if generationViewMode:
                        foundIt = True
                        foundItGen = _gen
                        foundItIndividual = _ind
                    if parentViewMode:
                        foundItGen = _gen
                        foundItIndividual = _ind
                        patch.set_facecolor(generationToColorDict[_gen])
                        patch.set_zorder(5)
                        foundIt = True
                    if individualViewMode:
                        foundItGen = _gen
                        foundItIndividual = _ind
                        patch.set_facecolor(generationToColorDict[_gen])
                        if _isApproximated:
                            patch.set_edgecolor('red')
                        else:
                            patch.set_edgecolor('black')
                        patch.set_zorder(5)
                        foundIt = True
                        break

            if foundIt:
                if individualViewMode:
                    descendants = {}
                    _parentInd = foundItIndividual
                    for _i in range(foundItGen - 1, -1, -1):
                        _temp = math.floor(_parentInd / 2)
                        descendants[_i] = _temp
                        _parentInd = _temp
                    for patch in reversed(patches):
                        _gen = patch.additional_fields['generation']
                        _ind = patch.additional_fields['individualNumber']
                        _isApproximated = patch.additional_fields['isApproximated']
                        cont, ind = patch.contains(event)
                        if not cont:
                            if _gen in descendants and descendants[_gen] == patch.additional_fields['individualNumber']:
                                patch.set_facecolor(generationToColorOpacityDict2[_gen])
                                if _isApproximated:
                                    patch.set_edgecolor('red')
                                else:
                                    patch.set_edgecolor('black')
                                patch.set_zorder(3)
                            else:
                                patch.set_facecolor(generationToColorOpacityDict3[_gen])
                                if _isApproximated:
                                    patch.set_edgecolor('red')
                                else:
                                    patch.set_edgecolor('black')
                                patch.set_zorder(2)
                elif generationViewMode:
                    for patch in reversed(patches):
                        _gen = patch.additional_fields['generation']
                        _isApproximated = patch.additional_fields['isApproximated']
                        if _gen == foundItGen:
                            patch.set_facecolor(generationToColorDict[_gen])
                            if _isApproximated:
                                patch.set_edgecolor('red')
                            else:
                                patch.set_edgecolor('black')
                            patch.set_zorder(2)
                        else:
                            patch.set_facecolor(generationToColorOpacityDict[_gen])
                            if _isApproximated:
                                patch.set_edgecolor('red')
                            else:
                                patch.set_edgecolor('black')
                            patch.set_zorder(1)
                elif parentViewMode:
                    if foundItGen == 0:
                        for patch in reversed(patches):
                            _gen = patch.additional_fields['generation']
                            _isApproximated = patch.additional_fields['isApproximated']
                            if _gen != 0:
                                patch.set_facecolor(generationToColorOpacityDict[_gen])
                                if _isApproximated:
                                    patch.set_edgecolor('red')
                                else:
                                    patch.set_edgecolor('black')
                                patch.set_zorder(1)
                    else:
                        if foundItIndividual % 2 == 0:
                            spouse = foundItIndividual + 1
                        else:
                            spouse = foundItIndividual - 1
                        for patch in reversed(patches):
                            _gen = patch.additional_fields['generation']
                            _ind = patch.additional_fields['individualNumber']
                            _isApproximated = patch.additional_fields['isApproximated']
                            if _gen == foundItGen and (_ind == foundItIndividual or _ind == spouse):
                                patch.set_facecolor(generationToColorDict[_gen])
                                if _isApproximated:
                                    patch.set_edgecolor('red')
                                else:
                                    patch.set_edgecolor('black')
                                patch.set_zorder(5)
                            else:
                                patch.set_facecolor(generationToColorOpacityDict3[_gen])
                                if _isApproximated:
                                    patch.set_edgecolor('red')
                                else:
                                    patch.set_edgecolor('black')
                                patch.set_zorder(1)
            else:  # Did not find a patch: Clear all colors and hide the tooltip
                for patch in reversed(patches):
                    _gen = patch.additional_fields['generation']
                    _isApproximated = patch.additional_fields['isApproximated']
                    patch.set_facecolor(generationToColorDict[_gen])
                    if _isApproximated:
                        patch.set_edgecolor('red')
                    else:
                        patch.set_edgecolor('black')
                    patch.set_zorder(2)
                annot.set_visible(False)
            fig.canvas.draw_idle()
    else:
        if event.inaxes == ax:
            for patch in click_patches:
                cont, ind = patch.contains(event)
                if cont:
                    _personID = patch.additional_fields['personID']
                    # Hard-coded for the click example (We can only click on person 47 - we would need more data otherwise):
                    clickGenerationID = 48 - _personID
                    _gen = clickGeneration[clickGenerationID]
                    born_text = _gen[0]
                    death_text = _gen[1]
                    # The tooltip:
                    _text = '47'
                    if clickGenerationID == 0:
                        _text = "47's Older Sibling"
                    elif clickGenerationID > 1:
                        _text = "47's Younger Sibling"
                    annot.set_text(f'Sibling View\nName: {_text}\nBorn: {born_text}\nDied: {death_text}')
                    annot.xy = (event.xdata, event.ydata)
                    if tooltipViewMode:
                        annot.set_visible(True)
            fig.canvas.draw_idle()


def get_arc_vertices(arc, num_points=100):
    """Get the vertices of a matplotlib Arc object."""
    theta = np.linspace(arc.theta1, arc.theta2, num_points)
    theta_rad = np.deg2rad(theta)
    x = arc.center[0] + (arc.width / 2) * np.cos(theta_rad)
    y = arc.center[1] + (arc.height / 2) * np.sin(theta_rad)
    return np.column_stack([x, y])


def createCustomWedgeWithEndShape(_personID, widthAndHeight1, widthAndHeight2, _generation=0, individualNumber=0, _angle=90,
                                  birthYearApproximated=False):
    # Define the arcs
    _arc1 = Arc((0, 0), width=widthAndHeight1 * 2, height=widthAndHeight1 * 2, angle=0, theta1=0, theta2=_angle)
    _arc2 = Arc((0, 0), width=widthAndHeight2 * 2, height=widthAndHeight2 * 2, angle=0, theta1=0, theta2=_angle)

    # Get the vertices of the arcs
    vertices1 = get_arc_vertices(_arc1)
    vertices2 = get_arc_vertices(_arc2)

    # Combine the vertices into a single path
    vertices = np.concatenate([vertices1, vertices2[::-1]], axis=0)
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]

    # Create the path and path patch
    path = Path(vertices, codes)

    pp = PathPatch(path, facecolor=generationToColorDict[generation], edgecolor='black')
    pp.additional_fields = {'generation': _generation, 'individualNumber': individualNumber, 'isApproximated': birthYearApproximated,
              'personID': _personID}
    return pp, vertices1


def get_arc_points(arc, num_points=100):
    """
    Gets the points on a matplotlib Arc patch.

    Parameters:
    - arc: The matplotlib.patches.Arc object
    - num_points: The number of points to generate on the arc

    Returns:
    - A list of (x, y) coordinates for the points on the arc
    """

    # Get the arc's path
    path = arc.get_path()

    # Create a list of evenly spaced angles along the arc
    theta = np.linspace(arc.theta1, arc.theta2, num_points)

    # Convert angles to radians
    theta_rad = np.deg2rad(theta)

    # Transform the points to the arc's coordinates
    points = path.vertices.copy()
    points[:, 0] *= arc.width / 2
    points[:, 1] *= arc.height / 2
    points = arc.get_transform().transform(points)

    # Interpolate the path for the specified angles
    verts = path.interpolated(theta_rad).vertices
    verts[:, 0] *= arc.width / 2
    verts[:, 1] *= arc.height / 2
    verts = arc.get_transform().transform(verts)

    return verts


def dashed_arc(ax2, _x2, _y2, radius2, start_angle, end_angle, dash_length=10, gap_length=5, number_of_dashes=100,
               **kwargs):
    """Draws a dashed arc on the given axes."""

    # Calculate the arc's angles in radians
    start_angle_rad = np.radians(start_angle)
    end_angle_rad = np.radians(end_angle)

    # Generate points along the arc
    angles = np.linspace(start_angle_rad, end_angle_rad, number_of_dashes)
    arc_x = _x2 + radius2 * np.cos(angles)
    arc_y = _y2 + radius2 * np.sin(angles)

    # Create a dashed line
    for i in range(0, len(arc_x) - 1, 2):
        if i + 1 < len(arc_x):
            ax2.plot(arc_x[i:i + 2], arc_y[i:i + 2], linestyle='--', **kwargs)


generationToYears = {
    0: [(2018, 2025)],  # 1 person (Child)
    1: [(1978, 2025), (1980, 2025)],  # 2 people (Parents)
    2: [(1950, 2025), (1951, 2025), (1948, 2025), (1949, 2025)],  # 4 people (Grandparents)
    3: [(1922, 1951), (1923, 2006), (1929, 2019), (1931, 2009), (1922, 2016), (1925, 2023), (1886, 1962), (1919, 1997)],
    # 8 people (Great-grandparents)
    4: [(1899, 1962), (1900, 2001), (1879, 1970), (1883, 1980), (1898, 1976), (1900, 1991), (1907, 1988), (1910, 1985),
        (1892, 1972), (1893, 1991), (1880, 1975), (1892, 1975), (1862, 1942), (1866, 1961), (1896, 1991), (1895, 1968)],
    #16 people
    5: [(1866, 1951), (1874, 1959), (1876, 1945), (1884, 1947), (1853, 1908), (1859, 1933), (1849, 1904), (1853, 1921),
        (1861, 1952), (1868, 1947), (1869, 1946), (1867, 1944), (1882, 1948), (1888, 1972), (1882, 1934), (1885, 1959),
        (1832, 1900), (1854, 1931), (1859, 1937), (1860, 1935), (1854, 1906), (1861, 1935), (1862, 1922), (1865, 1933),
        (1837, 1915), (1836, 1921), (1834, 1919), (1838, 1906), (1865, 1952), (1867, 1948), (np.nan, 1934),
        (1864, 1940)],
    #32 people (Great-great grandparents)
}

clickGeneration = [(1831,1838), (1832,1900), (1835,1931), (1837,1929), (1840,1910)]

generationToColorDict = {
    0: '#f6de84',
    1: '#e0ff87',
    2: '#afffa3',
    3: '#affffe',
    4: '#c3cefc',
    5: '#efbedc',
}

generationToColorRGBDict = {
    0: (0.964705882352941, 0.870588235294118, 0.517647058823529),
    1: (0.87843137254902, 1, 0.529411764705882),
    2: (0.686274509803922, 1, 0.63921568627451),
    3: (0.686274509803922, 1, 0.996078431372549),
    4: (0.764705882352941, 0.807843137254902, 0.988235294117647),
    5: (0.937254901960784, 0.745098039215686, 0.862745098039216),
}

generationToColorOpacityDict = {
    0: (0.964705882352941, 0.870588235294118, 0.517647058823529, 0.25),
    1: (0.87843137254902, 1, 0.529411764705882, 0.25),
    2: (0.686274509803922, 1, 0.63921568627451, 0.25),
    3: (0.686274509803922, 1, 0.996078431372549, 0.25),
    4: (0.764705882352941, 0.807843137254902, 0.988235294117647, 0.25),
    5: (0.937254901960784, 0.745098039215686, 0.862745098039216, 0.25),
}

opacity2 = 0.75
generationToColorOpacityDict2 = {
    0: (0.964705882352941, 0.870588235294118, 0.517647058823529, opacity2),
    1: (0.87843137254902, 1, 0.529411764705882, opacity2),
    2: (0.686274509803922, 1, 0.63921568627451, opacity2),
    3: (0.686274509803922, 1, 0.996078431372549, opacity2),
    4: (0.764705882352941, 0.807843137254902, 0.988235294117647, opacity2),
    5: (0.937254901960784, 0.745098039215686, 0.862745098039216, opacity2),
}

opacity3 = 0.25
generationToColorOpacityDict3 = {
    0: (0.964705882352941, 0.870588235294118, 0.517647058823529, opacity3),
    1: (0.87843137254902, 1, 0.529411764705882, opacity3),
    2: (0.686274509803922, 1, 0.63921568627451, opacity3),
    3: (0.686274509803922, 1, 0.996078431372549, opacity3),
    4: (0.764705882352941, 0.807843137254902, 0.988235294117647, opacity3),
    5: (0.937254901960784, 0.745098039215686, 0.862745098039216, opacity3),
}

opacity4 = 0.05
generationToColorOpacityDict4 = {
    0: (0.964705882352941, 0.870588235294118, 0.517647058823529, opacity4),
    1: (0.87843137254902, 1, 0.529411764705882, opacity4),
    2: (0.686274509803922, 1, 0.63921568627451, opacity4),
    3: (0.686274509803922, 1, 0.996078431372549, opacity4),
    4: (0.764705882352941, 0.807843137254902, 0.988235294117647, opacity4),
    5: (0.937254901960784, 0.745098039215686, 0.862745098039216, opacity4),
}

# Create a figure and axes
fig, ax = plt.subplots()

# "annot" is the tooltip:
annot = ax.annotate("additional_fields", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)
annot.set_zorder(20)

parentViewMode, generationViewMode, individualViewMode, tooltipViewMode, lineViewMode = False, False, True, True, True
clicked = False
siblingViewMode, childrenViewMode = True, False

viewMode = ax.annotate("(3) Hover: Individual View Mode", xy=(-180, 180), bbox=dict(boxstyle="round", fc="w"))
viewMode.set_visible(True)
viewMode.set_zorder(20)

clickViewMode = ax.annotate("(5) Click: Family - Siblings View Mode", xy=(100, 180), bbox=dict(boxstyle="round", fc="w"))
clickViewMode.set_visible(True)
clickViewMode.set_zorder(20)

tooltipsMode = ax.annotate("(4) Tooltips On", xy=(-180, 190), bbox=dict(boxstyle="round", fc="w"))
tooltipsMode.set_visible(True)
tooltipsMode.set_zorder(20)

current_year = 2025

min_year = 1945
diff_years = current_year - min_year

numberOfGenerations = 6
patches = []
click_patches = []

# We are hard-coding one person's siblings. If we don't then we will need access to a database full of information:
click_example_patches = []

personID = (2 ** numberOfGenerations) - 1
fs = 8.5

for generation in range(numberOfGenerations - 1, -1, -1):
    people = generationToYears[generation]
    _numberOfWedges = 2 ** generation
    _angle = 180 / _numberOfWedges
    t_angle = 0

    for i, person in enumerate(people):
        birthYear = person[0]
        deathYear = person[1]
        isApproximated = False
        if math.isnan(birthYear):
            isApproximated = True
            birthYear = 1875
        age = deathYear - birthYear
        birth_years_from_current_year = current_year - birthYear
        death_years_from_current_year = current_year - deathYear
        custom_path, _vertices = createCustomWedgeWithEndShape(_personID=personID,
                                                               widthAndHeight1=birth_years_from_current_year,
                                                               widthAndHeight2=death_years_from_current_year,
                                                               _generation=generation,
                                                               individualNumber=i,
                                                               _angle=_angle,
                                                               birthYearApproximated=isApproximated)
        t2 = mpl.transforms.Affine2D().rotate_deg(t_angle) + ax.transData
        _center = np.mean(_vertices, axis=0)
        custom_path.set_transform(t2)
        if isApproximated:
            custom_path.set_edgecolor('red')
            custom_path.set_linewidth(2)
        ax.add_patch(custom_path)
        t_angle += _angle
        patches.append(custom_path)

        if personID == 1:
            patch_text = ax.text(_center[0], _center[1], str(personID), fontsize=fs, zorder=15, ha='center', va='center',
                    transform=t2)
        else:
            patch_text = ax.text(_center[0] - 5, _center[1], str(personID), fontsize=fs, zorder=15, ha='center', va='center',
                    transform=t2)
        custom_path.patch_text = patch_text
        personID -= 1

generation = 5
_numberOfWedges = 2 ** generation
_angle = 180 / _numberOfWedges
t_angle = 0
# For this hard-coded example, we set the angle of the siblings to the exact place where the person is located.
t_angle = _angle * 15
personID = 48
for i, person in enumerate(clickGeneration):
    birthYear = person[0]
    deathYear = person[1]
    age = deathYear - birthYear
    birth_years_from_current_year = current_year - birthYear
    death_years_from_current_year = current_year - deathYear
    custom_path, _vertices = createCustomWedgeWithEndShape(_personID=personID,
                                                           widthAndHeight1=birth_years_from_current_year,
                                                           widthAndHeight2=death_years_from_current_year,
                                                           _generation=generation,
                                                           individualNumber=i,
                                                           _angle=_angle,
                                                           birthYearApproximated=False)
    t2 = mpl.transforms.Affine2D().rotate_deg(t_angle) + ax.transData
    _center = np.mean(_vertices, axis=0)
    custom_path.set_transform(t2)
    custom_path.set_visible(False)
    custom_path.set_facecolor('orange')
    ax.add_patch(custom_path)
    t_angle += _angle
    click_patches.append(custom_path)

    _text = f'{personID} S'
    if personID == 47:
        _text = '47'

    patch_text = ax.text(_center[0] - 5, _center[1], _text, fontsize=fs, zorder=15, ha='center', va='center', transform=t2)
    custom_path.patch_text = patch_text
    patch_text.set_visible(False)
    personID -= 1

year_line_height = 1.0
distance_from_axis = -year_line_height * 4

# 2025
x = 0
text = '2025'
ax.text(x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([x, x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)

# 2020
x = 25
text = '2000'
dashed_arc(ax, 0, 0, x, 0, 180, dash_length=10, gap_length=5, color='black', number_of_dashes=x * 2)
ax.text(-x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([-x, -x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)
ax.text(x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([x, x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)

# 1950
x = 75
text = '1950'
dashed_arc(ax, 0, 0, x, 0, 180, dash_length=10, gap_length=5, color='black', number_of_dashes=x * 2)
ax.text(-x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([-x, -x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)
ax.text(x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([x, x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)

# 1900
x = 125
text = '1900'
dashed_arc(ax, 0, 0, x, 0, 180, dash_length=10, gap_length=5, color='black', number_of_dashes=x * 2)
ax.text(-x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([-x, -x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)
ax.text(x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([x, x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)

# 1850
x = 175
text = '1850'
dashed_arc(ax, 0, 0, x, 0, 180, dash_length=10, gap_length=5, color='black', number_of_dashes=x * 2)
ax.text(-x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([-x, -x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)
ax.text(x, distance_from_axis, text, fontsize=fs, zorder=15, ha='center', va='center')
plt.plot([x, x], [-year_line_height, year_line_height], color='black', linewidth=1.0, zorder=15)

# Set the aspect of the axes to 'equal' so the arc looks like a circle
ax.set_aspect('equal')
ax.set_xlim(-200, 200)
ax.set_ylim(-10, 200)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.xticks([])
plt.yticks([])
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

fig.canvas.mpl_connect("motion_notify_event", hover)
fig.canvas.mpl_connect("axes_leave_event", leave_event)
fig.canvas.mpl_connect("key_press_event", key_press)
fig.canvas.mpl_connect('button_press_event', onclick)

# Show the plot
plt.show()
# plt.savefig('time_line_fan_chart.png', dpi=200)
