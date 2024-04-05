from crud.base_crud import BaseCrud
from datetime import datetime
from models import Herb
from sqlalchemy import desc
from sqlalchemy.orm import Session
from log.logger import logger as logging


class HerbCrud(BaseCrud):
    pass
