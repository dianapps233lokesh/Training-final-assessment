from rest_framework import status
from rest_framework.renderers import JSONRenderer


def parse_error(errors):
    response = None

    if isinstance(errors, str):
        response = errors

    elif isinstance(errors, dict):
        for i in errors.keys():
            if isinstance(errors[i], list):
                response = parse_error(errors[i][0])
            elif isinstance(errors[i], str):
                response = errors[i]
            elif isinstance(errors[i], dict):
                response = parse_error(errors[i])
            break

    elif isinstance(errors, list):
        if isinstance(errors[0], list):
            response = parse_error(errors[0])
        elif isinstance(errors[0], str):
            response = errors[0]
        elif isinstance(errors[0], dict):
            response = parse_error(errors[0])

    return response


def get_error_data(errors, status_text):
    try:
        error_data = parse_error(errors)
    except Exception:
        error_data = "Something went wrong."
    return error_data if error_data else status_text


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        response_status = "success"
        response_data = data
        errors = []
        response_message = (
            data.pop("message", "")
            if isinstance(data, dict)
            else data
            if isinstance(data, str)
            else ""
        )

        if status.is_client_error(status_code) or status.is_server_error(status_code):
            response_status = "failure"
            if response_data:
                errors = response_data.get("errors", None) or response_data
            response_data = []
            if not response_message:
                response_message = get_error_data(
                    errors, renderer_context["response"].status_text
                )

            custom_data = {
                "status": response_status,
                "message": response_message or "Failed",
                "errors": errors,
                "data": response_data,
            }
        else:
            if isinstance(response_data, dict):
                if "data" in response_data:
                    if (
                        isinstance(response_data["data"], list)
                        and not response_data["data"]
                    ):
                        response_data = []
                    else:
                        response_data = response_data["data"]

            custom_data = {
                "status": response_status,
                "message": response_message or "Successful",
                "data": response_data,
            }

        response = super(CustomJSONRenderer, self).render(
            custom_data, accepted_media_type, renderer_context
        )
        return response
