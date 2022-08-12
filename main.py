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
    start_odometer: int = Form(),
    arrive_odometer: int = Form()
):
    distance = arrive_odometer - start_odometer
    trip_consumption = round((distance * consumption) / 100, 1)
    cost = round(trip_consumption * petrol_price)

    return templates.TemplateResponse(
        "calculations.html", {
            "request": request,
            "consumption": consumption,
            "trip_consumption": trip_consumption,
            "petrol_price": petrol_price,
            "cost": cost
        }
    )
