from fastapi import Header, HTTPException


def get_current_user_id(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    print(f"X-User-Id: {x_user_id}")
    if not x_user_id:
        raise HTTPException(
            status_code=401, detail="X-User-Id header is required")
    return x_user_id
