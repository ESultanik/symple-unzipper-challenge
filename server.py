import os
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI, HTTPException, UploadFile
from pyunpack import Archive, PatoolError

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


def read_files(directory: Union[str, Path]) -> Dict[str, Union[Optional[bytes], Dict[str, Any]]]:
    if not isinstance(directory, Path):
        directory = Path(directory)
    contents: Dict[str, Union[Optional[bytes], Dict[str, Any]]] = {}
    for path in directory.iterdir():
        if path.is_dir():
            contents[path.name] = read_files(path)
        else:
            try:
                contents[path.name] = path.read_bytes()
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
        # make sure the file is a zip because patool does not extract symlinks from zip (no hacking!)
        if not zipfile.is_zipfile(file_to_extract):
            raise HTTPException(status_code=415, detail="The input file must be a zip")
        with TemporaryDirectory(dir=tmpdir) as extract_to_dir:
            try:
                Archive(str(file_to_extract)).extractall_patool(extract_to_dir, None)
            except PatoolError as e:
                raise HTTPException(status_code=400, detail=f"Error extracting ZIP {file_to_extract.name}: {e!s}")
            return read_files(extract_to_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host='0.0.0.0', port=8080, reload=True, debug=True, workers=3)
