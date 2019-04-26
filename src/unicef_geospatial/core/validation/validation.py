from django.contrib.gis.db.models.functions import Intersection, IsValid
from django.contrib.gis.db.models.functions import Distance, PointOnSurface, Area, Transform
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Polygon
from unicef_geospatial.core.models import Boundary, BoundaryType
from difflib import SequenceMatcher
from django.db.models import Q
from django.db.models import Sum

country_id = 1
level = 1
bt = [bt.id for bt in BoundaryType.objects.filter(country_id=country_id, level=level)]
null_name_err = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval') & (Q(name='') | (Q(name__isnull=True)))) # list new Boundaries with null names
null_pc_err = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval') & (Q(p_code='') | (Q(p_code__isnull=True)))) # list new Boundaries with null pcodes
null_ppc_err = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval') & Q(parent__isnull=True)) # list new Boundaries with null parents
invalid_geom_err = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval') & Q(geom__isvalid=False)) # list new Boundaries with invalid geometry

cntry_bt = [cntry_bt.id for cntry_bt in BoundaryType.objects.filter(country_id=country_id, level=0)]
cntry_boundary = Boundary.objects.filter(Q(boundary_type_id__in=cntry_bt) & Q(state='Pending Approval'))[0]
outside_parent_err = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval') & ~Q(geom__coveredby=cntry_boundary.geom)) # list new Boundaries that are not completely covered by the country Boundary

btp = [btp.id for btp in BoundaryType.objects.filter(country_id=country_id, level=level-1)] # get parent Boundary Types
new_parent_boundaries = Boundary.objects.filter(Q(boundary_type_id__in=btp) & Q(state='Pending Approval')) # get parent Boundaries

new_boundaries = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Pending Approval'))
old_boundaries = Boundary.objects.filter(Q(boundary_type_id__in=bt) & Q(state='Active'))

for nb in new_boundaries:
	# check for overlaps
	overlap_area = new_boundaries.filter(geom__intersects=nb.geom).exclude(pk=nb.pk).annotate(intersection=Intersection('geom', nb.geom)).aggregate(Sum(Area('intersection')))
	#######
	# debug mode
	print(nb.name, overlap_area)
	overlaps = new_boundaries.filter(geom__intersects=nb.geom).exclude(pk=nb.pk).annotate(intersection=Transform(Intersection('geom', nb.geom), 3857)).order_by(Area('intersection'))
	for ov in overlaps:
		ov.name, ov.intersection.area, ov.geom.area
	#######
	# check parents
	parent = Boundary.objects.get(pk=nb.parent_id)
	if level != 0:
		# check if parent is correct
		found_parents = new_parent_boundaries.filter(geom__intersects=nb.geom.point_on_surface) # get parents intersecting with centroid
		if len(found_parents)==1:
			found_parent = found_parents[0]
			print("Found parent: {}".format(found_parent))
		elif len(found_parents)==0:
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
	print('Warning: different number of features in new dataset! Count of features at level {}:, old: {}, new: {}'.format(level,len(old_boundaries),len(new_boundaries)))

total_area_new = new_boundaries.aggregate(Sum(Area(Transform('geom',3857))))['Area__sum'].sq_km
total_area_old = old_boundaries.aggregate(Sum(Area(Transform('geom',3857))))['Area__sum'].sq_km
area_diff_threshold = 1
if abs(total_area_new - total_area_old) > area_diff_threshold:
	print('Warning: different total area of the new dataset! Total area of features at level {}:, old: {:+.2f}, new: {:+.2f}'.format(level,total_area_old,total_area_new))
