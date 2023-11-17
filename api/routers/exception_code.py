from fastapi import HTTPException, status

E_code = {
    "400": HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Email already registered!"
    ),
    "401": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password!",
        headers={"WWW-Authenticate": "Bearer"},
    ),
    "403": HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    ),
    "4031": HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized requests!",
    ),
    "404": HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found!",
    ),
    "423": HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="Account is being locked!",
        headers={"WWW-Authenticate": "Bearer"},
    )
}