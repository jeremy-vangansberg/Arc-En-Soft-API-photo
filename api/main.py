from fastapi import FastAPI, HTTPException, Query, Request
from typing import Optional, List
import os
from celery_worker import celery_app

app = FastAPI()

def get_parameters(request: Request, prefix: str) -> List:
    params = []
    for i in range(1, 100):  # Suppose un maximum de 100 paramètres par type
        param = request.query_params.get(f"{prefix}{i}")
        if param is not None:
            params.append(param)
        else:
            break
    return params

@app.get("/create_image/")
def create_image(
    request: Request,
    template_url: str = Query('https://edit.org/img/blog/ate-preschool-yearbook-templates-free-editable.webp', alias="template_url", description="URL of the template image"),
    image_url: str = Query('https://www.photosscolaire.com/wp-content/uploads/2023/05/03-0285-0086-scaled.jpg', alias="image_url", description="URL of the image to be added"),
    result_file: Optional[str] = Query('test.png', alias="result_file", description="Name of the file to save the result. exemple: test.png"),
    xs: List[Optional[int]] = Query([], alias="xs", description="Liste des coordonnées x en %"),
    ys: List[Optional[int]] = Query([], alias="ys", description="Liste des coordonnées y en %"),
    rs: List[Optional[int]] = Query([], alias="rs", description="Liste des rotations en angle. (clockwise) ex: 90 ou -90"),
    ws: List[Optional[float]] = Query([], alias="ws", description="Liste des largeurs en %"),
    cs: List[Optional[str]] = Query([], alias="cs", description="Liste des filtres à appliquer. ex: NB"),
    dhs: List[Optional[int]] = Query([], alias="dhs", description="Liste des % de hauteur à couper en haut"),
    dbs: List[Optional[int]] = Query([], alias="dbs", description="Liste des % de hauteur à couper en bas"),
    ts: List[Optional[str]] = Query([], alias="ts", description="Liste des textes à écrire"),
    tfs: List[Optional[str]] = Query([], alias="tfs", description="Liste des polices. ex: arial, tnr"),
    tcs: List[Optional[str]] = Query([], alias="tcs", description="Liste des couleurs du texte. ex: black, white"),
    tts: List[Optional[int]] = Query([], alias="tts", description="Liste des tailles de la police"),
    txs: List[Optional[int]] = Query([], alias="txs", description="Liste des positions x absolues"),
    tys: List[Optional[int]] = Query([], alias="tys", description="Liste des positions y absolues")
):
    # Extraire les paramètres dynamiques
    dynamic_xs = get_parameters(request, 'x')
    dynamic_ys = get_parameters(request, 'y')
    dynamic_rs = get_parameters(request, 'r')
    dynamic_ws = get_parameters(request, 'w')
    dynamic_cs = get_parameters(request, 'c')
    dynamic_dhs = get_parameters(request, 'dh')
    dynamic_dbs = get_parameters(request, 'db')
    dynamic_ts = get_parameters(request, 't')
    dynamic_tfs = get_parameters(request, 'tf')
    dynamic_tcs = get_parameters(request, 'tc')
    dynamic_tts = get_parameters(request, 'tt')
    dynamic_txs = get_parameters(request, 'tx')
    dynamic_tys = get_parameters(request, 'ty')

    # Combine les paramètres fixes et dynamiques
    xs.extend(dynamic_xs)
    ys.extend(dynamic_ys)
    rs.extend(dynamic_rs)
    ws.extend(dynamic_ws)
    cs.extend(dynamic_cs)
    dhs.extend(dynamic_dhs)
    dbs.extend(dynamic_dbs)
    ts.extend(dynamic_ts)
    tfs.extend(dynamic_tfs)
    tcs.extend(dynamic_tcs)
    tts.extend(dynamic_tts)
    txs.extend(dynamic_txs)
    tys.extend(dynamic_tys)

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
            os.getenv("FTP_PASSWORD")
        ]
    )
    return {"message": "Image processed successfully", "task_id": task.id}
