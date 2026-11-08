import io
from datetime import date, timedelta
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from food.models import FoodItem
from resources.models import Resource
from uploads.forms import UploadForm
from uploads.models import Upload
from users.models import User


def png_bytes():
    buf = io.BytesIO(); Image.new('RGB', (4, 4), 'red').save(buf, 'PNG'); return buf.getvalue()


class Fixes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='a@x.com', email='a@x.com', password='S3cure-pass-123')
        self.other = User.objects.create_user(username='b@x.com', email='b@x.com', password='S3cure-pass-123')
        self.client.force_login(self.user)

    def item(self, **kw):
        d = dict(user=self.user, name='Milk', category='dairy', quantity=1, unit='L',
                 purchase_date=date.today(), expiration_date=date.today() + timedelta(days=1), price='5.00')
        d.update(kw); return FoodItem.objects.create(**d)

    def test_recommendations_with_dairy(self):
        from food.utils import generate_recommendations
        Resource.objects.create(title='Store milk', description='d', url='https://example.com', category='storage_tips',
                                relevant_food_categories=['dairy'], tags=['expiration'])
        self.item()
        self.item(name='Cheese', expiration_date=date.today() - timedelta(days=2))
        generate_recommendations(self.user)

    def test_resources_list_filters(self):
        r = self.client.get(reverse('resources:resources_list'), {'tag': 'expiration', 'food_category': 'dairy'})
        self.assertEqual(r.status_code, 200)

    def test_delete_requires_post(self):
        it = self.item()
        self.assertEqual(self.client.get(reverse('food:inventory_delete', args=[it.pk])).status_code, 405)
        self.assertTrue(FoodItem.objects.filter(pk=it.pk).exists())
        self.client.post(reverse('food:inventory_delete', args=[it.pk]))
        self.assertFalse(FoodItem.objects.filter(pk=it.pk).exists())

    def test_edit_form_prefilled(self):
        it = self.item(notes='keep me')
        html = self.client.get(reverse('food:inventory_edit', args=[it.pk])).content.decode()
        self.assertIn('value="5.00"', html)
        self.assertIn(f'value="{it.expiration_date.isoformat()}"', html)
        self.assertIn('value="dairy" class="peer sr-only" checked', html)
        self.assertIn('value="L" selected', html)
        self.assertIn('name="notes" value="keep me"', html)

    def test_upload_flow(self):
        f = SimpleUploadedFile('r.png', png_bytes(), content_type='image/png')
        r = self.client.post(reverse('uploads:upload_form'), {'file': f, 'file_type': 'receipt', 'notes': ''})
        up = Upload.objects.get(user=self.user)
        self.assertEqual(self.client.get(reverse('uploads:upload_file', args=[up.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('uploads:link_to_inventory', args=[up.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('uploads:upload_detail', args=[up.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('uploads:upload_list')).status_code, 200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('uploads:upload_file', args=[up.pk])).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('uploads:upload_delete', args=[up.pk])).status_code, 405)
        self.client.post(reverse('uploads:upload_delete', args=[up.pk]))
        self.assertFalse(Upload.objects.filter(pk=up.pk).exists())

    def test_fake_png_rejected(self):
        f = SimpleUploadedFile('r.png', b'<?php echo 1; ?>', content_type='image/png')
        form = UploadForm(data={'file_type': 'receipt'}, files={'file': f})
        self.assertFalse(form.is_valid())

    def test_weak_password_rejected(self):
        self.client.logout()
        r = self.client.post(reverse('users:register'), {'full_name': 'C', 'email': 'c@x.com', 'password': 'abc',
                                                         'confirm_password': 'abc', 'household_size': 1, 'location': 'x'})
        self.assertFalse(User.objects.filter(email='c@x.com').exists())
        self.assertEqual(r.status_code, 200)

    @override_settings(GOOGLE_CLIENT_ID='cid')
    def test_google_unverified_email(self):
        self.client.logout()
        with mock.patch('users.views.id_token.verify_oauth2_token', return_value={'email': 'a@x.com', 'email_verified': False}):
            r = self.client.post(reverse('users:google_auth'), '{"credential": "t"}', content_type='application/json')
        self.assertEqual(r.status_code, 403)
        self.assertNotIn('_auth_user_id', self.client.session)
        with mock.patch('users.views.id_token.verify_oauth2_token', return_value={'email': 'a@x.com', 'email_verified': True}):
            r = self.client.post(reverse('users:google_auth'), '{"credential": "t"}', content_type='application/json')
        self.assertEqual(r.json()['status'], 'ok')

    def test_media_not_public(self):
        from django.urls import resolve, Resolver404
        with self.assertRaises(Resolver404):
            resolve('/media/uploads/x.png')
