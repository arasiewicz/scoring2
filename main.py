import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Funkcja do inicjalizacji bazy danych
def init_db():
    conn = sqlite3.connect('scoring_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            deal_name TEXT,
            customer_type TEXT,
            total_score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Inicjalizacja bazy danych przed uruchomieniem aplikacji
init_db()

@app.route('/', methods=['GET', 'POST'])
def calculate_score():
    if request.method == 'POST':
        # Pobieranie danych z formularza
        deal_name = request.form.get('deal_name')
        customer_type = request.form.get('customer_type')

        geography = request.form.get('geography')
        technology = request.form.getlist('technology')
        scale = request.form.get('scale')
        industry = request.form.get('industry')
        tech_awareness = request.form.getlist('tech_awareness')
        other = request.form.getlist('other')
        project_length = request.form.get('project_length')

        # Inicjalizacja punktacji
        total_score = 0

        # Obliczanie punktacji na podstawie wybranych kryteriów
        if geography == 'EU + UK':
            total_score += 3
        elif geography == 'USA East' or geography == 'PL':
            total_score += 2
        elif geography == 'Middle East':
            total_score += 1

        tech_score = 0
        if 'Java' in technology:
            tech_score = max(tech_score, 3)
        if 'React' in technology:
            tech_score = max(tech_score, 3)
        if 'iOS' in technology:
            tech_score = max(tech_score, 3)
        if 'Android' in technology:
            tech_score = max(tech_score, 3)
        if 'PHP' in technology:
            tech_score = max(tech_score, 2)
        if '.NET' in technology:
            tech_score = max(tech_score, 2)
        if 'node.js' in technology:
            tech_score = max(tech_score, 2)
        if 'Angular' in technology:
            tech_score = max(tech_score, 2)
        if 'Legacy code' in technology:
            tech_score = max(tech_score, -1)
        total_score += tech_score

        if scale == '3-4 FTE':
            total_score += 2
        elif scale == 'powyżej 8 FTE':
            total_score += 1

        if industry in ['Banking', 'Insurance', 'Fintech', 'Edtech']:
            total_score += 3

        tech_awareness_score = 0
        if 'Greenfield' in tech_awareness:
            tech_awareness_score = max(tech_awareness_score, 3)
        if 'Klient ma swój dział IT' in tech_awareness or 'PM po stronie Speednet' in tech_awareness:
            tech_awareness_score = max(tech_awareness_score, 2)
        total_score += tech_awareness_score

        for item in other:
            if item == 'Front do klienta i kontakt z osobami decyzyjnymi':
                total_score += 3
            elif item == 'Znamy budżet klienta':
                total_score += 2
            elif item in ['Brak timeline lub timeline nierealistyczny', 'Fixed Price', 'Klient uważa cenę za przesadnie dużą',
                         'Przetargi/public', 'RFI/RFP/konkursy piękności']:
                total_score -= 1

        if project_length == '3-6 miesięcy':
            total_score += 0
        elif project_length == '6-12 miesięcy':
            total_score += 2
        elif project_length == 'powyżej 12 miesiecy':
            total_score += 3

        # Zapisywanie danych do bazy danych
        conn = sqlite3.connect('scoring_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scores (deal_name, customer_type, total_score) VALUES (?, ?, ?)",
                       (deal_name, customer_type, total_score))
        conn.commit()
        conn.close()

        # Dodać log, aby sprawdzić, czy dane są poprawnie zapisane
        print(f"Dane zapisane: deal_name={deal_name}, customer_type={customer_type}, total_score={total_score}")

        # Pobieranie wyników z bazy danych
        conn = sqlite3.connect('scoring_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT deal_name, customer_type, total_score FROM scores")
        results = cursor.fetchall()
        conn.close()

        # Dodać log, aby sprawdzić pobrane wyniki
        print("Wyniki z bazy danych:")
        for row in results:
            print(row)

        return render_template('result.html', total_score=total_score, results=results)

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
