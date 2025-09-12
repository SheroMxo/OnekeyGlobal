import os
import asyncio

if __name__ == "__main__":
    try:
        from src.main import main

        asyncio.run(main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\nProgram exited")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.system("pause")
