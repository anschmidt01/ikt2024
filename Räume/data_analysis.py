import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(file_path):
    # CSV-Datei laden
    data = pd.read_csv(file_path, dtype={
        'result': str,
        'table': int,
        '_start': str,
        '_stop': str,
        '_time': str,
        '_value': float,
        '_field': str,
        '_measurement': str
    })

    # Daten bereinigen und Spalten umbenennen
    data.columns = ['result', 'table', '_start', '_stop', '_time', '_value', '_field', '_measurement']

    return data

def preprocess_data(data):
    # '_time' Spalte in datetime konvertieren
    data['_time'] = pd.to_datetime(data['_time'], errors='coerce')

    # '_value' in numerischen Typ konvertieren und Fehler ignorieren
    data['_value'] = pd.to_numeric(data['_value'], errors='coerce')

    # Zeilen mit NaN in '_time' oder '_value' Spalten entfernen
    data = data.dropna(subset=['_time', '_value'])


    return data

def plot_data(data, title, plot_file_path):
    # Daten plotten
    plt.figure(figsize=(12, 6))
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

    # Gruppiere die Daten nach dem angegebenen Zeitraum
    data[period_col] = data['_time'].dt.to_period(period_format)

    # Erstelle für jeden Zeitraum eine separate Visualisierung
    for period, group in data.groupby(period_col):
        title = plot_title_format.format(period=period, room=room)
        plot_file_path = os.path.join(output_dir, plot_filename_format.format(period=period))
        plot_data(group, title, plot_file_path)

    print(f"Plots wurden im Verzeichnis '{output_dir}' gespeichert.")

def create_monthly_plots(data, output_dir, room):
    create_plots_by_period(data, 'YearMonth', 'M', output_dir, room,
                           'Gerätezählung im {period} in Raum {room}', 'geraetezaehlung_{period}.png')

def create_daily_plots(data, output_dir, room):
    create_plots_by_period(data, 'YearMonthDay', 'D', output_dir, room,
                           'Gerätezählung am {period} in Raum {room}', 'geraetezaehlung_{period}.png')

def analyze_room(data, room):
    # Daten für den spezifischen Raum filtern
    room_data = data[data['_measurement'] == room]

    # Daten vorverarbeiten
    room_data = preprocess_data(room_data)

    return room_data
