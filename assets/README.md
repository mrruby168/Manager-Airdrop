# Assets

`app.ico` — icon ứng dụng dùng khi build exe bằng PyInstaller:

```
pyinstaller --name "Manager Airdrop" --onedir --windowed --icon assets\app.ico --add-data "app/ui;app/ui" main.py
```

