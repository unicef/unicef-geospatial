from django.contrib.gis.db.models.functions import Area, Intersection, Transform
from django.db.models import Sum

from unicef_geospatial.core.models import Boundary, BoundaryType, Country
from unicef_geospatial.core.models.mixins import GeoModel


def consistency_validation(country_iso_code_2, admin_level):

    country = Country.objects.get(iso_code2=country_iso_code_2)

    bts = BoundaryType.objects.filter(country=country, level=admin_level)
    pending_boundaries = Boundary.objects.filter(boundary_type__in=bts, state=GeoModel.PENDING_APPROVAL)
    pending_without_name = pending_boundaries.filter(name='')  # list new Boundaries with null name
    pending_without_pcode = pending_boundaries.filter(p_code__in=['', None])
    pending_without_parent = pending_boundaries.filter(parent__isnull=True)
    pending_invalid_geometry = pending_boundaries.filter(geom__isvalid=False)

    bt0 = BoundaryType.objects.filter(country=country, level=0)
    pending_country = Boundary.objects.filter(boundary_type__in=bt0, state='Pending Approval').first()  # why from pending?
    pending_outside_country = pending_boundaries.exclude(geom__coveredby=pending_country.geom)

    print('Pending Issues')
    print('--------------')
    print('No Name', pending_without_name)
    print('No PCode', pending_without_pcode)
    print('No Parent', pending_without_parent)
    print('Invalid Geometry', pending_invalid_geometry)
    print('Outside Country', pending_outside_country)

    parent_boundary = BoundaryType.objects.filter(country=country, level=admin_level - 1)
    new_parent_boundaries = Boundary.objects.filter(boundary_type__in=parent_boundary, state=GeoModel.PENDING_APPROVAL)  # get parent Boundaries

    new_boundaries = Boundary.objects.filter(boundary_type__in=bts, state=GeoModel.PENDING_APPROVAL)
    old_boundaries = Boundary.objects.filter(boundary_type__in=bts, state=GeoModel.ACTIVE)

    for nb in new_boundaries:
        # check for overlaps
        overlap_area = new_boundaries.filter(geom__intersects=nb.geom).exclude(pk=nb.pk).annotate(intersection=Intersection('geom', nb.geom)).aggregate(Sum(Area('intersection')))

        # debug mode
        print(nb.name, overlap_area)
        overlaps = new_boundaries.filter(geom__intersects=nb.geom).exclude(pk=nb.pk).annotate(intersection=Transform(Intersection('geom', nb.geom), 3857)).order_by(Area('intersection'))
        for ov in overlaps:
            ov.name, ov.intersection.area, ov.geom.area
        #######
        # check parents
        parent = Boundary.objects.get(pk=nb.parent_id)
        if admin_level:
            # check if parent is correct
            found_parents = new_parent_boundaries.filter(geom__intersects=nb.geom.point_on_surface)  # get parents intersecting with centroid
            if len(found_parents) == 1:
                found_parent = found_parents[0]
                print("Found parent: {}".format(found_parent))
            elif len(found_parents) == 0:
                print("Warning - no parent found for {}".format(nb))
            else:
                print("Warning - more than one parent for {}".format(nb))
            if nb.parent is None:
                print("Warning - no parent defined for {}".format(nb))
            else:
                is_inside_parent = nb.geom.point_on_surface.intersects(parent.geom)
                if not is_inside_parent:
                    print("Warning - centroid is not within parent boundary for {}".format(nb))
                if parent.p_code != found_parent.p_code:
                    print('Warning - wrong parent Pcode provided for {}'.format(nb))

    if len(new_boundaries) != len(old_boundaries):
        print('Warning: different number of features in new dataset! Count of features at level {}:, old: {}, new: {}'.format(admin_level, len(old_boundaries), len(new_boundaries)))

    total_area_new = new_boundaries.aggregate(Sum(Area(Transform('geom', 3857))))['Area__sum'].sq_km
    total_area_old = old_boundaries.aggregate(Sum(Area(Transform('geom', 3857))))['Area__sum'].sq_km
    area_diff_threshold = 1
    if abs(total_area_new - total_area_old) > area_diff_threshold:
        print('Warning: different total area of the new dataset! Total area of features at level {}:, old: {:+.2f}, new: {:+.2f}'.format(admin_level, total_area_old, total_area_new))
