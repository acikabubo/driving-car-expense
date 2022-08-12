from datetime import time
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request})


@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    petrol_price: float = Form(),
    consumption: float = Form(),
    start_odometer: Optional[int] = Form(None),
    arrive_odometer: int = Form(),
    driven_km: Optional[float] = Form(None),
    driven_time: time = Form(),
    arrive_dt: datetime = Form()
):
    if start_odometer is None and driven_km is None:
        return templates.TemplateResponse(
            "missing_fields.html", {"request": request}
        )

    if driven_km:
        start_odometer = arrive_odometer - driven_km

    start_dt = arrive_dt - timedelta(
        hours=driven_time.hour,
        minutes=driven_time.minute,
    )
    start_dt = start_dt.strftime("%d.%m.%Y %H:%M")

    distance = arrive_odometer - start_odometer
    trip_consumption = round((distance * consumption) / 100, 1)
    cost = round(trip_consumption * petrol_price)

    return templates.TemplateResponse(
        "calculations.html", {
            "request": request,
            "consumption": consumption,
            "trip_consumption": trip_consumption,
            "petrol_price": petrol_price,
            "cost": cost,
            "start_dt": start_dt
        }
    )
