# phiTool - Phigros 数据管理工具
# Copyright (C) 2026 Chnynnya
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import sys
import json
from typing import Optional, Dict, Any


class Logger:
    def __init__(self, name: Optional[str] = None, silent: bool = False, json_output: bool = False):
        self.silent = silent
        self.json_output = json_output
        self.logger = logging.getLogger(name or "phiTool")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        if not silent:
            console_handler = logging.StreamHandler(sys.stdout)
            
            if json_output:
                formatter = logging.Formatter("%(message)s")
            else:
                log_format = (
                    "\033[36m%(asctime)s\033[0m "
                    "\033[1;%(color)s%(levelname)-8s\033[0m "
                    "%(message)s"
                )
                
                level_colors = {
                    logging.DEBUG: "37m",
                    logging.INFO: "32m",
                    logging.WARNING: "33m",
                    logging.ERROR: "31m",
                    logging.CRITICAL: "41m",
                }
                
                class ColoredFormatter(logging.Formatter):
                    def format(self, record):
                        record.color = level_colors.get(record.levelno, "37m")
                        return super().format(record)
                
                formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
            
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        self.logger.propagate = False
    
    def _log(self, level: int, message: str, **kwargs):
        if self.silent:
            return
        
        if self.json_output:
            log_data: Dict[str, Any] = {
                "level": logging.getLevelName(level),
                "message": message
            }
            log_data.update(kwargs)
            print(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.log(level, message)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def init_console_logger(
        name: Optional[str] = None,
        level: int = logging.INFO,
        log_format: Optional[str] = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    if log_format is None:
        log_format = (
            "\033[36m%(asctime)s\033[0m "
            "\033[1;%(color)s%(levelname)-8s\033[0m "
            "%(message)s"
        )
    level_colors = {
        logging.DEBUG: "37m",
        logging.INFO: "32m",
        logging.WARNING: "33m",
        logging.ERROR: "31m",
        logging.CRITICAL: "41m",
    }

    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            record.color = level_colors.get(record.levelno, "37m")
            return super().format(record)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger