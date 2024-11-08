from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    class Config:
        from_attributes = True


class User(BaseModel, table=True):  # 'table=True' makes this a database table
    id: int = Field(default=None, primary_key=True)  # Primary key
    name: str = Field(index=True)  # Indexed column
    email: str = Field(unique=True)  # Unique constraint

    # This column will not be indexed or have a unique constraint
    age: int = Field(default=0)
