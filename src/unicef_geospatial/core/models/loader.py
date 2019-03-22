import os
from datetime import datetime
from difflib import SequenceMatcher
from math import atan2, cos, radians, sin, sqrt


def getval(ft, field):
    result = ""
    if field:
        val = ft[field]
        if val:
            if isinstance(val, str):
                result = "{}".format(val.encode('UTF-8').strip())
            else:
                result = "{}".format(val)
    return result


def calc_distance(lat1dd, lon1dd, lat2dd, lon2dd):
    # approximate radius of earth in m
    R = 6373.0

    lat1 = radians(lat1dd)
    lon1 = radians(lon1dd)
    lat2 = radians(lat2dd)
    lon2 = radians(lon2dd)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 1000
    return distance


start_time = datetime.now()
print("Started at: {}".format(start_time))

#######################
# DEFINE INPUT PARAMETERS HERE
adm_level = 3

old_lyr_name = 'mwi_popa_adm3_tradauth_geonode_nso2008_ocha'
old_pcode_field = 'ADM3_PCODE'
old_name_field = 'ADM3_EN'
old_lyr_label = 'Ver1'

new_lyr_name = 'mwi_admbnda_adm3_nso_20181016'
new_pcode_field = 'ADM3_PCODE'
new_name_field = 'ADM3_EN'
new_lyr_label = 'Ver2'
# END OF INPUT PARAMETERS
#######################


# get QGIS layers
old_lyr = [layer for layer in qgis.utils.iface.legendInterface().layers() if layer.name() == old_lyr_name][0]
new_lyr = [layer for layer in qgis.utils.iface.legendInterface().layers() if layer.name() == new_lyr_name][0]

# build spatial index for new features
n_index = QgsSpatialIndex()
for f in new_lyr.getFeatures():
    n_index.insertFeature(f)

# get old and new features into dictionaries
new_fts = {feature.id(): feature for (feature) in new_lyr.getFeatures()}  # [ft for ft in new_lyr.getFeatures()]
old_fts = {feature.id(): feature for (feature) in old_lyr.getFeatures()}  # [ft for ft in old_lyr.getFeatures()]

old2new_remaps = []

# loop through all "old" admin boundaries to get matching "new" boundary
for oft in old_fts.values():
    old2new_remap_overlaps = []
    old2new_remap_neighbors = []
    oft_centr = oft.geometry().pointOnSurface()
    match_found = 0

    # first try intersecting with nearest neighbors
    near_ids = n_index.intersects(oft.geometry().boundingBox())
    for nid in near_ids:
        nnft = new_fts[nid]
        nn_intersect_geom = oft.geometry().intersection(nnft.geometry())
        if nn_intersect_geom.area() > 0:
            perc_overlap = nn_intersect_geom.area() / oft.geometry().area() * 100
            old2new_remap_overlaps.append([oft, nnft, perc_overlap, "intersect"])
            # print("{}\t{}\t{}".format(oft[old_pcode_field],nnft[new_pcode_field],perc_overlap))
            match_found += 1

    # do if no intersecting neighbors found
    if match_found == 0:

        # loop through all "new" admin boundaries and calculate distance
        for nft in new_fts.values():
            dist = oft.geometry().pointOnSurface().distance(nft.geometry())  # ToDo: measure distance to the nearset edge not between centroids
            old2new_remap_neighbors.append([oft, nft, dist, "neigbor"])
            # print("{}\t{}\t{}".format(oft[old_pcode_field],nft[new_pcode_field],dist))

    # find best match
    best_match = []
    if match_found == 0:
        # get the closest new boundary as the best match
        best_match = min(old2new_remap_neighbors, key=lambda x: x[2])
        dist = best_match[2]
    else:
        # get a new boundary which overlaps the largest portion of the "old" boundary as the best match
        best_match = max(old2new_remap_overlaps, key=lambda x: x[2])
        dist = 0

    # get "old" and "new" matching boundaries
    oft = best_match[0]
    nft = best_match[1]
    old_name = getval(oft, old_name_field)
    old_pcode = oft[old_pcode_field]
    new_name = getval(nft, new_name_field)
    new_pcode = nft[new_pcode_field]

    # intersect both geometries and calculate similarities
    intersect_geom = nft.geometry().intersection(oft.geometry())
    geomsim_old = (intersect_geom.area() / oft.geometry().area() * 100)
    geomsim_new = (intersect_geom.area() / nft.geometry().area() * 100)
    centr_dist = calc_distance(oft.geometry().pointOnSurface().asPoint().y(), oft.geometry().pointOnSurface().asPoint().x(), nft.geometry().pointOnSurface().asPoint().y(), nft.geometry().pointOnSurface().asPoint().x())

    # calculate name similarity
    name_sim = SequenceMatcher(None, old_name, new_name).ratio() * 100

    # add a pair of "old" and "new" polygons to the remap table
    old2new_remaps.append([old_pcode, new_pcode, old_name, new_name, name_sim, geomsim_old, geomsim_new, dist, centr_dist, 'OK'])


# write a remap table to txt/csv file
outpath = os.path.join(os.path.dirname(new_lyr.dataProvider().dataSourceUri()), "Adm{}_{}_remappedTO_{}.txt".format(adm_level, old_lyr_label, new_lyr_label))
f = open(outpath, 'w')
header_csv = "{}_pcode\t{}_pcode\tpcode_check\t{}_name\t{}_name\tname_sim\tgeomsim_{}\tgeomsim_{}\tdis_dd\tcentr_dist_m\tcomment".format(old_lyr_label, new_lyr_label, old_lyr_label, new_lyr_label, old_lyr_label, new_lyr_label)
f.write("{}\n".format(header_csv))

for l in old2new_remaps:
    csv_output = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(l[0], l[1], l[0] == l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9])
    f.write("{}\n".format(csv_output))
f.close()

# print summary to the console
print("old_pcode_field = {}".format(old_pcode_field))
print("old_name_field = {}".format(old_name_field))
print("old_lyr_name = {}".format(old_lyr_name))
print("old_lyr_label = {}".format(old_lyr_label))

print("new_pcode_field = {}".format(new_pcode_field))
print("new_name_field = {}".format(new_name_field))
print("new_lyr_name = {}".format(new_lyr_name))
print("new_lyr_label = {}".format(new_lyr_label))

avg_name_sim = sum([a[4] for a in old2new_remaps]) / len(old2new_remaps)
print("Average name sim: {}".format(avg_name_sim))

print("Finished at: {}".format(datetime.now()))
print("Time: {}".format(datetime.now() - start_time))
