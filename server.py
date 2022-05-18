import asyncio
from base64 import b64encode
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional, Union
from zipfile import is_zipfile

from fastapi import FastAPI, HTTPException, UploadFile
from patoolib import extract_archive
from patoolib.util import PatoolError

app = FastAPI()

ROOT_DIR = Path(__file__).absolute().parent
UPLOAD_DIR = ROOT_DIR / "uploads"
FLAG_PATH = ROOT_DIR / "flag.txt"

if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir()

if not FLAG_PATH.exists() and "FLAG" in os.environ:
    FLAG_PATH.write_text(os.environ["FLAG"])


@app.get("/")
async def root():
    return {"flag": os.environ.get("FLAG")}


def read_files(directory: Union[str, Path]) -> Dict[str, Union[Optional[str], Dict[str, Any]]]:
    if not isinstance(directory, Path):
        directory = Path(directory)
    contents: Dict[str, Union[Optional[str], Dict[str, Any]]] = {}
    for path in directory.iterdir():
        if path.is_dir():
            contents[path.name] = read_files(path)
        else:
            try:
                content = path.read_bytes()
                try:
                    contents[path.name] = content.decode("utf-8")
                except UnicodeDecodeError:
                    contents[path.name] = b64encode(content).decode("utf-8")
            except IOError:
                contents[path.name] = None
    return contents


@app.post("/extract")
async def extract(file: UploadFile):
    with TemporaryDirectory(dir=UPLOAD_DIR) as tmpdir:
        file_to_extract = Path(tmpdir) / file.filename
        with open(file_to_extract, "wb") as f:
            while True:
                data = await file.read(2048)
                if not data:
                    break
                f.write(data)
        # make sure the file is a valid zip because Python's zipfile doesn't support symlinks (no hacking!)
        if not is_zipfile(file_to_extract):
            raise HTTPException(status_code=415, detail=f"The input file must be an ZIP archive.")
        with TemporaryDirectory(dir=tmpdir) as extract_to_dir:
            try:
                extract_archive(str(file_to_extract), outdir=extract_to_dir)
            except PatoolError as e:
                raise HTTPException(status_code=400, detail=f"Error extracting ZIP {file_to_extract.name}: {e!s}")
            return read_files(extract_to_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host='0.0.0.0', port=8080, reload=True, debug=True, workers=3)
