from django.db import models


class SoftDeleteManager(models.Manager):
    def save_soft_delete(self):
        self.is_deleted = True
        self.save()
        return True

    def get_soft_delete(self):
        return self.filter(is_deleted=True)

    def get_unsoft_delete(self):
        return self.filter(is_deleted=False)
