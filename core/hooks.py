from drf_spectacular.plumbing import build_object_type


def response_format_hook(generator, request, public, result):
    paths = result.get("paths", {})
    for path_item in paths.values():
        for operation in path_item.values():
            responses = operation.get("responses", {})
            for status_code, response in responses.items():
                schema = (
                    response.get("content", {})
                    .get("application/json", {})
                    .get("schema")
                )

                if not schema:
                    continue

                if status_code.startswith("2"):
                    response_schema = {
                        "message": {"type": "string", "example": "Success"},
                        "data": response["content"]["application/json"]["schema"],
                        "status_code": {"type": "integer", "example": 200},
                    }
                elif status_code.startswith("4"):
                    response_schema = {
                        "message": {"type": "string", "example": "Validation error"},
                        "data": response["content"]["application/json"]["schema"],
                        "status_code": {"type": "integer", "example": 400},
                    }
                else:
                    continue

                response["content"]["application/json"]["schema"] = build_object_type(
                    properties=response_schema
                )
    return result
