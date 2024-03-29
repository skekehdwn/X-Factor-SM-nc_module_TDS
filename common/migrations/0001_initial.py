# Generated by Django 4.0.3 on 2023-10-20 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Daily_Statistics',
            fields=[
                ('daily_statistics_num', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('classification', models.CharField(max_length=500)),
                ('item', models.TextField()),
                ('item_count', models.IntegerField()),
                ('statistics_collection_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Daily_Statistics_log',
            fields=[
                ('daily_statistics_num', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('classification', models.CharField(max_length=500)),
                ('item', models.TextField()),
                ('item_count', models.IntegerField()),
                ('statistics_collection_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Auth',
            fields=[
                ('auth_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('auth_name', models.CharField(max_length=500)),
                ('auth_url', models.CharField(max_length=500)),
                ('auth_num', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Common',
            fields=[
                ('computer_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('computer_name', models.CharField(max_length=100)),
                ('ip_address', models.CharField(max_length=100)),
                ('mac_address', models.CharField(max_length=100)),
                ('chassistype', models.CharField(max_length=100)),
                ('os_simple', models.CharField(max_length=100)),
                ('os_total', models.CharField(max_length=100)),
                ('os_version', models.CharField(max_length=500)),
                ('os_build', models.CharField(max_length=500)),
                ('hw_cpu', models.CharField(max_length=500)),
                ('hw_ram', models.CharField(max_length=500)),
                ('hw_mb', models.CharField(max_length=500)),
                ('hw_disk', models.CharField(max_length=500)),
                ('hw_gpu', models.CharField(max_length=500)),
                ('sw_list', models.TextField()),
                ('sw_ver_list', models.TextField()),
                ('sw_install', models.TextField(null=True)),
                ('sw_lastrun', models.TextField(null=True)),
                ('first_network', models.TextField(null=True)),
                ('last_network', models.TextField(null=True)),
                ('hotfix', models.TextField(null=True)),
                ('hotfix_date', models.TextField(null=True)),
                ('subnet', models.TextField(null=True)),
                ('memo', models.TextField(null=True)),
                ('essential1', models.CharField(max_length=100, null=True)),
                ('essential2', models.CharField(max_length=100, null=True)),
                ('essential3', models.CharField(max_length=100, null=True)),
                ('essential4', models.CharField(max_length=100, null=True)),
                ('essential5', models.CharField(max_length=100, null=True)),
                ('mem_use', models.CharField(max_length=100, null=True)),
                ('disk_use', models.CharField(max_length=100, null=True)),
                ('t_cpu', models.CharField(max_length=100, null=True)),
                ('logged_name', models.CharField(max_length=100, null=True)),
                ('user_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Common_Cache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computer_id', models.CharField(max_length=100)),
                ('computer_name', models.CharField(max_length=100)),
                ('ip_address', models.CharField(max_length=100)),
                ('mac_address', models.CharField(max_length=100)),
                ('chassistype', models.CharField(max_length=100)),
                ('os_simple', models.CharField(max_length=100)),
                ('os_total', models.CharField(max_length=100)),
                ('os_version', models.CharField(max_length=500)),
                ('os_build', models.CharField(max_length=500)),
                ('hw_cpu', models.CharField(max_length=500)),
                ('hw_ram', models.CharField(max_length=500)),
                ('hw_mb', models.CharField(max_length=500)),
                ('hw_disk', models.CharField(max_length=500)),
                ('hw_gpu', models.CharField(max_length=500)),
                ('sw_list', models.TextField()),
                ('sw_ver_list', models.TextField()),
                ('sw_install', models.TextField(null=True)),
                ('sw_lastrun', models.TextField(null=True)),
                ('first_network', models.TextField(null=True)),
                ('last_network', models.TextField(null=True)),
                ('hotfix', models.TextField(null=True)),
                ('hotfix_date', models.TextField(null=True)),
                ('subnet', models.TextField(null=True)),
                ('memo', models.TextField(null=True)),
                ('essential1', models.CharField(max_length=100, null=True)),
                ('essential2', models.CharField(max_length=100, null=True)),
                ('essential3', models.CharField(max_length=100, null=True)),
                ('essential4', models.CharField(max_length=100, null=True)),
                ('essential5', models.CharField(max_length=100, null=True)),
                ('mem_use', models.CharField(max_length=100, null=True)),
                ('disk_use', models.CharField(max_length=100, null=True)),
                ('t_cpu', models.CharField(max_length=100, null=True)),
                ('logged_name', models.CharField(max_length=100, null=True)),
                ('cache_date', models.DateTimeField(null=True)),
                ('user_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Daily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computer_id', models.CharField(max_length=100)),
                ('computer_name', models.CharField(max_length=100)),
                ('ip_address', models.CharField(max_length=100)),
                ('mac_address', models.CharField(max_length=100)),
                ('chassistype', models.CharField(max_length=100)),
                ('os_simple', models.CharField(max_length=100)),
                ('os_total', models.CharField(max_length=100)),
                ('os_version', models.CharField(max_length=500)),
                ('os_build', models.CharField(max_length=500)),
                ('hw_cpu', models.CharField(max_length=500)),
                ('hw_ram', models.CharField(max_length=500)),
                ('hw_mb', models.CharField(max_length=500)),
                ('hw_disk', models.CharField(max_length=500)),
                ('hw_gpu', models.CharField(max_length=500)),
                ('sw_list', models.TextField()),
                ('sw_ver_list', models.TextField()),
                ('sw_install', models.TextField(null=True)),
                ('sw_lastrun', models.TextField(null=True)),
                ('first_network', models.TextField(null=True)),
                ('last_network', models.TextField(null=True)),
                ('hotfix', models.TextField(null=True)),
                ('hotfix_date', models.TextField(null=True)),
                ('subnet', models.CharField(max_length=100)),
                ('memo', models.TextField(null=True)),
                ('essential1', models.CharField(max_length=100)),
                ('essential2', models.CharField(max_length=100)),
                ('essential3', models.CharField(max_length=100)),
                ('essential4', models.CharField(max_length=100)),
                ('essential5', models.CharField(max_length=100)),
                ('mem_use', models.CharField(max_length=100)),
                ('disk_use', models.CharField(max_length=100)),
                ('t_cpu', models.CharField(max_length=100)),
                ('security1', models.CharField(max_length=100)),
                ('security2', models.CharField(max_length=100)),
                ('security3', models.CharField(max_length=100)),
                ('security4', models.CharField(max_length=100)),
                ('security5', models.CharField(max_length=100)),
                ('security1_ver', models.CharField(max_length=100)),
                ('security2_ver', models.CharField(max_length=100)),
                ('security3_ver', models.CharField(max_length=100)),
                ('security4_ver', models.CharField(max_length=100)),
                ('security5_ver', models.CharField(max_length=100)),
                ('uuid', models.CharField(max_length=100)),
                ('multi_boot', models.CharField(max_length=100)),
                ('ext_chr', models.TextField()),
                ('ext_chr_ver', models.TextField()),
                ('ext_edg', models.TextField()),
                ('ext_edg_ver', models.TextField()),
                ('ext_fir', models.TextField()),
                ('ext_fir_ver', models.TextField()),
                ('logged_name', models.CharField(max_length=100, null=True)),
                ('user_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Group',
            fields=[
                ('group_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=500)),
                ('group_note', models.TextField(null=True)),
                ('computer_id_list', models.TextField(null=True)),
                ('computer_name_list', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_func', models.CharField(max_length=100)),
                ('log_item', models.CharField(max_length=100)),
                ('log_result', models.CharField(max_length=100)),
                ('log_user', models.CharField(max_length=100)),
                ('log_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_ncdb',
            fields=[
                ('companyCode', models.CharField(max_length=100, null=True)),
                ('userName', models.CharField(max_length=100, null=True)),
                ('userNameEn', models.CharField(max_length=100, null=True)),
                ('userId', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100, null=True)),
                ('empNo', models.CharField(max_length=100, null=True)),
                ('joinDate', models.CharField(max_length=100, null=True)),
                ('retireDate', models.CharField(max_length=100, null=True)),
                ('deptCode', models.CharField(max_length=100, null=True)),
                ('deptName', models.CharField(max_length=100, null=True)),
                ('managerUserName', models.CharField(max_length=100, null=True)),
                ('managerUserId', models.CharField(max_length=100, null=True)),
                ('managerEmpNo', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Report',
            fields=[
                ('report_num', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('classification', models.CharField(max_length=500)),
                ('item', models.TextField()),
                ('item_count', models.IntegerField()),
                ('report_collection_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Xuser',
            fields=[
                ('x_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('x_pw', models.CharField(max_length=500, null=True)),
                ('x_name', models.CharField(max_length=50, null=True)),
                ('x_email', models.CharField(max_length=500, null=True)),
                ('x_auth', models.CharField(max_length=500, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Xuser_Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xgroup_name', models.CharField(max_length=500)),
                ('xgroup_note', models.TextField(null=True)),
                ('xuser_id_list', models.TextField(null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Xuser_Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_use', models.CharField(max_length=500)),
                ('xfactor_auth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth', to='common.xfactor_auth')),
                ('xfactor_xuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='xuser', to='common.xfactor_xuser')),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Xgroup_Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_use', models.CharField(max_length=500)),
                ('xfactor_xgroup', models.TextField(null=True)),
                ('xfactor_auth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_auth', to='common.xfactor_auth')),
                ('xgroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='xgroup', to='common.xfactor_xuser_group')),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Security',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('security1', models.CharField(max_length=100)),
                ('security2', models.CharField(max_length=100)),
                ('security3', models.CharField(max_length=100)),
                ('security4', models.CharField(max_length=100)),
                ('security5', models.CharField(max_length=100)),
                ('security1_ver', models.CharField(max_length=100)),
                ('security2_ver', models.CharField(max_length=100)),
                ('security3_ver', models.CharField(max_length=100)),
                ('security4_ver', models.CharField(max_length=100)),
                ('security5_ver', models.CharField(max_length=100)),
                ('uuid', models.CharField(max_length=500)),
                ('multi_boot', models.TextField()),
                ('first_network', models.TextField()),
                ('last_boot', models.TextField()),
                ('ext_chr', models.TextField()),
                ('ext_chr_ver', models.TextField()),
                ('ext_edg', models.TextField()),
                ('ext_edg_ver', models.TextField()),
                ('ext_fir', models.TextField()),
                ('ext_fir_ver', models.TextField()),
                ('user_date', models.DateTimeField(auto_now_add=True)),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.xfactor_common')),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mem_use', models.TextField()),
                ('disk_use', models.TextField()),
                ('user_date', models.DateTimeField(auto_now_add=True)),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.xfactor_common')),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Nano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=50, null=True)),
                ('user_email', models.EmailField(max_length=254, null=True)),
                ('user_dep', models.CharField(max_length=50, null=True)),
                ('domain_id', models.CharField(max_length=50, null=True)),
                ('open_id', models.CharField(max_length=50, null=True)),
                ('xfactor_id', models.CharField(max_length=50, null=True)),
                ('depno', models.CharField(max_length=50, null=True)),
                ('location', models.CharField(max_length=100, null=True)),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.xfactor_common')),
            ],
        ),
        migrations.CreateModel(
            name='Xfactor_Deploy',
            fields=[
                ('deploy_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('deploy_name', models.CharField(max_length=500)),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.xfactor_group')),
            ],
        ),
    ]
