from django.contrib.gis.db.models.functions import Area, Intersection, Transform
from django.db.models import Q, Sum

from unicef_geospatial.core.models import Boundary, BoundaryType, Country


def consistency_validation(country_iso_code_2, admin_level):

    country = Country.objects.get(iso_code2=country_iso_code_2)

    bts = BoundaryType.objects.filter(country=country, level=admin_level)
    null_name_err = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval') & (Q(name='') | (Q(name__isnull=True))))  # list new Boundaries with null names
    null_pc_err = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval') & (Q(p_code='') | (Q(p_code__isnull=True))))  # list new Boundaries with null pcodes
    null_ppc_err = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval') & Q(parent__isnull=True))  # list new Boundaries with null parents
    invalid_geom_err = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval') & Q(geom__isvalid=False))  # list new Boundaries with invalid geometry

    cntry_bts = BoundaryType.objects.filter(country=country, level=0)
    cntry_boundary = Boundary.objects.filter(Q(boundary_type__in=cntry_bts) & Q(state='Pending Approval')).first()
    outside_parent_err = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval') & ~Q(geom__coveredby=cntry_boundary.geom))  # list new Boundaries that are not completely covered by the country Boundary

    btp = [btp.id for btp in BoundaryType.objects.filter(country=country, level=admin_level - 1)]  # get parent Boundary Types
    new_parent_boundaries = Boundary.objects.filter(Q(boundary_type_id__in=btp) & Q(state='Pending Approval'))  # get parent Boundaries

    new_boundaries = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Pending Approval'))
    old_boundaries = Boundary.objects.filter(Q(boundary_type__in=bts) & Q(state='Active'))

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

    print(null_name_err)
    print(null_pc_err)
    print(null_ppc_err)
    print(invalid_geom_err)

    print(cntry_boundary)
    print(outside_parent_err)
