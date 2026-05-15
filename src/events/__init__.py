import pkgutil
import importlib
from aiogram import Router
from logging import getLogger, Logger

logger: Logger = getLogger()

def get_all_routers() -> list[Router]:
    routers = []
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
        full_module_name = f"{__name__}.{module_name}"
        module = importlib.import_module(full_module_name)
        if hasattr(module, "router") and isinstance(module.router, Router):
            routers.append(module.router)
    return routers
