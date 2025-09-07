import logging
import colorlog


def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """Cria e retorna um logger com cores usando colorlog"""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = colorlog.ColoredFormatter(
            fmt="[%(log_color)s%(asctime)s] - [%(filename)s]:[%(lineno)d] - [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

log = get_logger("ms-integracao-gemini")

if __name__ == "__main__":

    log.debug("Mensagem DEBUG")
    log.info("Mensagem INFO")
    log.warning("Mensagem WARNING")
    log.error("Mensagem ERROR")
    log.critical("Mensagem CRITICAL")
