import os


CONFIG_DIR = os.environ.get(
    "PLAINCHECKER_CONFIG_DIR",
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "../config"
    ))
)
LOG_DIR = os.environ.get(
    "PLAINCHECKER_LOG_DIR",
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "../logs"
    ))
)