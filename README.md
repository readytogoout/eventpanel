# Eventpanel
Eventpanel ist ein Flask-Server, der zur Verwaltung der Events und der Instanzen dient.

## Required Files

Required files in the `data/` directory:

### `data/config.json`

```json
{
  "DEBUG": true,
  "DATABASE": {
    "name": "data/data.db",
    "engine": "peewee.SqliteDatabase"
  },
  "SECRET_KEY": "CHOOSE_A_FANCY_SECRET_KEY",
  "GMAIL": {
    "username": "A_MAIL_SENDER@gmail.com",
    "password": "GMAIL_PASSWORD",
    "from": " readytogoout@heliand-pfadfinderschaft.de"
  }
}
```
## Sources
Login Panel: https://bootsnipp.com/snippets/bxzmb
