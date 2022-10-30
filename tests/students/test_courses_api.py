import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from students.models import Course, Student


class Client(APIClient):
    url = '/api/v1/courses/'

    def get_course(self, pk='', **kwargs):
        return self.get(self.url + pk, **kwargs)

    def add_course(self, load_data):
        return self.post(self.url, data=load_data)

    def update_course(self, course_id, update_data):
        return self.patch(f'{self.url}{course_id}/', data=update_data)

    def delete_course(self, course_id):
        return self.delete(f'{self.url}{course_id}/')


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_one_course(client, course_factory):
    course = course_factory()
    response = client.get_course()
    data = response.json()

    assert response.status_code == 200
    assert data[0]['id'] == course.id
    assert data[0]['name'] == course.name


@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get_course()
    data = response.json()

    assert response.status_code == 200
    assert len(data) == len(courses)
    for i, course in enumerate(courses):
        assert data[i]['id'] == course.id
        assert data[i]['name'] == course.name


@pytest.mark.django_db
def test_id_filter(client, course_factory):
    courses = course_factory(_quantity=10)
    for course in courses:
        params = {'id': course.id}
        response = client.get_course(data=params)
        data = response.json()

        assert response.status_code == 200
        assert data[0]['id'] == course.id
        assert data[0]['name'] == course.name


@pytest.mark.django_db
def test_name_filter(client, course_factory):
    courses = course_factory(_quantity=10)
    for course in courses:
        params = {'name': course.name}
        response = client.get_course(data=params)
        data = response.json()

        assert response.status_code == 200
        assert data[0]['id'] == course.id
        assert data[0]['name'] == course.name


@pytest.mark.django_db
def test_create_course(client):
    load_data = {"name": "python-dev"}
    post = client.add_course(load_data)
    get = client.get_course()
    get_data = get.json()

    assert post.status_code == 201
    assert get.status_code == 200
    assert get_data[0]['name'] == load_data['name']


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course_factory()
    update_data = {"name": "fullstack"}
    update = client.update_course(1, update_data)
    response = client.get_course().json()

    assert update.status_code == 200
    assert response[0]['name'] == update_data['name']


@pytest.mark.django_db
def test_destroy_course(client, course_factory):
    course_factory()
    before = client.get_course()
    destroy = client.delete_course(1)
    after = client.get_course()

    assert destroy.status_code == 204
    assert len(before.data) == len(after.data) + 1
