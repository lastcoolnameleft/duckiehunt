# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Users(models.Model):
    ip_address = models.CharField(max_length=45)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=100)
    activation_code = models.CharField(max_length=40, blank=True, null=True)
    forgotten_password_code = models.CharField(max_length=40, blank=True, null=True)
    forgotten_password_time = models.PositiveIntegerField(blank=True, null=True)
    remember_code = models.CharField(max_length=40, blank=True, null=True)
    created_on = models.PositiveIntegerField()
    last_login = models.PositiveIntegerField(blank=True, null=True)
    active = models.PositiveIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'



class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    user_agent = models.CharField(max_length=200, blank=True, null=True)
    action = models.CharField(max_length=10, blank=True, null=True)
    client_ip = models.PositiveIntegerField(blank=True, null=True)
    duck_id = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CiSessions(models.Model):
    session_user_id = models.IntegerField()
    session_id = models.CharField(primary_key=True, max_length=40)
    ip_address = models.CharField(max_length=16)
    user_agent = models.CharField(max_length=150)
    last_page = models.CharField(max_length=150)
    last_activity = models.PositiveIntegerField()
    session_data = models.TextField(blank=True, null=True)
    user_data = models.TextField()

    class Meta:
        managed = False
        db_table = 'ci_sessions'


class ClGroupUri(models.Model):
    group_id = models.IntegerField()
    request_uri = models.CharField(max_length=40)
    is_admin = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'cl_group_uri'


class ClGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'cl_groups'


class ClUserAutologin(models.Model):
    key_id = models.CharField(primary_key=True, max_length=32)
    user_id = models.IntegerField()
    user_agent = models.CharField(max_length=150)
    last_ip = models.CharField(max_length=40)
    last_login = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cl_user_autologin'
        unique_together = (('key_id', 'user_id'),)


class ClUserProfile(models.Model):
    user_id = models.IntegerField(primary_key=True)
    fullname = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=25, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cl_user_profile'


class ClUserTemp(models.Model):
    user_ip = models.CharField(max_length=40)
    username = models.CharField(max_length=255)
    username_clean = models.CharField(max_length=255)
    password = models.CharField(max_length=34)
    email = models.CharField(max_length=100)
    activation_key = models.CharField(max_length=50)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cl_user_temp'


class ClUsers(models.Model):
    group_id = models.IntegerField()
    user_ip = models.CharField(max_length=40)
    username = models.CharField(unique=True, max_length=25)
    username_clean = models.CharField(max_length=25)
    password = models.CharField(max_length=34)
    email = models.CharField(max_length=100)
    banned = models.CharField(max_length=1)
    ban_reason = models.CharField(max_length=255, blank=True, null=True)
    login_attempts = models.PositiveIntegerField()
    newpass = models.CharField(max_length=34, blank=True, null=True)
    newpass_key = models.CharField(max_length=32, blank=True, null=True)
    newpass_time = models.DateTimeField(blank=True, null=True)
    active_time = models.PositiveIntegerField()
    last_visit = models.DateTimeField()
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cl_users'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Duck(models.Model):
    duck_id = models.IntegerField(primary_key=True)
    create_time = models.IntegerField()
    name = models.CharField(max_length=128, blank=True, null=True)
    current_owner_id = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    total_distance = models.FloatField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)

    def natural_key(self):
        return {'duck_id': self.duck_id, 'name': self.name}

    class Meta:
        managed = False
        db_table = 'duck'


class DuckAssign(models.Model):
    duck_id = models.IntegerField()
    user_id = models.IntegerField()
    duck_history_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_assign'


class DuckChoice(models.Model):
    comments = models.CharField(max_length=200)
    duck = models.ForeignKey('DuckDuck', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'duck_choice'


class DuckDuck(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'duck_duck'


class DuckHistory(models.Model):
    duck_history_id = models.AutoField(primary_key=True)
    duck_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    action_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField()
    user_ip = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_history'


class DuckHistoryAction(models.Model):
    duck_history_action_id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_history_action'


class DuckLocation(models.Model):
    duck_location_id = models.AutoField(primary_key=True)
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    link = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    duck_history_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)
    distance_to = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_location'


class DuckLocationLink(models.Model):
    duck_location_link_id = models.AutoField(primary_key=True)
    duck_location_id = models.IntegerField(blank=True, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_location_link'


class DuckLocationPhoto(models.Model):
    duck_location_photo_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, models.DO_NOTHING)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    flickr_thumbnail_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_location_photo'


class DuckTrack(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    duck_id = models.IntegerField(blank=True, null=True)
    duck_history_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_track'


class DuckUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duck_user'


class Groups(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'groups'


class LoginAttempts(models.Model):
    ip_address = models.CharField(max_length=15)
    login = models.CharField(max_length=100)
    time = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login_attempts'


class Permissions(models.Model):
    role_id = models.IntegerField()
    data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permissions'


class Roles(models.Model):
    parent_id = models.IntegerField()
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'roles'


class UserAutologin(models.Model):
    key_id = models.CharField(primary_key=True, max_length=32)
    user_id = models.IntegerField()
    user_agent = models.CharField(max_length=150)
    last_ip = models.CharField(max_length=40)
    last_login = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_autologin'
        unique_together = (('key_id', 'user_id'),)


class UserProfile(models.Model):
    user_id = models.IntegerField()
    country = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_profile'


class UserTemp(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=34)
    email = models.CharField(max_length=100)
    activation_key = models.CharField(max_length=50)
    last_ip = models.CharField(max_length=40)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_temp'



class UsersGroups(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING)
    group = models.ForeignKey(Groups, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_groups'
        unique_together = (('user', 'group'),)


class UsersOld(models.Model):
    role_id = models.IntegerField()
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=34)
    email = models.CharField(max_length=100)
    banned = models.IntegerField()
    ban_reason = models.CharField(max_length=255, blank=True, null=True)
    newpass = models.CharField(max_length=34, blank=True, null=True)
    newpass_key = models.CharField(max_length=32, blank=True, null=True)
    newpass_time = models.DateTimeField(blank=True, null=True)
    last_ip = models.CharField(max_length=40)
    last_login = models.DateTimeField()
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users_old'
