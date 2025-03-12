# ProjetDataScience

For frontend:
1. Execute the front_end_07_03_25.py to launch the site
2. Copy the link (Dash is running on http://127.0.0.1:8050/) and paste into web browser
3. Enjoy the amazing interface

For backend:
install the dependencies with:
pip install fastapi uvicorn pandas pmdarima statsmodels filterpy openpyxl
to check api:
uvicorn main:app --reload
Next, open http://127.0.0.1:8000/docs

files:
requirements.txt -> required requirements (c'est ce que j'ai sur mon pc)
models.py -> definied models
main.py -> launch this to make work all the stuff
backend -> folder with 
            __init__.py -> 
            predictions.py ->             
data -> excel files for 2023, 2024, 2025 (need to be treated correctly)