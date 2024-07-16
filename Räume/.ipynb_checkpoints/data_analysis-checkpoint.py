import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(file_path):
    # Daten laden
    data = pd.read_csv(file_path, parse_dates=['_start', '_stop', '_time'])
    data.columns = ['result', 'table', '_start', '_stop', '_time', '_value', '_field', '_measurement', 'room']
    return data

def preprocess_data(data):


    # '_time' Spalte in datetime konvertieren
    data['_time'] = pd.to_datetime(data['_time'], errors='coerce')

    # '_value' in numerischen Typ konvertieren und Fehler ignorieren
    data['_value'] = pd.to_numeric(data['_value'], errors='coerce')

    # Zeilen mit NaN in '_time' oder '_value' Spalten entfernen
    data = data.dropna(subset=['_time', '_value'])

    # Entferne alle Zeilen, die immer noch NaN-Werte enthalten
    data = data.dropna()

    # Entferne Duplikate
    data = data.drop_duplicates()

    # Negative Werte in „_value“ entfernen
    data = data[data['_value'] >= 0]

    # Außreißer behandeln
    q_low = data['_value'].quantile(0.01)
    q_high = data['_value'].quantile(0.99)
    data = data[(data['_value'] > q_low) & (data['_value'] < q_high)]

    return data

def filter_data(data):
    # Filterung der Daten auf Montag bis Freitag und 08:00 bis 18:00 Uhr
    data['_time'] = pd.to_datetime(data['_time'])
    data = data[data['_time'].dt.weekday < 5]  # Montag=0, Sonntag=6
    data = data.between_time('08:00', '18:00')

    # Pausenzeiten ausschließen
    pauses = [
        ('09:30', '09:45'),
        ('11:15', '12:15'),
        ('13:45', '14:00'),
        ('15:30', '15:45'),
        ('17:15', '17:30')
    ]
    for start, end in pauses:
        data = data[~data['_time'].between(start, end)]

    return data


def plot_data(data, title, plot_file_path):
    # Daten plotten
    plt.figure(figsize=(10, 6))
    plt.plot(data['_time'], data['_value'], marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.title(title)
    plt.xlabel('Zeitstempel')
    plt.ylabel('Gerätezählung')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Plot speichern
    plt.savefig(plot_file_path)
    plt.close()  # Vermeidet die Anzeige des Plots in einer laufenden Schleife

def create_plots_by_period(data, period_col, period_format, output_dir, room, plot_title_format, plot_filename_format):
    # Verzeichnis für die Plots erstellen
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # die Daten nach dem angegebenen Zeitraum gruppieren
    data[period_col] = data['_time'].dt.to_period(period_format)

    # Für jeden Zeitraum eine separate Visualisierung erstellen
    for period, group in data.groupby(period_col):
        title = plot_title_format.format(period=period, room=room)
        plot_file_path = os.path.join(output_dir, plot_filename_format.format(period=period))
        plot_data(group, title, plot_file_path)

    print(f"Plots wurden im Verzeichnis '{output_dir}' gespeichert.")

def create_monthly_plots(data, output_dir, room):
    data['month'] = data['_time'].dt.to_period('M')
    for month, group in data.groupby('month'):
        plot_title = f'Gerätezählung im {month} in {room}'
    plot_file_path = f'{output_dir}/geraetezaehlung_{month}.png'
    plot_data(group, plot_title, plot_file_path)

def create_daily_plots(data, output_dir, room):
    create_plots_by_period(data, 'YearMonthDay', 'D', output_dir, room,
                           'Gerätezählung am {period} in Raum {room}', 'geraetezaehlung_{period}.png')

def analyze_room(data, room):
    # Daten für den spezifischen Raum filtern
    room_data = data[data['Room'] == room]

    # Daten vorverarbeiten
    room_data = preprocess_data(room_data)

    return room_data
