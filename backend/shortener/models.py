import string
from random import choice, randint

from django.db import models

from core.constants import MAX_HASH, MAX_HASH_LEN, MIN_HASH, URL_LEN


def gen_hash() -> str:
    """Random str generator."""

    return ''.join(
        choice(string.ascii_letters + string.digits)
        for _ in range(randint(MIN_HASH, MAX_HASH))
    )


class LinkMapped(models.Model):
    """Short links model."""

    url_hash = models.CharField(
        max_length=MAX_HASH_LEN,
        default=gen_hash,
        unique=True
    )
    original_url = models.CharField(
        max_length=URL_LEN
    )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return f'{self.original_url} -> {self.url_hash}'
