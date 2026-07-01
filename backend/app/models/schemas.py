from pydantic import BaseModel
from typing import List, Optional, Any


class QueryRequest(BaseModel):
    queries: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "queries": [
                    'SELECT * FROM "empleados.csv" WHERE edad > 25',
                    'SELECT nombre, ciudad FROM "empleados.csv" ORDER BY nombre LIMIT 5',
                    'SELECT * FROM ""'           # ejemplo con error semántico
                ]
            }]
        }
    }


class SingleQueryResult(BaseModel):
    index: int
    query: str
    status: str                          # "ok" | "error"
    n_queries_parsed: int
    syntactic_errors: List[str]
    semantic_errors: List[str]
    total_errors: int
    data: Optional[List[Any]] = None     # lista de resultados por sub-query del bloque
    execution_error: Optional[str] = None


class BatchQueryResponse(BaseModel):
    total_submitted: int
    successful: int
    failed: int
    results: List[SingleQueryResult]