import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..config import DATA_DIR

router = APIRouter(prefix="/data", tags=["Data"])


@router.post(
    "/upload-csv",
    summary="Subir un CSV al servidor",
    description=(
        "Sube un archivo `.csv` al directorio `backend/data/`. "
        "Una vez subido, refiérelo en tus queries con "
        "`FROM \"nombre-del-archivo.csv\"`."
    ),
)
async def upload_csv(
    file: UploadFile = File(..., description="Archivo CSV a subir")
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .csv")

    dest = os.path.join(DATA_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "message": f"'{file.filename}' subido correctamente.",
        "uso_en_query": f'FROM "{file.filename}"',
    }


@router.get("/list-csv", summary="Listar CSVs disponibles")
def list_csvs():
    """Lista los CSVs que el servidor puede usar en queries."""
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return {"csv_files": files, "count": len(files)}