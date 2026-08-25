from fastapi import FastAPI, Request, HTTPException
from src.exceptions import exceptions


def setup_exceptions(app: FastAPI):

    @app.exception_handler(exceptions.RuleNotFoundException)
    async def rule_not_found_exception_handler(request: Request, exc: exceptions.RuleNotFoundException):
        raise HTTPException(
            status_code=404,
            detail=exc.detail
        )

    @app.exception_handler(exceptions.RuleAlreadyExistException)
    async def rule_already_exist_exception_handler(request: Request, exc: exceptions.RuleAlreadyExistException):
        raise HTTPException(
            status_code=400,
            detail=exc.detail
        )

