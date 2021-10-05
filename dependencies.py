from fastapi import Request

def get_db(request:Request):
    try:
        yield request.state.db
    finally:
        request.state.db.close()
    # return request.state.db