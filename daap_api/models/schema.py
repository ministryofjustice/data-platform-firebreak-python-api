from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str
    type: str = Field(
        json_schema_extra={
            "pattern": r"^(u?(tiny|small|big|)int)|float|double|decimal\(\d{1,2},\s?\d{1,2}\)|char\(\d{1,3}\)|varchar\(\d{0,5}\)|varchar|string|boolean|date|timestamp$",
            "description": "The data type of the Column. See https://docs.aws.amazon.com/athena/latest/ug/data-types.html",
        }
    )
    description: str


class Schema(BaseModel):
    tableDescription: str
    columns: list[Column]
