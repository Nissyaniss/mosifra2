from django.apps import apps


def test_accounts_app_installed():
    assert apps.is_installed("accounts")
