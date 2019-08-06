from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth.models import User
from django.conf import settings
import ldap
class Command(BaseCommand):

    help = 'Add a specific user from LDAP'                                                                        
    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=str) 

    def gen_random_password(self):
        import random
        random.seed()
        characters = 'abcdefghijklmnopqrstuvwxyzABCDFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?'
        passlen = 16
        password = "".join(random.sample(characters,passlen))
        return password

    def handle(self, *args, **options):
        l = ldap.initialize(settings.LDAP_URL)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(settings.LDAP_ADMIN_USER, settings.LDAP_ADMIN_PASSWORD)
        total = 0
        total_created = 0
        for user_id in options['user_id']:
            print("Looking up {}".format(user_id))
            results = l.search_s(settings.LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(cn={})".format(user_id))
            for e, r in results:
                username = r['cn'][0].decode('utf-8')
                first_name = r['givenName'][0].decode('utf-8')
                last_name = r['sn'][0].decode('utf-8')
                email = r['mail'][0].decode('utf-8')
                user, created = User.objects.get_or_create(username=username, email=email, first_name=first_name, last_name=last_name)
                total += 1
                if created:
                    user.set_password(self.gen_random_password())
                    user.save()
                    total_created += 1
                    print("Added {}".format(user_id))
                else:
                    print("{} already exists".format(user_id))
    print("Found {}/{} users, added {}".format(total, len(options['user_id']), total_created))
