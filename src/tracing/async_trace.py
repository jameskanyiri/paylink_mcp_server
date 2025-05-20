import functools
import inspect
import time
import os
from datetime import datetime
from typing import Any, Callable
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

load_dotenv(override=True)

# Create a new client and connect to the server
client = MongoClient(os.getenv("MONGO_URL"), server_api=ServerApi("1"))

trace_collection = client["paylink"]["traces"]


def async_trace(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        arguments = bound_args.arguments

        # Extract trace-relevant fields
        transaction_context = {
            "phone_number": arguments.get("phone_number"),
            "amount": arguments.get("amount"),
            "account_reference": arguments.get("account_reference"),
            "transaction_desc": arguments.get("transaction_desc"),
            "transaction_type": arguments.get("transaction_type"),
            "currency": "KES",  # hardcoded for now
            "provider": "M-Pesa",  # inferred from function or config
        }

        trace_log = {
            "function": func_name,
            "status": "started",
            "timestamp": datetime.utcnow(),
            "transaction": transaction_context,
            "metadata": {
                "env": "production",  # optional: infer from os.getenv
            },
        }

        # Insert the initial trace and store the _id
        insert_result = trace_collection.insert_one(trace_log)
        trace_id = insert_result.inserted_id

        try:
            result = await func(*args, **kwargs)
            trace_collection.update_one(
                {"_id": trace_id},
                {
                    "$set": {
                        "status": "success",
                        "duration": round(time.time() - start_time, 3),
                        "timestamp": datetime.utcnow(),
                        "result": result if isinstance(result, dict) else str(result),
                    }
                },
            )
            return result
        except Exception as e:
            trace_collection.update_one(
                {"_id": trace_id},
                {
                    "$set": {
                        "status": "error",
                        "duration": round(time.time() - start_time, 3),
                        "error": str(e),
                        "timestamp": datetime.utcnow(),
                    }
                },
            )
            raise

    return wrapper
