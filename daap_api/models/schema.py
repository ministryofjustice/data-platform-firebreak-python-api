from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str = Field(
        pattern=r"^[a-z0-9_]+$",
        description="The name of a column within your data.",
    )
    type: str = Field(
        pattern=r"^(u?(tiny|small|big|)int)|float|double|decimal\(\d{1,2},\s?\d{1,2}\)|char\(\d{1,3}\)|varchar\(\d{0,5}\)|varchar|string|boolean|date|timestamp$",
        description="The data type of the Column. See https://docs.aws.amazon.com/athena/latest/ug/data-types.html",
    )
    description: str = Field(
        description="A description of the column that will feed the data catalogue."
    )


class Schema(BaseModel):
    tableDescription: str = Field(
        description="A description of the data contained within the table",
        default="this table contains example data for an example data product.",
    )

    columns: list[Column] = Field(
        description="A list of objects which relate to columns in your data, each list item will contain, a name of the column, data type of the column and description of the column."
    )
