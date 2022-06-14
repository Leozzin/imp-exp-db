from unittest import result
import zipfile
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.conf import settings
from imp_exp_db.settings import BASE_DIR

from loger.models import *
from document.models import *

import mysql.connector
from zipfile import ZipFile
import datetime
import shutil
import os

def ending():
    loger = Loger(content='Fin')
    loger.save()

def login_infos():
    host = 'localhost'
    username = 'om_user'
    password = 'MVlIamWevIph8CSC'
    return host, username, password

def indexPgae(request, db):
    host, username, password = login_infos()
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db
        )
    except:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' not found!</center></h1>")
    return render(request, "index.html")

def export_db(request, db):
    host, username, password = login_infos()
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db
        )
    except:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' not found!</center></h1>")
    
    cursor = conn.cursor()
    cursor.execute("show tables")
    tables = [table[0] for table in cursor]
    
    result_sturucture = []
    content_structure = ''
    for table in tables:
        loger = Loger(content=f"Saving table structure of {table}")
        loger.save()
        query = "show create table {}".format(table)
        cursor.execute(query)
        for row in cursor:
            result_sturucture.append(row[1])
            content_structure += 'DROP TABLE IF EXISTS `{}`;\n'.format(table)
            content_structure += row[1] + ";\n"
    
    result_data = []
    content_data = ''
    for table in tables:
        loger = Loger(content=f"Saving table data of {table}")
        loger.save()
        # query = f"select count(id) from {table}"
        # cursor.execute(query)
        # count=0
        # for row in cursor:
        #     count = row[0]
        query = f"select * from {table}"
        print(query)
        cursor.execute(query)
        fetchall =[]
        fetchall = cursor.fetchall()
        # print(fetchall)
        for row in fetchall:
            # lls = [str(val).encode('utf-8') for val in row]
            # print(lls)
            # print(row)
            content_data += f"INSERT INTO {table} VALUES"
            if row != None:
                content_data += f"\n{row},"
            content_data[-1] = ';\n'

    f = open(settings.MEDIA_ROOT + "structure/structure.sql", "w+")
    f.writelines(content_structure)
    f.close()
    with open(settings.MEDIA_ROOT + "data/data.sql", "w+", encoding='utf-8') as f:
        f.writelines(content_data)
    # f = open(settings.MEDIA_ROOT + "data/data.sql", "w+")
    # f.writelines(content_data)
    # f.close()
    # zipfilename = datetime.datetime.now().strftime("%d-%m-%Y__%H-%M")
    with ZipFile(settings.MEDIA_ROOT + "zip-files/"+db+".zip", "w") as z :
        structure_file = settings.MEDIA_ROOT+"structure/structure.sql"
        data_file = settings.MEDIA_ROOT+"data/data.sql"
        z.write(structure_file, os.path.basename(structure_file))
        z.write(data_file, os.path.basename(data_file))
    struct = Structure(document=settings.MEDIA_ROOT+"structure/structure.sql")
    struct.save()
    data = Data(document=settings.MEDIA_ROOT+"data/data.sql")
    data.save()

    ending()
    return JsonResponse({"message": "done"}, safe=False)

def get_log(request, id):
    log = Loger.objects.filter(id__gt=id).values()
    data = dict(log[0])
    if log[0]['content'] == 'Fin':
        logs = Loger.objects.all()
        logs.delete()
    return JsonResponse(data, safe=False)

def import_db(request, db):

    host, username, password = login_infos()
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db
        )
    except:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' not found!</center></h1>")
    
    cursor = conn.cursor()
    
    shutil.unpack_archive(settings.MEDIA_ROOT + "zip-files/"+db+".zip", settings.MEDIA_ROOT + "zip-files")
    
    with open(settings.MEDIA_ROOT + "zip-files/structure.sql", "r") as struct_file:
        structure_query = struct_file.readlines()
        query = "".join(structure_query)
        # print(query)
        result = cursor.execute(query, multi=True)
        try:
            for res in result:
                pass
        except Exception as e:
            pass
    
    with open(settings.MEDIA_ROOT + "zip-files/data.sql", "r", encoding='utf-8') as data_file:
        data_query = data_file.readlines()
        query = "".join(data_query)
        result = cursor.execute(query, multi=True)
        try:
            for res in result:
                pass
        except Exception as e:
            pass
        conn.commit()


    return JsonResponse({"message": "done"}, safe=False)


def exp(request, db):
    host, username, password = login_infos()
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db
        )
    except:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' not found!</center></h1>")
    
    db_file = BASE_DIR / f'media/db/{db}.sql'
    # os.system('mysqldump -u root -p%s database > database.sql' % password)
    os.system(f'mysqldump -u {username} -p{password} {db} > {db_file}')
    list_zips = os.listdir(settings.MEDIA_ROOT + "zip-files")
    for f in list_zips:
        if db+'__' in f:
            os.remove(settings.MEDIA_ROOT + "zip-files/" + f)
    exp_time = datetime.datetime.now().strftime("%d-%m-%Y__%H-%M")
    with ZipFile(settings.MEDIA_ROOT + "zip-files/"+db+"__"+exp_time+".zip", "w") as z :
        db_file = BASE_DIR / f'media/db/{db}.sql'
        z.write(db_file, os.path.basename(db_file))

    return JsonResponse({"export": "done"}, safe=False)

def imp(request, db):
    host, username, password = login_infos()
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db
        )
    except:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' not found!</center></h1>")
    
    db_filename = ""
    list_zips = os.listdir(settings.MEDIA_ROOT + "zip-files")
    for f in list_zips:
        if db+'__' in f:
            db_filename = f
            break
    else:
        return HttpResponseNotFound("<h1><center>The database '"+db+"' didn't have a backup file!</center></h1>")
    shutil.unpack_archive(settings.MEDIA_ROOT + "zip-files/"+db_filename, settings.MEDIA_ROOT + "zip-files")
    db_file = settings.MEDIA_ROOT + "zip-files/" + db + ".sql"
    # os.system('mysqldump -u root -p%s database > database.sql' % password)
    os.system(f'mysql -u {username} -p{password} {db} < {db_file}')
    os.remove(db_file)
    return JsonResponse({"import": "done"}, safe=False)