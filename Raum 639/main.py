import pandas as pd
import matplotlib.pyplot as plt

# Pfad zur CSV-Datei
file_path = '/Raum639.csv'  # Ersetze dies durch den tatsächlichen Pfad zur Datei

# CSV-Datei laden
data = pd.read_csv(file_path)

# Daten bereinigen und Spalten umbenennen
data.columns = ['Unnamed1', 'Unnamed2', 'Unknown1', 'StartDate', 'EndDate', 'Timestamp', 'DeviceCount', 'CountLabel', 'DeviceType', 'Room']

# 'Timestamp' Spalte in datetime konvertieren
data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')

# Zeilen mit NaN in 'Timestamp' oder 'DeviceCount' Spalten entfernen
data = data.dropna(subset=['Timestamp', 'DeviceCount'])

# 'DeviceCount' in numerischen Typ konvertieren
data['DeviceCount'] = pd.to_numeric(data['DeviceCount'], errors='coerce')

# Daten plotten
plt.figure(figsize=(12, 6))
plt.plot(data['Timestamp'], data['DeviceCount'], marker='o', linestyle='-', color='b')
plt.title('Gerätezählung über die Zeit in Raum639')
plt.xlabel('Zeitstempel')
plt.ylabel('Gerätezählung')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Plot speichern
plot_file_path = 'geraetezaehlung_ueber_zeit.png'
plt.savefig(plot_file_path)

# Plot anzeigen
plt.show()
