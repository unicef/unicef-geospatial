from difflib import SequenceMatcher

from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.measure import Distance

from unicef_geospatial.core.models import Boundary


def check_overlapping(admin_level, country_iso_code_2):

    #   = NEW objects from loading
    old_boundaries = Boundary.objects.filter(boundary_type__admin_level=admin_level,
                                             country__iso_code_2=country_iso_code_2,  # filter_active
                                             )  # old_fts
    new_boundaries = Boundary.objects.filter(boundary_type__admin_level=admin_level, country__iso_code_2=country_iso_code_2,)  # tofix
    # handle what loaded data can have multiple country and multiple admin_level

    for old_boundary in old_boundaries:
        overlapping_boundaries = new_boundaries.filter(geom__intersects=old_boundary.geom).annotate(
            intersection=Intersection('geom', old_boundary.geom))

        if overlapping_boundaries.exists():
            best_match = max(overlapping_boundaries, key=lambda x: x.intersection.area)  # most overlapping boundary
            # best_match = overlapping_boundaries.order_by('intersection').last()
        else:
            # find nearest boundary
            nearest_boundaries = new_boundaries.annotate(distance=Distance('geom', old_boundary.geom.centroid))  # todo - find distance between actual boundaries not centroid
            best_match = nearest_boundaries.order_by('distance').first()

        # calculate name similarity
        name_sim = SequenceMatcher(None, old_boundary.name, best_match.name).ratio() * 100

        # calculate distance between centroids
        centr_dist = old_boundary.geom.point_on_surface.distance(best_match.geom.point_on_surface) * 100

        # calculate geom similarities
        geomsim_old, geomsim_new = 0
        if best_match.intersection:
            intersect_geom = best_match.intersection
            geomsim_old = (intersect_geom.area / old_boundary.geom.area * 100)
            geomsim_new = (intersect_geom.area / best_match.geom.area * 100)

        # ToDo:
        # - write old and new uuids, names, pcodes and similarities (name and geometry) to the remap table
