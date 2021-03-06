from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel,Field
from typing import Optional
from objectid import PydanticObjectId
class Location(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    'atm','bank','church','gas_station','hospital','mosque','pharmacy','restaurant','school','competitors'
   
    atm : float
    bank :float
    church : float
    gas_station : float
    hospital:float
    mosque :float
    pharmacy : float
    name :str
    nearest:list
    rating : float
    restaurant: float
    school: float
    latitude:float
    longitude:float
    Males : float
    Females : float
    latitude_grid:float
    longitude_grid:float
    competitors:float
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
