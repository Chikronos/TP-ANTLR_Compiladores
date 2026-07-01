from fastapi import APIRouter, UploadFile, File, HTTPException

from ..models.schemas import QueryRequest, BatchQueryResponse, SingleQueryResult
from ..services.query_runner import run_single_query

router = APIRouter(prefix="/queries", tags=["Queries"])


def _process_batch(query_list: list[str]) -> BatchQueryResponse:
    results    = []
    successful = 0
    failed     = 0

    for i, raw_query in enumerate(query_list):
        query = raw_query.strip()
        try:
            result = run_single_query(query)
        except Exception as e:
            result = {
                "status": "error", "n_queries_parsed": 0,
                "syntactic_errors": [], "semantic_errors": [],
                "total_errors": 1, "data": None,
                "execution_error": f"Error interno: {e}",
            }

        if result["status"] == "ok":
            successful += 1
        else:
            failed += 1

        results.append(SingleQueryResult(index=i, query=query, **result))

    return BatchQueryResponse(
        total_submitted=len(query_list),
        successful=successful,
        failed=failed,
        results=results,
    )


@router.get("/health", summary="Health check")
def health():
    """Verifica que el servicio esté en línea."""
    return {"status": "online", "service": "QueryBit API"}


@router.post(
    "/run",
    response_model=BatchQueryResponse,
    summary="Ejecutar queries como lista de strings",
    description=(
        "Recibe una lista de queries QueryBit. Cada una se procesa de forma "
        "independiente — si una falla, las demás continúan. "
        "Retorna un array con el resultado de cada query."
    ),
)
def run_queries(body: QueryRequest):
    """
    **Body de ejemplo:**
```json
    {
      "queries": [
        "SELECT * FROM \\"empleados.csv\\" WHERE salario >= 3000",
        "SELECT nombre FROM \\"empleados.csv\\" ORDER BY nombre LIMIT 3",
        "SELECT * FROM \\"\\"",
        "SELECT nombre, nombre FROM \\"empleados.csv\\""
      ]
    }
```
    Las dos últimas tienen errores semánticos a propósito para probar la
    continuación del batch.
    """
    if not body.queries:
        raise HTTPException(status_code=400, detail="La lista de queries está vacía.")
    return _process_batch(body.queries)


@router.post(
    "/run-from-file",
    response_model=BatchQueryResponse,
    summary="Ejecutar queries desde archivo .txt",
    description=(
        "Sube un archivo `.txt` con una query QueryBit por línea. "
        "Las líneas vacías se ignoran automáticamente. "
        "Si una query falla, el procesamiento continúa con la siguiente."
    ),
)
async def run_from_file(
    file: UploadFile = File(..., description="Archivo .txt con queries, una por línea")
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .txt")

    content = await file.read()
    text    = content.decode("utf-8")
    queries = [line.strip() for line in text.splitlines() if line.strip()]

    if not queries:
        raise HTTPException(
            status_code=400, detail="El archivo no contiene queries válidas."
        )
    return _process_batch(queries)