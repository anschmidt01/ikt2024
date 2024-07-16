import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(file_path):
    # CSV-Datei laden
    data = pd.read_csv(file_path, skiprows=[0, 1, 2])  # Überspringe die ersten drei Zeilen mit Metadaten

    # Entferne leere Spalten
    data = data.dropna(axis=1, how='all')

    # Überprüfen der Anzahl der Spalten
    print(f"Die Datei enthält {len(data.columns)} Spalten.")
    print(f"Spaltennamen: {list(data.columns)}")

    # Erwarten wir bestimmte Spaltennamen, oder benennen wir die vorhandenen Spalten
    expected_columns = ['table', '_start', '_stop', '_time', '_value', '_field', '_measurement', 'room']
    if len(data.columns) == len(expected_columns):
        data.columns = expected_columns
    else:
        # Wenn die Anzahl der Spalten nicht übereinstimmt, zeigen wir die ersten Zeilen der Datei zur Diagnose an
        print("Erste Zeilen der CSV-Datei zur Diagnose:")
        print(data.head())
        raise ValueError(f"Erwartete {len(expected_columns)} Spalten, aber CSV enthält {len(data.columns)} Spalten.")

    # Konvertiere Datentypen
    data['table'] = pd.to_numeric(data['table'], errors='coerce')
    data['_start'] = data['_start'].astype(str)
    data['_stop'] = data['_stop'].astype(str)
    data['_time'] = pd.to_datetime(data['_time'], errors='coerce')
    data['_value'] = pd.to_numeric(data['_value'], errors='coerce')
    data['_field'] = data['_field'].astype(str)
    data['_measurement'] = data['_measurement'].astype(str)
    data['room'] = data['room'].astype(str)

    return data
def preprocess_data(data):


    # '_time' Spalte in datetime konvertieren und Zeitzone korrekt setzen
    data['_time'] = pd.to_datetime(data['_time'], errors='coerce', utc=True)

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
    data['_time'] = pd.to_datetime(data['_time'], utc=True).dt.tz_convert('Europe/Berlin')
    data = data[data['_time'].dt.weekday < 5]  # Montag=0, Sonntag=6
    data = data.set_index('_time').between_time('08:00', '18:00').reset_index()

    # Pausenzeiten ausschließen
    pauses = [
        ('09:30', '09:45'),
        ('11:15', '12:15'),
        ('13:45', '14:00'),
        ('15:30', '15:45'),
        ('17:15', '17:30')
    ]
    for start, end in pauses:
        data = data[~((data['_time'].dt.time >= pd.to_datetime(start).time()) & (data['_time'].dt.time <= pd.to_datetime(end).time()))]

    return data


def plot_data(data, title, plot_file_path):
    # Daten plotten
    plt.figure(figsize=(10, 6))
    for room, group in data.groupby('room'):
        plt.plot(group['_time'], group['_value'], marker='o', linestyle='-', label=f'Room {room}')

    plt.title(title)
    plt.xlabel('Zeitstempel')
    plt.ylabel('Gerätezählung')
    plt.grid(True)

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
    data['date'] = data['_time'].dt.date
    for date, group in data.groupby('date'):
        plot_title = f'Gerätezählung am {date} in {room}'
        plot_file_path = f'{output_dir}/geraetezaehlung_{date}.png'
        plot_data(group, plot_title, plot_file_path)

def analyze_room(data, room):
    # Daten für den spezifischen Raum filtern
    room_data = data[data['Room'] == room]

    # Daten vorverarbeiten
    room_data = preprocess_data(room_data)

    return room_data

