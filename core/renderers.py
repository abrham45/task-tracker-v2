from rest_framework.renderers import JSONRenderer


class JSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"] if renderer_context else None

        if response and response.status_code >= 400:
            # Extract first error message
            first_error_message = "An error occurred"

            if isinstance(data, dict):
                if "detail" in data:
                    first_error_message = data["detail"]  # Global error
                elif "non_field_errors" in data and isinstance(
                    data["non_field_errors"], list
                ):
                    first_error_message = data["non_field_errors"][
                        0
                    ]  # Form-level error
                else:
                    # Get the first field-specific error
                    for field_name, errors in data.items():
                        if isinstance(errors, list) and errors:
                            first_error_message = (
                                f"{field_name.replace('_', ' ').capitalize()}"
                                f" - {errors[0]}"
                            )
                            break

            formatted_response = {
                "message": first_error_message,
                "errors": data,
                "status_code": response.status_code,
            }
        else:
            formatted_response = {
                "message": "",
                "data": data,
                "status_code": response.status_code if response else 200,
            }

        return super().render(formatted_response, accepted_media_type, renderer_context)
