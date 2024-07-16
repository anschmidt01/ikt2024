import os
from data_analysis import load_data, plot_data, create_monthly_plots, create_daily_plots, preprocess_data, filter_data

# Pfad zur CSV-Datei
file_path = '2024-05-18_Export_01_DRA.csv'  # Ersetze dies durch den tatsächlichen Pfad zur Datei

# Pfad zur gefilterten CSV-Datei
filtered_file_path = 'filtered_2024-05-18_Export_01_DRA 2.csv'

# CSV-Datei laden
data = load_data(file_path)

# Gefilterte CSV-Datei laden und Spaltennamen anpassen
filtered_data = load_data(filtered_file_path)
filtered_data.columns = ['table', '_start', '_stop', '_time', '_value', '_field', '_measurement', 'room']


# Räume, die analysiert werden sollen
rooms = ['625', '639', '640']

# Erstelle Verzeichnisse für die Plots
output_dirs = {
    'daily': 'taegliche_plots',
    'monthly': 'monatliche_plots',
    'overall': 'gesamt_plots',
    'filtered_daily': 'gefilterte_taegliche_plots',
    'filtered_monthly': 'gefilterte_monatliche_plots',
    'filtered_overall': 'gefilterte_gesamt_plots'
}

for key, output_dir in output_dirs.items():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

for room in rooms:
    room_data = data[data['room'] == room]

    # Daten vorverarbeiten
    room_data = preprocess_data(room_data)

    # Gesamte Gerätezählung plotten
    plot_title = f'Gerätezählung über die Zeit in {room}'
    plot_file_path = f'{output_dirs["overall"]}/geraetezaehlung_ueber_zeit_{room}.png'
    plot_data(room_data, plot_title, plot_file_path)

    # Monatliche Plots erstellen
    create_monthly_plots(room_data, f'{output_dirs["monthly"]}_{room}', room)

    # Tägliche Plots erstellen
    create_daily_plots(room_data, f'{output_dirs["daily"]}_{room}', room)

    # Daten vorverarbeiten und filtern
    filtered_data = preprocess_data(filtered_data)
    filtered_data = filter_data(filtered_data)

    for room in rooms:
        filtered_room_data = filtered_data[filtered_data['room'] == room]

    # Gesamte gefilterte Gerätezählung plotten
    plot_title = 'Gefilterte Gerätezählung in verschiedenen Räumen (Mo-Fr, 08:00-18:00)'
    plot_file_path = f'{output_dirs["filtered_overall"]}/geraetezaehlung_gefiltert_ueber_zeit_{room}.png'
    plot_data(filtered_data, plot_title, plot_file_path)

    # Monatliche gefilterte Plots erstellen
    create_monthly_plots(filtered_room_data, f'{output_dirs["filtered_monthly"]}_{room}', room)

    # Tägliche gefilterte Plots erstellen
    create_daily_plots(filtered_room_data, f'{output_dirs["filtered_daily"]}_{room}', room)