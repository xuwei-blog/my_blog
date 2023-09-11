from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from .models import UserProfile, EmailVerifyRecord

#官方默认通过UserAdmin这个类注册到后台
from django.contrib.auth.admin import UserAdmin

#取消关联注册
admin.site.unregister(User)

# 定义关联对象的样式，StackedInline为纵向排列每一行，TabularInline为并排排列
class UserProfileInline(admin.StackedInline):
    model = UserProfile   # 关联的模型

# 关联UserProfile
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]


#注册User模型
admin.site.register(User, UserProfileAdmin)


#admin后台管理邮箱验证码
@admin.register(EmailVerifyRecord)
class EamilVerifyRecordAdmin(admin.ModelAdmin):
    '''Admin View for EamilVerifyRecord'''

    list_display = ('code',)