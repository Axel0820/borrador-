from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea los grupos de usuarios: Cliente, Peluquero, Cajero, Vendedor, Gerente'
    
    def handle(self, *args, **options):
        grupos = ['Cliente', 'Peluquero', 'Cajero', 'Vendedor', 'Gerente']
        
        for nombre_grupo in grupos:
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Grupo "{nombre_grupo}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Grupo "{nombre_grupo}" ya existe')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Sistema de grupos configurado correctamente')
        )
