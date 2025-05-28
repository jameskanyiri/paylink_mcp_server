import functools
import inspect
import time
import os
from typing import Any, Callable
from .logger import logger # Import logger from the same directory

SENSITIVE_KEYS = {"access_token", "passkey", "password"} # Keys to exclude from logs

def async_trace(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Filter out sensitive arguments
        log_arguments = {
            k: v for k, v in bound_args.arguments.items() if k not in SENSITIVE_KEYS
        }

        # Extract transaction context keys if they exist in arguments
        tx_context_keys = [
            "phone_number", "amount", "checkout_request_id", 
            "merchant_name", "ref_no", "trx_code", "cpi",
            "account_reference", "transaction_desc", "transaction_type"
        ]
        transaction_context = {
            key: bound_args.arguments.get(key) for key in tx_context_keys if key in bound_args.arguments
        }

        metadata = {
            "env": os.getenv("APP_ENV", "unknown"),
            "currency": "KES",  # Placeholder, ideally from context/args
            "provider": "M-Pesa",  # Placeholder, ideally from context/args
        }
        
        log_extra_base = {
            "func_name": func_name,
            "transaction_context": transaction_context,
            "metadata": metadata,
        }

        logger.info(
            "Function started",
            extra={
                **log_extra_base,
                "args": log_arguments,
            },
        )

        try:
            result = await func(*args, **kwargs)
            duration = round(time.time() - start_time, 3)
            status = "error" if isinstance(result, dict) and "error" in result else "success"

            log_extra_completed = {
                **log_extra_base,
                "duration_seconds": duration,
                "status": status,
            }

            if status == "success":
                # Log result only if it's not overly large or sensitive; adapt as needed
                log_extra_completed["result"] = result if isinstance(result, (dict, str, int, float, bool, list)) else str(type(result))
                logger.info("Function completed", extra=log_extra_completed)
            else: # error status
                log_extra_completed["error_details"] = result.get("error") if isinstance(result, dict) else str(result)
                logger.error("Function completed with error", extra=log_extra_completed)
            
            return result
        except Exception as e:
            duration = round(time.time() - start_time, 3)
            logger.error(
                "Function failed with exception",
                extra={
                    **log_extra_base,
                    "duration_seconds": duration,
                    "status": "exception",
                    "error_message": str(e),
                    "exception_type": type(e).__name__,
                },
                exc_info=True # Include exception traceback in the log
            )
            raise

    return wrapper
