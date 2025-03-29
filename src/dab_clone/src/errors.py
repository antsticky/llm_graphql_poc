from typing import Dict, Any


def custom_format_error(error) -> Dict[str, str]:
    print(f"GraphQL Error: {error}")

    return {
        "message": "An unexpected error occurred. Please contact support if this persists."
    }
