from datetime import time
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, validator, root_validator
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "missing_fields.html", {
            "request": request,
            "err_msg": exc.detail
        }
    )


class DCEData(BaseModel):
    petrol_price: float
    consumption: float
    start_odometer: Optional[int]
    arrive_odometer: int
    driven_km: Optional[float]
    driven_time: time
    arrive_dt: datetime

    # TODO: Check this validator (Pydantic required fields???)
    @validator('start_odometer', 'driven_km', pre=True)
    def change_type(cls, v):
        return v or None

    @root_validator
    def check(cls, values):
        if (
            values['start_odometer'] == values['driven_km']
        ) or (
            None not in [values['start_odometer'], values['driven_km']]
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Required 'start_odometer' or 'driven_km'"
            )

        if values['driven_km']:
            values['start_odometer'] = \
                values['arrive_odometer'] - values.pop('driven_km')

        if values['arrive_odometer'] < values['start_odometer']:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                (
                    "'arrive_odometer' must be greated "
                    f"then {values['start_odometer']}"
                )
            )

        return values


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
async def calculate(request: Request):
    form_data = await request.form()

    data = DCEData(**form_data)

    start_dt = data.arrive_dt - timedelta(
        hours=data.driven_time.hour,
        minutes=data.driven_time.minute,
    )
    start_dt = start_dt.strftime("%d.%m.%Y %H:%M")

    distance = data.arrive_odometer - data.start_odometer
    trip_consumption = round((distance * data.consumption) / 100, 1)
    cost = round(trip_consumption * data.petrol_price)
    cost_by_km = round((cost / distance), 2)

    # Save petrol price to file. Its useful for next calculation
    f = open("petrol_price.txt", 'w')
    f.write(str(data.petrol_price))
    f.close()

    return templates.TemplateResponse(
        "calculations.html", {
            "request": request,
            "consumption": data.consumption,
            "trip_consumption": trip_consumption,
            "petrol_price": data.petrol_price,
            "cost": cost,
            "start_dt": start_dt,
            "cost_by_km": cost_by_km
        }
    )
