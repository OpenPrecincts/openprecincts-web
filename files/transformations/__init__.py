from . import basic
from ..models import Transformations


TRANSFORMATION_CLASSES = {
    Transformations.ZIP: basic.ZipFiles,
    Transformations.TO_GEOJSON: basic.ToGeoJSON,
    Transformations.GEOJSON_TO_MAPBOX: basic.GeojsonToMbtile,
}
