# Local
workon driving-car-expense
uvicorn main:app --host 0.0.0.0 --port 8088 --reload

# Docker
docker build -t driving-car-expense .
docker run --rm --name driving-car-expense -p 8088:80 driving-car-expense
