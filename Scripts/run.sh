xterm -T "Flask Build" -hold -e "cd FlaskAPI && docker build -t apitest . && docker run -p 5000:5000 apitest" &
cd Frontend &&
source venv/bin/activate &&
python manage.py runserver