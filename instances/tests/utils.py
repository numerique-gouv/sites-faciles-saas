from contacts.models import Contact
from instances.models import Instance


def create_instance(status="REQUEST", **kwargs):
    """
    Creates an instance without triggering the Scalingo calls made by save()
    for advanced statuses: the status is set afterwards with a queryset update.
    """
    contact, _created = Contact.objects.get_or_create(
        email="camille@example.com",
        defaults={"first_name": "Camille", "last_name": "Dupont"},
    )
    kwargs.setdefault("name", "Test")
    kwargs.setdefault("scalingo_application_name", "sf-test")
    instance = Instance.objects.create(main_contact=contact, **kwargs)

    if status != "REQUEST":
        Instance.objects.filter(pk=instance.pk).update(status=status)
        instance.refresh_from_db()

    return instance


def configure_scalingo_mock(sc, host_url=""):
    """
    Sets sensible return values on a mocked Scalingo client
    """
    sc.app_variables_dict.return_value = {"SECRET_KEY": "s3cr3t", "HOST_URL": host_url}
    sc.app_variables_bulk_update.return_value = {"variables": []}
    sc.app_detail.return_value = {"app": {"status": "running"}}
    sc.app_containers.return_value = {"containers": [{"name": "web", "amount": 1}]}
    sc.app_addon_list.return_value = {"addons": []}
    sc.app_addon_detail.return_value = {"addon": {"status": "running"}}
    sc.app_deployment_list.return_value = {
        "deployments": [
            {
                "id": "dep-1",
                "status": "success",
                "created_at": "2026-01-01T10:00:00.000+01:00",
            }
        ]
    }
    sc.app_run.return_value = {}
    sc.app_scale.return_value = {"status": "success", "message": ""}
    return sc
