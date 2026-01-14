"""
Models do app reserveme.
"""
from django.db import models
from django.contrib.auth.models import User


class ExampleModel(models.Model):
    """Model de exemplo para demonstrar a arquitetura."""
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome do exemplo'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do exemplo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_examples',
        verbose_name='Criado por'
    )
    
    class Meta:
        db_table = 'reserveme_example'
        verbose_name = 'Example'
        verbose_name_plural = 'Examples'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'<ExampleModel: {self.name}>'
