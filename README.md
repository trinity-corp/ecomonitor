<img width="1925" height="435" alt="logooutlien" src="https://github.com/user-attachments/assets/bfc07e80-ea4d-4d7d-b4ad-86a24170819a" />

##
EcoMonitor is a web platform for monitoring EcoMonitor devices, such as GasGuard, TempGuard and HumidGuard.
It provides user authentication, device registration by serial number, real-time dashboards, device management.

See also: *[Device Firmware Repository](https://github.com/galukosi/ecomonitor-firmware)*

![Знімок екрана_20-11-2025_215157_ecomonitor-znv9 onrender com](https://github.com/user-attachments/assets/356f25b8-c4af-4724-87a8-9d5992b29017)

## Features
- User registration and authentication.
- Device linking via unique serial number.
- Real-time measurement monitoring.
- Historical data storage (SQLite/PostgreSQL):
  - View all readings on the website.
  - Export all readings in JSON.
  - Export all readings in CSV.
  - Clear all readings.
- Send command to the device:
  - Enable/disable screen.
  - Reboot.
  - Factory reset.
- Configuration options:
  - Set minimum and maximum safe thresholds.
  - Link custom Telegram bot for getting alerts.

## Tech stack
- **Backend:** Django + Django REST Framework  
- **Frontend:** HTML, CSS, JavaScript, BootStrap 5  
- **Database:** SQLite or PostgreSQL
- **API:** REST (data from ESP32)

## Supported devices
- **GasGuard** - measures carbon monoxide concentration (ppmv)
- **TempGuard** - measures air temperature (°C)
- **HumidGuard** - measures air humidity (%RH)

Firmware for every device is available in [ecomonitor-firmware repo](https://github.com/trinity-corp/ecomonitor-firmware/)

## Benefits of EcoMonitor
The advantages of EcoMonitor over other systems are its affordability, openness, flexibility, and scalability.

EcoMonitor can be used by everyone, from ordinary people to industrial enterprises. It is specifically designed so that you can use either a single device for a specific purpose or an entire network of devices for systematic monitoring of the microclimate.

Note: EcoMonitor is designed solely for monitoring. Its sole purpose is to provide data for further analysis and to alert the user to potential hazards. It does not automatically prevent hazards. 

## How to run
```bash
# Clone project
git clone https://github.com/galukosi/ecomonitor.git
cd ecomonitor

# Install dependencies
pip install -r requirements.txt

# Configure .env
mv .env.example .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver

```

## Future ideas
- More -Guard devices.
- Detailed readings management, such as selecting specific values readings, or readings from specific dates.
- Detailed statictics (graphics, diagrams etc.)
- Translating the website to other languages.
- Advanced device management.

Made by Andriy Tymchuk, 2026.
