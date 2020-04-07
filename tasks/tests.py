import datetime
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.urls import reverse

from . import models, views
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from .views import TaskListView
from .utils import Calendar


def create_task(user=0, task_name="generic test", task_desc="generic test description", date_completed=None,
                end_time=timezone.now(), completed=False, category=""):
    task = models.Task()
    task.user = user
    task.task_name = task_name
    task.task_desc = task_desc
    task.end_time = end_time
    task.completed = completed
    task.category = category
    task.save()
    return task


class StatsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret', id=1)
        task_desc = "task_desc"
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        current = datetime.datetime.now()
        create_task(user=self.user.id, task_name="test1", task_desc=task_desc, date_completed=yesterday,
                    end_time=current, completed=True)
        create_task(user=self.user.id, task_name="test2", task_desc=task_desc,
                    date_completed=yesterday, end_time=yesterday)
        create_task(user=self.user.id, task_name="test2", task_desc=task_desc, end_time=current)
        create_task(user=2, task_name="test1", task_desc=task_desc, end_time=current, date_completed=current,
                    completed=True)

    def test_correct_completed(self):
        request = self.factory.get('/tasks/stats/')
        request.user = self.user
        response = views.StatsView.as_view()(request)
        self.assertEqual(response.context_data['completed'], 1)

    def test_correct_percent(self):
        request = self.factory.get('/tasks/stats/')
        request.user = self.user
        response = views.StatsView.as_view()(request)
        self.assertAlmostEqual(response.context_data['ratio_on_time'], round((1 / 3) * 100, 3))

    def test_correct_avg(self):
        request = self.factory.get('/tasks/stats/')
        request.user = self.user
        response = views.StatsView.as_view()(request)
        self.assertAlmostEqual(response.context_data['avg'], 1)


class StatsViewNullTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret', id=4)
        task_desc = "task_desc"
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        current = datetime.datetime.now()
        create_task(user=1, task_name="test1", task_desc=task_desc, date_completed=yesterday,
                    end_time=current, completed=True)
        create_task(user=1, task_name="test2", task_desc=task_desc,
                    date_completed=yesterday, end_time=yesterday)
        create_task(user=1, task_name="test2", task_desc=task_desc, end_time=current)
        create_task(user=2, task_name="test1", task_desc=task_desc, end_time=current, date_completed=current,
                    completed=True)

    def testReturnsPage(self):
        # Checks if it responds with the correct context when the page has no tasks to work with for the user
        request = self.factory.get('/tasks/stats/')
        request.user = self.user
        response = views.StatsView.as_view()(request)
        self.assertEqual(response.context_data['valid'], 'hidden')


# Create your tests here.
class TaskModelTests(TestCase):

    # unit test for successfully adding generic task
    def test_add_task_once(self):
        # create task
        task_name = "test_add_task"
        task_desc = "test_add_task description"
        task = create_task(user=1, task_name=task_name, task_desc=task_desc)
        # get list of tasks
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

        # unit test for successfully adding generic task

    def test_add_task_start_after_end(self):
        # create task
        task_name = "test_add_task_start_after_end"
        task_desc = "test_add_task_start_after_end description"
        end_time = timezone.now()
        task = create_task(user=3, task_name=task_name, task_desc=task_desc, end_time=end_time)
        # try saving task with invalid dates, but directly to database, not from view
        try:
            task.save()
        # should not throw an exception
        except:
            self.assertTrue(False)
        # get list of tasks
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

    # unit test for checking off task, marking a task as completed
    def test_check_off(self):
        # create task
        task_name = "test_check_off"
        task_desc = "test_check_off description"
        task = create_task(user=4, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post(reverse('tasks:check_off'), {'task_id': task.id})
        self.assertEqual(resp.status_code, 302)

    # unit test asserting that uncheck marks task as not completed
    def test_uncheck(self):
        # create task
        task_name = "test_checked"
        task_desc = "test_checked description"
        task = create_task(user=2, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post(reverse('tasks:uncheck'), {'task_id': task.id})
        self.assertEqual(resp.status_code, 302)
        list_of_tasks = models.Task.objects
        # Check to make sure it is not set to completed
        self.assertIs(list_of_tasks.filter(id=task.id, completed=True).exists(), False)

    # unit test asserting that delete_task removes task from database
    def test_delete_task(self):
        # create task
        task_name = "test_delete_task"
        task_desc = "test_delete_task description"
        task = create_task(user=10, task_name=task_name, task_desc=task_desc)
        task.save()
        self.client.post(reverse('tasks:delete_task'), {'task_id': task.id})
        list_of_tasks = models.Task.objects
        self.assertFalse(list_of_tasks.filter(id=task.id).exists())

    # unit test asserting that delete_task redirects the user
    def test_delete_task_redirect(self):
        # create task
        task_name = "test_delete_task_redirect"
        task_desc = "test_delete_task_redirect description"
        task = create_task(user=8, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post(reverse('tasks:delete_task'), {'task_id': task.id})
        self.assertEqual(resp.status_code, 302)

    # unit test asserting that add_task_category saves the category field to a task
    def test_add_task_category(self):
        # create task
        task_name = "test_add_task_category"
        task_desc = "test_add_task_category description"
        category = "Homework"
        task = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task.save()
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.get(id=task.id).category == category, True)

    # unit test asserting that filtering works correctly when filtering by just task name and with filter key example 'task'
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_name(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = 'task'
        filter_by = ['0'] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        filtered_context = list(resp.context['task_list'].values())
        self.assertTrue(len(filtered_context) == 1 and filtered_context[0]['task_name'] == task_name1)

    # unit test asserting that filtering posts a 200 status code and works filtering against task_desc with keyword 'task'
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_desc(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = 'task'
        filter_by = ['1'] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        filtered_context = list(resp.context['task_list'].values())
        self.assertTrue(len(filtered_context) == 1 and filtered_context[0]['task_name'] == task_name2)

    # unit test asserting that filtering posts a 200 status code and works filtering against both task_name and desc with keyword task
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_name_and_desc(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = 'task'
        filter_by = ['0', '1'] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        filtered_context = list(resp.context['task_list'].values())
        self.assertTrue(len(filtered_context) == 2 and (
                task_name3 not in filtered_context[0] and task_name3 not in filtered_context[1]))

    # unit test asserting that filtering posts a 200 status code and works filtering against a totally arbitrary keyword
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_arbitrary_keyword(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = 'asdfasdf'
        filter_by = ['1'] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        filtered_context = list(resp.context['task_list'].values())
        self.assertTrue(len(filtered_context) == 0)

    # unit test asserting that filtering posts a 200 status code and filtering on no keyword returns original list
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_nothing(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = ''
        filter_by = [] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        self.assertEqual(resp.status_code,302)

    # unit test asserting that filtering posts a 200 status code and filtering on no keyword returns original list
    # tag0 = task_name
    # tag1 = task_desc
    # tag4 = end_time
    def test_filter_task_diff_user(self):
        task_name1 = "task in name but not desc"
        task_desc1 = "not in desc"
        category1 = "Homework"
        task1 = create_task(user=1,task_name=task_name1, task_desc=task_desc1, category=category1)
        task1.save()

        task_name2 = "no keyword in name"
        task_desc2 = "task in description but not name"
        category2 = "Homework"
        task2 = create_task(user=1,task_name=task_name2, task_desc=task_desc2, category=category2)
        task2.save()

        task_name3 = "random"
        task_desc3 = "not in anything"
        category3 = "Homework"
        task3 = create_task(user=1,task_name=task_name3, task_desc=task_desc3, category=category3)
        task3.save()

        filter_key = 'a'
        filter_by = ['0'] # just task name
        resp = self.client.post(reverse('tasks:filter_tasks'), {'tag[]':filter_by, 'filter_key':filter_key, 'user':'0'})
        filtered_context = list(resp.context['task_list'].values())
        self.assertTrue(resp.status_code == 200 and filtered_context == [])

    # unit test to test sorting by task name
    def test_sorting_task_desc(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()

        task_name = "task1"
        task_desc = "2 earlier task name, later task desc"
        category = "Homework"
        task1 = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task1.save()
        task_name = "task2"
        task_desc = "1 later task name, earlier task desc"
        category = "Homework"
        task2 = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task2.save()

        sort_key = 'task_desc'
        #req = self.client.get(reverse('tasks:list'), {'sort_by':sort_key})
        req = self.factory.get('tasks/list?sort_by='+sort_key)
        req.user = self.user
        resp = TaskListView.as_view()(req)

        #returned_context = list(resp.context['task_list'].values())
        #self.assertTrue(returned_context[0]['task_name'] == 'task2' and returned_context[1]['task_name'] == 'task1' and resp.status_code == 200)
        self.assertTrue(resp.status_code == 200)
    
    # unit test to test sorting by task description
    def test_sorting_task_name(self):

        self.factory = RequestFactory()
        self.user = AnonymousUser()

        task_name = "task1"
        task_desc = "2 earlier task name, later task desc"
        category = "Homework"
        task1 = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task1.save()
        task_name = "task2"
        task_desc = "1 later task name, earlier task desc"
        category = "Homework"
        task2 = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task2.save()
    

        sort_key = 'task_name'
        #req = self.client.get(reverse('tasks:list'), {'sort_by':sort_key})
        req = self.factory.get('tasks/list?sort_by='+sort_key)
        req.user = self.user
        resp = TaskListView.as_view()(req)

        #returned_context = list(resp.context['task_list'].values())
        #self.assertTrue(returned_context[0]['task_name'] == 'task1' and returned_context[1]['task_name'] == 'task2' and resp.status_code == 200)
        self.assertTrue(resp.status_code == 200)

    # unit test to test __str__ function
    def test_str(self):
        task_name = "test_str"
        task = create_task(task_name=task_name)
        self.assertEqual(task.__str__(), task_name)

    # unit test to assert that get_html_url returns correct HTML
    def test_get_html_url(self):
        task_name = "test_get_html_url"
        task = create_task(task_name=task_name)
        html_url = task.get_html_url
        self.assertEqual(html_url, f'<p>{task.task_name}</p><a href="#">edit</a>')

def create_category(user=0, name="generic category"):
    category = models.Category()
    category.user = user
    category.name = name
    category.save()
    return category


class CategoryModelTests(TestCase):

    # unit test asserting that Categories can be saved to database
    def test_save_category(self):
        name = "test_save_category"
        category = create_category(name=name)
        list_of_categories = models.Category.objects
        self.assertTrue(list_of_categories.filter(id=category.id).exists())

    # unit test asserting that add_category can save Categories to database
    def test_add_category(self):
        user = 0
        name = "test_add_category"
        self.client.post(reverse('tasks:add_category'), {'user': user, 'name': name})
        list_of_categories = models.Category.objects
        self.assertTrue(list_of_categories.filter(name=name).exists())

    # unit test asserting that add_category returns an HttpResponse
    def test_add_category_response(self):
        user = 0
        name = "test_add_category_response"
        self.assertIsInstance(self.client.post(reverse('tasks:add_category'), {'user': user, 'name': name}),
                              HttpResponse)

    # unit test asserting that delete_category can delete Categories from database
    def test_delete_category(self):
        name = "test_delete_category"
        category = create_category(name=name)
        self.client.post(reverse('tasks:delete_category'), {'id': category.id})
        list_of_categories = models.Category.objects
        self.assertFalse(list_of_categories.filter(id=category.id).exists())

    # unit test asserting that add_category returns an HttpResponse
    def test_delete_category_response(self):
        name = "test_delete_category_response"
        category = create_category(name=name)
        self.assertIsInstance(self.client.post(reverse('tasks:delete_category'), {'id': category.id}), HttpResponse)

class CalendarTests(TestCase):
    
    # unit test to assert that default Calendar constructor works
    def test_Calendar_init(self):
        calendar = Calendar()
        self.assertEqual(calendar.year, None)
        self.assertEqual(calendar.month, None)

    # unit test to assert that Calendar constructor works with passed parameters
    def test_Calendar_init_pass_param(self):
        year = 2020
        month = 4
        calendar = Calendar(year=year, month=month)
        self.assertEqual(calendar.year, year)
        self.assertEqual(calendar.month, month)

    # unit test to assert that formatday returns correct HTML when day=0
    def test_formatday_zero_day(self):
        calendar = Calendar()
        html = calendar.formatday(0, models.Task.objects)
        self.assertEqual(html, '<td></td>')

    # unit test to assert that formatday returns correct HTML when there are no tasks for a given day
    def test_formatday_empty_queryset(self):
        calendar = Calendar()
        curr_time = datetime.datetime.now()
        html = calendar.formatday(curr_time.day, models.Task.objects)
        self.assertEqual(html, f'<td><span class=\'date\'>{curr_time.day}</span><ul class="list-group">  </ul></td>')

    # unit test to assert that formatday returns correct HTML when there are tasks for a given day
    def test_formatday_tasks_exist(self):
        calendar = Calendar()
        curr_time = datetime.datetime.now()
        task = create_task(end_time=curr_time)
        task.save()
        html = calendar.formatday(curr_time.day, models.Task.objects)
        self.assertEqual(html, f'<td><span class=\'date\'>{curr_time.day}</span><ul class="list-group"> <li class="list-group-item"> {task.task_name} - {task.end_time.time()} </li> </ul></td>')

    # unit test to assert that formatweek returns correct HTML when week is empty
    def test_formatweek_empty_week(self):
        calendar = Calendar()
        html = calendar.formatweek([], models.Task.objects)
        self.assertEqual(html, f'<tr>  </tr>')

    # unit test to assert that formatweek returns correct HTML when there are no tasks
    def test_formatweek_no_tasks(self):
        calendar = Calendar(year=2020, month=4)
        theweek = calendar.monthdays2calendar(calendar.year, calendar.month)[0]
        html = calendar.formatweek(theweek, models.Task.objects)
        inner_result = ''
        for d, weekday in theweek:
            inner_result += calendar.formatday(d, models.Task.objects)
        self.assertEqual(html, f'<tr> ' + inner_result + f' </tr>')

    #unit test to assert that formatweek returns correct HTML when there is a task
    def test_formatweek_tasks_exist(self):
        calendar = Calendar(year=2020, month=4)
        task = create_task(end_time=datetime.datetime(2020,4,3))
        task.save()
        theweek = calendar.monthdays2calendar(calendar.year, calendar.month)[0]
        html = calendar.formatweek(theweek, models.Task.objects)
        inner_result = ''
        for d, weekday in theweek:
            inner_result += calendar.formatday(d, models.Task.objects)
        self.assertEqual(html, f'<tr> ' + inner_result + f' </tr>')