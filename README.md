mood-music-ai/
│
├── vision/                      # PERSON A
│   ├── emotion_detector.py
│   ├── calibrator.py
│   ├── test_capture.py
│   └── __init__.py
│
├── music/                       # PERSON B
│   ├── music_engine.py
│   └── prompt_templates.py
│
├── mapper/                      # PERSON C
│   ├── mapper.py
│   ├── profile.json
│   └── __init__.py
│
├── app/                         # PERSON D
│   ├── desktop_app.py          # (PyQt6)
│   ├── static/
│   ├── templates/
│   │   └── ui.html
│   └── api_server.py           # Flask API
│
├── shared/
│   ├── schemas.py
│   ├── utils.py
│   └── constants.py
│
├── requirements.txt
└── README.md
