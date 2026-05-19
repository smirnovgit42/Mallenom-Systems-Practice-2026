import os
from datetime import datetime

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from PIL import Image

from database import SessionLocal
from database import engine

from models import Base
from models import ImageModel

from schemas import ImageResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image API")


IMAGE_FOLDER = "images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


# Подключение к БД

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# 1. Добавление изображения

@app.post("/api/image/add")
def add_image(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):

    file_path = os.path.join(
        IMAGE_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    image = Image.open(file_path)

    width, height = image.size

    file_size = os.path.getsize(file_path)

    image_data = ImageModel(
        name=file.filename,
        size=f"{file_size} bytes",
        width=width,
        height=height,
        type=file.content_type,
        created_at=str(datetime.now()),
        path=file_path
    )

    db.add(image_data)

    db.commit()

    db.refresh(image_data)

    return {
        "message": "Изображение успешно добавлено",
        "id": image_data.id
    }

# 2. Изменение размера изображения

@app.put("/api/image/change/size")
def resize_image(
        image_id: int,
        new_width: int,
        new_height: int,
        db: Session = Depends(get_db)
):

    image_record = db.query(ImageModel).filter(
        ImageModel.id == image_id
    ).first()

    if not image_record:
        raise HTTPException(
            status_code=404,
            detail="Изображение не найдено"
        )

    image = Image.open(image_record.path)

    resized_image = image.resize(
        (new_width, new_height)
    )

    resized_image.save(image_record.path)

    image_record.width = new_width
    image_record.height = new_height

    db.commit()

    return {
        "message": "Размер изображения изменен"
    }

# 3. Поворот изображения

@app.put("/api/image/change/rotate")
def rotate_image(
        image_id: int,
        angle: int,
        db: Session = Depends(get_db)
):

    image_record = db.query(ImageModel).filter(
        ImageModel.id == image_id
    ).first()

    if not image_record:
        raise HTTPException(
            status_code=404,
            detail="Изображение не найдено"
        )

    image = Image.open(image_record.path)

    rotated_image = image.rotate(angle)

    rotated_image.save(image_record.path)

    return {
        "message": "Изображение повернуто"
    }

# 4. Получить все изображения

@app.get(
    "/api/image",
    response_model=list[ImageResponse]
)
def get_images(
        db: Session = Depends(get_db)
):

    return db.query(ImageModel).all()