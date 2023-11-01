from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class addHomeworkCriteria:
    subject: str
    teacher: Union[str, None] = None
    title: str
    description: Optional[str] = None
    assigned_date: Optional[str] = None
    due_date: str


@dataclass
class getHomeworksCriteria:
    count: Union[int, None] = None
    page: Union[int, None] = None
    assigned_before_date: Union[str, None] = None
    assigned_after_date: Union[str, None] = None
    due_before_date: Union[str, None] = None
    due_after_date: Union[str, None] = None


async def add_homework(
    http_client,
    api_url,
    classroom_secret,
    classroom_password,
    criteria: addHomeworkCriteria,
):
    json_query = {
        "classroom_secret": classroom_secret,
        "classroom_password": classroom_password,
        "subject": criteria.subject,
        "teacher": criteria.teacher,
        "title": criteria.title,
        "description": criteria.description,
        "assigned_date": criteria.assigned_date,
        "due_date": criteria.due_date,
    }

    api_response = await http_client.post(
        api_url + "/api/add_homework", json=json_query
    )

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


async def remove_homework(
    http_client,
    api_url,
    classroom_secret,
    classroom_password,
    homework_id: int,
):
    json_query = {
        "classroom_secret": classroom_secret,
        "classroom_password": classroom_password,
        "homework_id": homework_id,
    }

    api_response = await http_client.post(
        api_url + "/api/remove_homework", json=json_query
    )

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


async def get_homeworks(
    http_client, api_url, classroom_secret, criteria: getHomeworksCriteria
):
    json_query = {
        "secret": classroom_secret,
        "count": criteria.count,
        "page": criteria.page,
        "assigned_before": criteria.assigned_before_date,
        "assigned_after": criteria.assigned_after_date,
        "due_before": criteria.due_before_date,
        "due_after": criteria.due_after_date,
    }

    api_response = await http_client.post(
        api_url + "/api/get_homeworks", json=json_query
    )

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]
