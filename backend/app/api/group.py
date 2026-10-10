from fastapi import APIRouter, HTTPException

from app.ml.grouping import cluster_riders
from app.models.schemas import GroupRequest, GroupResponse
from app.services.catalog import station_by_id

router = APIRouter()


@router.post("/group", response_model=GroupResponse)
def post_group(body: GroupRequest) -> GroupResponse:
    if not body.riders:
        return GroupResponse(clusters=[], ungrouped=[])
    bays = 3
    if body.station_id:
        try:
            bays = station_by_id(body.station_id).bays
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown station {exc}") from exc
    clusters, ungrouped = cluster_riders(body.riders, bays=bays)
    return GroupResponse(clusters=clusters, ungrouped=ungrouped)
