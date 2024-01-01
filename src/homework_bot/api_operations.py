from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class addHomeworkCriteria:
    subject: str
    title: str
    due_date: str
    teacher: Union[str, None] = None
    description: Optional[str] = None
    assigned_date: Optional[str] = None


@dataclass
class listHomeworksCriteria:
    count: Union[int, None] = None
    page: Union[int, None] = None
    assigned_before_date: Union[str, None] = None
    assigned_after_date: Union[str, None] = None
    due_before_date: Union[str, None] = None
    due_after_date: Union[str, None] = None


@dataclass
class getStatisticsCriteria:
    subject: Union[str, None] = None
    assigned_before_date: Union[str, None] = None
    assigned_after_date: Union[str, None] = None


async def new_classroom(http_client, api_url, classroom_name: str, classroom_password: str):
    json_query = {
        "classroom_name": classroom_name,
        "classroom_password": classroom_password,
    }

    api_response = await http_client.post(api_url + "/classroom/new", json=json_query)

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


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

    api_response = await http_client.post(api_url + "/homework/add", json=json_query)

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

    api_response = await http_client.post(api_url + "/homework/remove", json=json_query)

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


async def list_homeworks(
    http_client, api_url, classroom_secret, criteria: listHomeworksCriteria
):
    json_query = {
        "classroom_secret": classroom_secret,
        "count": criteria.count,
        "page": criteria.page,
        "assigned_before_date": criteria.assigned_before_date,
        "assigned_after_date": criteria.assigned_after_date,
        "due_before_date": criteria.due_before_date,
        "due_after_date": criteria.due_after_date,
    }

    api_response = await http_client.post(api_url + "/homework/list", json=json_query)

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


async def get_homework(http_client, api_url, classroom_secret, homework_id: str):
    json_query = {
        "classroom_secret": classroom_secret,
        "homework_id": homework_id,
    }

    api_response = await http_client.post(api_url + "/homework/get", json=json_query)

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]


async def get_statistics(
    http_client, api_url, classroom_secret, criteria: getStatisticsCriteria
):
    json_query = {
        "classroom_secret": classroom_secret,
        "subject": criteria.subject,
        "assigned_before_date": criteria.assigned_before_date,
        "assigned_after_date": criteria.assigned_after_date,
    }

    api_response = await http_client.post(
        api_url + "/homework/statistics", json=json_query
    )

    json_response = api_response.json()
    return json_response, json_response["response"]["error"]
