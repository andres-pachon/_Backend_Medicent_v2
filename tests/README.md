# Pruebas de regresión del backend

Desde la carpeta `_Backend_Medicent_v2`, ejecuta:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

La suite crea y elimina una base SQLite en memoria en cada prueba. No usa ni modifica la base MySQL configurada para la aplicación.
