from fastapi import FastAPI, Query, Request, HTTPException
from typing import Optional, List, Dict, Any
import os
from celery_worker import celery_app
import re

app = FastAPI()

def parse_dynamic_params(request: Request) -> Dict[str, List[Any]]:
    params = request.query_params
    dynamic_params = {}

    for key, value in params.items():
        match = re.match(r"([a-z]+)(\d+)", key)
        if match:
            param_name, index = match.groups()
            if param_name not in dynamic_params:
                dynamic_params[param_name] = []
            dynamic_params[param_name].append(value)

    return dynamic_params

@app.get("/create_image/")
def create_image(
    request: Request,
    template_url: str = Query('https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp', alias="template_url", description="URL of the template image"),
    image_url: str = Query('https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg', alias="image_url", description="URL of the image to be added"),
    result_file: Optional[str] = Query('test.png', alias="result_file", description="Name of the file to save the result"),
    xs: List[Optional[int]] = Query([5], alias="xs", description="List of x coordinates in %"),
    ys: List[Optional[int]] = Query([5], alias="ys", description="List of y coordinates in %"),
    rs: List[Optional[int]] = Query([90], alias="rs", description="List of rotations in angle (clockwise)"),
    ws: List[Optional[float]] = Query([10], alias="ws", description="List of widths in %"),
    cs: List[Optional[str]] = Query(['string'], alias="cs", description="List of filters to apply"),
    dhs: List[Optional[int]] = Query([10], alias="dhs", description="List of % of height to cut at the top"),
    dbs: List[Optional[int]] = Query([5], alias="dbs", description="List of % of height to cut at the bottom"),
    ts: List[Optional[str]] = Query(['test'], alias="ts", description="List of texts to write"),
    tfs: List[Optional[str]] = Query(['arial'], alias="tfs", description="List of fonts (e.g., arial, tnr)"),
    tcs: List[Optional[str]] = Query(['black'], alias="tcs", description="List of text colors (e.g., black, white)"),
    tts: List[Optional[int]] = Query([10], alias="tts", description="List of font sizes"),
    txs: List[Optional[int]] = Query([3], alias="txs", description="List of absolute x positions"),
    tys: List[Optional[int]] = Query([3], alias="tys", description="List of absolute y positions")
):
    # Parse dynamic parameters
    dynamic_params = parse_dynamic_params(request)
    
    # Extract dynamic coordinates and other parameters if they exist
    dynamic_xs = list(map(int, dynamic_params.get('x', [])))
    dynamic_ys = list(map(int, dynamic_params.get('y', [])))
    dynamic_rs = list(map(int, dynamic_params.get('r', [])))
    dynamic_ws = list(map(float, dynamic_params.get('w', [])))
    dynamic_cs = dynamic_params.get('c', [])
    dynamic_dhs = list(map(int, dynamic_params.get('dh', [])))
    dynamic_dbs = list(map(int, dynamic_params.get('db', [])))
    dynamic_ts = dynamic_params.get('t', [])
    dynamic_tfs = dynamic_params.get('tf', [])
    dynamic_tcs = dynamic_params.get('tc', [])
    dynamic_tts = list(map(int, dynamic_params.get('tt', [])))
    dynamic_txs = list(map(int, dynamic_params.get('tx', [])))
    dynamic_tys = list(map(int, dynamic_params.get('ty', [])))

    # Merge fixed and dynamic parameters without duplicates
    xs.extend([x for x in dynamic_xs if x not in xs])
    ys.extend([y for y in dynamic_ys if y not in ys])
    rs.extend([r for r in dynamic_rs if r not in rs])
    ws.extend([w for w in dynamic_ws if w not in ws])
    cs.extend([c for c in dynamic_cs if c not in cs])
    dhs.extend([dh for dh in dynamic_dhs if dh not in dhs])
    dbs.extend([db for db in dynamic_dbs if db not in dbs])
    ts.extend([t for t in dynamic_ts if t not in ts])
    tfs.extend([tf for tf in dynamic_tfs if tf not in tfs])
    tcs.extend([tc for tc in dynamic_tcs if tc not in tcs])
    tts.extend([tt for tt in dynamic_tts if tt not in tts])
    txs.extend([tx for tx in dynamic_txs if tx not in txs])
    tys.extend([ty for ty in dynamic_tys if ty not in tys])

    # Ensure consistent list lengths by filling missing values if necessary
    max_length = max(len(xs), len(ys), len(rs), len(ws), len(cs), len(dhs), len(dbs), len(ts), len(tfs), len(tcs), len(tts), len(txs), len(tys))
    
    def fill_list(lst, default_value, length):
        return lst + [default_value] * (length - len(lst))
    
    xs = fill_list(xs, 0, max_length)
    ys = fill_list(ys, 0, max_length)
    rs = fill_list(rs, 0, max_length)
    ws = fill_list(ws, 0.0, max_length)
    cs = fill_list(cs, '', max_length)
    dhs = fill_list(dhs, 0, max_length)
    dbs = fill_list(dbs, 0, max_length)
    ts = fill_list(ts, '', max_length)
    tfs = fill_list(tfs, '', max_length)
    tcs = fill_list(tcs, '', max_length)
    tts = fill_list(tts, 0, max_length)
    txs = fill_list(txs, 0, max_length)
    tys = fill_list(tys, 0, max_length)
    
    # Call the Celery task
    task = celery_app.send_task(
        "tasks.process_and_upload_task",
        args=[
            template_url,
            image_url,
            result_file,
            xs,
            ys,
            rs,
            ws,
            cs,
            dhs,
            dbs,
            ts,
            tfs,
            tcs,
            tts,
            txs,
            tys,
            os.getenv("FTP_HOST"), 
            os.getenv("FTP_USERNAME"), 
            os.getenv("FTP_PASSWORD")
        ]
    )

    return {"message": "Image processing started", "task_id": task.id}
