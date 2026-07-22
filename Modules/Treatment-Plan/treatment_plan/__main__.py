import uvicorn
from .config import Settings


def main() -> None:
    settings = Settings.from_env()
    uvicorn.run("treatment_plan.app:app", host="0.0.0.0", port=8000, reload=settings.environment == "development")


if __name__ == "__main__":
    main()

