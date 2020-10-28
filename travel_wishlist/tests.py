from django.test import TestCase
from django.urls import reverse

from .models import Place

class TestHomePage(TestCase):

    def test_home_page_shows_empty_list_message_for_empty_database(self):
        home_page_url = reverse('place_list')
        response = self.client.get(home_page_url)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'You have no places in your wishlist')


class TestVisitedPage(TestCase):

    def test_visited_page_shows_empty_list_message_for_empty_database(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'You have not visited any places yet')

class TestVisitedList(TestCase):

    fixtures = ['test_places']

    def test_viewing_places_visited_shows_visited_places(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')

        self.assertNotContains(response, 'Tokyo')
        self.assertNotContains(response, 'New York')
        self.assertContains(response, 'San Francisco')
        self.assertContains(response, 'Moab')

class TestAddNewPlace(TestCase):

    def test_add_new_unvisited_place_to_wishlist(self):

        add_place_url = reverse('place_list')
        new_place_data = {'name': 'Tokyo', 'visited': False}

        response = self.client.post(add_place_url, new_place_data, follow=True)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html') #check correct template used

        response_places = response.context['places'] #what data used to populate
        self.assertEqual(1, len(response_places))
        tokyo_response = response_places[0]

        tokyo_in_database = Place.objects.get(name='Tokyo', visited=False)

        self.assertEqual(tokyo_in_database, tokyo_response)

        response = self.client.post(reverse('place_list'), {'name': 'Yosemite', 'visited': False}, follow=True)

        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        response_places = response.context['places']
        self.assertEqual(2, len(response_places))

        place_in_database = Place.objects.get(name='Yosemite', visited=False)
        place_in_database = Place.objects.get(name='Tokyo', visited=False)

        places_in_database = Place.objects.all()

        self.assertCountEqual(list(places_in_database), list(response_places))

    def test_add_new_visited_place_to_wishlist(self):

        response = self.client.post(reverse('place_list'), {'name': 'Tokyo', 'visited': True}, follow=True)

        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        response_places = response.context['places']

        self.assertEqual(0, len(response_places))

        place_in_database = Place.objects.get(name='Tokyo', visited=True)


class TestVisitPlace(TestCase):

    fixtures = ['test_places']

    def test_visit_place(self):

        visit_place_url = reverse('place_was_visited', args=(2, ))
        response = self.client.post(visit_place_url, follow=True)

        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        self.assertNotContains(response, 'New York')

        new_york = Place.objects.get(pk=2)

        self.assertTrue(new_york.visited)

    def test_visit_non_existent_place(self):

        visit_place_url = reverse('place_was_visited', args=(12314, ))
        response = self.client.post(visit_place_url, follow=True)
        self.assertEqual(404, response.status_code)