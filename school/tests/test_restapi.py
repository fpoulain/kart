import json
import datetime
from django.utils import timezone
# import time
from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase
from django.urls import reverse

from people.tests.factories import ArtistFactory
from school.models import StudentApplication, StudentApplicationSetup, Promotion


class TestApplicationEndPoint(TestCase):
    """
    Tests concernants le endpoint des Student Application
    """

    def setUp(self):
        self.artist = ArtistFactory()
        self.user = self.artist.user

        # save generate token
        self.token = ""
        self.client_auth = APIClient()

    def tearDown(self):
        pass

    def _get_list(self):
        url = reverse('studentapplication-list')
        return self.client.get(url)

    def _get_list_auth(self):
        url = reverse('studentapplication-list')
        return self.client_auth.get(url)

    def test_list(self):
        """
        Test list of applications without authentification
        """
        # set up a candidature
        application = StudentApplication(artist=self.artist)
        application.save()

        self.token = ""
        response = self._get_list()
        candidatures = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(candidatures)
        self.assertEqual(len(candidatures), 1)
        # info is NOT accessible when anonymous user
        self.assertRaises(KeyError, lambda: candidatures[0]['current_year_application_count'])

    def test_list_auth(self):
        """
        Test list of applications with authentification
        """
        # set up a candidature
        application = StudentApplication(artist=self.artist)
        application.save()

        self.client_auth.force_authenticate(user=self.user)
        response = self._get_list_auth()
        candidature = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # info is accessible when user is auth
        assert candidature[0]['current_year_application_count'] is not None

    def test_create_student_application(self):
        """
        Test creating an studentapplication
        """
        self.client_auth.force_authenticate(user=self.user)
        studentapplication_url = reverse('studentapplication-list')
        response = self.client_auth.post(studentapplication_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentApplication.objects.count(), 1)
        self.assertEqual(StudentApplication.objects.last().artist.user.first_name, self.user.first_name)

    def test_update_student_application(self):
        """
        Test creating an studentapplication
        """
        # set up a campaign
        promotion = Promotion(starting_year=2000, ending_year=2001)
        promotion.save()
        campaign = StudentApplicationSetup(candidature_date_start=timezone.now(),
                                           candidature_date_end=timezone.now() + datetime.timedelta(days=1),
                                           promotion=promotion,
                                           is_current_setup=True,)
        campaign.save()
        # add a candidature
        application = StudentApplication(artist=self.artist, campaign=campaign)
        application.save()
        self.client_auth.force_authenticate(user=self.user)
        studentapplication_url = reverse('studentapplication-detail', kwargs={'pk': application.pk})
        # update an info
        response = self.client_auth.patch(studentapplication_url,
                                          data={'remote_interview': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # update more than one info
        response = self.client_auth.patch(studentapplication_url,
                                          data={'remote_interview': 'true', 'remote_interview_type': 'Skype'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestApplicationSetupEndPoint(TestCase):
    """
    Tests concernants le endpoint des Student Application Setups
    """
    def setUp(self):
        promotion = Promotion(starting_year=2000, ending_year=2001)
        promotion.save()
        campaign = StudentApplicationSetup(candidature_date_start=timezone.now() - datetime.timedelta(days=1),
                                           candidature_date_end=timezone.now() + datetime.timedelta(days=1),
                                           promotion=promotion,
                                           is_current_setup=True,)
        campaign.save()

        campaign = StudentApplicationSetup(candidature_date_start=timezone.now() - datetime.timedelta(days=2),
                                           candidature_date_end=timezone.now() - datetime.timedelta(days=1),
                                           promotion=promotion,
                                           is_current_setup=False,)
        campaign.save()

    def tearDown(self):
        pass

    def _get_list(self):
        url = reverse('studentapplicationsetup-list')
        return self.client.get(url)

    def _get_current_campaign(self):
        url = reverse('studentapplicationsetup-list')
        return self.client.get("{}?is_current_setup=true".format(url))

    def test_list(self):
        """
        Test list of applications without authentification
        """
        response = self._get_list()
        campaign = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(campaign), 2)

    def test_campaign_open(self):
        """
        Test list of applications without authentification
        """
        response = self._get_current_campaign()
        campaign = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(campaign), 1)
        # info is True
        self.assertTrue(campaign[0]['candidature_open'])
