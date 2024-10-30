from fastapi import FastAPI, Query, Request
from typing import Optional, List
import os
from celery_worker import celery_app

app = FastAPI()

@app.get("/create_image/")
def create_image(
    request: Request,
    ftp_host : str = Query('ftp.pdgw1190.odns.fr',
        alias="ftp_host",
        description="FTP url"),
    template_url: str = Query(
        'https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp',
        alias="template_url",
        description="URL of the template image. Example: 'https://example.com/template.jpg'"
    ),
    image_url: str = Query(
        'https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg',
        alias="image_url",
        description="URL of the image to be added. Example: 'https://example.com/image.jpg'"
    ),
    result_file: Optional[str] = Query(
        'test.png',
        alias="result_file",
        description="Name of the file to save the result. Example: 'result.png'"
    ),
    result_w: Optional[int] = Query(None, alias="result_w", description="width of result image"),
    x1: Optional[int] = Query(0, alias="x1", description="x coordinate 1 in %. Example: 50"),
    y1: Optional[int] = Query(0, alias="y1", description="y coordinate 1 in %. Example: 50"),
    r1: Optional[int] = Query(None, alias="r1", description="Rotation 1 in angle (clockwise). Example: 90"),
    w1: Optional[float] = Query(None, alias="w1", description="Width 1 in %. Example: 10.0"),
    c1: Optional[str] = Query(None, alias="c1", description="Filter 1. Example: 'NB'"),
    db1: Optional[int] = Query(None, alias="db1", description="% of height to cut at the bottom 1. Example: 5"),
    dh1: Optional[int] = Query(None, alias="dh1", description="% of height to cut at the top 1. Example: 5"),
    x2: Optional[int] = Query(None, alias="x2", description="x coordinate 2 in %. Example: 20"),
    y2: Optional[int] = Query(None, alias="y2", description="y coordinate 2 in %. Example: 20"),
    r2: Optional[int] = Query(None, alias="r2", description="Rotation 2 in angle (clockwise). Example: 45"),
    w2: Optional[float] = Query(None, alias="w2", description="Width 2 in %. Example: 20.0"),
    c2: Optional[str] = Query(None, alias="c2", description="Filter 2. Example: 'sepia'"),
    db2: Optional[int] = Query(None, alias="db2", description="% of height to cut at the bottom 2. Example: 10"),
    dh2: Optional[int] = Query(None, alias="dh2", description="% of height to cut at the top 2. Example: 10"),
    x3: Optional[int] = Query(None, alias="x3", description="x coordinate 3 in %. Example: 30"),
    y3: Optional[int] = Query(None, alias="y3", description="y coordinate 3 in %. Example: 30"),
    r3: Optional[int] = Query(None, alias="r3", description="Rotation 3 in angle (clockwise). Example: 30"),
    w3: Optional[float] = Query(None, alias="w3", description="Width 3 in %. Example: 30.0"),
    c3: Optional[str] = Query(None, alias="c3", description="Filter 3. Example: 'blur'"),
    db3: Optional[int] = Query(None, alias="db3", description="% of height to cut at the bottom 3. Example: 15"),
    dh3: Optional[int] = Query(None, alias="dh3", description="% of height to cut at the top 3. Example: 15"),
    x4: Optional[int] = Query(None, alias="x4", description="x coordinate 4 in %. Example: 40"),
    y4: Optional[int] = Query(None, alias="y4", description="y coordinate 4 in %. Example: 40"),
    r4: Optional[int] = Query(None, alias="r4", description="Rotation 4 in angle (clockwise). Example: 15"),
    w4: Optional[float] = Query(None, alias="w4", description="Width 4 in %. Example: 40.0"),
    c4: Optional[str] = Query(None, alias="c4", description="Filter 4. Example: 'sharpen'"),
    db4: Optional[int] = Query(None, alias="db4", description="% of height to cut at the bottom 4. Example: 20"),
    dh4: Optional[int] = Query(None, alias="dh4", description="% of height to cut at the top 4. Example: 20"),
    x5: Optional[int] = Query(None, alias="x5", description="x coordinate 5 in %. Example: 50"),
    y5: Optional[int] = Query(None, alias="y5", description="y coordinate 5 in %. Example: 50"),
    r5: Optional[int] = Query(None, alias="r5", description="Rotation 5 in angle (clockwise). Example: 60"),
    w5: Optional[float] = Query(None, alias="w5", description="Width 5 in %. Example: 50.0"),
    c5: Optional[str] = Query(None, alias="c5", description="Filter 5. Example: 'contrast'"),
    db5: Optional[int] = Query(None, alias="db5", description="% of height to cut at the bottom 5. Example: 25"),
    dh5: Optional[int] = Query(None, alias="dh5", description="% of height to cut at the top 5. Example: 25"),
    x6: Optional[int] = Query(None, alias="x6", description="x coordinate 6 in %. Example: 60"),
    y6: Optional[int] = Query(None, alias="y6", description="y coordinate 6 in %. Example: 60"),
    r6: Optional[int] = Query(None, alias="r6", description="Rotation 6 in angle (clockwise). Example: 75"),
    w6: Optional[float] = Query(None, alias="w6", description="Width 6 in %. Example: 60.0"),
    c6: Optional[str] = Query(None, alias="c6", description="Filter 6. Example: 'brightness'"),
    db6: Optional[int] = Query(None, alias="db6", description="% of height to cut at the bottom 6. Example: 30"),
    dh6: Optional[int] = Query(None, alias="dh6", description="% of height to cut at the top 6. Example: 30"),
    x7: Optional[int] = Query(None, alias="x7", description="x coordinate 7 in %. Example: 70"),
    y7: Optional[int] = Query(None, alias="y7", description="y coordinate 7 in %. Example: 70"),
    r7: Optional[int] = Query(None, alias="r7", description="Rotation 7 in angle (clockwise). Example: 120"),
    w7: Optional[float] = Query(None, alias="w7", description="Width 7 in %. Example: 70.0"),
    c7: Optional[str] = Query(None, alias="c7", description="Filter 7. Example: 'grayscale'"),
    db7: Optional[int] = Query(None, alias="db7", description="% of height to cut at the bottom 7. Example: 35"),
    dh7: Optional[int] = Query(None, alias="dh7", description="% of height to cut at the top 7. Example: 35"),
    x8: Optional[int] = Query(None, alias="x8", description="x coordinate 8 in %. Example: 80"),
    y8: Optional[int] = Query(None, alias="y8", description="y coordinate 8 in %. Example: 80"),
    r8: Optional[int] = Query(None, alias="r8", description="Rotation 8 in angle (clockwise). Example: 135"),
    w8: Optional[float] = Query(None, alias="w8", description="Width 8 in %. Example: 80.0"),
    c8: Optional[str] = Query(None, alias="c8", description="Filter 8. Example: 'invert'"),
    db8: Optional[int] = Query(None, alias="db8", description="% of height to cut at the bottom 8. Example: 40"),
    dh8: Optional[int] = Query(None, alias="dh8", description="% of height to cut at the top 8. Example: 40"),
    x9: Optional[int] = Query(None, alias="x9", description="x coordinate 9 in %. Example: 90"),
    y9: Optional[int] = Query(None, alias="y9", description="y coordinate 9 in %. Example: 90"),
    r9: Optional[int] = Query(None, alias="r9", description="Rotation 9 in angle (clockwise). Example: 150"),
    w9: Optional[float] = Query(None, alias="w9", description="Width 9 in %. Example: 90.0"),
    c9: Optional[str] = Query(None, alias="c9", description="Filter 9. Example: 'edge_enhance'"),
    db9: Optional[int] = Query(None, alias="db9", description="% of height to cut at the bottom 9. Example: 45"),
    dh9: Optional[int] = Query(None, alias="dh9", description="% of height to cut at the top 9. Example: 45"),
    x10: Optional[int] = Query(None, alias="x10", description="x coordinate 10 in %. Example: 100"),
    y10: Optional[int] = Query(None, alias="y10", description="y coordinate 10 in %. Example: 100"),
    r10: Optional[int] = Query(None, alias="r10", description="Rotation 10 in angle (clockwise). Example: 180"),
    w10: Optional[float] = Query(None, alias="w10", description="Width 10 in %. Example: 100.0"),
    c10: Optional[str] = Query(None, alias="c10", description="Filter 10. Example: 'emboss'"),
    db10: Optional[int] = Query(None, alias="db10", description="% of height to cut at the bottom 10. Example: 50"),
    dh10: Optional[int] = Query(None, alias="dh10", description="% of height to cut at the top 10. Example: 50"),
    t1: Optional[str] = Query(None, alias="t1", description="Text 1. Example: 'Hello World'"),
    tx1: Optional[int] = Query(1, alias="tx1", description="Text x position 1 in %. Example: 5"),
    ty1: Optional[int] = Query(96, alias="ty1", description="Text y position 1 in %. Example: 5"),
    tf1: Optional[str] = Query('arial', alias="tf1", description="Font 1. Example: 'arial'"),
    tc1: Optional[str] = Query('000000', alias="tc1", description="Text color 1. Hex format. Example: '000000'"),
    tt1: Optional[int] = Query(10, alias="tt1", description="Text size 1. Example: 10"),
    t2: Optional[str] = Query(None, alias="t2", description="Text 2. Example: 'Bonjour le monde'"),
    tf2: Optional[str] = Query('arial', alias="tf2", description="Font 2. Example: 'times new roman'"),
    tc2: Optional[str] = Query('000000', alias="tc2", description="Text color 2. Hex format. Example: 'FFFFFF'"),
    tt2: Optional[int] = Query(10, alias="tt2", description="Text size 2. Example: 15"),
    tx2: Optional[int] = Query(50, alias="tx2", description="Text x position 2 in %. Example: 50"),
    ty2: Optional[int] = Query(96, alias="ty2", description="Text y position 2 in %. Example: 5")
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
        "result_w":result_w,
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
            result_w,
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
            ftp_host, 
            os.getenv("FTP_USERNAME"), 
            os.getenv("FTP_PASSWORD"), 
            params
        ]
    )

    return {"message": "Image processing started", "task_id": task.id}


@app.post("/intercalaire/")
def create_intercalaire(
    request: Request,
    result_file: Optional[str] = Query(
        'exemple/test.png',
        alias="result_file",
        description="Name of the file to save the result. Example: 'result.png'"
    ),
    ftp_host : str = Query('ftp.pdgw1190.odns.fr',
        alias="ftp_host",
        description="FTP url"),
    background_color: str = Query(
        'FFFFFF',
        alias="background_color",
        description="Background color in hex format. Example: 'FFFFFF' for white"
    ),
    width: int = Query(
        800,
        alias="width",
        description="Width of the image in pixels. Example: 800"
    ),
    height: int = Query(
        600,
        alias="height",
        description="Height of the image in pixels. Example: 600"
    ),
    text1: Optional[str] = Query(
        'Première ligne \<br>Deuxième ligne',
        alias="text1",
        description="Text for the first block. Example: 'Première ligne \<br>Deuxième ligne'"
    ),
    x1: Optional[int] = Query(
        10,
        alias="x1",
        description="x coordinate for the first text block in percentage of the image width. Example: 10"
    ),
    y1: Optional[int] = Query(
        10,
        alias="y1",
        description="y coordinate for the first text block in percentage of the image height. Example: 10"
    ),
    font_size1: Optional[int] = Query(
        20,
        alias="font_size1",
        description="Font size for the first text block. Example: 20"
    ),
    color1: Optional[str] = Query(
        '000000',
        alias="color1",
        description="Color for the first text block in hex format. Example: '000000' for black"
    ),
    font_name1: Optional[str] = Query(
        'arial',
        alias="font_name1",
        description="Font name for the first text block. Example: 'arial'"
    ),
    align1: Optional[str] = Query(
        'left',
        alias="align1",
        description="Alignment for the first text block. Example: 'left'"
    ),
    text2: Optional[str] = Query(
        None,
        alias="Première ligne <br>Deuxième ligne"
    ),
    x2: Optional[int] = Query(
        20,
        alias="x2"
    ),
    y2: Optional[int] = Query(
        20,
        alias="y2"
    ),
    font_size2: Optional[int] = Query(
        20,
        alias="font_size2"
    ),
    color2: Optional[str] = Query(
        '000000',
        alias="color2"
    ),
    font_name2: Optional[str] = Query(
        'arial',
        alias="font_name2"
    ),
    align2: Optional[str] = Query(
        'left',
        alias="align2"
    ),
    text3: Optional[str] = Query(
        None,
        alias="text3"
    ),
    x3: Optional[int] = Query(
        30,
        alias="x3",
    ),
    y3: Optional[int] = Query(
        30,
        alias="y3",
    ),
    font_size3: Optional[int] = Query(
        20,
        alias="font_size3",
    ),
    color3: Optional[str] = Query(
        '000000',
        alias="color3",
    ),
    font_name3: Optional[str] = Query(
        'arial',
        alias="font_name3",
    ),
    align3: Optional[str] = Query(
        'left',
        alias="align3",
    ),
    text4: Optional[str] = Query(
        None,
        alias="text4",
    ),
    x4: Optional[int] = Query(
        40,
        alias="x4",
    ),
    y4: Optional[int] = Query(
        40,
        alias="y4",
    ),
    font_size4: Optional[int] = Query(
        20,
        alias="font_size4",
    ),
    color4: Optional[str] = Query(
        '000000',
        alias="color4",
    ),
    font_name4: Optional[str] = Query(
        'arial',
        alias="font_name4",
    ),
    align4: Optional[str] = Query(
        'left',
        alias="align4",
    ),
    text5: Optional[str] = Query(
        None,
        alias="text5",
    ),
    x5: Optional[int] = Query(
        50,
        alias="x5",
    ),
    y5: Optional[int] = Query(
        50,
        alias="y5",
    ),
    font_size5: Optional[int] = Query(
        20,
        alias="font_size5",
    ),
    color5: Optional[str] = Query(
        '000000',
        alias="color5",
    ),
    font_name5: Optional[str] = Query(
        'arial',
        alias="font_name5",
    ),
    align5: Optional[str] = Query(
        'left',
        alias="align5",
    )
):

    text_blocks = []
    for i in range(1, 6):
        text = locals().get(f"text{i}")
        if text:
            text_blocks.append({
                "text": text,
                "x": locals().get(f"x{i}"),
                "y": locals().get(f"y{i}"),
                "font_size": locals().get(f"font_size{i}"),
                "color": locals().get(f"color{i}"),
                "font_name": locals().get(f"font_name{i}"),
                "align": locals().get(f"align{i}")
            })

    # Call the Celery task
    task = celery_app.send_task(
        "tasks.process_intercalaire_task",
        args=[
            result_file,
            background_color,
            width,
            height,
            text_blocks,
            ftp_host,
            os.getenv("FTP_USERNAME"),
            os.getenv("FTP_PASSWORD")
        ]
    )

    return {"message": "Intercalaire processing started", "task_id": task.id}