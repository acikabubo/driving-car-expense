from datetime import datetime, time
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request})


@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    petrol_price: int = Form(),
    consumption: int = Form(),
    start_time: datetime = Form(),
    start_odometer: int = Form(),
    arrive_time: datetime = Form(),
    arrive_odometer: int = Form()
):
    print()
    print(petrol_price)
    print(consumption)
    print(start_time)
    print(start_odometer)
    print(arrive_time)
    print(arrive_odometer)
    print()
    print(arrive_time - start_time)
    print()

    distance = arrive_odometer - start_odometer
    current_consumption = (distance * consumption) / 100
    cost = current_consumption * petrol_price
    petrol_cost = f'{consumption} L/100 ({current_consumption} x {petrol_price} = {cost})'

    return templates.TemplateResponse(
        "calculations.html", {
            "request": request,
            "distance": distance,
            "current_consumption": current_consumption,
            "cost": cost,
            "petrol_cost": petrol_cost
        }
    )
