Create this folder structure first , don't add any code in it.
app/
└── services/
    └── podcast/
        ├── __init__.py
        ├── service.py                 # PodcastService class + generate_full_podcast
        ├── audio.py                   # ← NEW: all TTS calling + chunk combining + mp3 conversion
        ├── translation.py
        ├── script_splitting.py
        ├── file_utils.py
        └── ffmpeg_check.py


Also for this no code in it.
app/
└── services/
    └── unified_agent/
        ├── __init__.py
        ├── service.py              # main class + high-level orchestration
        ├── agent_init.py           # agent creation & session service setup
        ├── prompt_builder.py       # prompt construction logic
        ├── runner_execution.py     # running the agent & collecting response
        ├── script_cleaner.py       # post-processing of generated script
        └── error_handling.py       # simple error response helpers