from fastapi import FastAPI, Query, Request
from typing import Optional, List
import os
from celery_worker import celery_app

app = FastAPI()

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


@app.get("/create_image_v2/")
def create_image(
    request: Request,
    template_url: str = Query('https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp', alias="template_url", description="URL of the template image"),
    image_url: str = Query('https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg', alias="image_url", description="URL of the image to be added"),
    result_file: Optional[str] = Query('test.png', alias="result_file", description="Name of the file to save the result. exemple: test.png"),
    x1: Optional[int] = Query(50, alias="x1", description="x coordinate 1 in %"),
    x2: Optional[int] = Query(None, alias="x2", description="x coordinate 2 in %"),
    x3: Optional[int] = Query(None, alias="x3", description="x coordinate 3 in %"),
    x4: Optional[int] = Query(None, alias="x4", description="x coordinate 4 in %"),
    x5: Optional[int] = Query(None, alias="x5", description="x coordinate 5 in %"),
    x6: Optional[int] = Query(None, alias="x6", description="x coordinate 6 in %"),
    x7: Optional[int] = Query(None, alias="x7", description="x coordinate 7 in %"),
    x8: Optional[int] = Query(None, alias="x8", description="x coordinate 8 in %"),
    x9: Optional[int] = Query(None, alias="x9", description="x coordinate 9 in %"),
    x10: Optional[int] = Query(None, alias="x10", description="x coordinate 10 in %"),
    y1: Optional[int] = Query(50, alias="y1", description="y coordinate 1 in %"),
    y2: Optional[int] = Query(None, alias="y2", description="y coordinate 2 in %"),
    y3: Optional[int] = Query(None, alias="y3", description="y coordinate 3 in %"),
    y4: Optional[int] = Query(None, alias="y4", description="y coordinate 4 in %"),
    y5: Optional[int] = Query(None, alias="y5", description="y coordinate 5 in %"),
    y6: Optional[int] = Query(None, alias="y6", description="y coordinate 6 in %"),
    y7: Optional[int] = Query(None, alias="y7", description="y coordinate 7 in %"),
    y8: Optional[int] = Query(None, alias="y8", description="y coordinate 8 in %"),
    y9: Optional[int] = Query(None, alias="y9", description="y coordinate 9 in %"),
    y10: Optional[int] = Query(None, alias="y10", description="y coordinate 10 in %"),
    r1: Optional[int] = Query(90, alias="r1", description="rotation 1 in angle (clockwise)"),
    r2: Optional[int] = Query(None, alias="r2", description="rotation 2 in angle (clockwise)"),
    r3: Optional[int] = Query(None, alias="r3", description="rotation 3 in angle (clockwise)"),
    r4: Optional[int] = Query(None, alias="r4", description="rotation 4 in angle (clockwise)"),
    r5: Optional[int] = Query(None, alias="r5", description="rotation 5 in angle (clockwise)"),
    r6: Optional[int] = Query(None, alias="r6", description="rotation 6 in angle (clockwise)"),
    r7: Optional[int] = Query(None, alias="r7", description="rotation 7 in angle (clockwise)"),
    r8: Optional[int] = Query(None, alias="r8", description="rotation 8 in angle (clockwise)"),
    r9: Optional[int] = Query(None, alias="r9", description="rotation 9 in angle (clockwise)"),
    r10: Optional[int] = Query(None, alias="r10", description="rotation 10 in angle (clockwise)"),
    w1: Optional[float] = Query(10, alias="w1", description="width 1 in %"),
    w2: Optional[float] = Query(None, alias="w2", description="width 2 in %"),
    w3: Optional[float] = Query(None, alias="w3", description="width 3 in %"),
    w4: Optional[float] = Query(None, alias="w4", description="width 4 in %"),
    w5: Optional[float] = Query(None, alias="w5", description="width 5 in %"),
    w6: Optional[float] = Query(None, alias="w6", description="width 6 in %"),
    w7: Optional[float] = Query(None, alias="w7", description="width 7 in %"),
    w8: Optional[float] = Query(None, alias="w8", description="width 8 in %"),
    w9: Optional[float] = Query(None, alias="w9", description="width 9 in %"),
    w10: Optional[float] = Query(None, alias="w10", description="width 10 in %"),
    c1: Optional[str] = Query('NB', alias="c1", description="filter 1"),
    c2: Optional[str] = Query(None, alias="c2", description="filter 2"),
    c3: Optional[str] = Query(None, alias="c3", description="filter 3"),
    c4: Optional[str] = Query(None, alias="c4", description="filter 4"),
    c5: Optional[str] = Query(None, alias="c5", description="filter 5"),
    c6: Optional[str] = Query(None, alias="c6", description="filter 6"),
    c7: Optional[str] = Query(None, alias="c7", description="filter 7"),
    c8: Optional[str] = Query(None, alias="c8", description="filter 8"),
    c9: Optional[str] = Query(None, alias="c9", description="filter 9"),
    c10: Optional[str] = Query(None, alias="c10", description="filter 10"),
    dh1: Optional[int] = Query(5, alias="dh1", description="% of height to cut at the top 1"),
    dh2: Optional[int] = Query(None, alias="dh2", description="% of height to cut at the top 2"),
    dh3: Optional[int] = Query(None, alias="dh3", description="% of height to cut at the top 3"),
    dh4: Optional[int] = Query(None, alias="dh4", description="% of height to cut at the top 4"),
    dh5: Optional[int] = Query(None, alias="dh5", description="% of height to cut at the top 5"),
    dh6: Optional[int] = Query(None, alias="dh6", description="% of height to cut at the top 6"),
    dh7: Optional[int] = Query(None, alias="dh7", description="% of height to cut at the top 7"),
    dh8: Optional[int] = Query(None, alias="dh8", description="% of height to cut at the top 8"),
    dh9: Optional[int] = Query(None, alias="dh9", description="% of height to cut at the top 9"),
    dh10: Optional[int] = Query(None, alias="dh10", description="% of height to cut at the top 10"),
    db1: Optional[int] = Query(5, alias="db1", description="% of height to cut at the bottom 1"),
    db2: Optional[int] = Query(None, alias="db2", description="% of height to cut at the bottom 2"),
    db3: Optional[int] = Query(None, alias="db3", description="% of height to cut at the bottom 3"),
    db4: Optional[int] = Query(None, alias="db4", description="% of height to cut at the bottom 4"),
    db5: Optional[int] = Query(None, alias="db5", description="% of height to cut at the bottom 5"),
    db6: Optional[int] = Query(None, alias="db6", description="% of height to cut at the bottom 6"),
    db7: Optional[int] = Query(None, alias="db7", description="% of height to cut at the bottom 7"),
    db8: Optional[int] = Query(None, alias="db8", description="% of height to cut at the bottom 8"),
    db9: Optional[int] = Query(None, alias="db9", description="% of height to cut at the bottom 9"),
    db10: Optional[int] = Query(None, alias="db10", description="% of height to cut at the bottom 10"),
    t1: Optional[str] = Query('text1', alias="t1", description="text 1"),
    t2: Optional[str] = Query('text2', alias="t2", description="text 2"),
    tf1: Optional[str] = Query('arial', alias="tf1", description="font 1"),
    tf2: Optional[str] = Query('tnr', alias="tf2", description="font 2"),
    tc1: Optional[str] = Query('black', alias="tc1", description="text color 1"),
    tc2: Optional[str] = Query('white', alias="tc2", description="text color 2"),
    tt1: Optional[int] = Query(10, alias="tt1", description="text size 1"),
    tt2: Optional[int] = Query(15, alias="tt2", description="text size 2"),
    tx1: Optional[int] = Query(5, alias="tx1", description="text x position 1"),
    tx2: Optional[int] = Query(50, alias="tx2", description="text x position 2"),
    ty1: Optional[int] = Query(5, alias="ty1", description="text y position 1"),
    ty2: Optional[int] = Query(5, alias="ty2", description="text y position 2")
):
    # Agréger les paramètres en listes
    xs = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10]
    ys = [y1, y2, y3, y4, y5, y6, y7, y8, y9, y10]
    rs = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
    ws = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10]
    cs = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]
    dhs = [dh1, dh2, dh3, dh4, dh5, dh6, dh7, dh8, dh9, dh10]
    dbs = [db1, db2, db3, db4, db5, db6, db7, db8, db9, db10]
    ts = [t1, t2]
    tfs = [tf1, tf2]
    tcs = [tc1, tc2]
    tts = [tt1, tt2]
    txs = [tx1, tx2]
    tys = [ty1, ty2]
    
    # Filtrer les valeurs None
    xs = [x for x in xs if x is not None]
    ys = [y for y in ys if y is not None]
    rs = [r for r in rs if r is not None]
    ws = [w for w in ws if w is not None]
    cs = [c for c in cs if c is not None]
    dhs = [dh for dh in dhs if dh is not None]
    dbs = [db for db in dbs if db is not None]
    ts = [t for t in ts if t is not None]
    tfs = [tf for tf in tfs if tf is not None]
    tcs = [tc for tc in tcs if tc is not None]
    tts = [tt for tt in tts if tt is not None]
    txs = [tx for tx in txs if tx is not None]
    tys = [ty for ty in tys if ty is not None]

    # Paramètres de la requête
    params = {
        "template_url": template_url,
        "image_url": image_url,
        "result_file": result_file,
        "xs": xs,
        "ys": ys,
        "rs": rs,
        "ws": ws,
        "cs": cs,
        "dhs": dhs,
        "dbs": dbs,
        "ts": ts,
        "tfs": tfs,
        "tcs": tcs,
        "tts": tts,
        "txs": txs,
        "tys": tys
    }



    # Appeler la tâche Celery
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
            os.getenv("FTP_PASSWORD"), 
            params
        ]
    )

    return {"message": "Image processing started", "task_id": task.id}