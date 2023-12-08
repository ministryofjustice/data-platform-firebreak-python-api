from pydantic import BaseModel


class DataProduct(BaseModel):
    name: str
    description: str
    domain: str
    dataProductOwner: str
    dataProductOwnerDisplayName: str
    email: str
    status: str
    retentionPeriod: int
    dpiaRequired: bool
    schemas: list[str]


class DataProductInput(BaseModel):
    name: str
    description: str
    domain: str
    dataProductOwner: str
    dataProductOwnerDisplayName: str
    email: str
    status: str
    retentionPeriod: int
    dpiaRequired: bool
