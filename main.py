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
    f = open("petrol_price.txt", 'r')
    petrol_price = float(f.read() or 0)

    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "petrol_price": petrol_price
        }
    )


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
    err_msg = ""

    if (start_odometer is None and driven_km is None) or (
            start_odometer is not None and driven_km is not None):

        err_msg = "Required 'start_odometer' or 'driven_km'"

    if driven_km:
        start_odometer = arrive_odometer - driven_km

    if arrive_odometer < start_odometer:
        err_msg = f"'arrive_odometer' must be greated then {start_odometer}"

    if err_msg != "":
        return templates.TemplateResponse(
            "missing_fields.html", {
                "request": request,
                "err_msg": err_msg
            }
        )

    start_dt = arrive_dt - timedelta(
        hours=driven_time.hour,
        minutes=driven_time.minute,
    )
    start_dt = start_dt.strftime("%d.%m.%Y %H:%M")

    distance = arrive_odometer - start_odometer
    trip_consumption = round((distance * consumption) / 100, 1)
    cost = round(trip_consumption * petrol_price)
    cost_by_km = round((cost / distance), 2)

    f = open("petrol_price.txt", 'w')
    f.write(str(petrol_price))
    f.close()

    return templates.TemplateResponse(
        "calculations.html", {
            "request": request,
            "consumption": consumption,
            "trip_consumption": trip_consumption,
            "petrol_price": petrol_price,
            "cost": cost,
            "start_dt": start_dt,
            "cost_by_km": cost_by_km
        }
    )
