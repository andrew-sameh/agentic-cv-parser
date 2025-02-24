from fastapi import Request


async def user_id_identifier(request: Request):
    # Authentication based limmiting is disabled since we dont have authentication yet.
    # if request.scope["type"] == "http":
    #     # Retrieve the Authorization header from the request
    #     auth_header = request.headers.get("Authorization")
    #
    #     if auth_header is not None:
    #         # Check that the header is in the correct format
    #         header_parts = auth_header.split()
    #         if len(header_parts) == 2 and header_parts[0].lower() == "bearer":
    #             token = header_parts[1]
    #             try:
    #                 payload = decode_token(token)
    #             except ExpiredSignatureError:
    #                 raise HTTPException(
    #                     status_code=status.HTTP_403_FORBIDDEN,
    #                     detail="Your token has expired. Please log in again.",
    #                 )
    #             except DecodeError:
    #                 raise HTTPException(
    #                     status_code=status.HTTP_403_FORBIDDEN,
    #                     detail="Error when decoding the token. Please check your request.",
    #                 )
    #             except MissingRequiredClaimError:
    #                 raise HTTPException(
    #                     status_code=status.HTTP_403_FORBIDDEN,
    #                     detail="There is no required field in your token. Please contact the administrator.",
    #                 )
    #
    #             user_id = payload["sub"]
    #
    #             return user_id
    if request.scope["type"] == "websocket":
        return request.scope["path"]

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]

    client = request.client
    ip = getattr(client, "host", "0.0.0.0")
    return ip + ":" + request.scope["path"]
