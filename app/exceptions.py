from fastapi import HTTPException, status


class CRUDException(HTTPException):
    status_code = 500
    detail = ''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class MusicianNotFoundException(CRUDException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Musician not found'


class MoreThanOneRecordException(CRUDException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = 'More than one record found, one was expected'

