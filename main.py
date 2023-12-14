from fastapi import FastAPI, HTTPException, Query
from PIL import Image
import requests
from io import BytesIO
from typing import Optional
from starlette.responses import StreamingResponse

app = FastAPI()

def process_image(image_url, template, x, y, w):
    response = requests.get(image_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"URL {image_url} is not valid")

    try:
        image = Image.open(BytesIO(response.content))
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid image format")

    # Resize and place the image on the template
    image = image.resize((w, int(w * image.height / image.width)))
    template.paste(image, (x, y))
    return template


@app.get("/process-template/")
async def process_template(
    template_url: str = Query(..., alias="template_url"),
    image1_url: Optional[str] = Query(None, alias="image1_url"),
    image2_url: Optional[str] = Query(None, alias="image2_url"),
    image3_url: Optional[str] = Query(None, alias="image3_url"),
    image4_url: Optional[str] = Query(None, alias="image4_url"),
    image1_x: Optional[int] = Query(None, alias="image1x"),
    image1_y: Optional[int] = Query(None, alias="image1y"),
    image1_w: Optional[int] = Query(None, alias="image1w"),
    image2_x: Optional[int] = Query(None, alias="image2x"),
    image2_y: Optional[int] = Query(None, alias="image2y"),
    image2_w: Optional[int] = Query(None, alias="image2w"),
    image3_x: Optional[int] = Query(None, alias="image3x"),
    image3_y: Optional[int] = Query(None, alias="image3y"),
    image3_w: Optional[int] = Query(None, alias="image3w"),
    image4_x: Optional[int] = Query(None, alias="image4x"),
    image4_y: Optional[int] = Query(None, alias="image4y"),
    image4_w: Optional[int] = Query(None, alias="image4w"),
):
    # Télécharger le template
    response = requests.get(template_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Template URL is not valid")

    try:
        template = Image.open(BytesIO(response.content))
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid image format")

    # Process each image (example for image1)
    if image1_url:
        template = process_image(image1_url, template, image1_x, image1_y, image1_w)
    if image2_url:
        template = process_image(image2_url, template, image2_x, image2_y, image2_w)
    if image3_url:
        template = process_image(image3_url, template, image3_x, image3_y, image3_w)
    if image4_url:
        template = process_image(image4_url, template, image4_x, image4_y, image4_w)

    # Save or respond with the processed image
    img_byte_arr = BytesIO()
    template.save(img_byte_arr, format='PNG')  # Sauvegarde l'image traitée dans un buffer en mémoire
    img_byte_arr = img_byte_arr.getvalue()

    return StreamingResponse(BytesIO(img_byte_arr), media_type="image/png")

