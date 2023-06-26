from flask import Flask, render_template, redirect, request, session, flash, jsonify, url_for
from werkzeug.datastructures import FileStorage

from flask_mysqldb import MySQL
import hashlib
import boto3, botocore
import requests, json
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy

from datetime import datetime, timedelta
import pytz
import time
from time import mktime
import os
import time
from werkzeug.utils import secure_filename

from models.projects import projects
from constants.constants import project_fields, roles, materials

from PIL import Image
from io import BytesIO
import random
import json
import uuid



# Debit note

# Indent audit trail

# Project co ordinator wise order indents

# All Bills Project co ordinator

# Line break check on work order

# Shifting entry to not have edit button on view inventory

# Do not include transportation and laoading unloading in total amount 


# Last labour stage id 412
app = Flask(__name__)
# Sql setup
app.config['MYSQL_HOST'] = '166.62.6.102'
app.config['MYSQL_USER'] = 'buildahome'
app.config['MYSQL_PASSWORD'] = 'build*2019'
app.config['MYSQL_DB'] = 'buildahome2016'
app.config['UPLOAD_FOLDER'] = '../static/files'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
app.config['S3_SECRET'] = os.environ.get('S3_SECRET')
app.config['S3_KEY'] = os.environ.get('S3_KEY')
app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET')
app.config['S3_LOCATION'] = os.environ.get('S3_LOCATION')
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

mysql = MySQL(app)

s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
)

app.secret_key = 'bAhSessionKey'
ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpeg', 'jpg']

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def getProjectName(project_id):
    cur = mysql.connection.cursor()
    query = 'SELECT project_name from projects WHERE project_id='+str(project_id)
    cur.execute(query)
    result = cur.fetchone()
    if result is not None:
        return str(result[0])
    else:
        return 'Invalid project'


def make_entry_in_audit_log(activity):
    cur = mysql.connection.cursor()
    query = 'INSERT into erp_audit_log(activity, time) values (%s, %s)'
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    timestamp = current_time.strftime('%d-%m-%Y %H:%M:%S')
    cur.execute(query, (activity, timestamp))
    mysql.connection.commit()    


def send_to_s3(file, bucket_name, filename, acl="public-read", content_type=''):
    try:
        if content_type == '':
            content_type = file.content_type
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": content_type  # Set appropriate content type as per the file
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return str(e)
    return 'success'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_projects():
    cur = mysql.connection.cursor()
    projects = []
    if len(get_projects_for_current_user()) > 0:
        if session['role'] not in ['Super Admin', 'COO', 'QS Head','Purchase Head', 'Site Engineer', 'Design Head','QS Info', 'Billing', 'Planning','Finance']:
            query = 'SELECT project_id, project_name from projects WHERE is_approved=1 AND archived=0 ' \
                    'AND project_id IN ' + str(get_projects_for_current_user())+ ' ORDER BY project_number'
            cur.execute(query)
            projects = cur.fetchall()
        else:
            query = 'SELECT project_id, project_name from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
            cur.execute(query)
            projects = cur.fetchall()
    return projects


def get_projects_for_current_user(user_id = '', role = ''):
    if 'user_id' in session:
        user_id = session['user_id']
        role = session['role']
        cur = mysql.connection.cursor()
    if role in ['Super Admin', 'COO', 'QS Head', 'Purchase Head', 'Site Engineer', 'Design Head', 'Billing', 'Planning','QS Info','Finance']:
        return ('All')
    elif role == 'Project Coordinator':
        query = 'SELECT project_id from project_operations_team WHERE co_ordinator=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Project Manager':
        query = 'SELECT project_id from project_operations_team WHERE project_manager=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Purchase Executive':
        query = 'SELECT project_id from project_operations_team WHERE purchase_executive=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'QS Engineer':
        query = 'SELECT project_id from project_operations_team WHERE qs_engineer=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Architect':
        query = 'SELECT project_id from project_design_team WHERE architect=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            if len(str(i[0])) > 0:
                projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Structural Designer':
        query = 'SELECT project_id from project_design_team WHERE structural_designer=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Electrical Designer':
        query = 'SELECT project_id from project_design_team WHERE electrical_designer=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'PHE Designer':
        query = 'SELECT project_id from project_design_team WHERE phe_designer=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    elif role == 'Senior Architect':
        query = 'SELECT project_id from project_design_team WHERE senior_architect=' + str(user_id)
        cur.execute(query)
        result = cur.fetchall()
        projects = []
        for i in result:
            projects.append(i[0])
        if len(projects) == 1:
            projects.append(0)
        return tuple(projects)
    else:
        return []

@app.route('/set_material_timestamps', methods=['GET'])
def set_material_timestamps():
    cur = mysql.connection.cursor()
    query = 'SELECT id, created_at from procurement'
    cur.execute(query)
    res = cur.fetchall()
    for i in res:
        if str(i[1]).strip() != '':
            time = datetime.strptime(str(i[1]) , '%d %m %Y at %H %M').strftime('%Y-%m-%d %H:%M:%S')
            IST = pytz.timezone('Asia/Kolkata')

            update_query = 'UPDATE procurement SET created_at_datetime="'+time+'" WHERE id='+str(i[0])
            cur.execute(update_query)

    mysql.connection.commit()

    return 'Done'

@app.route('/documents', methods=['GET'])
def documents():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    project_id = request.args['project_id']
    cur = mysql.connection.cursor()
    query = 'SELECT * from project_documents WHERE project_id='+str(project_id)
    cur.execute(query)
    res = cur.fetchall()

    return render_template('documents.html', documents=res)

@app.route('/add_document', methods=['POST'])
def add_document():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    
    project_id = request.form['project_id']
    name = request.form['name']
    type = 'custom'

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            picture_filename = str(project_id)+'_'+ filename
            output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
            if output != 'success':
                flash('File upload failed', 'danger')
                return redirect(request.referrer)
            else:
                cur = mysql.connection.cursor()
                query = 'INSERT into project_documents(name, filename, type, project_id) values(%s,%s,%s,%s)'
                cur.execute(query, (name, str(project_id)+'_'+ filename, type, project_id))
                mysql.connection.commit()
                flash('File uploaded', 'success')
                return redirect(request.referrer)
            
@app.route('/delete_project_doc', methods=['GET'])
def delete_project_doc():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    if session['role'] not in ['Super Admin']:
        flash('You do not have permission to view that page', 'danger')
        return redirect('/login')
    
    id = request.args['id']
    cur = mysql.connection.cursor()
    query = 'DELETE from project_documents WHERE id='+str(id)
    cur.execute(query)
    mysql.connection.commit()
    
    flash('File deleted', 'danger')
    return redirect(request.referrer)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        data = {}
        projects = get_projects()
        if 'project_id' in request.args:
            project_id = request.args['project_id']

            cur = mysql.connection.cursor()

            project_value_query = 'SELECT project_value from projects WHERE project_id = '+str(project_id)
            cur.execute(project_value_query)
            res = cur.fetchone()
            if res is not None:
                try:
                    data['project_value'] = int(res[0])
                except:
                    return 'Project value incorrect'


            data['total_nt'] = 0
            data['total_billed'] = 0
            data['total_outstanding'] = 0

            tasks_query = 'SELECT payment_percentage, paid, due, is_non_tender_task, task_name from Tasks WHERE project_id='+str(project_id)
            cur.execute(tasks_query)
            res = cur.fetchall()
            if res is not None:
                for task in res:
                    if str(task[3]) == '1':
                        if str(task[0]).strip() != '':  
                            try:
                                data['total_nt'] += float(str(task[0]).strip())
                                data['total_nt'] = int(data['total_nt'])
                            except:
                                return 'Error: Task '+  str(task[4]) + ' has value '+ str(task[0]) +' which is not a number' 
                    else:
                        if str(task[0]).strip() != '':                     
                            try:
                                task_value =  data['project_value'] * float(str(task[0]).strip()) // 100
                                if str(task[2]) == '1':
                                    data['total_billed'] += task_value
                                    data['total_billed'] = int(data['total_billed'])
                                if str(task[2]) == '1' and str(task[1]) == '0':
                                    data['total_outstanding'] += task_value
                                    data['total_outstanding'] = int(data['total_outstanding'])
                            except:
                                return 'Error: Task '+ str(task[4]) + ' has value '+ str(task[0]) +' which is not a number' 

            data['total_material_spend'] = 0
            data['total_material_difference_cost'] = 0

            procurement_query = 'SELECT total_amount, difference_cost, id FROM procurement WHERE project_id='+str(project_id)
            cur.execute(procurement_query)
            res = cur.fetchall()
            if res is not None:
                for entry in res:
                    if str(entry[0]).strip() != '':
                        try:  
                            data['total_material_spend'] += int(float(str(entry[0]).strip()))
                        except:
                            return 'Error: Material Entry with id '+ str(entry[2]) + ' has incorrect amount'
                    if str(entry[1]).strip() != '':
                        try:  
                            data['total_material_difference_cost'] += int(float(str(entry[1]).strip()))
                        except:
                            return 'Error: Material Entry with id '+ str(entry[2]) + ' has incorrect difference cost'
                    
            data['total_WO_spend'] = 0
            data['total_WO_value'] = 0
            data['total_WO_NT'] = 0

            work_order_value_query = 'SELECT id, wo_number, value, contractor_id, trade from work_orders WHERE project_id='+ str(project_id)
            cur.execute(work_order_value_query)
            res = cur.fetchall()

            work_order_ids = []

            if res is not None:
                for wo in res:
                    if str(wo[2]).strip() != '':
                        try:
                            data['total_WO_value'] += int(float(str(wo[2]).strip().replace(',','').replace('/','').replace('\\','').replace('-','')))
                        except:
                            return 'Error: Value incorrect for work order with id '+ str(wo[0]) +' and number '+ str(wo[1])
                    work_order_id = str(wo[0]).strip()
                    if work_order_id not in work_order_ids:
                        work_order_ids.append(work_order_id)

                        contractor_id = wo[3]
                        trade = wo[4]
                        contractor_query = 'SELECT code from contractors WHERE id='+str(contractor_id)
                        cur.execute(contractor_query)
                        cresult = cur.fetchone()
                        if cresult is not None:
                            contractor_code = cresult[0]

                            bills_query = 'SELECT SUM(amount), COUNT(amount) from wo_bills WHERE trade="'+str(trade)+'" AND contractor_code="'+str(contractor_code)+'" AND project_id='+str(project_id)
                            cur.execute(bills_query)
                            bres = cur.fetchone()
                            if bres is not None and str(bres[1]) != '0':
                                if str(bres[0]).strip() != '' and str(bres[0]).strip() != 'NULL':
                                    try:
                                        data['total_WO_spend'] += int(float(str(bres[0]).strip().replace(',','').replace('/','').replace('\\','').replace('-','')))
                                    except:
                                        return 'Error: Amount incorrect for bill with trade "'+str(trade)+'" AND contractor_code "'+str(contractor_code)
                        
            nt_query = 'SELECT SUM(total_payable), id FROM wo_bills WHERE project_id='+str(project_id)+' AND trade="NT/NMR"'
            cur = mysql.connection.cursor()
            cur.execute(nt_query)
            nt_query_res = cur.fetchone()
            if nt_query_res is not None:
                try:
                    data['total_WO_NT'] += int(float(str(nt_query_res[0]).strip().replace(',','').replace('/','').replace('\\','').replace('-','')))
                except:
                    return 'Error: Amount incorrect for nt bill with id '+ str(nt_query_res[1]) 


            return render_template('expenses.html', data=data, projects=projects)
        
        return render_template('expenses.html', projects=projects)

@app.route('/reports', methods=['GET'])
def reports():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO','Planning']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    return render_template('reports.html')

@app.route('/material_report', methods=['GET'])
def material_report():
    cur = mysql.connection.cursor()
    get_projects_query = 'SELECT project_id, project_number, project_name from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
    cur.execute(get_projects_query)
    projects = cur.fetchall()
    
    materials_column_no = {}

    rb = open_workbook("../static/material_report.xls")
    wb = copy(rb)
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    current_time = now.strftime('%d-%m-%Y')
    current_datetime = now.strftime('%d-%m-%Y %H:%M')
    ws = wb.add_sheet(' ' + str(now.strftime('%d-%m-%Y %H-%M-%S')))
    style = xlwt.XFStyle()

    ws.write(1, 0, 'Report as on '+current_datetime)
    ws.write(2, 0, 'Project Name')
    ws.write(2, 1, 'Project Number')

    heading_row_column_no = 2

    project_row_number = 3

    ws.col(0).width = 5000

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font

    for project in projects:
        project_id = project[0]
        project_number = project[1]
        project_name = project[2]

        ws.write(project_row_number, 0, project_name)
        ws.write(project_row_number, 1, project_number)

        project_material_cost = {}
        project_material_difference_cost = {}

        material_query = 'SELECT material, total_amount, difference_cost FROM procurement WHERE project_id='+str(project_id)
        cur.execute(material_query)
        result = cur.fetchall()
        for item in result:
            material = item[0]
            if material not in materials_column_no.keys():
                materials_column_no[material] = heading_row_column_no
                
                ws.col(heading_row_column_no).width = 5000
                ws.write(2, heading_row_column_no, material)
                heading_row_column_no += 1
                
                materials_column_no[material+ " DC"] = heading_row_column_no
                
                ws.col(heading_row_column_no).width = 5000
                ws.write(2, heading_row_column_no, material+ " DC")
                heading_row_column_no += 1
                

            total_amount = item[1]
            if material not in project_material_cost.keys():
                try:
                    project_material_cost[material] = int(float(total_amount)) 
                except:
                    print()
            else:
                try:
                    project_material_cost[material] = project_material_cost[material] + int(float(total_amount)) 
                except:
                    print()
            

            difference_cost = item[2]
            if material not in project_material_difference_cost.keys():
                try:
                    project_material_difference_cost[material] = int(float(difference_cost)) 
                except:
                    print()
            else:
                try:
                    project_material_difference_cost[material] = project_material_difference_cost[material] + int(float(difference_cost)) 
                except:
                    print()

        for material in project_material_cost:
            ws.write(project_row_number, materials_column_no[material], project_material_cost[material])

        for material in project_material_difference_cost:
            ws.write(project_row_number, materials_column_no[material + ' DC'], project_material_difference_cost[material])
        
        project_row_number += 1    

    wb.save('../static/material_report.xls')

    return 'Job done!'

@app.route('/trade_report', methods=['GET'])
def trade_report():
    cur = mysql.connection.cursor()
    get_projects_query = 'SELECT project_id, project_number, project_name from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
    cur.execute(get_projects_query)
    projects = cur.fetchall()
    
    trade_column_no = {}

    rb = open_workbook("../static/trade_report.xls")
    wb = copy(rb)
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    current_time = now.strftime('%d-%m-%Y')
    current_datetime = now.strftime('%d-%m-%Y %H:%M')
    ws = wb.add_sheet(' ' + str(now.strftime('%d-%m-%Y %H-%M-%S')))
    style = xlwt.XFStyle()

    ws.write(1, 0, 'Report as on '+current_datetime)
    ws.write(2, 0, 'Project Name')
    ws.write(2, 1, 'Project Number')

    heading_row_column_no = 2

    project_row_number = 3

    ws.col(0).width = 5000

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font

    for project in projects:
        project_id = project[0]
        project_number = project[1]
        project_name = project[2]

        ws.write(project_row_number, 0, project_name)
        ws.write(project_row_number, 1, project_number)


        trade_query = 'SELECT DISTINCT trade from wo_bills WHERE project_id='+str(project_id)
        cur.execute(trade_query)
        res = cur.fetchall()
        if res is not None:
            for item in res:
                trade = item[0]

                if trade not in trade_column_no.keys():
                    trade_column_no[trade] = heading_row_column_no
                    
                    ws.col(heading_row_column_no).width = 5000
                    ws.write(2, heading_row_column_no, trade)
                    heading_row_column_no += 1

                trade_total_query = 'SELECT SUM(approval_2_amount) from wo_bills WHERE project_id='+str(project_id)+' AND trade="'+trade+'"'
                cur.execute(trade_total_query)
                total_res = cur.fetchone()
                if total_res is not None:
                    total_amount = total_res[0]

                    ws.write(project_row_number, trade_column_no[trade], total_amount)

        project_row_number += 1    

    wb.save('../static/trade_report.xls')

    return 'Job done!'


@app.route('/get_dlr_report', methods=['GET'])
def get_dlr_report():
    cur = mysql.connection.cursor()
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    current_date = current_time.strftime('%A %B %d') 
    get_projects_query = 'SELECT project_id, project_number, project_name from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
    cur.execute(get_projects_query)
    projects = cur.fetchall()

    dlr_data = []  
    for project in projects:
        project_id = project[0]
        project_name = project[2]
        project_number = project[1]
        project2update = {
            'project_name': project_name,
            'project_number': project_number,
        } 
        current_day_update = 'SELECT update_title, tradesmenMap from App_updates WHERE project_id='+str(project_id)+' AND date="'+ current_date +'"'
        cur.execute(current_day_update)
        update_result = cur.fetchone()
        if update_result is not None:
            project2update['update'] = update_result[0]
            project2update['workman_status'] = update_result[1]
        else:
            project2update['update'] = 'DLR not updated'
            project2update['workman_status'] = ''
        dlr_data.append(project2update)

    rb = open_workbook("../static/updates.xls")
    wb = copy(rb)
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    current_time = now.strftime('%d-%m-%Y')
    current_datetime = now.strftime('%d-%m-%Y %H:%M')
    ws = wb.add_sheet(' ' + str(current_time))
    style = xlwt.XFStyle()

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font


    yellow_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
    yellow_style.pattern = pattern

    ws.write(1, 0, 'Report as on '+current_datetime)
    ws.write(2, 0, 'Project name', style=style)
    ws.write(2, 1, 'Project number', style=style)
    ws.write(2, 2, 'Update', style=style)
    column = 3
    tradesMen = [
        'Mason',
        'Helper',
        'Carpenter',
        'Barbender',
        'Painter',
        'Electrician',
        'Plumber',
        'Tile mason',
        'Granite mason',
        'Fabricator',
        'Other workers',
        'Interior carpenter'
    ] 
    for i in tradesMen:
        ws.col(column).width = 5000
        ws.write(2, column, i, style=style)
        column = column+1

    row = 3
    column = 0
    read_only = xlwt.easyxf("")

    for project_data in dlr_data:
        column = 0
        ws.col(column).width = 8000
        ws.write(row, column, project_data['project_name'], read_only)

        column = column + 1
        ws.col(column).width = 8000
        ws.write(row, column, project_data['project_number'], read_only)

        column = column + 1
        ws.col(column).width = 15000
        if project_data['update'] == 'DLR not updated':
            ws.write(row, column, project_data['update'], style=yellow_style)
        else:
            ws.write(row, column, project_data['update'], read_only)

        column = column + 1
        ws.col(column).width = 5000
        if len(project_data['workman_status'].strip()) > 0 and len(project_data['workman_status'][1:-1].strip()) > 0:
            workMenSplit = project_data['workman_status'][1:-1].split(',')

            for t in tradesMen:

                for workmen2Nos in workMenSplit:
                    if len(workmen2Nos) > 0:
                        workMenName = workmen2Nos.split(':')[0]
                        workMenCount = workmen2Nos.split(':')[1]

                        if t == workMenName.strip():         
                            ws.write(row, column, workMenCount, read_only)
                column = column + 1

        row = row + 1

    wb.save('../static/updates.xls')

    return 'Job done!'

@app.route('/delete_old_drawings', methods=['GET'])
def delete_old_drawings():
    cur = mysql.connection.cursor()
    
    f = open('../static/projects_to_delete.txt','r')
    for i in f:
        project_number = i.strip()
        project_id_query = 'SELECT project_id from projects WHERE project_number='+project_number
        cur.execute(project_id_query)
        res = cur.fetchone()
        if res is not None:
            project_id = res[0]
            get_drawings_for_projects = 'SELECT pdf FROM Docs WHERE project_id='+str(project_id)+' AND folder!="RECEIPTS" AND folder!="AGREEMENT "'
            cur.execute(get_drawings_for_projects)
            res = cur.fetchall()
            for d in res:
                try:
                    os.remove('/home/buildahome2016/public_html/app.buildahome.in/team/Drawings/'+d[0])
                except:
                    pass
            delete_drawing_query = 'DELETE from Docs WHERE project_id='+str(project_id)+' AND folder!="RECEIPTS" AND folder!="AGREEMENT "'
            cur.execute(delete_drawing_query)
            
    return 'success'



@app.route('/migrate', methods=['GET'])
def migrate():
    BASE_DIR = '/home/buildahome2016/public_html'
    abs_path = os.path.join(BASE_DIR, '/home/buildahome2016/public_html/app.buildahome.in/api/images')
    files = os.listdir(abs_path)
    im = Image.open(r'/home/buildahome2016/public_html/app.buildahome.in/api/images/' + i)
    width, height = im.size
    while width > 640 and height > 320:
        width = width - 100
        height = height - 100
    im.resize((width, height))
    im.save('/home/buildahome2016/public_html/app.buildahome.in/api/images/' + i)
    try:
        for i in files[0: 10]:
            with open(
                    '/home/buildahome2016/public_html/app.buildahome.in/api/images/' + i,
                    'rb') as fp:
                file = FileStorage(fp, content_type='image/' + i.split('.')[-1])
                send_to_s3(file, app.config["S3_BUCKET"], i)
        return 'success'
    except Exception as e:
        print("Something Happened: ", e)
        return str(e)

@app.route('/audit_log', methods=['GET'])
def audit_log():
    cur = mysql.connection.cursor()
    query = 'SELECT * from erp_audit_log ORDER BY id DESC'
    cur.execute(query)
    logs = cur.fetchall()
    return render_template('audit_log.html',logs=logs)


@app.route('/files/<filename>', methods=['GET'])
def files(filename):
    if 'work_order_' in filename:
        wo_id = filename.replace('work_order_','').replace('.pdf','')
        cur = mysql.connection.cursor()
        query = 'SELECT filename from work_orders WHERE id='+str(wo_id)
        cur.execute(query)
        res = cur.fetchone()
        if res is not None and res[0].strip() != '':
            filename = res[0] 

    response = redirect(app.config['S3_LOCATION'] + filename)
    return response

@app.route('/upload_migrated_image', methods=['GET','POST'])
def upload_migrated_image():
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'danger ')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output = send_to_s3(file, app.config["S3_BUCKET"], 'migrated/'+filename)
            if output != 'success':
                return 'failed'
        return 'success'
    return 'No image'

@app.route('/transfer_image_to_s3', methods=['GET'])
def transfer_image_to_s3():
    last_file_query = 'SELECT image from Daily_images ORDER BY updated_at DESC LIMIT 1'
    cur = mysql.connection.cursor()
    cur.execute(last_file_query)
    res = cur.fetchone()
    last_file = res[0]
    with open(
            '/home/buildahome2016/public_html/app.buildahome.in/api/images/' + last_file,
            'rb') as fp:
        file = FileStorage(fp, content_type='image/' + last_file.split('.')[-1])
        res = send_to_s3(file, os.environ.get('S3_BUCKET'), 'migrated/' + last_file)
        if res == 'success':
            os.remove('/home/buildahome2016/public_html/app.buildahome.in/api/images/' + last_file)
    return ''

@app.route('/', methods=['GET'])
def index():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/erp'
        return redirect('/login')
    
    projects = get_projects()

    cur = mysql.connection.cursor()
    
    vendors_query = 'SELECT COUNT(id) FROM vendors ORDER by code'
    cur.execute(vendors_query)
    res = cur.fetchone()
    vendor_count = 0
    if res is not None:
        vendor_count = str(res[0]).strip()

    contractors_query = 'SELECT COUNT(id) FROM contractors'
    cur.execute(contractors_query)
    res = cur.fetchone()
    contractor_count = 0
    if res is not None:
        contractor_count = str(res[0]).strip()

    work_orders_query = 'SELECT COUNT(id) FROM work_orders'
    cur.execute(work_orders_query)
    res = cur.fetchone()
    work_orders_count = 0
    if res is not None:
        work_orders_count = str(res[0]).strip()

    current_user_role = session['role']
    indents_query = ''
    approved_pos_count = 0
    
    if current_user_role in ['Super Admin', 'COO', 'QS Head', 'Purchase Head','Billing']:
        indents_query = 'SELECT indents.id, ' \
                        'projects.project_id, ' \
                        'projects.project_name, ' \
                        'indents.material, ' \
                        'indents.quantity, ' \
                        'indents.unit, ' \
                        'indents.purpose, ' \
                        'App_users.name, ' \
                        'indents.timestamp, indents.billed, indents.po_number FROM indents ' \
                        'INNER JOIN projects on ' \
                        'indents.status="approved_by_ph" AND ' \
                        'indents.project_id=projects.project_id ' \
                        'LEFT OUTER JOIN App_users on ' \
                        'indents.created_by_user=App_users.user_id'
        cur.execute(indents_query)
        res = cur.fetchall()
        if res is not None:
            approved_pos_count = len(res)
    elif current_user_role in ['Purchase Executive']:
        indents_query = 'SELECT indents.id, ' \
                        'projects.project_id, ' \
                        'projects.project_name, ' \
                        'indents.material, ' \
                        'indents.quantity, ' \
                        'indents.unit, ' \
                        'indents.purpose, ' \
                        'App_users.name, ' \
                        'indents.timestamp, indents.billed, indents.po_number FROM indents ' \
                        'INNER JOIN projects on ' \
                        'indents.status="approved_by_ph" AND ' \
                        'indents.project_id=projects.project_id AND ' \
                        'indents.project_id IN ' + str(get_projects_for_current_user()) +' '\
                        'LEFT OUTER JOIN App_users on ' \
                        'indents.created_by_user=App_users.user_id'
         
        cur.execute(indents_query)
        res = cur.fetchall()
        if res is not None:
            approved_pos_count = len(res)

    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    current_date = current_time.strftime('%A %B %d') 
    dpr_query = 'SELECT COUNT(update_id) FROM `App_updates` WHERE YEAR(updated_at) = YEAR(CURDATE()) AND date = "'+current_date+'"'
    cur.execute(dpr_query)
    res = cur.fetchone()
    dpr_count = 0
    if res is not None:
        dpr_count = res[0]

    current_month = current_time.strftime('%B')

    time_now = datetime.now()
    total_material_spend = {}
    

    for i in range(0, 12, 1):

        total_material_spend[current_month] = 0
           
        total_material_previous_month_spend_query = 'SELECT SUM(CAST(total_amount AS UNSIGNED)) from procurement WHERE MONTH(created_at_datetime) = MONTH(DATE_SUB(curdate(), INTERVAL '+str(i)+' MONTH)) and YEAR(created_at_datetime) = YEAR(DATE_SUB(curdate(), INTERVAL '+str(i)+' MONTH))'
        cur.execute(total_material_previous_month_spend_query)
        res = cur.fetchone()
        if res is not None:
            total_material_spend[current_month] = res[0]

        weeks_to_sub =  4 * (i+1)
        current_month = time_now - timedelta(weeks=weeks_to_sub)
        current_month = current_month.strftime('%B')


    return render_template('index.html',current_user_projects = get_projects_for_current_user(), projects=projects, vendor_count=vendor_count, contractor_count=contractor_count, work_orders_count=work_orders_count, approved_pos_count=approved_pos_count, dpr_count=dpr_count, total_material_spend=total_material_spend)

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            cur = mysql.connection.cursor()
            view_user_query = 'SELECT user_id, email, name, role, phone, profile_picture FROM App_users WHERE user_id=' + str(user_id)
            cur.execute(view_user_query)
            result = cur.fetchone()
            return render_template('profile.html', user=result)
        else: 
            return redirect('/login')
    else:


        user_id = request.form['user_id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                picture_filename = 'user_dp_'+str(user_id)+'_'+ filename
                output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
                else:
                    cur = mysql.connection.cursor()
                    update_query = 'UPDATE App_users set profile_picture="'+picture_filename+'" WHERE user_id=' + str(
                        user_id)
                    cur.execute(update_query)
                    mysql.connection.commit()

        if len(password.strip()) > 0:
            old_password = request.form['old_password']
            if old_password.strip() == '':
                flash('Current password field cannot be empty to change password', 'danger')
                return redirect(request.referrer)
            else: 
                c_password = request.form['confirm_password']
                if password != c_password:
                    flash('Passwords did not match. Operation failed', 'danger')
                    return redirect(request.referrer)

                old_password = hashlib.sha256(old_password.encode()).hexdigest()
                cur = mysql.connection.cursor()
                query = "SELECT user_id, password FROM App_users WHERE user_id=" + user_id
                cur.execute(query)
                result = cur.fetchone()
                if result is not None and result[1] == old_password:                           
                    cur = mysql.connection.cursor()
                    password = hashlib.sha256(password.encode()).hexdigest()
                    values = (name, phone, email, password)
                    
                    update_query = 'UPDATE App_users set name=%s, phone=%s, email=%s, password=%s WHERE user_id=' + str(
                        user_id)
                    cur.execute(update_query, values)
                    flash('User details and password updated', 'success')
                    mysql.connection.commit()
                    return redirect(request.referrer)
                else: 
                    flash('Incorrect old password. Operation failed', 'danger')
                    return redirect(request.referrer)
                    
        else:
            cur = mysql.connection.cursor()
            values = (name, phone, email)
            update_query = 'UPDATE App_users set name=%s, phone=%s, email=%s WHERE user_id=' + str(user_id)
            cur.execute(update_query, values)
            flash('Details updated', 'success')
            mysql.connection.commit()
            return redirect(request.referrer)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'email' in session:
            if 'last_route' in session:
                last_route = session['last_route']
                del session['last_route']
                return redirect(last_route)
            else:
                return redirect('/erp')
        else:
            return render_template('login.html')
    else:
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in list(request.form.keys()):
                flash('Missing fields. Operation failed', 'danger')
                return redirect(request.referrer)

        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()
        cur = mysql.connection.cursor()
        query = "SELECT user_id, email, name, role, password, access_level, profile_picture FROM App_users WHERE email='" + username + "'"
        cur.execute(query)
        result = cur.fetchone()
        if result is not None:
            if result[4] == password:
                session['user_id'] = result[0]
                session['email'] = result[1]
                session['role'] = result[3]
                session['name'] = result[2]
                session['access_level'] = result[5]
                
                profile_picture = '/static/profile_picture.PNG'
                if len(str(result[6])) > 0:
                    profile_picture = '/files/'+result[6] 
                    
                session['profile_picture'] = profile_picture                 
                
                session['projects'] = get_projects_for_current_user()
                flash('Logged in successfully', 'success')
                return redirect('/erp')
            else:
                flash('Incorrect credentials', 'danger')
                return redirect('/login')
        else:
            flash('Incorrect credentials. User not found', 'danger')
            return redirect('/login')


@app.route('/mobile_app_banner', methods=['GET', 'POST'])
def mobile_app_banner():
    if request.method == 'GET':
        return render_template('mobile_app_banner.html')
    else:
        if 'banner' in request.files:
            file = request.files['banner']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'mobile_banner.png'))
                flash('Banner updated successfully', 'success')
                return redirect(request.referrer)
            else:
                flash('Invalid file type. Only png images allowed. Operation failed', 'failed')
                return redirect(request.referrer)
        else:
            flash('Missing file. Operation failed', 'failed')
            return redirect(request.referrer)

@app.route('/delete_note', methods=['GET'])
def delete_note():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO']:
        flash('You do not have permission to delete a note', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        note_id = request.args['id']
        get_note = 'SELECT n.note, p.project_name FROM ' \
                            'notes_and_comments n LEFT OUTER JOIN projects p on p.project_id=n.project_id ' \
                            ' WHERE n.id =' + str(note_id)
        cur.execute(get_note)
        res = cur.fetchone()
        if res is not None:
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted note :'+ str(res[0]) + ' from project '+ str(res[1]) )
        cur = mysql.connection.cursor()
        delete_note_query = 'DELETE from notes_and_comments WHERE id=' + str(note_id)
        cur.execute(delete_note_query)        
        mysql.connection.commit()
        flash('Note deleted', 'danger')
        return redirect(request.referrer)

@app.route('/projects_with_team', methods=['GET'])
def projects_with_team():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if request.method == 'GET':
        query = 'SELECT project_id, project_name from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
        cur = mysql.connection.cursor()
        cur.execute(query)
        projects = cur.fetchall()
        team = []
        for project in projects:
            project_map = {'Project Name': project[1]}
            existing_team_query = 'SELECT * FROM project_operations_team WHERE project_id=' + str(project[0])
            cur.execute(existing_team_query)
            res = cur.fetchone()
            if res is not None:
                pc_query = 'SELECT name from App_users WHERE user_id='+str(res[2])
                cur.execute(pc_query)
                user = cur.fetchone()
                if user is not None:
                    project_map['Project Coordinator'] = user[0]
                pm_query = 'SELECT name from App_users WHERE user_id='+str(res[3])
                cur.execute(pm_query)
                user = cur.fetchone()
                if user is not None:
                    project_map['Project Manager'] = user[0]

            users_query = 'SELECT name from App_users WHERE role="Site Engineer" AND access LIKE "%'+str(project[0])+'%"'
            cur.execute(users_query)
            res = cur.fetchall()
            site_engineers = []
            for i in res:
                site_engineers.append(i[0])
            
            project_map['Site engineers'] = ', '.join(site_engineers)
            team.append(project_map)

        return render_template('projects_with_team.html', team=team)

@app.route('/project_notes', methods=['GET','POST'])
def project_notes():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if request.method == 'GET':
        if 'project_id' not in request.args:
            projects = get_projects()
            return render_template('notes_and_comments.html', projects=projects)
        else:
            projects = get_projects()
            project_id = request.args['project_id']
            cur = mysql.connection.cursor()
            get_notes = 'SELECT n.note, n.timestamp, u.name, n.id, n.attachment, n.internal FROM ' \
                            'notes_and_comments n LEFT OUTER JOIN projects p on p.project_id=n.project_id ' \
                            ' LEFT OUTER JOIN App_users u on u.user_id=n.user_id' \
                            ' WHERE p.project_id =' + str(project_id)
            cur.execute(get_notes)
            res = cur.fetchall()
            return render_template('notes_and_comments.html', projects=projects, notes=res)
    else:
        note = request.form['note']
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')
        user_id = session['user_id']
        project_id = request.form['project_id']
        internal = 0
        if 'internal' in request.form:
            internal = 1

        cur = mysql.connection.cursor()
        query = 'INSERT into notes_and_comments(note, timestamp, user_id, project_id, internal) values(%s, %s, %s, %s, %s)'
        cur.execute(query, (note, timestamp, user_id, project_id, str(internal)))

        note_id = cur.lastrowid        
        file = request.files['file']
        if file.filename != '' and file and allowed_file(file.filename):
            filetype = file.filename.split('.')[-1]
            output = send_to_s3(file, app.config["S3_BUCKET"], 'note_'+str(note_id)+'.'+filetype)
            if output != 'success':
                flash('Failed', 'danger')
                return redirect('/project_notes?project_id='+str(project_id))

            cur = mysql.connection.cursor()
            query = 'UPDATE notes_and_comments SET attachment="note_'+str(note_id)+'.'+filetype+'" WHERE id='+str(note_id)
            cur.execute(query)
            mysql.connection.commit()
            

        mysql.connection.commit()
        flash('Note Added', 'success')
        return redirect('/project_notes?project_id='+str(project_id))

@app.route('/add_work_order_note', methods=['POST'])
def add_work_order_note():
    work_order_id = request.form['work_order_id']
    note = request.form['note']
    query = 'INSERT into work_order_notes (work_order_id, note, posted_by, posted_at, posted_by_email) values(%s,%s,%s,%s,%s)'
    cur = mysql.connection.cursor()
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    timestamp = current_time.strftime('%d-%m-%Y at %H:%M')
    values = (work_order_id, note, session['name'], timestamp, session['email'])
    cur.execute(query, values)
    flash('Note added!', 'success')
    mysql.connection.commit()

    return redirect(redirect_url())

@app.route('/delete_work_order_note', methods=['GET'])
def delete_work_order_note():
    id = request.args['id']
    query = 'DELETE FROM work_order_notes WHERE id='+str(id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    flash('Note deleted', 'danger')

    return redirect(redirect_url())

@app.route('/lock_wo', methods=['GET'])
def lock_wo():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    id = request.args['id']
    query = 'UPDATE work_orders SET locked=1 WHERE id='+str(id)
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' locked work order with id' + str(id))
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    flash('work order locked', 'danger')

    return redirect(redirect_url())

@app.route('/unlock_wo', methods=['GET'])
def unlock_wo():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    id = request.args['id']
    query = 'UPDATE work_orders SET locked=0 WHERE id='+str(id)
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' locked work order with id' + str(id))
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    flash('work order unlocked', 'success')

    return redirect(redirect_url())


@app.route('/enter_material', methods=['GET', 'POST'])
def enter_material():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/enter_material'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        projects = get_projects()
        vendors = get_vendors()
        return render_template('enter_material.html', projects=projects, vendors=vendors, materials=materials)
    else:
        required_fields = ['material', 'description', 'vendor', 'project', 'po_no', 'invoice_no', 'invoice_date',
                           'quantity', 'unit', 'rate', 'gst', 'total_amount', 'difference_cost', 'photo_date','transportation','loading_unloading']
        for field in required_fields:
            if field not in list(request.form.keys()):
                flash('Missing fields. Operation failed', 'danger')
                return redirect(request.referrer)

        material = request.form['material']
        description = request.form['description']
        vendor = request.form['vendor']
        project = request.form['project']
        po_no = request.form['po_no']
        invoice_no = request.form['invoice_no']
        invoice_date = request.form['invoice_date']
        quantity = request.form['quantity']
        unit = request.form['unit']
        rate = request.form['rate']
        gst = request.form['gst']
        total_amount = request.form['total_amount']
        difference_cost = request.form['difference_cost']
        photo_date = request.form['photo_date']
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')
        
        transportation = request.form['transportation']
        loading_unloading = request.form['loading_unloading']


        cur = mysql.connection.cursor()

        vendor_query = 'SELECT name from vendors WHERE id='+str(vendor)
        cur.execute(vendor_query)
        result = cur.fetchone()
        if result is not None:
            vendor = result[0]

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            project) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        cur.execute(material_quantity_query)
        result = cur.fetchone()
        if result is None:
            flash('Total quantity of material has not been specified under KYP material. Entry not recorded', 'danger')
            return redirect('/enter_material')
        elif float(result[0]) < (float(quantity)):
            flash('Total quantity of material exceeded limit specified under KYP material. Entry not recorded',
                  'danger')
            return redirect('/enter_material')
        else:
            quantity_limit = result[0]
            existing_quantity_query = "SELECT SUM(quantity) from procurement WHERE project_id=" + str(project) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
            cur.execute(existing_quantity_query)
            result = cur.fetchone()
            if result is not None and result[0] is not None:
                if (float(result[0]) + float(quantity)) > float(quantity_limit): 
                    flash('Total quantity of material exceeded limit specified under KYP material. Entry not recorded','danger')
                    return redirect('/enter_material')

        created_at_datetime = current_time.strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT into procurement (material, description, vendor, project_id, po_no, invoice_no, invoice_date," \
                "quantity, unit, rate, gst, total_amount, difference_cost, photo_date, transportation, loading_unloading, created_at, created_at_datetime) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (material, description, vendor, project, po_no, invoice_no, invoice_date, quantity, unit, rate, gst,
                  total_amount, difference_cost, photo_date, transportation, loading_unloading, timestamp, created_at_datetime)
        cur.execute(query, values)
        mysql.connection.commit()
        flash('Material was inserted successfully', 'success')
        return redirect('/enter_material')


@app.route('/view_inventory', methods=['GET'])
def view_inventory():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_inventory'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive','QS Engineer','QS Head','QS Info','Project Manager','Finance']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    cur = mysql.connection.cursor()
    projects = get_projects()
    procurements = None
    project = None
    material = None
    material_total_quantity = None
    if 'project_id' in request.args and 'material' in request.args:
        project_id = request.args['project_id']
        material = request.args['material']
        if material == 'All':
            procurement_query = 'SELECT * from procurement WHERE project_id=' + str(
                project_id)
        else:
            if str(material) == 'Cement':
                procurement_query = "SELECT * from procurement WHERE project_id=" + str(
                    project_id) + " AND material='Cement'"
            else:    
                procurement_query = "SELECT * from procurement WHERE project_id=" + str(
                    project_id) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        cur.execute(procurement_query)
        procurements = cur.fetchall()
        for i in projects:
            if str(i[0]) == str(project_id):
                project = i[1]

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            project_id) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        cur.execute(material_quantity_query)
        result = cur.fetchone()
        if result is not None:
            material_total_quantity = result[0]
    return render_template('view_inventory.html', projects=projects, procurements=procurements, project=project,
                           material=material, material_total_quantity=material_total_quantity, materials=materials)

@app.route('/debit_note', methods=['GET','POST'])
def debit_note():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_procurement'
        return redirect('/login')
    if request.method == 'GET':
        projects = get_projects()

        cur = mysql.connection.cursor()
        contractors_query = 'SELECT id, name, trade FROM contractors'
        cur.execute(contractors_query)
        contractors = cur.fetchall()

        return render_template('debit_note.html', contractors=contractors, projects=projects)
    else:
        project = request.form['project']
        contractor = request.form['contractor']
        trade = request.form['trade'].strip()
        stage = request.form['stage'] + '(Debit note)'
        value = request.form['value']
        note = request.form['note']

        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')

        cur = mysql.connection.cursor()
        contractor_query = 'SELECT name, code, pan from contractors WHERE id='+str(contractor)
        cur.execute(contractor_query)
        res = cur.fetchone()

        get_wo_query = 'SELECT id from work_orders WHERE trade=%s AND project_id=%s AND contractor_id=%s'
        cur.execute(get_wo_query, (trade, project, contractor))
        wo_res = cur.fetchone()
        if wo_res is None:
            flash('Work order not created for this trade','danger')
            return redirect(request.referrer)    

        
        bill_query = 'INSERT into wo_bills (project_id, contractor_name, contractor_code, contractor_pan, trade, stage, approval_2_amount, approved_on, approval_2_notes, amount) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        values = (project, res[0], res[1], res[2], trade, stage, str(value).strip(), timestamp, note.replace('"','""').replace("'","''"),str(value).strip())
        cur.execute(bill_query, values)
        mysql.connection.commit()
        flash('Debit note created successfully', 'success')
        return redirect(request.referrer)

@app.route('/edit_procurement', methods=['GET','POST'])
def edit_procurement():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_procurement'
        return redirect('/login')
    if request.method == 'GET':
        if 'procurement_id' not in request.args:
            flash('Something went wrong', 'danger')
            return redirect(request.referrer)
        if 'procurement_id' in request.args:
            procurement_id = request.args['procurement_id']
            procurement_query = 'SELECT * from procurement WHERE id=' + str(procurement_id) 
            cur = mysql.connection.cursor()
            cur.execute(procurement_query)
            result = cur.fetchone()
            return render_template('edit_procurement.html', data=result, materials=materials)
    else:
        procurement_id = request.form['procurement_id']
        material = request.form['material']
        description = request.form['description']
        po_no = request.form['po_no']
        invoice_no = request.form['invoice_no']
        invoice_date = request.form['invoice_date']
        quantity = request.form['quantity']
        unit = request.form['unit']
        rate = request.form['rate']
        gst = request.form['gst']
        total_amount = request.form['total_amount']
        difference_cost = request.form['difference_cost']
        photo_date = request.form['photo_date']
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        project=request.form['project_id']
        timestamp = current_time.strftime('%d %m %Y at %H %M')
        
        transportation = request.form['transportation']
        loading_unloading = request.form['loading_unloading']


        cur = mysql.connection.cursor()

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            project) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        cur.execute(material_quantity_query)
        result = cur.fetchone()
        if result is None:
            flash('Total quantity of material has not been specified under KYP material. Entry not recorded', 'danger')
            return redirect('/enter_material')
        if float(result[0]) < (float(quantity)):
            flash('Total quantity of material exceeded limit specified under KYP material. Entry not recorded',
                  'danger')
            return redirect('/enter_material')

        query = 'UPDATE procurement set material=%s, description=%s, po_no=%s, invoice_no=%s, invoice_date=%s, quantity=%s, unit=%s, rate=%s, gst=%s,' \
                  'total_amount=%s, difference_cost=%s, photo_date=%s, transportation=%s, loading_unloading=%s WHERE id='+str(procurement_id)
        values = (material, description, po_no, invoice_no, invoice_date, quantity, unit, rate, gst,
                  total_amount, difference_cost, photo_date, transportation, loading_unloading)
    

        cur.execute(query, values)
        mysql.connection.commit()
        flash('Procurement was updated successfully', 'success')
        return redirect('/view_inventory?project_id='+project+'&material=All')

    

@app.route('/shifting_entry', methods=['GET', 'POST'])
def shifting_entry():
    if request.method == 'GET':
        if 'email' not in session:
            flash('You need to login to continue', 'danger')
            session['last_route'] = '/view_inventory'
            return redirect('/login')
        projects = get_projects()
        material_quantity_data = {}
        for i in materials:
            material_quantity_data[i] = ''        

        return render_template('shifting_entry.html', projects=projects, material_quantity_data=material_quantity_data)
    else:
        from_project = request.form['from_project']
        to_project = request.form['to_project']
        shifting_date = request.form['shifting_date']

        if from_project == to_project:
            flash('Shifting entry failed. Cannot shift to same project', 'danger')
            return redirect(request.referrer)

        cur = mysql.connection.cursor()

        from_project_name = ''
        from_project_name_query = 'SELECT project_name FROM projects WHERE project_id='+str(from_project)
        cur.execute(from_project_name_query)
        result = cur.fetchone()
        if result is not None:
            from_project_name = result[0]

        
        to_project_name = ''
        to_project_name_query = 'SELECT project_name FROM projects WHERE project_id='+str(to_project)
        cur.execute(to_project_name_query)
        result = cur.fetchone()
        if result is not None:
            to_project_name = result[0]



        material = request.form['material']
        quantity = request.form['quantity']
        unit = request.form['unit']
        difference_cost = request.form['difference_cost']
        description = 'Shifting entry'
        negative_diff = ''
        positive_diff = ''
        if difference_cost != '':
            negative_diff = '-'+str(difference_cost)
            positive_diff = str(difference_cost)

        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            from_project) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        
        cur.execute(material_quantity_query)
        result = cur.fetchone()
        if result is None:
            flash('Total quantity of material has not been specified under KYP material of source project. Entry not recorded', 'danger')
            return redirect('/enter_material')
        if float(result[0]) < (float(quantity)):
            flash('Total quantity of material exceeded limit specified under KYP material of source project. Entry not recorded',
                  'danger')
            return redirect('/enter_material')

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            from_project) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        
        cur.execute(material_quantity_query)
        result = cur.fetchone()
        if result is None:
            flash('Total quantity of material has not been specified under KYP material of destination project. Entry not recorded', 'danger')
            return redirect('/enter_material')
        if float(result[0]) < (float(quantity)):
            flash('Total quantity of material exceeded limit specified under KYP material of destination project. Entry not recorded',
                  'danger')
            return redirect('/enter_material')

        check_if_shifting_is_possible = 'SELECT SUM(quantity) from procurement WHERE project_id=%s AND material=%s'
        
        cur.execute(check_if_shifting_is_possible, (from_project, material))
        result = cur.fetchone()

        created_at_datetime = current_time.strftime('%Y-%m-%d %H:%M:%S')

        if result[0] is None or (result is not None and result[0] is not None and int(quantity) < int(result[0])):
            deduction_query = "INSERT into procurement (material, description, project_id," \
                          "quantity, unit, difference_cost, created_at, created_at_datetime) values (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (material, description+' to '+to_project_name+' on '+str(shifting_date), from_project, int(quantity) * -1, unit, negative_diff, timestamp, created_at_datetime)
            cur.execute(deduction_query, values)

            addition_query = "INSERT into procurement (material, description, project_id," \
                            "quantity, unit, difference_cost, created_at, created_at_datetime) values (%s, %s,  %s, %s, %s, %s, %s, %s)"
            values = (material, description+" from "+from_project_name+' on '+str(shifting_date), to_project, quantity, unit, positive_diff, timestamp, created_at_datetime)
            cur.execute(addition_query, values)

            mysql.connection.commit()
            flash('Shifting entry successful. Material Shifted!', 'success')
            return redirect(request.referrer)


        else:
            flash('Shifting entry failed. Insufficient quantity in source project', 'danger')
            return redirect(request.referrer)
        

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_user'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        return render_template('create_user.html', roles=roles)
    else:
        required_fields = ['name', 'role', 'email', 'phone', 'password', 'confirm_password']
        for field in required_fields:
            if field not in list(request.form.keys()):
                flash('Missing fields. Operation failed', 'danger')
                return redirect(request.referrer)

        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        c_password = request.form['confirm_password']
        if password != c_password:
            flash('Passwords did not match. Operation failed', 'danger')
            return redirect(request.referrer)
        cur = mysql.connection.cursor()
        password = hashlib.sha256(password.encode()).hexdigest()

        check_if_user_exists = 'SELECT user_id from App_users WHERE email="' + str(email) + '"'
        cur.execute(check_if_user_exists)
        res = cur.fetchone()
        if res is not None:
            update_query = 'UPDATE App_users set name=%s, role=%s, phone=%s, password=%s WHERE user_id=' + str(res[0])
            cur.execute(update_query, (name, role, phone, password))
            flash('User with that email already exists. Role updated', 'warning')
        else:
            new_user_query = 'INSERT into App_users (name, role, email, phone, password) values(%s, %s, %s, %s, %s)'
            values = (name, role, email, phone, password)
            cur.execute(new_user_query, values)
            flash('User created successfully', 'success')
        mysql.connection.commit()
        return redirect('/view_users')


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_user'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        user_id = request.args['user_id']
        cur = mysql.connection.cursor()
        view_user_query = 'SELECT user_id, email, name, role, phone FROM App_users WHERE user_id=' + str(user_id)
        cur.execute(view_user_query)
        result = cur.fetchone()
        return render_template('edit_user.html', user=result, roles=roles)
    else:
        required_fields = ['name', 'role', 'email', 'phone', 'password', 'confirm_password']
        for field in required_fields:
            if field not in list(request.form.keys()):
                flash('Missing fields. Operation failed', 'danger')
                return redirect(request.referrer)

        user_id = request.form['user_id']
        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        if len(password.strip()) > 0:
            c_password = request.form['confirm_password']
            if password != c_password:
                flash('Passwords did not match. Operation failed', 'danger')
                return redirect(request.referrer)
            cur = mysql.connection.cursor()
            password = hashlib.sha256(password.encode()).hexdigest()
            values = (name, role, phone, email, password)
            update_query = 'UPDATE App_users set name=%s, role=%s, phone=%s, email=%s, password=%s WHERE user_id=' + str(
                user_id)
            cur.execute(update_query, values)
            flash('User details and password updated', 'success')
            mysql.connection.commit()
            return redirect('/view_users')
        else:
            cur = mysql.connection.cursor()
            if str(role) == '':
                values = (name, phone, email)
                update_query = 'UPDATE App_users set name=%s, phone=%s, email=%s WHERE user_id=' + str(user_id)
                cur.execute(update_query, values)
            else:
                values = (name, role, phone, email)
                update_query = 'UPDATE App_users set name=%s, role=%s, phone=%s, email=%s WHERE user_id=' + str(user_id)
                cur.execute(update_query, values)
            flash('User updated', 'success')
            mysql.connection.commit()
            return redirect('/view_users')


@app.route('/delete_user', methods=['GET'])
def delete_user():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_user'
        return redirect('/login')

    if session['role'] not in ['Super Admin', 'COO', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)

    if 'user_id' not in request.args:
        flash('Missing fields. Operation failed', 'danger')
        return redirect(request.referrer)

    user_id = request.args['user_id']
    cur = mysql.connection.cursor()

    user_query = 'SELECT email from App_users WHERE user_id=' + str(user_id)
    cur.execute(user_query)
    res = cur.fetchone()
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted user with email ' + str(res[0]))
    
    delete_user_query = 'DELETE from App_users WHERE user_id=' + str(user_id)
    cur.execute(delete_user_query)
    mysql.connection.commit()
    flash('User deleted', 'danger')
    return redirect('/view_users')


@app.route('/view_users', methods=['GET'])
def view_users():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_users'
        return redirect('/login')

    if session['role'] not in ['Super Admin', 'COO', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)

    cur = mysql.connection.cursor()
    view_users_query = 'SELECT user_id, email, name, role, phone FROM App_users'
    cur.execute(view_users_query)
    result = cur.fetchall()
    return render_template('view_users.html', users=result)


@app.route('/add_trade', methods=['GET','POST'])
def add_trade():
    if session['role'] not in ['Super Admin']:
        return 'You do not have permission to view this page'
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        trades_query = 'SELECT DISTINCT trade from labour_stages WHERE stage=""'
        cur.execute(trades_query)
        result = cur.fetchall()
        trades = []
        for i in result:
            trades.append(i[0])
        return render_template('add_trade.html',trades=trades)
    else:
        cur = mysql.connection.cursor()
        trade = request.form['trade']
        trades_query = 'INSERT into labour_stages (trade) values ("'+str(trade)+'")'
        cur.execute(trades_query)
        mysql.connection.commit()
        flash('Trade added!', 'success')
        return redirect('/add_trade')


@app.route('/contractor_registration', methods=['GET', 'POST'])
def contractor_registration():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/contractor_registration'
        return redirect('/login')

    if request.method == 'GET':
        cur = mysql.connection.cursor()
        trades_query = 'SELECT DISTINCT trade from labour_stages'
        cur.execute(trades_query)
        result = cur.fetchall()
        trades = []
        trades.append('Deep cleaning')
        trades.append('Civil 1')
        trades.append('Civil 2')        
        trades.append('Civil 3')
        trades.append('Civil 4')
        trades.append('Fabrication 1')
        trades.append('Fabrication 2')
        trades.append('Fabrication 3')
        trades.append('Fabrication 4')
        trades.append('Pile foundation')
        trades.append('Flooring 1')
        trades.append('Flooring 2')
        trades.append('Elevation Flooring')
        trades.append('Painting 1')
        trades.append('Painting 2')

        for i in result:
            trades.append(i[0])
        trades.append('NT/NMR')
        return render_template('contractor_registration.html', trades=trades)
    else:
        column_names = list(request.form.keys())
        values = list(request.form.values())
        values[2] = str(request.form.getlist('trade')).replace("'","")

        cur = mysql.connection.cursor()

        check_if_code_exists = 'SELECT id FROM contractors WHERE code="'+request.form['code']+'"'
        cur.execute(check_if_code_exists)
        res = cur.fetchone()
        if res is not None:
            flash('Contractor with that code already exists. Operation failed', 'danger')
            return redirect(request.referrer)

        new_vendor_query = 'INSERT into contractors' + str(tuple(column_names)).replace("'", "") + 'values ' + str(
            tuple(values))
        cur.execute(new_vendor_query)
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                picture_filename = 'contractor_dp_' + str(cur.lastrowid)
                output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
        mysql.connection.commit()
        flash('Contractor registered', 'success')
        return redirect('/view_contractors')


@app.route('/view_contractors', methods=['GET'])
def view_contractors():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_contractors'
        return redirect('/login')

    cur = mysql.connection.cursor()
    contractors_query = 'SELECT id, name, code, pan, phone_number, address, trade, aadhar FROM contractors'
    cur.execute(contractors_query)
    result = cur.fetchall()
    return render_template('view_contractors.html', contractors=result)


@app.route('/edit_contractor', methods=['GET', 'POST'])
def edit_contractor():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_contractor'
        return redirect('/login')
    if request.method == 'GET':
        if 'contractor_id' in request.args:
            cur = mysql.connection.cursor()
            contractor_query = 'SELECT * from contractors WHERE id=' + request.args['contractor_id']
            cur.execute(contractor_query)
            contractor_details = cur.fetchone()
            trades_query = 'SELECT DISTINCT trade from labour_stages'
            cur.execute(trades_query)
            result = cur.fetchall()
            trades = []

            trades.append('Deep cleaning')
            trades.append('Civil 1')
            trades.append('Civil 2')        
            trades.append('Civil 3')
            trades.append('Civil 4')
            trades.append('Fabrication 1')
            trades.append('Fabrication 2')
            trades.append('Fabrication 3')
            trades.append('Fabrication 4')
            trades.append('Pile foundation')
            trades.append('Flooring 1')
            trades.append('Flooring 2')
            trades.append('Elevation Flooring')
            trades.append('Painting 1')
            trades.append('Painting 2')
            
            for i in result:
                trades.append(i[0])
            return render_template('edit_contractor.html', trades=trades, contractor_details=contractor_details[1:],
                                   contractor_id=request.args['contractor_id'])
    else:
        cur = mysql.connection.cursor()

        column_names = list(request.form.keys())

        update_string = ""
        for i in column_names[:-1]:
            if i=='trade': 
                update_string += i + '="' + str(request.form.getlist('trade')).replace("'","") + '", '
            else:
                update_string += i + '="' + request.form[i] + '", '
        # Remove the last comma
        update_string = update_string[:-2]
        update_vendor_query = 'UPDATE contractors SET ' + update_string + ' WHERE id=' + str(
            request.form['contractor_id'])
        cur.execute(update_vendor_query)
        mysql.connection.commit()

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':                
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    picture_filename = 'contractor_dp_' + str(request.form['contractor_id'])
                    output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
                    if output != 'success':
                        flash('File upload failed', 'danger')
                        return redirect(request.referrer)
        flash('Contractor updated successfully', 'success')
        return redirect('/view_contractors')


@app.route('/delete_contractor', methods=['GET'])
def delete_contractor():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_contractor'
        return redirect('/login')
    if request.method == 'GET':
        if 'contractor_id' in request.args:
            cur = mysql.connection.cursor()
            contractor_query = 'SELECT name from contractors WHERE id=' + str(request.args['contractor_id'])
            cur.execute(contractor_query)
            res = cur.fetchone()
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted contractor ' + str(request.args['contractor_id']))
            
            contractor_query = 'DELETE from contractors WHERE id=' + request.args['contractor_id']
            cur.execute(contractor_query)
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted contractor with id ' + str(request.args['contractor_id']))
            mysql.connection.commit()
            flash('Contractor deleted', 'danger')
            return redirect('/view_contractors')


@app.route('/vendor_registration', methods=['GET', 'POST'])
def vendor_registration():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/vendor_registration'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        return render_template('vendor_registration.html', materials=materials)
    else:
        column_names = list(request.form.keys())
        values = list(request.form.values())
        values[2] = str(request.form.getlist('location')).replace("'","")
        values[7] = str(request.form.getlist('material_type')).replace("'","")

        cur = mysql.connection.cursor()

        check_query = 'SELECT id from vendors WHERE code="'+request.form['code']+'"'
        cur.execute(check_query)
        result = cur.fetchone()
        if result is not None:
            flash('Vendor with code '+request.form['code']+' already exists', 'danger')
            return redirect(request.referrer)

        new_vendor_query = 'INSERT into vendors' + str(tuple(column_names)).replace("'", "") + 'values ' + str(
            tuple(values))
        cur.execute(new_vendor_query)
        mysql.connection.commit()

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                picture_filename = 'vendor_dp_' + str(cur.lastrowid)
                output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
        flash('Vendor registered', 'success')
        return redirect('/view_vendors')


@app.route('/view_vendors', methods=['GET'])
def view_vendors():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_vendors'
        return redirect('/login')

    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)

    cur = mysql.connection.cursor()
    vendors_query = 'SELECT id, name, code, contact_no FROM vendors ORDER by code'
    cur.execute(vendors_query)
    result = cur.fetchall()
    return render_template('view_vendors.html', vendors=result)


# Field validation for form done till here

@app.route('/view_vendor_details', methods=['GET'])
def view_vendor_details():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_vendor_details'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    vendor_details = []
    if 'vendor_id' in request.args:
        cur = mysql.connection.cursor()
        vendor_query = 'SELECT * from vendors WHERE id=' + request.args['vendor_id']
        cur.execute(vendor_query)
        vendor_details = cur.fetchone()
    return render_template('view_vendor_details.html', vendor_details=vendor_details[1:])


@app.route('/edit_vendor', methods=['GET', 'POST'])
def edit_vendor():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_vendor'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        if 'vendor_id' in request.args:
            cur = mysql.connection.cursor()
            vendor_query = 'SELECT * from vendors WHERE id=' + request.args['vendor_id']
            cur.execute(vendor_query)
            vendor_details = cur.fetchone()
            return render_template('edit_vendor.html', vendor_details=vendor_details[1:],
                                   vendor_id=request.args['vendor_id'], materials=materials)
    else:
        cur = mysql.connection.cursor()
        


        column_names = list(request.form.keys())[:-1]

        update_string = ""
        for i in column_names[:-1]:
            if i=='location':
                update_string += i + '="' + str(request.form.getlist('location')).replace("'","''").replace('"','""') + '", '
            elif i=='material_type': 
                update_string += i + '="' + str(request.form.getlist('material_type')).replace("'","''").replace('"','""') + '", '
            else:
                update_string += i + '="' + request.form[i] + '", '
        # Remove the last comma
        update_string = update_string[:-2]
        update_vendor_query = 'UPDATE vendors SET ' + update_string + ' WHERE id=' + str(
            request.form['vendor_id'])
        
        cur.execute(update_vendor_query)
        mysql.connection.commit()
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                picture_filename = 'vendor_dp_' + str(request.form['vendor_id'])
                output = send_to_s3(file, app.config["S3_BUCKET"], picture_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
        flash('Vendor updated successfully', 'success')
        return redirect('/view_vendor_details?vendor_id=' + request.form['vendor_id'])


@app.route('/delete_vendor', methods=['GET'])
def delete_vendor():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_vendor'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        if 'vendor_id' in request.args:
            cur = mysql.connection.cursor()
            vendor_query = 'SELECT name from vendors WHERE id=' + str(request.args['vendor_id'])
            cur.execute(vendor_query)
            res = cur.fetchone()
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted vendor ' + str(res[0]))
            
            vendor_query = 'DELETE from vendors WHERE id=' + request.args['vendor_id']
            cur.execute(vendor_query)
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted vendor with id ' + str(request.args['vendor_id']))
            mysql.connection.commit()
            flash('Vendor deleted', 'danger')
            return redirect('/view_vendors')


def get_vendors():
    cur = mysql.connection.cursor()
    vendors_query = 'SELECT id, name, code FROM vendors'
    cur.execute(vendors_query)
    result = cur.fetchall()
    vendors = {}
    for i in result:
        vendors[str(i[0])] = str(i[1]) + str(i[2])
    return vendors

@app.route('/get_vendors_for_material', methods=['POST'])
def get_vendors_for_material():
    material_selected = request.form['material_selected']
    cur = mysql.connection.cursor() 
    material_selected = material_selected.replace('"','')
    query = "SELECT id, name from vendors WHERE material_type LIKE '%" + material_selected + "%'"
    cur.execute(query)
    res = cur.fetchall()
    return jsonify(res)


@app.route('/kyp_material', methods=['GET', 'POST'])
def kyp_material():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/kyp_material'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive','QS Info']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    material_quantity_data = {}
    for i in materials:
        material_quantity_data[i] = ''

    if request.method == 'GET':
        cur = mysql.connection.cursor()
        projects = get_projects()

        project = None
        project_id = None
        if 'project_id' in request.args:
            project_id = request.args['project_id']
            material_query = 'SELECT * from kyp_material WHERE project_id=' + str(project_id)
            cur.execute(material_query)
            result = cur.fetchall()
            for i in result:
                material_name = i[2]
                material_quantity_data[material_name] = i[3]
            for i in projects:
                if str(i[0]) == str(project_id):
                    project = i[1]
        return render_template('kyp_material.html', projects=projects, project_id=project_id, project=project,
                               material_quantity_data=material_quantity_data)
    else:
        cur = mysql.connection.cursor()
        project_id = request.form['project_id']
        delete_old_quantity_chart_query = 'DELETE from kyp_material WHERE project_id=' + str(project_id)
        cur.execute(delete_old_quantity_chart_query)
        for i in material_quantity_data:
            quantity_of_i = request.form[i]

            if len(str(quantity_of_i)):
                material_quantity_insert_query = "INSERT into kyp_material (project_id, material, total_quantity) values (" + str(
                    project_id) + ",'" + str(i) + "','" + str(quantity_of_i) + "')"

                cur.execute(material_quantity_insert_query)
                mysql.connection.commit()
        flash('Quantity chart updated successfully', 'success')
        return redirect('/kyp_material')


@app.route('/delete_wo', methods=['GET'])
def delete_wo():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_work_order'
        return redirect('/login')
    if session['role'] not in ['Super Admin']:
        flash('You do not have permission delete', 'danger')
        return redirect(request.referrer)
    wo_id = request.args['id']
    cur = mysql.connection.cursor()
    get_wo = 'SELECT w.trade, p.project_name FROM ' \
                        'work_orders w LEFT OUTER JOIN projects p on p.project_id=w.project_id ' \
                        ' WHERE w.id =' + str(wo_id)
    cur.execute(get_wo)
    res = cur.fetchone()
    if res is not None:
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted '+ str(res[0]) + ' work order from project '+ str(res[1]) )
    

    query = 'DELETE FROM work_orders WHERE id='+wo_id
    cur.execute(query)
    
    mysql.connection.commit()
    flash('Work order has been deleted', 'danger')
    return redirect(request.referrer)

@app.route('/upload_doc', methods=['POST'])
def upload_doc():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_work_order'
        return redirect('/login')
    if 'difference_cost_sheet' in request.files:
        file = request.files['difference_cost_sheet']
        work_order_id = request.form['wo_id']
        if file.filename != '':                
            if file and allowed_file(file.filename): 
                filename = 'dc_for_wo_' + str(work_order_id) + file.filename
                output = send_to_s3(file, app.config["S3_BUCKET"], filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
                cur = mysql.connection.cursor()
                query = 'UPDATE work_orders set difference_cost_sheet=%s WHERE id=%s'
                values = (filename, work_order_id)
                cur.execute(query, values)

                mysql.connection.commit()
                flash("Difference cost sheet uploaded", 'success')
                return redirect(request.referrer)

@app.route('/create_work_order', methods=['GET', 'POST'])
def create_work_order():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_work_order'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        projects = get_projects()
        floors = ['G + 1', 'G + 2', 'G + 3', 'G + 4','G + 5','G + 6']
        trades_query = 'SELECT DISTINCT trade from labour_stages'
        cur.execute(trades_query)
        result = cur.fetchall()
        trades = []
        for i in result:
            trades.append(i[0])
        contractors = []
        contractors_query = 'SELECT id, name, trade FROM contractors'
        cur.execute(contractors_query)
        result = cur.fetchall()
        for i in result:
            contractors.append(i)
        return render_template('create_work_order.html', projects=projects, floors=floors, trades=trades,
                               contractors=contractors)
    else:
        project_id = request.form['project']
        contractor_id = request.form['contractor_id']
        wo_value = request.form['wo_value']
        wo_number = request.form['wo_number']
        cheque_no = request.form['cheque_no']
        comments = request.form['comments']
        total_bua = request.form['total_bua']
        cost_per_sqft = request.form['cost_per_sqft']
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')

        milestones = request.form.getlist('milestone[]')
        percentages = request.form.getlist('percentage[]')

        percentage_sum_total = 0
        try:
            for i in percentages:
                percentage_sum_total += float(i)
            if int(percentage_sum_total) != 100:
                flash('Percentages do not add up to 100', 'danger')
                return redirect(request.referrer)
        except:
            flash('Percentages do not add up to 100', 'danger')
            return redirect(request.referrer)

        cur = mysql.connection.cursor()

        trade = request.form['trade'].strip()

        check_if_exist_query = 'SELECT id from work_orders WHERE project_id=' + str(project_id) + ' AND trade="' + str(
            trade) + '" AND contractor_id='+str(contractor_id)
        cur.execute(check_if_exist_query)   
        result = cur.fetchone()
        if result is not None:
            flash("Work order already exists. Operation failed", 'danger')
            return redirect('/create_work_order')
        else:
            verification_code = str(random.randint(1000,9999))
            insert_query = 'INSERT into work_orders (project_id, value, trade, wo_number, cheque_no, contractor_id, comments, created_at, total_bua, cost_per_sqft, verification_code) ' \
                           'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            values = (project_id, wo_value, trade, wo_number, cheque_no, contractor_id, comments, timestamp, total_bua, cost_per_sqft, verification_code)
            cur.execute(insert_query, values)
            work_order_id = cur.lastrowid


            if 'difference_cost_sheet' in request.files:
                file = request.files['difference_cost_sheet']
                if file.filename != '':                
                    if file and allowed_file(file.filename): 
                        filename = 'dc_for_wo_' + str(work_order_id) + file.filename
                        output = send_to_s3(file, app.config["S3_BUCKET"], filename)
                        if output != 'success':
                            flash('File upload failed', 'danger')
                            return redirect(request.referrer)
                        cur = mysql.connection.cursor()
                        query = 'UPDATE work_orders set difference_cost_sheet=%s WHERE id=%s'
                        values = (filename, work_order_id)
                        cur.execute(query, values)

            for i in range(len(milestones)):
                if milestones[i].strip() != '' and percentages[i].strip() != '':
                    insert_milestones_query = 'INSERT into wo_milestones(work_order_id, stage, percentage) values (%s, %s, %s)'
                    cur.execute(insert_milestones_query, (work_order_id, milestones[i].strip(), percentages[i]))



            mysql.connection.commit()
            flash('Work order created successfully', 'success')

            return redirect('/create_work_order')

@app.route('/get_milsetones', methods=['GET', 'POST'])
def get_milsetones():
    work_order_id = request.form['work_order_id']
    cur = mysql.connection.cursor()
    milestones_query = 'SELECT stage, percentage from wo_milestones WHERE work_order_id='+str(work_order_id)
    cur.execute(milestones_query)
    result = cur.fetchall()
    return jsonify(list(result))


@app.route('/create_bill', methods=['GET', 'POST'])
def create_bill():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_bill'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        projects = get_projects()
        cur = mysql.connection.cursor()
        contractors_query = 'SELECT id, name FROM contractors'
        cur.execute(contractors_query)
        result = cur.fetchall()
        return render_template('create_bill.html', projects=projects, contractors=result)
    else:
        project_id = request.form['project_id']
        trade = request.form['trade']
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')
        cur = mysql.connection.cursor()
        if trade == 'NT/NMR':
            quantity = request.form['quantity']
            rate = request.form['rate']
            nt_nmr_bill_amount = request.form['nt_nmr_bill_amount']
            description = request.form['description'] 


            contractor_query = 'SELECT name, code, pan from contractors WHERE id='+request.form['contractor']
            cur.execute(contractor_query)
            res = cur.fetchone()

            insert_query = 'INSERT into wo_bills (project_id, trade, stage, payment_percentage, amount, total_payable, contractor_name, contractor_code, contractor_pan, created_at, quantity, rate, nt_due) values (%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s)'
            values = (project_id, trade, description,'', nt_nmr_bill_amount, nt_nmr_bill_amount, res[0], res[1], res[2], timestamp, quantity, rate,'1')
            cur.execute(insert_query, values)
            mysql.connection.commit()
            flash('Bill created successfully', 'success')
            return redirect('/create_bill')


        
        stage = request.form['stage']
        # stage = stage.replace("'","''").strip()
        payment_percentage = request.form['payment_percentage']
        amount = request.form['amount']
        contractor_name = request.form['contractor_name']
        contractor_code = request.form['contractor_code']
        contractor_pan = request.form['contractor_pan']

        contractor_query = 'SELECT id from contractors WHERE code="'+request.form['contractor_code']+'"'
        cur.execute(contractor_query)
        contractor_query_res = cur.fetchone()

        check_if_wo_locked_query = 'SELECT locked FROM work_orders WHERE project_id='+str(project_id)+' AND trade="'+str(trade)+'" AND contractor_id='+str(contractor_query_res[0])
        cur.execute(check_if_wo_locked_query)
        res = cur.fetchone()
        if res is not None:
            if str(res[0]) == '1':
                flash("Work order locked. Please ask your administrator to unlock the work order. Operation failed", 'danger')
                return redirect('/create_bill')

        double_quotes_escaped_stage = stage.replace('"','""')
        get_debit_note_bill = 'SELECT approval_2_amount from wo_bills WHERE project_id='+str(project_id)+' AND stage LIKE "%' + double_quotes_escaped_stage +'(Debit note)%" AND contractor_code="'+str(contractor_code)+'" AND trade != "NT/NMR"'
        cur.execute(get_debit_note_bill)
        res = cur.fetchone()
        if res is not None:
            amount = float(amount) - float(res[0])

        
        total_payable = float(amount)
        check_if_exists_query = 'SELECT id FROM wo_bills WHERE project_id=' + str(project_id) + ' AND trade="' + str(
            trade) + '" AND stage="' + str(double_quotes_escaped_stage) + '" AND contractor_code="' + str(contractor_code) + '"'
        cur.execute(check_if_exists_query)
        res = cur.fetchone()
        if res is not None:
            flash("Older bill already exists. Operation failed", 'danger')
            return redirect('/create_bill')
        else:
            insert_query = 'INSERT into wo_bills (project_id, trade, stage, payment_percentage, amount, total_payable, contractor_name, contractor_code, contractor_pan, created_at) values (%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)'
            values = (
            project_id, trade, stage, payment_percentage, amount, total_payable, contractor_name, contractor_code,
            contractor_pan, timestamp)
            cur.execute(insert_query, values)
            mysql.connection.commit()
            flash('Bill created successfully', 'success')
            return redirect('/create_bill')


@app.route('/update_trades_for_project', methods=['POST'])
def update_trades_for_project():
    project_id = request.form['project_id']
    trades_query = 'SELECT id, trade from work_orders WHERE signed=1 AND approved=1 AND project_id=' + str(project_id)
    cur = mysql.connection.cursor()
    cur.execute(trades_query)
    result = cur.fetchall()
    return jsonify(list(result))

@app.route('/update_trades_for_contractor', methods=['POST'])
def update_trades_for_contractor():
    contractor_id = request.form['contractor_id']
    trades_query = 'SELECT trade from contractors WHERE id=' + str(contractor_id)
    cur = mysql.connection.cursor()
    cur.execute(trades_query)
    result = cur.fetchone()
    trades = []
    if result is not None:
        contractor_trades = result[0]
        if ',' in contractor_trades or ']' in contractor_trades:
            trades = contractor_trades[1:-1].split(',')
        else:
            trades.append(contractor_trades)
    for i in range(len(trades)):
        trades[i] = trades[i].strip()
        
    return jsonify(trades)


@app.route('/update_payment_stages', methods=['POST'])
def update_payment_stages():
    project_id = request.form['project_id']    
    trade = request.form['trade']    
    cur = mysql.connection.cursor()
    
    old_bills_query = 'SELECT stage FROM wo_bills WHERE project_id=' + str(project_id) + ' AND trade="' + str(
            trade) + '"'
    cur.execute(old_bills_query)
    res = cur.fetchall()
    old_bills = []
    for i in res:
        old_bills.append(i[0].strip())

    work_order_id_for_trade = request.form['work_order_id_for_trade']
    work_order_query = 'SELECT wo.value, c.name, c.code, c.pan from work_orders wo INNER JOIN contractors c ON ' \
                       'wo.contractor_id=c.id WHERE wo.id=' + str(work_order_id_for_trade)
    cur.execute(work_order_query)
    res = cur.fetchone()
    if res is not None:
        work_order_value = res[0]
        contractor_name = res[1]
        contractor_code = res[2]
        contractor_pan = res[3]
        payment_stages_query = 'SELECT stage, percentage from wo_milestones WHERE work_order_id=' + str(
            work_order_id_for_trade)
        cur.execute(payment_stages_query)
        result = cur.fetchall()
        stages = {}
        for i in result:
            if i[0].strip() not in old_bills:
                stages[i[0]] = i[1].replace('%', '')

        response = {'work_order_value': work_order_value,
                    'stages': stages,
                    'contractor_name': contractor_name,
                    'contractor_code': contractor_code,
                    'contractor_pan': contractor_pan
                    }
        return jsonify(response)


@app.route('/get_wo_milestones_and_percentages', methods=['POST'])
def get_wo_milestones_and_percentages():
    trade = request.form['trade'].strip()
    project_id = request.form['project_id']
    contractor_id = request.form['contractor_id']
    
    cur = mysql.connection.cursor()

    get_contractor_query = 'SELECT code from contractors WHERE id='+str(contractor_id)
    cur.execute(get_contractor_query)
    res = cur.fetchone()
    contractor_code = 0
    if res is not None:
        contractor_code = res[0]

    get_wo_query = 'SELECT id from work_orders WHERE trade=%s AND project_id=%s AND contractor_id=%s'
    cur.execute(get_wo_query, (trade, project_id, contractor_id))
    res = cur.fetchone()
    work_order_id = 0
    if res is not None:
        work_order_id = res[0]

    get_bills_query = 'SELECT w.stage, w.percentage' \
                        ' FROM wo_milestones w LEFT OUTER JOIN wo_bills b ON b.stage=w.stage AND b.contractor_code=%s AND b.project_id=%s AND trade=%s WHERE w.work_order_id=%s'
    cur.execute(get_bills_query, (contractor_code, project_id, trade, work_order_id))
    bills = []
    res = cur.fetchall()
    milestones_and_percentages = {}
    for i in res:
        milestones_and_percentages[i[0]] = i[1].replace('%', '')
    response = {'milestones_and_percentages': milestones_and_percentages, 'message': 'success'}
    return jsonify(response)

@app.route('/get_standard_milestones_and_percentages', methods=['POST'])
def get_standard_milestones_and_percentages():
    trade = request.form['trade']
    project_id = request.form['project_id']
    if str(trade).strip() == '':
        return jsonify({'message': 'Trade field empty'})
    if str(project_id).strip() == '':
        return jsonify({'message': 'Project id field empty'})
    get_floors_for_project_query = 'SELECT no_of_floors from projects WHERE project_id=' + project_id
    cur = mysql.connection.cursor()
    cur.execute(get_floors_for_project_query)
    res = cur.fetchone()
    if res is None or len(res) == 0:
        return jsonify({'message': 'Project not found with id ' + str(project_id)})
    floors = res[0]
    payment_stages_query = 'SELECT stage, payment_percentage from labour_stages WHERE floors="' + str(
        floors) + '" AND trade LIKE "%' + trade + '%"'
    cur.execute(payment_stages_query)
    result = cur.fetchall()
    milestones_and_percentages = {}
    for i in result:
        milestones_and_percentages[i[0]] = i[1].replace('%', '')
    response = {'milestones_and_percentages': milestones_and_percentages, 'message': 'success'}
    return jsonify(response)


def get_bills_as_json(bills_query):
    cur = mysql.connection.cursor()
    cur.execute(bills_query)
    data = {}
    res = cur.fetchall()
    for i in res:
        project_id = i[0]
        if project_id not in data:
            data[project_id] = {'project_name': i[1], 'bills': []}
        data[project_id]['bills'].append(
            {'bill_id': i[16], 'contractor_name': i[7], 'contractor_pan': i[9], 'contractor_code': i[8], 'trade': i[2],
             'stage': i[3], 'amount': i[5], 'total_payable': i[6],
             'approval_1_amount': i[11], 'approval_1_notes': i[12], 'approval_2_amount': i[14],
             'approval_2_notes': i[15], 'created_at': i[17],}
        )
    return data


@app.route('/view_nt_due_bills', methods=['GET'])
def view_nt_due_bills():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head','QS Engineer','Project Manager']:
        flash('You do not have permission to view that page', 'danger')
    bills_query = 'SELECT projects.project_id, projects.project_name, wo_bills.trade, wo_bills.stage, wo_bills.payment_percentage,' \
                      'wo_bills.amount, wo_bills.total_payable, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.contractor_pan,' \
                      'wo_bills.approval_1_status, wo_bills.approval_1_amount, wo_bills.approval_1_notes,' \
                      'wo_bills.approval_2_status, wo_bills.approval_2_amount, wo_bills.approval_2_notes, wo_bills.id, wo_bills.created_at' \
                      ' FROM wo_bills INNER JOIN projects on wo_bills.project_id = projects.project_id AND wo_bills.is_archived=0 AND ' \
                      '(wo_bills.approval_2_amount = 0 OR wo_bills.approval_2_amount IS NULL) AND nt_due = 1'
    
    data = get_bills_as_json(bills_query)
    first_bill_id = 0
    for project in data:
        for i in data[project]['bills']:
            first_bill_id = i['bill_id']
            break
        break
    return render_template('view_nt_due_bills.html', data=data, first_bill_id=first_bill_id)

@app.route('/approve_nt_bill', methods=['GET'])
def approve_nt_bill():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head','QS Engineer','Project Manager']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    bill_id = request.args['bill_id']
    cur = mysql.connection.cursor()
    query = 'UPDATE wo_bills SET nt_due = 0 WHERE id='+str(bill_id)
    cur.execute(query)
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' approved nt bill with id ' + str(request.args['bill_id']))
    mysql.connection.commit()
    flash('Bill approved','success')

    return redirect(request.referrer)

@app.route('/reject_nt_bill', methods=['GET'])
def reject_nt_bill():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head','QS Engineer','Project Manager']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    bill_id = request.args['bill_id']
    cur = mysql.connection.cursor()
    query = 'UPDATE wo_bills SET nt_due = "-1" WHERE id='+str(bill_id)
    cur.execute(query)
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' rejected nt bill with id ' + str(request.args['bill_id']))
    mysql.connection.commit()
    flash('Bill rejected','danger')

    return redirect(request.referrer)


@app.route('/view_bills', methods=['GET'])
def view_bills():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head','QS Engineer','Project Manager']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':

        if session['role'] in ['Super Admin', 'COO', 'QS Head','QS Engineer']:
            coordinators_query = 'SELECT pot.project_id, pot.co_ordinator, u.name, p.project_name FROM project_operations_team pot JOIN App_users u ON pot.co_ordinator = u.user_id JOIN projects p on pot.project_id=p.project_id WHERE co_ordinator is not NULL order by pot.co_ordinator'

        elif session['role'] in ['Project Manager']:
            coordinators_query = 'SELECT pot.project_id, pot.co_ordinator, u.name, p.project_name FROM project_operations_team pot JOIN App_users u ON pot.co_ordinator = u.user_id JOIN projects p on pot.project_id=p.project_id WHERE co_ordinator is not NULL AND p.project_id IN ' + str(get_projects_for_current_user()) +'  order by pot.co_ordinator'
                  
            
        cur = mysql.connection.cursor()
        cur.execute(coordinators_query)
        coordinators_res = cur.fetchall()

        data = {}

        for p in coordinators_res:
            coordinator_id = p[1]
            coordinator_name = p[2]
            if coordinator_id not in data:
                data[coordinator_id] = {'coordinator_name': coordinator_name, 'projects': {}}            

            project_id = p[0]
            if project_id not in data[coordinator_id]['projects']:
                data[coordinator_id]['projects'][project_id] = {'project_name': p[3]}

            bills_query = 'SELECT trade, stage, payment_percentage, amount, total_payable, contractor_name, contractor_code, '\
                        'contractor_pan, approval_1_status, approval_1_amount, approval_1_notes,' \
                        'approval_2_status, approval_2_amount, approval_2_notes, id, created_at' \
                        ' FROM wo_bills WHERE project_id='+ str(p[0]) +' AND (approval_2_amount = 0 OR approval_2_amount IS NULL) AND nt_due != 1 AND nt_due != -1'
            cur.execute(bills_query)
            res = cur.fetchall()
            bills = []
            for i in res:
                bills.append({
                    'trade': i[0],
                    'stage': i[1],
                    'payment_percentage': i[2],
                    'amount': i[3],
                    'total_payable': i[4],
                    'contractor_name': i[5],
                    'contractor_code': i[6],
                    'contractor_pan': i[7],
                    'approval_1_status': i[8],
                    'approval_1_amount': i[9],
                    'approval_1_notes': i[10],
                    'approval_2_status': i[11],
                    'approval_2_amount': i[12],
                    'approval_2_notes': i[13],
                    'bill_id': i[14],
                    'created_at': i[15]
                
                })
            data[coordinator_id]['projects'][project_id]['bills'] = bills
       
        access_level = session['access_level']
        return render_template('view_bills.html', data=data, access_level=access_level)


@app.route('/export_bills', methods=['GET'])
def export_bills():
    bills_query = 'SELECT projects.project_id, projects.project_name, wo_bills.trade, wo_bills.stage, wo_bills.payment_percentage,' \
                  'wo_bills.amount, wo_bills.total_payable, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.contractor_pan,' \
                  'wo_bills.approval_1_status, wo_bills.approval_1_amount, wo_bills.approval_1_notes,' \
                  'wo_bills.approval_2_status, wo_bills.approval_2_amount, wo_bills.approval_2_notes, wo_bills.id, wo_bills.created_at' \
                  ' FROM wo_bills INNER JOIN projects on wo_bills.project_id = projects.project_id AND wo_bills.is_archived=0 AND ' \
                  '(wo_bills.approval_2_amount != 0 AND wo_bills.approval_2_amount IS NOT NULL)'

    data = get_bills_as_json(bills_query)
    cur = mysql.connection.cursor()
    archive_bill = 'UPDATE wo_bills SET is_archived=1 WHERE approval_2_amount != 0 AND approval_2_amount IS NOT NULL'
    cur.execute(archive_bill)
    rb = open_workbook("../static/bills.xls")
    wb = copy(rb)
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    current_time = current_time.strftime('%d %m %Y at %H %M')
    ws = wb.add_sheet('Bills on ' + str(current_time))
    style = xlwt.XFStyle()

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font

    
    ws.write(1, 0, 'Contractor Name', style=style)
    ws.write(1, 1, 'Contractor PAN', style=style)
    ws.write(1, 2, 'Contractor Code', style=style)
    ws.write(1, 3, 'Trade', style=style)
    ws.write(1, 4, 'Stage', style=style)
    ws.write(1, 5, 'Amount', style=style)
    ws.write(1, 6, 'Created on', style=style)
    ws.write(1, 7, 'Notes', style=style)
    row = 2
    column = 0
    read_only = xlwt.easyxf("")
    for project in data:
        column = 0
        cwidth = ws.col(column).width
        if (len(data[project]['project_name']) * 367) > cwidth:
            ws.col(column).width = (len(data[project]['project_name']) * 367)

        ws.write(row, column, data[project]['project_name'], read_only)
        row = row + 1
        for i in data[project]['bills']:

            column = 0
            ws.write(row, column, i['contractor_name'], read_only)
            cwidth = ws.col(column).width
            if (len(i['contractor_name']) * 367) > cwidth:
                ws.col(column).width = (len(i['contractor_name']) * 367)
            column = column + 1

            ws.write(row, column, i['contractor_pan'], read_only)
            cwidth = ws.col(column).width
            if (len(i['contractor_pan']) * 367) > cwidth:
                ws.col(column).width = (len(i['contractor_pan']) * 367)
            column = column + 1

            ws.write(row, column, i['contractor_code'], read_only)
            cwidth = ws.col(column).width
            if (len(i['contractor_code']) * 367) > cwidth:
                ws.col(column).width = (len(i['contractor_code']) * 367)
            column = column + 1

            ws.write(row, column, i['trade'], read_only)
            cwidth = ws.col(column).width
            if (len(i['trade']) * 367) > cwidth:
                ws.col(column).width = (len(i['trade']) * 367)
            column = column + 1

            ws.write(row, column, i['stage'], read_only)
            cwidth = ws.col(column).width
            if (len(i['stage']) * 367) > cwidth:
                if len(i['stage']) * 367 > 65536:
                    ws.col(column).width = 65535
                else: 
                    ws.col(column).width = (len(i['stage']) * 367)
            column = column + 1

            ws.write(row, column, float(i['approval_2_amount']))
            cwidth = ws.col(column).width
            if (len(i['approval_2_amount']) * 367) > cwidth:
                ws.col(column).width = (len(i['approval_2_amount']) * 367)
            column = column + 1

            ws.write(row, column, i['created_at'])
            cwidth = ws.col(column).width
            if (len(i['created_at']) * 367) > cwidth:
                ws.col(column).width = (len(i['created_at']) * 367)
            column = column + 1

            ws.write(row, column, i['approval_2_notes'])
            cwidth = ws.col(column).width
            if (len(i['approval_2_notes']) * 367) > cwidth:
                ws.col(column).width = (len(i['approval_2_notes']) * 367)
            column = column + 1
            row = row + 1
        row = row + 1
    mysql.connection.commit()
    wb.save('../static/bills.xls')

    flash('Bills exported successfully', 'success')
    return redirect(request.referrer + '?exported=true')


@app.route('/delete_bill', methods=['GET'])
def delete_bill():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/delete_bill'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Purchase Head', 'Purchase Executive']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        if 'bill_id' in request.args:
            cur = mysql.connection.cursor()
            delete_bill_query = 'DELETE from wo_bills WHERE id=' + request.args['bill_id']
            cur.execute(delete_bill_query)
            make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted bill with id ' + str(request.args['bill_id']))
            mysql.connection.commit()
            flash('Bill deleted', 'danger')
            return redirect('/view_bills')


@app.route('/view_approved_bills', methods=['GET'])
def view_approved_bills():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        bills_query = 'SELECT projects.project_id, projects.project_name, wo_bills.trade, wo_bills.stage, wo_bills.payment_percentage,' \
                      'wo_bills.amount, wo_bills.total_payable, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.contractor_pan,' \
                      'wo_bills.approval_1_status, wo_bills.approval_1_amount, wo_bills.approval_1_notes,' \
                      'wo_bills.approval_2_status, wo_bills.approval_2_amount, wo_bills.approval_2_notes, wo_bills.id, wo_bills.created_at' \
                      ' FROM wo_bills INNER JOIN projects on wo_bills.project_id = projects.project_id AND wo_bills.is_archived=0 AND ' \
                      '(wo_bills.approval_2_amount != 0 AND wo_bills.approval_2_amount IS NOT NULL)'
        data = get_bills_as_json(bills_query)
        first_bill_id = 0
        for project in data:
            for i in data[project]['bills']:
                first_bill_id = i['bill_id']
                break
            break
        return render_template('view_approved_bills.html', data=data, first_bill_id=first_bill_id)


@app.route('/view_archived_bills', methods=['GET'])
def view_archived_bills():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_bills'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        bills_query = 'SELECT projects.project_id, projects.project_name, wo_bills.trade, wo_bills.stage, wo_bills.payment_percentage,' \
                      'wo_bills.amount, wo_bills.total_payable, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.contractor_pan,' \
                      'wo_bills.approval_1_status, wo_bills.approval_1_amount, wo_bills.approval_1_notes,' \
                      'wo_bills.approval_2_status, wo_bills.approval_2_amount, wo_bills.approval_2_notes, wo_bills.id, wo_bills.created_at' \
                      ' FROM wo_bills INNER JOIN projects on wo_bills.project_id = projects.project_id AND wo_bills.is_archived=1 AND (wo_bills.approval_2_amount != 0 AND wo_bills.approval_2_amount IS NOT NULL)'
        data = get_bills_as_json(bills_query)
        first_bill_id = 0
        for project in data:
            for i in data[project]['bills']:
                first_bill_id = i['bill_id']
                break
            break
        return render_template('view_archived_bills.html', data=data, first_bill_id=first_bill_id)


def update_work_order_balance(project_id, trade, difference_amount):
    get_wo_query = 'SELECT id, balance from work_orders WHERE project_id=' + str(
        project_id) + ' AND trade="' + trade + '"'
    cur = mysql.connection.cursor()
    cur.execute(get_wo_query)
    res = cur.fetchone()
    if res is not None:
        balance = res[1]
        if str(balance).strip() == '':
            balance = 0
        else:
            balance = float(balance)
        updated_balance = balance + float(difference_amount)
        update_wo_query = 'UPDATE work_orders SET balance=' + str(updated_balance) + ' WHERE id=' + str(res[0])
        cur.execute(update_wo_query)
        mysql.connection.commit()


@app.route('/save_approved_bill', methods=['POST'])
def save_approved_bill():
    bill_id = request.form['bill_id']
    approved_amount = request.form['approved_amount']
    notes = request.form['notes']
    approval_level = request.form['approval_level']
    trade = request.form['trade']
    project_id = request.form['project_id']
    difference_amount = request.form['difference_amount']
    cur = mysql.connection.cursor()
    update_bill_query = ''
    if approval_level == 'Level 1':
        update_bill_query = 'UPDATE wo_bills SET approval_1_amount = "' + str(
            approved_amount) + '" , approval_1_notes = "' + str(notes) + '" WHERE id=' + str(bill_id)
    elif approval_level == 'Level 2':
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')

        update_bill_query = 'UPDATE wo_bills SET approved_on="'+ timestamp +'", approval_2_amount = "' + str(
            approved_amount) + '" , approval_2_notes = "' + str(notes) + '" WHERE id=' + str(bill_id)
    cur.execute(update_bill_query)
    if float(difference_amount) > 0 and approval_level == 'Level 2':
        update_work_order_balance(project_id, trade, difference_amount)
    mysql.connection.commit()
    return jsonify({"message": "success"})


@app.route('/project_contractor_info', methods=["GET"])
def project_contractor_info():
    project_id = request.args['project_id']
    contractor_name = request.args['name']
    contractor_code = request.args['code']
    trade = request.args['trade'].strip()

    cur = mysql.connection.cursor()
    data = {'name': '', 'code': '', 'pan': '', 'value': '', 'balance': '', 'trade': '', 'contractor_id': ''}

    get_contractor_query = 'SELECT id, name, code, pan from contractors WHERE code="'+contractor_code+'"'
    cur.execute(get_contractor_query)
    res = cur.fetchone()
    contractor_id = 0
    if res is not None:
        contractor_id = res[0]
        data['name'] = res[1]
        data['code'] = res[2]
        data['pan'] = res[3]

    get_wo_query = 'SELECT id, value, balance, difference_cost_sheet from work_orders WHERE trade=%s AND project_id=%s AND contractor_id=%s'
    cur.execute(get_wo_query, (trade, project_id, contractor_id))
    res = cur.fetchone()
    if res is not None:
        data['value'] = str(res[1]).replace(' ','').replace(',','')
        data['balance'] = res[2]
        data['trade'] = trade
        data['work_order_id'] = res[0]
        data['difference_cost_sheet'] = res[3]

    get_bills_query = 'SELECT w.stage, w.percentage, b.amount, b.approval_2_amount, b.trade, b.approved_on, b.cleared_balance, b.id' \
                        ' FROM wo_milestones w LEFT OUTER JOIN wo_bills b ON b.stage=w.stage AND b.contractor_code=%s AND b.project_id=%s AND trade=%s WHERE w.work_order_id=%s'
    cur.execute(get_bills_query, (contractor_code, project_id, trade, str(data['work_order_id'])))
    bills = []
    res = cur.fetchall()
    for i in res:
        bills.append(i)

    get_clearing_bills = "SELECT stage,amount, approval_2_amount, trade, approved_on, cleared_balance, id from wo_bills WHERE project_id="+str(project_id)+" AND stage LIKE '%Clearing balance%' AND contractor_code='"+str(contractor_code)+"' AND trade ='"+trade+"' AND trade != 'NT/NMR'"
    cur.execute(get_clearing_bills)
    res = cur.fetchall()
    for i in res:
        bills.append((i[0],'',i[1],i[2],i[3], i[4], i[5], i[6]))

    get_debit_note_bills = "SELECT stage, approval_2_amount, trade, approved_on, amount, approval_2_notes, id from wo_bills WHERE project_id="+str(project_id)+" AND stage LIKE '%Debit note%' AND contractor_code='"+str(contractor_code)+"' AND trade != 'NT/NMR' AND trade ='"+trade+"'"
    cur.execute(get_debit_note_bills)
    res = cur.fetchall()
    for i in res:
        bills.append((i[0],'',i[4],i[1],i[2], i[3],i[5], i[6]))

    get_project_query = 'SELECT project_name, project_number from projects WHERE project_id=' + str(project_id)
    cur.execute(get_project_query)
    project = cur.fetchone()

    get_work_order_notes_query = 'SELECT * from work_order_notes WHERE work_order_id='+str(data['work_order_id'] )+' ORDER BY id DESC'
    cur.execute(get_work_order_notes_query)
    notes = cur.fetchall()

    return render_template('project_contractor_info.html', bills=bills, project=project, data=data, notes=notes)

@app.route('/clear_nt_nmr_balance', methods=['GET'])
def clear_nt_nmr_balance():
    bill_id = request.args['bill_id']
    cur = mysql.connection.cursor()
    update_old_bill = 'UPDATE wo_bills SET cleared_balance=1 WHERE id='+str(bill_id)
    cur.execute(update_old_bill)
    mysql.connection.commit()
    
    bill_query = 'SELECT quantity, rate, approval_2_amount, stage, project_id, contractor_name, contractor_code, contractor_pan, trade from wo_bills WHERE id='+str(bill_id)
    cur.execute(bill_query)
    res = cur.fetchone()
    if res is not None:
        amount = int(res[0]) * int(res[1])
        payable  = int(res[2])
        difference = amount - payable
        stage = res[3].replace(' (Clear balance)','')+' (Clear balance)'
        project_id = res[4]
        contractor_name = res[5]
        contractor_code = res[6]
        contractor_pan = res[7]
        trade = res[8]


        bills_query = 'INSERT into wo_bills (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, total_payable) values (%s,%s, %s,%s,%s,%s,%s)'
        cur.execute(bills_query, (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, difference))
        mysql.connection.commit()

        flash('Cleared balance','success')
        return redirect(request.referrer)

@app.route('/check_if_clear_balance_bill_due', methods=['POST'])
def check_if_clear_balance_bill_due():
    balance_amnt = request.form['balance_amnt']
    contractor_name = request.form['contractor_name']
    contractor_code = request.form['contractor_code']
    contractor_pan = request.form['contractor_pan']
    project_id = request.form['project_id']
    trade = request.form['trade']
    work_order_id = request.form['work_order_id']
    stage = 'Clearing balance'

    cur = mysql.connection.cursor()
    get_bill = 'SELECT id from wo_bills WHERE project_id=%s AND trade=%s AND contractor_code=%s AND stage="Clearing balance" AND total_payable=%s AND (approval_2_amount = 0 OR approval_2_amount IS NULL)'
    cur.execute(get_bill, (project_id, trade, contractor_code, balance_amnt))
    res = cur.fetchone()
    if res is not None:
        return jsonify({'message': 'Bill for clearing balance exists'})
    else: 
        return jsonify({'message': 'Bill for clearing balance does not exists'})

@app.route('/force_open_clear_balance', methods=['POST'])
def force_open_clear_balance():
    bill_id = request.form['bill_id']

    cur = mysql.connection.cursor()

    update_old_bill = 'UPDATE wo_bills SET cleared_balance=0 WHERE id='+str(bill_id)
    cur.execute(update_old_bill)

    mysql.connection.commit()
    flash('Bill reversed to clear balance')
    return jsonify({'message': 'success'})

@app.route('/clear_individual_balance', methods=['POST'])
def clear_individual_balance():
    balance_amnt = request.form['balance_amnt']
    contractor_name = request.form['contractor_name']
    contractor_code = request.form['contractor_code']
    contractor_pan = request.form['contractor_pan']
    project_id = request.form['project_id']
    trade = request.form['trade']
    work_order_id = request.form['work_order_id']
    stage = 'Clearing balance for '+ request.form['stage']

    if 'Clearing balance' in request.form['stage'] and request.form['stage'][-1].isnumeric():
        stage = request.form['stage'][:-1] + str(int(request.form['stage'][-1]) + 1)
    elif 'Clearing balance' in request.form['stage']:
        stage = request.form['stage'] + ' 1'


    bill_id = request.form['bill_id']

    cur = mysql.connection.cursor()

    update_old_bill = 'UPDATE wo_bills SET cleared_balance=1 WHERE id='+str(bill_id)
    cur.execute(update_old_bill)


    bills_query = 'INSERT into wo_bills (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, total_payable, amount) values (%s,%s, %s,%s,%s,%s,%s,%s)'
    cur.execute(bills_query, (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, balance_amnt, balance_amnt))

    work_order_balance_query = 'SELECT balance from work_orders WHERE id=' + work_order_id
    cur.execute(work_order_balance_query)
    balance_res = cur.fetchone()
    if balance_res is not None:
        wo_balance = float(balance_res[0]) -  float(balance_amnt)

        work_order_query = 'UPDATE work_orders SET balance='+str(wo_balance)+' WHERE id=' + work_order_id
        cur.execute(work_order_query)

    mysql.connection.commit()
    return jsonify({'message': 'success'})

@app.route('/clear_wo_balance', methods=['POST'])
def clear_wo_balance():
    balance_amnt = request.form['balance_amnt']
    contractor_name = request.form['contractor_name']
    contractor_code = request.form['contractor_code']
    contractor_pan = request.form['contractor_pan']
    project_id = request.form['project_id']
    trade = request.form['trade']
    work_order_id = request.form['work_order_id']
    stage = 'Clearing balance'

    cur = mysql.connection.cursor()
    bills_query = 'INSERT into wo_bills (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, total_payable) values (%s,%s, %s,%s,%s,%s,%s)'
    cur.execute(bills_query, (project_id, trade, stage, contractor_name, contractor_code, contractor_pan, balance_amnt))

    work_order_query = 'UPDATE work_orders SET balance=0 WHERE id=' + work_order_id
    cur.execute(work_order_query)

    mysql.connection.commit()
    return jsonify({'message': 'success'})


def get_work_orders_for_project(project_id):
    cur = mysql.connection.cursor()
    get_wo_query = 'SELECT wo.id, c.name, c.pan, c.code, wo.trade,  wo.value, wo.balance, wo.filename, wo.locked from work_orders wo ' \
                   'INNER JOIN contractors c on wo.approved=1 AND c.id=wo.contractor_id AND wo.project_id=' + str(
        request.args['project_id']) + ' ORDER BY wo.trade'
    cur.execute(get_wo_query)
    res = cur.fetchall()
    return res


@app.route("/view_work_order", methods=['GET'])
def view_work_order():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_work_order'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer','Project Manager','Finance','Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        projects = get_projects()
        nt_nmr_bills = None
        work_orders = []
        if 'project_id' in request.args:
            project_id = request.args['project_id']
            work_orders = get_work_orders_for_project(project_id)

            bills_query = 'SELECT wo_bills.id, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.stage, wo_bills.quantity,' \
                        ' wo_bills.rate, wo_bills.approval_2_amount, wo_bills.cleared_balance, wo_bills.created_at, wo_bills.approved_on FROM wo_bills WHERE project_id='+str(project_id)+' AND trade="NT/NMR"'
            cur = mysql.connection.cursor()
            cur.execute(bills_query)
            nt_nmr_bills = cur.fetchall()

        return render_template('view_work_orders.html', projects=projects, work_orders=work_orders, nt_nmr_bills=nt_nmr_bills)


@app.route("/view_unsigned_work_order", methods=['GET'])
def view_unsigned_work_order():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_unsigned_work_order'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        work_orders = []

        unsigned_query = 'SELECT p.project_name, p.project_number, wo.id, wo.trade, wo.value, c.name, wo.verification_code FROM work_orders wo ' \
                         'INNER JOIN projects p on p.project_id=wo.project_id AND wo.signed=0 INNER JOIN contractors c on c.id=wo.contractor_id'
        cur = mysql.connection.cursor()
        cur.execute(unsigned_query)
        result = cur.fetchall()
        for i in result:
            work_orders.append({
                'project_name': i[0],
                'project_number': i[1],
                'id': i[2],
                'trade': i[3],
                'value': i[4],
                'contractor_name': i[5],
                'verification_code': i[6],

            })

        return render_template('unsigned_work_orders.html', work_orders=work_orders)


@app.route("/view_unapproved_work_order", methods=['GET'])
def view_unapproved_work_order():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_unapproved_work_order'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head','QS Engineer']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        work_orders = []

        unsigned_query = 'SELECT p.project_name, p.project_number, wo.id, wo.trade, wo.value, c.name FROM work_orders wo ' \
                         'INNER JOIN projects p on p.project_id=wo.project_id AND wo.signed=1 AND wo.approved=0 INNER JOIN contractors c on c.id=wo.contractor_id'
        cur = mysql.connection.cursor()
        cur.execute(unsigned_query)
        result = cur.fetchall()
        for i in result:
            value = 0
            if i[4].strip() != '':
                try:
                    value =  str(int(float(i[4].strip().replace(',',''))))
                except:
                    value = i[4].strip().replace(',','')
            work_orders.append({
                'project_name': i[0],
                'project_number': i[1],
                'id': i[2],
                'trade': i[3],
                'value': value,
                'contractor_name': i[5],

            })

        return render_template('unapproved_work_order.html', work_orders=work_orders)


@app.route('/update_slab_area', methods=['POST'])
def update_slab_area():
    project_id = request.form['project_id']
    query = 'SELECT basement_slab_area, gf_slab_area, ff_slab_area, sf_slab_area, tf_slab_area, fof_slab_area, fif_slab_area, tef_slab_area from projects WHERE project_id=' + str(project_id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchone()
    total_bua_sum = 0
    for i in result:
        if i is not None and str(i).strip() != '' and str(i).strip() != 'NIL':
            total_bua_sum = total_bua_sum + int(i)
    return str(total_bua_sum)


@app.route('/check_if_floors_updated', methods=['POST'])
def check_if_floors_updated():
    project_id = request.form['project_id']
    query = 'SELECT id, floors from work_orders WHERE project_id=' + str(project_id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchone()
    if result is not None:
        return jsonify({'floors_updated': True, 'floors': result[1]})
    return jsonify({'floors_updated': False})

@app.route('/view_ph_approval_indents', methods=['GET'])
def view_ph_approval_indents():
    cur = mysql.connection.cursor()
    indents_query = 'SELECT indents.id, ' \
                    'projects.project_id, ' \
                    'projects.project_name, ' \
                    'indents.material, ' \
                    'indents.quantity, ' \
                    'indents.unit, ' \
                    'indents.purpose, ' \
                    'App_users.name, ' \
                    'indents.timestamp FROM indents ' \
                    'INNER JOIN projects on ' \
                    'indents.status="po_uploaded" AND ' \
                    'indents.project_id=projects.project_id ' \
                    'LEFT OUTER JOIN App_users on ' \
                    'indents.created_by_user=App_users.user_id'
    cur.execute(indents_query)
    data = []
    projects = {}
    result = cur.fetchall()
    for i in result:
        i = list(i)
        if i[2] not in projects.keys():
            projects[i[2]] = []
        if len(str(i[8]).strip()) > 0:
            i[8] = str(i[8]).strip()
            timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
            IST = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(IST)
            time_since_creation = current_time - timestamp
            difference_in_seconds = time_since_creation.total_seconds()
            difference_in_hours = difference_in_seconds // 3600
            if difference_in_hours >= 24:
                difference_in_days = int(difference_in_hours // 24)
                hours_remaining = difference_in_hours % 24
                i[8] = str(int(difference_in_days)) + ' days, ' + str(
                    int(hours_remaining)) + 'hours'
            else:
                i[8] = str(int(difference_in_hours)) + ' hours'
        
        projects[i[2]].append(i)
        data.append(i)
    return render_template('ph_approval_indents.html', result=data, projects=projects)

@app.route('/view_qs_approval_indents', methods=['GET'])
def view_qs_approval_indents():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_indents'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Executive', 'Purchase Head', 'QS Info']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        current_user_role = session['role']
        indents_query = ''
        if current_user_role in ['Super Admin', 'COO', 'QS Head', 'Purchase Head','QS Info']:
            indents_query = 'SELECT indents.id, ' \
                            'projects.project_id, ' \
                            'projects.project_name, ' \
                            'indents.material, ' \
                            'indents.quantity, ' \
                            'indents.unit, ' \
                            'indents.purpose, ' \
                            'App_users.name, ' \
                            'indents.timestamp FROM indents ' \
                            'INNER JOIN projects on ' \
                            'indents.status="approved" AND ' \
                            'indents.project_id=projects.project_id ' \
                            'LEFT OUTER JOIN App_users on ' \
                            'indents.created_by_user=App_users.user_id'

        elif current_user_role in ['QS Engineer','Purchase Executive']:
            indents_query = 'SELECT indents.id, ' \
                            'projects.project_id, ' \
                            'projects.project_name, ' \
                            'indents.material, ' \
                            'indents.quantity, ' \
                            'indents.unit, ' \
                            'indents.purpose, ' \
                            'App_users.name, ' \
                            'indents.timestamp FROM indents ' \
                            'INNER JOIN projects on ' \
                            'indents.status="approved" AND ' \
                            'indents.project_id=projects.project_id AND ' \
                            'indents.project_id IN ' + str(get_projects_for_current_user()) +' '\
                            'LEFT OUTER JOIN App_users on ' \
                            'indents.created_by_user=App_users.user_id'
        cur.execute(indents_query)
        data = []
        result = cur.fetchall()
        for i in result:
            i = list(i)
            if len(str(i[8]).strip()) > 0:
                i[8] = str(i[8]).strip()
                timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                IST = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(IST)
                time_since_creation = current_time - timestamp
                difference_in_seconds = time_since_creation.total_seconds()
                difference_in_hours = difference_in_seconds // 3600
                if difference_in_hours >= 24:
                    difference_in_days = int(difference_in_hours // 24)
                    if difference_in_days >= 365:
                        years = int(difference_in_days // 365)
                        days = int(difference_in_days % 365)
                        difference_in_days = str(years) + ' year(s), ' + str(days)
                    
                    hours_remaining = difference_in_hours % 24
                    i[8] = str(difference_in_days) + ' days, ' + str(
                        int(hours_remaining)) + 'hours'
                else:
                    i[8] = str(int(difference_in_hours)) + ' hours'
            data.append(i)
        return render_template('qs_approval_indents.html', result=data)


@app.route('/view_ph_approved_indents', methods=['GET'])
def view_ph_approved_indents():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_indents'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Executive', 'Purchase Head','Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        current_user_role = session['role']
        indents_query = ''
        if current_user_role in ['Super Admin', 'COO', 'QS Head', 'Purchase Head','Billing']:
            indents_query = 'SELECT indents.id, ' \
                            'projects.project_id, ' \
                            'projects.project_name, ' \
                            'indents.material, ' \
                            'indents.quantity, ' \
                            'indents.unit, ' \
                            'indents.purpose, ' \
                            'App_users.name, ' \
                            'indents.timestamp, indents.billed, indents.po_number FROM indents ' \
                            'INNER JOIN projects on ' \
                            'indents.status="approved_by_ph" AND ' \
                            'indents.project_id=projects.project_id ' \
                            'LEFT OUTER JOIN App_users on ' \
                            'indents.created_by_user=App_users.user_id'
        elif current_user_role in ['Purchase Executive']:
            indents_query = 'SELECT indents.id, ' \
                            'projects.project_id, ' \
                            'projects.project_name, ' \
                            'indents.material, ' \
                            'indents.quantity, ' \
                            'indents.unit, ' \
                            'indents.purpose, ' \
                            'App_users.name, ' \
                            'indents.timestamp, indents.billed, indents.po_number FROM indents ' \
                            'INNER JOIN projects on ' \
                            'indents.status="approved_by_ph" AND ' \
                            'indents.project_id=projects.project_id AND ' \
                            'indents.project_id IN ' + str(get_projects_for_current_user()) +' '\
                            'LEFT OUTER JOIN App_users on ' \
                            'indents.created_by_user=App_users.user_id'
         
        cur.execute(indents_query)
        data = []
        projects = {}
        result = cur.fetchall()
        for i in result:
            i = list(i)
            if i[2] not in projects.keys():
                projects[i[2]] = []
        
            if len(str(i[8]).strip()) > 0:
                i[8] = str(i[8]).strip()
                timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                IST = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(IST)
                time_since_creation = current_time - timestamp
                difference_in_seconds = time_since_creation.total_seconds()
                difference_in_hours = difference_in_seconds // 3600
                if difference_in_hours >= 24:
                    difference_in_days = int(difference_in_hours // 24)
                    if difference_in_days >= 365:
                        years = int(difference_in_days // 365)
                        days = int(difference_in_days % 365)
                        difference_in_days = str(years) + ' year(s), ' + str(days)
                    hours_remaining = difference_in_hours % 24
                    i[8] = str(difference_in_days) + ' days, ' + str(
                        int(hours_remaining)) + 'hours'
                else:
                    i[8] = str(int(difference_in_hours)) + ' hours'
            projects[i[2]].append(i)
            data.append(i)
        return render_template('ph_approval_indents.html', result=data, projects=projects)

@app.route('/view_approved_indents', methods=['GET'])
def view_approved_indents():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_indents'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Executive', 'Purchase Head','QS Info']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        current_user_role = session['role']
        if current_user_role in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Head']:
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp FROM indents INNER JOIN projects on indents.status="approved_by_qs"' \
                            ' AND indents.project_id=projects.project_id ' \
                            ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'

            cur.execute(indents_query)
            data = []
            result = cur.fetchall()
            projects = {}
            for i in result:
                i = list(i)
                if i[2] not in projects.keys():
                    projects[i[2]] = []
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata') 
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                projects[i[2]].append(i)
                data.append(i)
            return render_template('approved_indents.html', result=data, projects=projects)
        elif current_user_role == 'Purchase Executive':
            access_tuple = get_projects_for_current_user()
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp FROM indents INNER JOIN projects on indents.status="approved_by_qs" AND indents.project_id=projects.project_id AND indents.project_id IN ' + str(
                access_tuple) + '' \
                                ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
            cur.execute(indents_query)
            data = []
            projects = {}
            result = cur.fetchall()
            for i in result:
                i = list(i)
                if i[2] not in projects.keys():
                    projects[i[2]] = []
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                projects[i[2]].append(i)
                data.append(i)
            return render_template('approved_indents.html', result=data, projects=projects)
        else:
            return 'You do not have access to view this page'

@app.route('/view_deleted_indents', methods=['GET'])
def view_deleted_indents():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_POs'
        return redirect('/login')

    if request.method == 'GET':
        cur = mysql.connection.cursor()
        current_user_role = session['role']
        if current_user_role in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Head']:
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp FROM indents INNER JOIN projects on indents.status="deleted" AND indents.project_id=projects.project_id ' \
                            ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'

            cur.execute(indents_query)
            data = []
            result = cur.fetchall()
            for i in result:
                i = list(i)
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                data.append(i)
            return render_template('deleted_indents.html', result=data)
        elif current_user_role == 'Purchase Executive':
            access_tuple = get_projects_for_current_user()
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.purchase_order FROM indents INNER JOIN projects on indents.status="deleted" AND indents.project_id=projects.project_id AND indents.project_id IN ' + str(
                access_tuple) + '' \
                                ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
            cur.execute(indents_query)
            data = []
            result = cur.fetchall()
            for i in result:
                i = list(i)
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                data.append(i)
            return render_template('deleted_indents.html', result=data)
        else:
            return 'You do not have access to view this page'

@app.route('/view_approved_POs', methods=['GET'])
def view_approved_POs():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_approved_POs'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Executive', 'Purchase Head']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        current_user_role = session['role']
        if current_user_role in ['Super Admin', 'COO', 'QS Head', 'QS Engineer', 'Purchase Head']:
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp FROM indents INNER JOIN projects on indents.status="po_uploaded" AND indents.project_id=projects.project_id ' \
                            ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'

            cur.execute(indents_query)
            data = []
            result = cur.fetchall()
            for i in result:
                i = list(i)
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                data.append(i)
            return render_template('approved_pos.html', result=data)
        elif current_user_role == 'Purchase Executive':
            access_tuple = get_projects_for_current_user()
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.purchase_order, indents.po_number FROM indents INNER JOIN projects on indents.status="po_uploaded" AND indents.project_id=projects.project_id AND indents.project_id IN ' + str(
                access_tuple) + '' \
                                ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
            cur.execute(indents_query)
            data = []
            result = cur.fetchall()
            for i in result:
                i = list(i)
                if len(str(i[8]).strip()) > 0:
                    i[8] = str(i[8]).strip()
                    timestamp = datetime.strptime(i[8] + ' 2022 +0530', '%A %d %B %H:%M %Y %z')
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = datetime.now(IST)
                    time_since_creation = current_time - timestamp
                    difference_in_seconds = time_since_creation.total_seconds()
                    difference_in_hours = difference_in_seconds // 3600
                    if difference_in_hours >= 24:
                        difference_in_days = int(difference_in_hours // 24)
                        if difference_in_days >= 365:
                            years = int(difference_in_days // 365)
                            days = int(difference_in_days % 365)
                            difference_in_days = str(years) + ' year(s), ' + str(days)
                        hours_remaining = difference_in_hours % 24
                        i[8] = str(difference_in_days) + ' days, ' + str(
                            int(hours_remaining)) + 'hours'
                    else:
                        i[8] = str(int(difference_in_hours)) + ' hours'
                data.append(i)
            return render_template('approved_pos.html', result=data)
        else:
            return 'You do not have access to view this page'

@app.route('/approve_indent_by_qs', methods=['GET'])
def approve_indent_by_qs():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_indent_details'
        return redirect('/login')
    if request.method == 'GET':
        indent_id = request.args['id']
        cur = mysql.connection.cursor()
        query = 'UPDATE indents set status=%s WHERE id=%s'
        cur.execute(query, ('approved_by_qs',indent_id))
        mysql.connection.commit()
        flash('Indent approved','success')
        return redirect('/view_qs_approval_indents')    

@app.route('/mark_as_billed', methods=['GET'])
def mark_as_billed():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/mark_as_billed'
    if request.method == 'GET':
        indent_id = request.args['id']
        cur = mysql.connection.cursor()
        query = 'UPDATE indents set billed=1 WHERE id='+str(indent_id)
        cur.execute(query)
        mysql.connection.commit()
        flash('Indent marked as billed','success')
        return redirect('/view_ph_approved_indents')

@app.route('/rollback_indent_to_qs', methods=['GET'])
def rollback_indent_to_qs():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/rollback_indent_to_qs'
    if request.method == 'GET':
        indent_id = request.args['id']
        cur = mysql.connection.cursor()
        query = 'UPDATE indents set status=%s WHERE id=%s'
        cur.execute(query, ('approved',indent_id))
        mysql.connection.commit()
        flash('Indent rolled back to qs','success')
        return redirect('/view_qs_approval_indents')

@app.route('/rollback_indent_by_ph', methods=['GET'])
def rollback_indent_by_ph():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/rollback_indent_by_ph'
    if request.method == 'GET':
        indent_id = request.args['id']
        cur = mysql.connection.cursor()
        query = 'UPDATE indents set status=%s WHERE id=%s'
        cur.execute(query, ('approved_by_qs',indent_id))
        mysql.connection.commit()
        flash('Indent rolled back','success')
        return redirect('/view_qs_approval_indents')

@app.route('/approve_indent_by_ph', methods=['GET'])
def approve_indent_by_ph():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/approve_indent_by_ph'
        return redirect('/login')
    if request.method == 'GET':
        indent_id = request.args['id']
        cur = mysql.connection.cursor()
        difference_cost = request.args['difference_cost']
        query = 'UPDATE indents set status="approved_by_ph" , difference_cost="'+str(difference_cost)+'" WHERE id='+str(indent_id)
        cur.execute(query)
        mysql.connection.commit()
        get_indent_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                                   ', indents.timestamp, indents.created_by_user, indents.acted_by_user FROM indents INNER JOIN projects on indents.project_id=projects.project_id ' \
                                   ' AND indents.id=' + str(indent_id)
        cur.execute(get_indent_query)
        result = cur.fetchone()
        if result is not None:
            notification_body = 'PO uploaded for indent with id ' + str(indent_id) + '. Details: ' + str(
                result[4]) + ' ' + str(result[5]) + ' ' + str(result[3]) + ' For project ' + str(result[2])
            IST = pytz.timezone('Asia/Kolkata')
            datetime_ist = datetime.now(IST)
            timestamp = datetime_ist.strftime('%A %d %B %H:%M')
            send_app_notification('PO Uploaded', notification_body, str(result[8]), str(result[8]),
                                    'PO uploads', timestamp)
            send_app_notification('PO Uploaded', notification_body, str(result[9]), str(result[9]),
                                    'PO uploads', timestamp)
        flash('Indent approved','success')
        return redirect('/view_approved_POs')

@app.route('/view_indent_details', methods=['GET'])
def view_indent_details():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_indent_details'
        return redirect('/login')
    if request.method == 'GET':
        indent_id = request.args['indent_id']
        cur = mysql.connection.cursor()
        indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                        ', App_users.name, indents.timestamp, indents.purchase_order, indents.status, indents.difference_cost, indents.approval_taken, indents.difference_cost_sheet, indents.comments, indents.attachment, indents.po_number FROM indents INNER JOIN projects on indents.id=' + str(
            indent_id) + ' AND indents.project_id=projects.project_id ' \
                         ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
        cur.execute(indents_query)
        result = cur.fetchone()
        return render_template('view_indent_details.html', result=result)

@app.route('/update_indent_comments', methods=['POST'])
def update_indent_comments():
    indent_id = request.form['indent_id']
    comments = request.form['comments']
    cur = mysql.connection.cursor()
    query = 'UPDATE  indents SET comments=%s WHERE id=%s'
    cur.execute(query, (comments, indent_id))
    mysql.connection.commit()
    flash('Comment updated', 'success')
    return redirect('/view_indent_details?indent_id='+str(indent_id))

@app.route('/edit_indent', methods=['GET','POST'])
def edit_indent():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_indent_details'
        return redirect('/login')
    if request.method == 'GET':
        indent_id = request.args['indent_id']
        cur = mysql.connection.cursor()
        indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                        ', App_users.name, indents.timestamp, indents.purchase_order, indents.status FROM indents INNER JOIN projects on indents.id=' + str(
            indent_id) + ' AND indents.project_id=projects.project_id ' \
                         ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
        cur.execute(indents_query)
        result = cur.fetchone()
        return render_template('edit_indent.html', result=result, materials=materials)
    else: 
        indent_id = request.form['indent_id']
        material = request.form['material']
        quantity = request.form['quantity']
        unit = request.form['unit']
        purpose = request.form['purpose']
        cur = mysql.connection.cursor()
        query = 'UPDATE indents SET material=%s, quantity=%s, unit=%s, purpose=%s WHERE id=%s'
        values = (material, quantity, unit, purpose, indent_id)
        cur.execute(query, values)
        mysql.connection.commit()
        flash('Indent updated','success')
        return redirect('/view_indent_details?indent_id='+str(indent_id))


@app.route('/delete_indent', methods=['GET'])
def delete_indent():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/view_indent_details'
        return redirect('/login')
    if request.method == 'GET':
        indent_id = request.args['indent_id'] 
        cur = mysql.connection.cursor()
        query = 'UPDATE indents SET status="deleted" WHERE id='+str(indent_id)
        cur.execute(query)
        mysql.connection.commit()
        flash('Indent deleted','danger')
        return redirect('/view_qs_approval_indents')

@app.route('/close_po_with_comments', methods=['POST'])
def close_po_with_comments():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_bill'
        return redirect('/login')
    if request.method == 'POST':
        indent_id = request.form['indent_id']
        comments = request.form['comments'].replace('"', '').replace("'", '')

        cur = mysql.connection.cursor()
        query = 'UPDATE indents set status=%s, comments=%s WHERE id=%s'
        values = ('po_uploaded',comments, indent_id)
        cur.execute(query, values)
        mysql.connection.commit()
        flash('Indent closed with comment successfully', 'success')
        return redirect('/view_approved_indents')



@app.route('/upload_po_for_indent', methods=['POST'])
def upload_po_for_indent():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_bill'
        return redirect('/login')
    if request.method == 'POST':
        indent_id = request.form['indent_id']

        difference_cost = request.form['difference_cost']
        po_number = request.form['po_number']
        
        cur = mysql.connection.cursor()
        query = 'UPDATE indents set difference_cost=%s, po_number=%s WHERE id=%s'
        values = (difference_cost, po_number, indent_id)
        cur.execute(query, values)
        mysql.connection.commit()

        if 'difference_cost_sheet' in request.files:
            file = request.files['difference_cost_sheet']
            if file.filename != '':                
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = time.time()
                    filename = str(current_time)+'_'+filename
                    output = send_to_s3(file, app.config["S3_BUCKET"], str(indent_id) + '_dc_' + filename)
                    if output != 'success':
                        flash('File upload failed', 'danger')
                        return redirect(request.referrer)
                    cur = mysql.connection.cursor()
                    query = 'UPDATE indents set difference_cost_sheet=%s WHERE id=%s'
                    values = (str(indent_id) + '_dc_' + filename, indent_id)
                    cur.execute(query, values)
                    mysql.connection.commit()
                    flash('Difference cost sheet Uploaded successfully', 'success')
                



        if 'purchase_order' in request.files:
            file = request.files['purchase_order']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    IST = pytz.timezone('Asia/Kolkata')
                    current_time = time.time()
                    filename = str(current_time)+'_'+filename
                    output = send_to_s3(file, app.config["S3_BUCKET"], str(indent_id) + '_' + filename)
                    if output != 'success':
                        flash('File upload failed', 'danger')
                        return redirect(request.referrer)
                    cur = mysql.connection.cursor()
                    query = 'UPDATE indents set status=%s, purchase_order=%s WHERE id=%s'
                    values = ('po_uploaded', str(indent_id) + '_' + filename, indent_id)
                    cur.execute(query, values)
                    mysql.connection.commit()

                    get_indent_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                                    ', indents.timestamp, indents.created_by_user, indents.acted_by_user FROM indents INNER JOIN projects on indents.project_id=projects.project_id ' \
                                    ' AND indents.id=' + str(indent_id)
                    cur.execute(get_indent_query)
                    result = cur.fetchone()
                    if result is not None:
                        notification_body = 'PO uploaded for indent with id ' + str(indent_id) + '. Details: ' + str(
                            result[4]) + ' ' + str(result[5]) + ' ' + str(result[3]) + ' For project ' + str(result[2])
                        IST = pytz.timezone('Asia/Kolkata')
                        datetime_ist = datetime.now(IST)
                        timestamp = datetime_ist.strftime('%A %d %B %H:%M')
                        send_app_notification('PO Uploaded', notification_body, str(result[8]), str(result[8]),
                                            'PO uploads', timestamp)
                        send_app_notification('PO Uploaded', notification_body, str(result[9]), str(result[9]),
                                            'PO uploads', timestamp)
                    flash('PO Uploaded successfully', 'success')
        return redirect('/view_indent_details?indent_id=' + str(indent_id))


@app.route('/sign_wo', methods=['GET', 'POST'])
def sign_wo():
    if request.method == 'GET':
        if 'wo_id' in request.args:
            work_order_query = 'SELECT p.project_name, p.project_number, wo.trade, wo.value, c.name,' \
                               'c.pan, c.code, c.address, wo.wo_number, wo.cheque_no, wo.comments, wo.created_at , wo.total_bua, wo.cost_per_sqft, wo.verification_code, wo.difference_cost_sheet' \
                               ' FROM work_orders wo ' \
                               'INNER JOIN projects p on p.project_id=wo.project_id AND wo.signed=0 AND wo.id=' + str(
                request.args['wo_id']) + ' INNER JOIN contractors c on c.id=wo.contractor_id'
            cur = mysql.connection.cursor()
            cur.execute(work_order_query)
            result = cur.fetchone()
            if result is None:
                flash('This work order is already signed', 'danger')
                return redirect('/login')

            milestones_query = 'SELECT stage, percentage from wo_milestones WHERE work_order_id='+str(request.args['wo_id'])
            cur.execute(milestones_query)
            milestones_result = cur.fetchall()
            milestone_data = []
            for item in milestones_result:
                try:
                    milestone_data.append({
                        "stage": item[0],
                        "percent": item[1],
                        "amount": int((float(item[1]) / 100 * float(result[3])))
                    })
                except:
                    milestone_data.append({
                        "stage": item[0],
                        "percent": '',
                        "amount": ''
                    })
        return render_template('sign_wo.html',milestone_data=milestone_data, wo=result, wo_id=str(request.args['wo_id']))


@app.route('/upload_signed_wo', methods=['POST'])
def upload_signed_wo():
    # project_name+trade+contractor_name
    wo_id = request.form['wo_id']
    cur = mysql.connection.cursor()

    check_if_signed_query = 'SELECT signed FROM work_orders WHERE id='+ request.form['wo_id']
    cur.execute(check_if_signed_query)
    check_if_signed_res = cur.fetchone()
    if str(check_if_signed_res[0]) == '1':
        flash('This work order is already signed', 'danger')
        return redirect('/login')


    project_name = request.form['project_name']
    trade = request.form['trade']
    contractor_name = request.form['contractor_name']
    
    project_name = project_name.capitalize().replace(' ', '_').replace('"', '').replace("'", '')
    trade = trade.capitalize().replace(' ', '_').replace('"', '').replace("'", '')
    contractor_name = contractor_name.capitalize().replace(' ', '_').replace('"', '').replace("'", '')

    filename = project_name+'_'+trade+'_'+contractor_name+'_'+ str(wo_id) + '.pdf'

    query = 'UPDATE work_orders SET signed=1, filename="'+filename+'" WHERE id=' + wo_id
    cur.execute(query)
    mysql.connection.commit()


    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash('Work order signed!', 'success')
            output = send_to_s3(file, app.config["S3_BUCKET"], filename, 'public-read','application/pdf')
            if output != 'success':
                flash('File upload failed', 'danger')
                return redirect(request.referrer)
            return 'success'


@app.route('/approve_wo', methods=['GET', 'POST'])
def approve_wo():
    if request.method == 'GET':
        if 'wo_id' in request.args:
            work_order_query = 'SELECT p.project_name, p.project_number, wo.trade, wo.value, c.name,' \
                               'c.pan, c.code, c.address, wo.wo_number, wo.cheque_no, wo.comments, wo.created_at, wo.filename, wo.difference_cost_sheet, wo.project_id' \
                               ' FROM work_orders wo ' \
                               'INNER JOIN projects p on p.project_id=wo.project_id AND wo.signed=1 AND wo.approved=0 AND wo.id=' + str(
                request.args['wo_id']) + ' ' \
                                         'INNER JOIN contractors c on c.id=wo.contractor_id'

            cur = mysql.connection.cursor()
            cur.execute(work_order_query)
            result = cur.fetchone()


            old_work_order_exists_for_same_trade = False
            older_work_order_exists_query = 'SELECT id from work_orders WHERE id !='+str(request.args['wo_id'])+' AND project_id='+str(result[14])+' AND trade LIKE "%'+str(result[2])+'%"'
            cur.execute(older_work_order_exists_query)
            old_wo_res = cur.fetchone()
            if  old_wo_res is not None:
                old_work_order_exists_for_same_trade = True


        return render_template('approve_wo.html', wo=result, wo_id=str(request.args['wo_id']), old_work_order_exists_for_same_trade=old_work_order_exists_for_same_trade)
    else:
        wo_id = request.form['wo_id']
        cur = mysql.connection.cursor()
        query = 'UPDATE work_orders SET approved=1 WHERE id=' + wo_id
        cur.execute(query)
        mysql.connection.commit()
        flash('Work order approved!', 'success')
        return redirect('/view_unapproved_work_order')


@app.route('/archive_project', methods=['GET'])
def archive_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/archive_project'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Sales Executive', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if 'project_id' in request.args:
        cur = mysql.connection.cursor()
        query = 'UPDATE projects set archived=1 WHERE project_id=' + str(request.args['project_id'])
        cur.execute(query)
        mysql.connection.commit()
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' archived project ' + request.args['project_name'])
        flash('Project archived', 'warning')
        return redirect(request.referrer)
    else:
        flash('Missing fields', 'danger')
        return redirect(request.referrer)


@app.route('/unarchive_project', methods=['GET'])
def unarchive_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/unarchive_project'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Sales Executive', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if 'project_id' in request.args:
        cur = mysql.connection.cursor()
        query = 'UPDATE projects set archived=0 WHERE project_id=' + str(request.args['project_id'])
        cur.execute(query)
        mysql.connection.commit()
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' unarchived project ' + request.args['project_name'])
        flash('Project unarchived', 'success')
        return redirect(request.referrer)
    else:
        flash('Missing fields', 'danger')
        return redirect(request.referrer)


@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/create_project'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Sales Executive', 'Billing','Planning']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        sales_executives_query = 'SELECT user_id, name from App_users WHERE role="Sales Executive"'
        cur.execute(sales_executives_query)
        result = cur.fetchall()
        return render_template('create_project.html', sales_executives=result)
    else:
        cur = mysql.connection.cursor()

        client_name = request.form['client_name']
        client_phone = request.form['client_phone']

        create_user_query = 'INSERT into App_users (name, phone, role) values (%s, %s, "Client")'
        cur.execute(create_user_query, (client_name, client_phone))    

        column_names = list(request.form.keys())
        values = list(request.form.values())

        column_names.append('created_at')
        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')
        values.append(timestamp)

        new_project_query = 'INSERT into projects' + str(tuple(column_names)).replace("'", "") + 'values ' + str(
            tuple(values))
        cur.execute(new_project_query)
        project_id = cur.lastrowid
        cost_sheet_filename = ''
        site_inspection_report_filename = ''
        if 'cost_sheet' in request.files:
            file = request.files['cost_sheet']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                cost_sheet_filename = 'cost_sheet_' + str(project_id) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], cost_sheet_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)

        if 'site_inspection_report' in request.files:
            file = request.files['site_inspection_report']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                site_inspection_report_filename = 'site_inspection_report_' + str(project_id) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], site_inspection_report_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
        
        if 'agreement' in request.files:
            file = request.files['agreement']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                site_inspection_report_filename = 'agreement' + str(project_id) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], site_inspection_report_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)

        update_filename_query = 'UPDATE projects set cost_sheet=%s, site_inspection_report=%s WHERE project_id=%s'
        cur.execute(update_filename_query, (cost_sheet_filename, site_inspection_report_filename, str(project_id)))
        flash('Project created successfully', 'success')
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' created project ' + request.form['project_name'] + ' with number ' + request.form['project_number'])
        mysql.connection.commit()
        return redirect(request.referrer)

@app.route('/edit_task', methods=['POST'])
def edit_task():
    task_id = request.form['task_id']
    task_name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    percent = request.form['percent']

    cur = mysql.connection.cursor()
    query = 'UPDATE Tasks set payment_percentage=%s, task_name=%s, task_start_date=%s, task_finish_date=%s WHERE task_id=%s'
    cur.execute(query, (percent, task_name, start_date, end_date, task_id))

    mysql.connection.commit()
    flash('Task has been edited', 'success')
    return redirect(request.referrer)

@app.route('/mark_task_complete', methods=['GET'])
def mark_task_complete():
    subtask_id = request.args['id']
    task_id = request.args['task_id']
    note = request.args['note']
    cur = mysql.connection.cursor()
    
    query = 'SELECT progress, s_note from Tasks WHERE task_id='+str(task_id)
    cur.execute(query)
    res = cur.fetchone()
    progress = res[0]
    progress = progress + subtask_id + '|'

    s_note = res[1]
    s_note = s_note + note
    s_note = s_note + '|'

    update_query = 'UPDATE Tasks SET progress=%s, s_note=%s WHERE task_id=%s'
    cur.execute(update_query, (progress, s_note, task_id))

    mysql.connection.commit()

    flash('Sub task marked as completed', 'success')
    return redirect(request.referrer)


@app.route('/mark_task_due', methods=['GET'])
def mark_task_due():
    task_id = request.args['id']
    note = request.args['note']
    cur = mysql.connection.cursor()
    query = 'UPDATE Tasks SET due=true, p_note=%s WHERE task_id=%s'
    cur.execute(query, (note, task_id))
    mysql.connection.commit()

    flash('Task marked as due', 'success')
    return redirect(request.referrer)

@app.route('/mark_task_paid', methods=['GET'])
def mark_task_paid():
    task_id = request.args['id']
    note = request.args['note']
    cur = mysql.connection.cursor()
    query = 'UPDATE Tasks SET paid=true, p_note=%s WHERE task_id=%s'
    cur.execute(query, (note, task_id))
    mysql.connection.commit()

    flash('Task marked as paid', 'success')
    return redirect(request.referrer)

@app.route('/client_billing', methods=['GET'])
def client_billing():
    project_id = request.args['project_id']
    cur = mysql.connection.cursor()
    project_details_query = 'SELECT project_name from projects WHERE project_id='+str(project_id)
    cur.execute(project_details_query)
    res = cur.fetchone()
    if res is None:
        return 'Invalid project id'
    project_name = res[0]
    
    tasks_query = 'SELECT * from Tasks WHERE project_id='+str(project_id)+' ORDER BY task_id'
    cur.execute(tasks_query)
    res = cur.fetchall()
    tasks = []
    if res is not None:
        for i in res:
            task_item = {
                'id': i[0],
                'name': i[2],
                'start_date': i[3],
                'end_date': i[4],
                'percent': i[7],
                'due': i[9],
                'paid': i[8],
                'is_non_tender': i[11],
                'progress': i[10],                
            }
            task_item['sub_tasks'] = []
            if len(i[6]) > 0:
                sub_task_list = i[6].split('^')
                progress_list =  i[10].split('|')
                for j in range(len(sub_task_list)):
                    sub_task_item = sub_task_list[j]
                    task_name = sub_task_item.split('|')
                    if len(task_name[0]) > 0:
                        task_item['sub_tasks'].append({
                            'name': task_name[0],
                            'is_complete': len(i[10].strip()) > 0 and  str(j) in i[10].strip()
                        })
            tasks.append(task_item)

    return render_template('client_billing.html', project_name=project_name, tasks=tasks)

@app.route('/edit_project', methods=['GET', 'POST'])
def edit_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/edit_project'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'COO', 'Sales Executive', 'Billing','Planning']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        fields_as_string = ", ".join(project_fields)
        get_details_query = 'SELECT ' + fields_as_string + ' from projects WHERE project_id=' + str(
            request.args['project_id'])
        cur = mysql.connection.cursor()
        cur.execute(get_details_query)
        result = cur.fetchone()
        project = projects(*result)
        sales_executives_query = 'SELECT user_id, name from App_users WHERE role="Sales Executive"'
        cur.execute(sales_executives_query)
        result = cur.fetchall()
        return render_template('edit_project.html', p=project, sales_executives=result)
    else:

        column_names = list(request.form.keys())

        update_string = ""
        for i in column_names[:-1]:
            if request.form[i].strip() != '':
                update_string += i + '="' + request.form[i].replace('"','""').replace("'","''") + '", '
        # Remove the last comma
        update_string = update_string[:-2]
        update_project_query = 'UPDATE projects SET ' + update_string + ' WHERE project_id=' + str(
            request.form['project_id'])
        cur = mysql.connection.cursor()
        cur.execute(update_project_query)
        mysql.connection.commit()
        cost_sheet_filename = ''
        site_inspection_report_filename = ''
        if 'cost_sheet' in request.files:
            file = request.files['cost_sheet']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                cost_sheet_filename = 'cost_sheet_' + str(request.form['project_id']) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], cost_sheet_filename)
                if output == 'success':
                    update_filename_query = 'UPDATE projects set cost_sheet=%s WHERE project_id=%s'
                    cur.execute(update_filename_query,
                                (cost_sheet_filename, str(request.form['project_id'])))

        if 'site_inspection_report' in request.files:
            file = request.files['site_inspection_report']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                site_inspection_report_filename = 'site_inspection_report_' + str(
                    request.form['project_id']) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], site_inspection_report_filename)
                if output == 'success':
                    update_filename_query = 'UPDATE projects set site_inspection_report=%s WHERE project_id=%s'
                    cur.execute(update_filename_query,
                                (site_inspection_report_filename, str(request.form['project_id'])))
        if 'agreement' in request.files:
            file = request.files['agreement']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                agreement_filename = 'agreement_' + str(request.form['project_id']) + '_' + filename
                output = send_to_s3(file, app.config["S3_BUCKET"], agreement_filename)
                if output == 'success':
                    update_filename_query = 'UPDATE projects set agreement=%s WHERE project_id=%s'
                    cur.execute(update_filename_query,
                                (agreement_filename, str(request.form['project_id'])))

        mysql.connection.commit()
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' updated project ' + request.form['project_name'] + ' with number ' + request.form['project_number'])
        flash('Project updated successfully', 'success')
        return redirect('/view_project_details?project_id=' + str(request.form['project_id']))

        # This has to be checked. The if condition is returning false even when everything is okay
        # if cur.rowcount == 1:
        #     flash('Project updated successfully', 'success')
        #     return redirect('/view_project_details?project_id=' + str(request.form['project_id']))
        # else:
        #     flash('Project not updated', 'danger')
        #     return redirect(request.referrer)


@app.route('/unapproved_projects', methods=['GET'])
def unapproved_projects():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/unapproved_projects'
        return redirect('/login')
    if session['role'] not in ['Super Admin', 'Billing']:
        flash('You do not have permission to view that page', 'danger')
        return redirect(request.referrer)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        unapproved_projects_query = 'SELECT project_id, project_name, project_number from projects WHERE is_approved=0 AND archived=0 ORDER BY project_number'
        cur.execute(unapproved_projects_query)
        result = cur.fetchall()
        return render_template('unapproved_projects.html', projects=result)

@app.route('/block_project', methods=['POST'])
def block_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/projects'
        return redirect('/login')
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        reason = request.form['reason']
        query = 'UPDATE projects SET blocked=1, block_reason= "'+reason.replace('"','""').replace("'","''")+'" WHERE project_id='+str(request.form['project_id'])
        cur.execute(query)
        mysql.connection.commit()
        project_name = getProjectName(str(request.form['project_id']))
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' blocked project ' + project_name + ' with reason '+ reason)
        return redirect('/projects')

@app.route('/unblock_project', methods=['GET'])
def unblock_project():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/projects'
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        query = 'UPDATE projects SET blocked=0 WHERE project_id='+str(request.args['project_id'])
        cur.execute(query)
        mysql.connection.commit()
        project_name = getProjectName(str(request.args['project_id']))
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' unblocked project ' + project_name)
        return redirect('/projects')

@app.route('/projects', methods=['GET'])
def approved_projects():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/projects'
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        result = []
        if len(get_projects_for_current_user()) > 0:
            if session['role'] not in ['Super Admin', 'COO', 'QS Head','Site Engineer', 'Purchase Head','Planning',
                                       'Sales Executive', 'Billing'] and 'All' not in str(get_projects_for_current_user()):
                approved_projects_query = 'SELECT project_id, project_name, project_number, blocked, client_phone from projects WHERE is_approved=1 AND archived=0 ' \
                                          'AND project_id IN ' + str(get_projects_for_current_user()) + ' ORDER BY project_number'
                cur.execute(approved_projects_query)
                result = cur.fetchall()
            else:
                approved_projects_query = 'SELECT project_id, project_name, project_number, blocked, client_phone from projects WHERE is_approved=1 AND archived=0 ORDER BY project_number'
                cur.execute(approved_projects_query)
                result = cur.fetchall()
        return render_template('approved_projects.html', projects=result)


@app.route('/archived_projects', methods=['GET'])
def archived_projects():
    if 'email' not in session:
        flash('You need to login to continue', 'danger')
        session['last_route'] = '/projects'
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        result = []
        if len(get_projects_for_current_user()) > 0:
            if session['role'] not in ['Super Admin', 'COO', 'QS Head', 'Site Engineer', 'Purchase Head', 'Billing'] and 'All' not in str(get_projects_for_current_user()):
                archived_projects_query = 'SELECT project_id, project_name, project_number from projects WHERE project_number!=0 AND project_number is not NULL AND archived=1 ' \
                                          'AND project_id IN ' + str(get_projects_for_current_user()) + ' ORDER BY project_number'
                cur.execute(archived_projects_query)
                result = cur.fetchall()
            else:
                archived_projects_query = 'SELECT project_id, project_name, project_number from projects WHERE project_number!=0 AND project_number is not NULL AND archived=1 ORDER BY project_number'
                cur.execute(archived_projects_query)
                result = cur.fetchall()
        return render_template('archived_projects.html', projects=result)


@app.route('/view_project_details', methods=['GET'])
def view_project_details():
    if request.method == 'GET':
        fields = [
            'project_name', 'project_number', 'project_location', 'package_type', 'no_of_floors', 'project_value',
            'date_of_initial_advance', 'date_of_agreement', 'sales_executive', 'site_area',
            'gf_slab_area', 'ff_slab_area', 'sf_slab_area','fof_slab_area','fif_slab_area', 'tf_slab_area', 'tef_slab_area', 'shr_oht',
            'elevation_details', 'additional_cost',
            'paid_percentage', 'comments', 'cost_sheet', 'site_inspection_report', 'is_approved', 'archived', 'created_at','client_name', 'client_phone','agreement','area_statement'
        ]
        fields_as_string = ", ".join(fields)
        get_details_query = 'SELECT ' + fields_as_string + ' from projects WHERE project_id=' + str(
            request.args['project_id'])
        cur = mysql.connection.cursor()
        cur.execute(get_details_query)
        result = cur.fetchone()
        details = {}

        if len(str(result[8])) > 0:
            sales_executive_query = 'SELECT name from App_users WHERE user_id=' + str(result[8])
            cur.execute(sales_executive_query)
            sales_executive_query_result = cur.fetchone()
        for i in range(len(fields)):
            fields_name_to_show = " ".join(fields[i].split('_')).title()
            if fields_name_to_show == 'Sales Executive' and len(
                    str(result[8])) > 0 and sales_executive_query_result is not None:
                details[fields_name_to_show] = sales_executive_query_result[0]
            else:
                details[fields_name_to_show] = result[i]
        return render_template('view_project_details.html', details=details, approved=str(result[-7]),
                               archived=str(result[-6]))


@app.route('/approve_project', methods=['GET'])
def approve_project():
    project_id = request.args['project_id']
    approve_project_query = 'UPDATE projects set is_approved="1" WHERE project_id=' + str(project_id)
    cur = mysql.connection.cursor()
    cur.execute(approve_project_query)
    mysql.connection.commit()
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' approved project ' + request.args['project_name'])
    flash('Project has been approved', 'success')
    return redirect('/view_project_details?project_id=' + str(project_id))


@app.route('/projects_with_no_design_team', methods=['GET'])
def projects_with_no_design_team():
    no_design_team_query = 'SELECT P.project_id, P.project_name from projects P left join project_design_team PDT ' \
                           'on P.project_id = PDT.project_id WHERE P.is_approved=1 AND P.archived=0 AND PDT.project_id is NULL'
    cur = mysql.connection.cursor()
    cur.execute(no_design_team_query)
    result = cur.fetchall()
    return render_template('projects_with_no_design_team.html', projects=result)


@app.route('/projects_with_design_team', methods=['GET'])
def projects_with_design_team():
    design_team_query = 'SELECT P.project_id, P.project_name from projects P left join project_design_team PDT ' \
                        'on P.project_id = PDT.project_id WHERE P.is_approved=1 AND P.archived=0 AND PDT.project_id is NOT NULL'
    cur = mysql.connection.cursor()
    cur.execute(design_team_query)
    result = cur.fetchall()
    return render_template('projects_with_design_team.html', projects=result)


@app.route('/projects_with_no_operations_team', methods=['GET'])
def projects_with_no_operations_team():
    no_ops_team_query = 'SELECT P.project_id, P.project_name from projects P left join project_operations_team POT ' \
                        'on P.project_id = POT.project_id WHERE P.is_approved=1 AND P.archived=0 AND POT.project_id is NULL'
    cur = mysql.connection.cursor()
    cur.execute(no_ops_team_query)
    result = cur.fetchall()
    return render_template('projects_with_no_operations_team.html', projects=result)


@app.route('/projects_with_operations_team', methods=['GET'])
def projects_with_operations_team():
    ops_team_query = 'SELECT P.project_id, P.project_name from projects P left join project_operations_team POT ' \
                     'on P.project_id = POT.project_id WHERE P.is_approved=1 AND P.archived=0 AND POT.project_id is NOT NULL'
    cur = mysql.connection.cursor()
    cur.execute(ops_team_query)
    result = cur.fetchall()
    return render_template('projects_with_operations_team.html', projects=result)


@app.route('/assign_team', methods=['GET', 'POST'])
def assign_team():
    if request.method == 'GET':
        design_team_query = 'SELECT user_id, name, role from App_users WHERE role="Architect" OR role="Senior Architect" OR role="Structural Designer" OR role="Electrical Designer" OR role="PHE Designer"'
        cur = mysql.connection.cursor()
        cur.execute(design_team_query)
        architects = []
        structural_designers = []
        electrical_designers = []
        phe_designers = []
        senior_architects = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Architect':
                architects.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Structural Designer':
                structural_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Electrical Designer':
                electrical_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'PHE Designer':
                phe_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Senior Architect':
                senior_architects.append({'id': i[0], 'name': i[1]})

        operations_team_query = 'SELECT user_id, name, role from App_users WHERE role="Project Coordinator" OR role="Project Manager" OR role="Purchase Executive" OR role="QS Engineer"'
        cur = mysql.connection.cursor()
        cur.execute(operations_team_query)
        co_ordinators = []
        project_managers = []
        purchase_executives = []
        qs_engineers = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Project Coordinator':
                co_ordinators.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Project Manager':
                project_managers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Purchase Executive':
                purchase_executives.append({'id': i[0], 'name': i[1]})
            if i[2] == 'QS Engineer':
                qs_engineers.append({'id': i[0], 'name': i[1]})

        return render_template('assign_team.html', co_ordinators=co_ordinators,
                                       project_managers=project_managers, purchase_executives=purchase_executives,
                                       qs_engineers=qs_engineers,  senior_architects=senior_architects, architects=architects,
                                       structural_designers=structural_designers, electrical_designers=electrical_designers,
                                       phe_designers=phe_designers)
    else:

        column_names = list(request.form.keys())
        values = list(request.form.values())

        design_team_columns = column_names[:5] + [column_names[-1]]
        design_team_values = values[:5] + [values[-1]]

        cur = mysql.connection.cursor()
        assign_design_team_query = 'INSERT into project_design_team' + str(tuple(design_team_columns)).replace("'","") + 'values ' + str(tuple(design_team_values))
        cur.execute(assign_design_team_query)

        operations_team_columns = column_names[5:]
        operations_team_values = values[5:]

        assign_operations_team_query = 'INSERT into project_operations_team' + str(tuple(operations_team_columns)).replace("'","") + 'values ' + str(tuple(operations_team_values))
        cur.execute(assign_operations_team_query)        

        mysql.connection.commit()
        flash('Team updated successfully', 'success')
        return redirect('/assign_team?project_id='+column_names[-1])

@app.route('/edit_team', methods=['GET', 'POST'])
def edit_team():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            flash('Missing fields', 'danger')
            return redirect('/projects_with_no_design_team')
        project_id = request.args['project_id']
        design_team_query = 'SELECT user_id, name, role from App_users WHERE role="Architect" OR role="Senior Architect" OR role="Structural Designer" OR role="Electrical Designer" OR role="PHE Designer"'
        cur = mysql.connection.cursor()
        cur.execute(design_team_query)
        architects = []
        structural_designers = []
        electrical_designers = []
        phe_designers = []
        senior_architects = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Architect':
                architects.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Structural Designer':
                structural_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Electrical Designer':
                electrical_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'PHE Designer':
                phe_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Senior Architect':
                senior_architects.append({'id': i[0], 'name': i[1]})

        existing_team = {
            'Architect': 'None',
            'Structural Designer': 'None',
            'Electrical Designer': 'None',
            'PHE Designer': 'None',
            'Senior Architect': 'None',
            'Project Coordinator': 'None',
            'Project Manager': 'None',
            'Purchase Executive': 'None',
            'QS Engineer': 'None'
        }


        existing_team_query = 'SELECT * FROM project_design_team WHERE project_id=' + str(project_id)
        cur.execute(existing_team_query)
        res = cur.fetchone()
        if res is not None:
            existing_team['Architect'] = res[2]
            existing_team['Structural Designer'] = res[3]
            existing_team['Electrical Designer'] = res[4]
            existing_team['PHE Designer'] = res[5]
            existing_team['Senior Architect'] = res[6]


        operations_team_query = 'SELECT user_id, name, role from App_users WHERE role="Project Coordinator" OR role="Project Manager" OR role="Purchase Executive" OR role="QS Engineer"'
        cur = mysql.connection.cursor()
        cur.execute(operations_team_query)
        co_ordinators = []
        project_managers = []
        purchase_executives = []
        qs_engineers = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Project Coordinator':
                co_ordinators.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Project Manager':
                project_managers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Purchase Executive':
                purchase_executives.append({'id': i[0], 'name': i[1]})
            if i[2] == 'QS Engineer':
                qs_engineers.append({'id': i[0], 'name': i[1]})
        existing_team_query = 'SELECT * FROM project_operations_team WHERE project_id=' + str(project_id)
        cur.execute(existing_team_query)
        res = cur.fetchone()
        if res is not None:
            existing_team['Project Coordinator'] = res[2]
            existing_team['Project Manager'] = res[3]
            existing_team['Purchase Executive'] = res[4]
            existing_team['QS Engineer'] = res[5]


        return render_template('edit_team.html', existing_team=existing_team,
                               senior_architects=senior_architects, architects=architects,
                               structural_designers=structural_designers, electrical_designers=electrical_designers,
                               phe_designers=phe_designers, co_ordinators=co_ordinators,
                               project_managers=project_managers, purchase_executives=purchase_executives,
                               qs_engineers=qs_engineers)

    else:
        cur = mysql.connection.cursor()
        column_names = list(request.form.keys())
        values = list(request.form.values())


        check_if_design_team_exists_query = 'SELECT id from project_design_team WHERE project_id='+str(request.form['project_id'])
        cur.execute(check_if_design_team_exists_query)
        result = cur.fetchone()
        if result is not None:

            update_string = ""
            for i in column_names[:5]:
                update_string += i + '="' + request.form[i] + '", '
            # Remove the last comma
            update_string = update_string[:-2]
            update_project_query = 'UPDATE project_design_team SET ' + update_string + ' WHERE project_id=' + str(
                request.form['project_id'])
            cur.execute(update_project_query)
        
        else :

            design_team_columns = column_names[:5] + [column_names[-1]]
            design_team_values = values[:5] + [values[-1]]

            cur = mysql.connection.cursor()
            assign_design_team_query = 'INSERT into project_design_team' + str(tuple(design_team_columns)).replace("'","") + 'values ' + str(tuple(design_team_values))
            cur.execute(assign_design_team_query)



        check_if_operations_team_exists_query = 'SELECT id from project_operations_team WHERE project_id='+str(request.form['project_id'])
        cur.execute(check_if_operations_team_exists_query)
        result = cur.fetchone()
        if result is not None:

            update_string = ""
            for i in column_names[5:-1]:
                update_string += i + '="' + request.form[i] + '", '
            # Remove the last comma
            update_string = update_string[:-2]
            update_project_query = 'UPDATE project_operations_team SET ' + update_string + ' WHERE project_id=' + str(
                request.form['project_id'])
            cur.execute(update_project_query)
        else : 

            operations_team_columns = column_names[5:]
            operations_team_values = values[5:]

            assign_operations_team_query = 'INSERT into project_operations_team' + str(tuple(operations_team_columns)).replace("'","") + 'values ' + str(tuple(operations_team_values))
            cur.execute(assign_operations_team_query)

        project_id = request.form['project_id']
        
        for i in values[:-1]:
            if str(i).strip() != '':
                access_to_projects = ''
                access_query = 'SELECT access from App_users WHERE user_id='+str(i)
                cur.execute(access_query)
                res = cur.fetchone()
                if res is not None and res[0] is not None:
                    access_to_projects = res[0]
                if str(project_id) not in access_to_projects:
                    access_to_projects = access_to_projects + ',' + str(project_id)
                access_update_query = 'UPDATE App_users SET access="'+access_to_projects+'" WHERE user_id='+str(i)     
                cur.execute(access_update_query)

                
        mysql.connection.commit()
        project_name = getProjectName(project_id)
        make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' updated team for project ' + project_name)
        flash('Team updated successfully', 'success')
        return redirect('/projects')

@app.route('/assign_design_team', methods=['GET', 'POST'])
def assign_design_team():
    if request.method == 'GET':
        design_team_query = 'SELECT user_id, name, role from App_users WHERE role="Architect" OR role="Senior Architect" OR role="Structural Designer" OR role="Electrical Designer" OR role="PHE Designer"'
        cur = mysql.connection.cursor()
        cur.execute(design_team_query)
        architects = []
        structural_designers = []
        electrical_designers = []
        phe_designers = []
        senior_architects = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Architect':
                architects.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Structural Designer':
                structural_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Electrical Designer':
                electrical_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'PHE Designer':
                phe_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Senior Architect':
                senior_architects.append({'id': i[0], 'name': i[1]})
        return render_template('assign_design_team.html', senior_architects=senior_architects, architects=architects,
                               structural_designers=structural_designers, electrical_designers=electrical_designers,
                               phe_designers=phe_designers)
    else:
        column_names = list(request.form.keys())
        values = list(request.form.values())

        cur = mysql.connection.cursor()
        assign_design_team_query = 'INSERT into project_design_team' + str(tuple(column_names)).replace("'",
                                                                                                        "") + 'values ' + str(
            tuple(values))
        cur.execute(assign_design_team_query)
        mysql.connection.commit()
        flash('Design team has been assigned successfully', 'success')
        return redirect('/projects_with_design_team')


@app.route('/edit_design_team', methods=['GET', 'POST'])
def edit_design_team():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            flash('Missing fields', 'danger')
            return redirect('/projects_with_no_design_team')
        project_id = request.args['project_id']
        design_team_query = 'SELECT user_id, name, role from App_users WHERE role="Architect" OR role="Senior Architect" OR role="Structural Designer" OR role="Electrical Designer" OR role="PHE Designer"'
        cur = mysql.connection.cursor()
        cur.execute(design_team_query)
        architects = []
        structural_designers = []
        electrical_designers = []
        phe_designers = []
        senior_architects = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Architect':
                architects.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Structural Designer':
                structural_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Electrical Designer':
                electrical_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'PHE Designer':
                phe_designers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Senior Architect':
                senior_architects.append({'id': i[0], 'name': i[1]})
        existing_team_query = 'SELECT * FROM project_design_team WHERE project_id=' + str(project_id)
        cur.execute(existing_team_query)
        res = cur.fetchone()
        existing_team = {
            'Architect': res[2],
            'Structural Designer': res[3],
            'Electrical Designer': res[4],
            'PHE Designer': res[5],
            'Senior Architect': res[6]
        }

        return render_template('edit_design_team.html', existing_team=existing_team,
                               senior_architects=senior_architects, architects=architects,
                               structural_designers=structural_designers, electrical_designers=electrical_designers,
                               phe_designers=phe_designers)
    else:

        cur = mysql.connection.cursor()
        column_names = list(request.form.keys())

        update_string = ""
        for i in column_names[:-1]:
            if request.form[i].strip() != '':
                update_string += i + '="' + request.form[i] + '", '
        # Remove the last comma
        update_string = update_string[:-2]
        update_project_query = 'UPDATE project_design_team SET ' + update_string + ' WHERE project_id=' + str(
            request.form['project_id'])

        cur.execute(update_project_query)
        mysql.connection.commit()
        flash('Design team has been updated successfully', 'success')
        return redirect('/projects_with_design_team')


@app.route('/assign_operations_team', methods=['GET', 'POST'])
def assign_operations_team():
    if request.method == 'GET':

        operations_team_query = 'SELECT user_id, name, role from App_users WHERE role="Project Coordinator" OR role="Project Manager" OR role="Purchase Executive" OR role="QS Engineer"'
        cur = mysql.connection.cursor()
        cur.execute(operations_team_query)
        co_ordinators = []
        project_managers = []
        purchase_executives = []
        qs_engineers = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Project Coordinator':
                co_ordinators.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Project Manager':
                project_managers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Purchase Executive':
                purchase_executives.append({'id': i[0], 'name': i[1]})
            if i[2] == 'QS Engineer':
                qs_engineers.append({'id': i[0], 'name': i[1]})

        return render_template('assign_operations_team.html', co_ordinators=co_ordinators,
                               project_managers=project_managers, purchase_executives=purchase_executives,
                               qs_engineers=qs_engineers)
    else:
        column_names = list(request.form.keys())
        values = list(request.form.values())

        cur = mysql.connection.cursor()
        assign_operations_team_query = 'INSERT into project_operations_team' + str(tuple(column_names)).replace("'",
                                                                                                                "") + 'values ' + str(
            tuple(values))
        cur.execute(assign_operations_team_query)
        mysql.connection.commit()
        flash('Operations team has been assigned successfully', 'success')
        return redirect('/projects_with_operations_team')


@app.route('/edit_operations_team', methods=['GET', 'POST'])
def edit_operations_team():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            flash('Missing fields', 'danger')
            return redirect('/projects_with_no_operations_team')
        project_id = request.args['project_id']
        operations_team_query = 'SELECT user_id, name, role from App_users WHERE role="Project Coordinator" OR role="Project Manager" OR role="Purchase Executive" OR role="QS Engineer"'
        cur = mysql.connection.cursor()
        cur.execute(operations_team_query)
        co_ordinators = []
        project_managers = []
        purchase_executives = []
        qs_engineers = []
        result = cur.fetchall()
        for i in result:
            if i[2] == 'Project Coordinator':
                co_ordinators.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Project Manager':
                project_managers.append({'id': i[0], 'name': i[1]})
            if i[2] == 'Purchase Executive':
                purchase_executives.append({'id': i[0], 'name': i[1]})
            if i[2] == 'QS Engineer':
                qs_engineers.append({'id': i[0], 'name': i[1]})
        existing_team_query = 'SELECT * FROM project_operations_team WHERE project_id=' + str(project_id)
        cur.execute(existing_team_query)
        res = cur.fetchone()
        existing_team = {
            'Project Coordinator': res[2],
            'Project Manager': res[3],
            'Purchase Executive': res[4],
            'QS Engineer': res[5],
        }
        return render_template('edit_operations_team.html', existing_team=existing_team, co_ordinators=co_ordinators,
                               project_managers=project_managers, purchase_executives=purchase_executives,
                               qs_engineers=qs_engineers)
    else:
        cur = mysql.connection.cursor()
        column_names = list(request.form.keys())

        update_string = ""
        for i in column_names[:-1]:
            if request.form[i].strip() != '':
                update_string += i + '="' + request.form[i] + '", '
        # Remove the last comma
        update_string = update_string[:-2]
        update_project_query = 'UPDATE project_operations_team SET ' + update_string + ' WHERE project_id=' + str(
            request.form['project_id'])

        cur.execute(update_project_query)
        mysql.connection.commit()
        flash('Opeartions team has been updated successfully', 'success')
        return redirect('/projects_with_operations_team')


@app.route('/revised_drawings', methods=['GET', "POST"])
def revised_drawings():
    if request.method == 'GET':
        projects = get_projects()
        drawings = []
        if 'project_id' in request.args:
            cur = mysql.connection.cursor()
            reviewed_drawings_query = 'SELECT id, type, name, file, revision from revised_drawings WHERE project_id=' + str(
                request.args['project_id'])
            cur.execute(reviewed_drawings_query)
            drawings = cur.fetchall()

        return render_template('revised_drawings.html', drawings=drawings, projects=projects)

@app.route('/view_drawings_requests', methods=['GET', "POST"])
def view_drawings_requests():
    if request.method == 'GET':
        projects = get_projects()
        cur = mysql.connection.cursor()

        
        if 'All' not in str(get_projects_for_current_user()):
            get_requests = 'SELECT p.project_name, p.project_number, r.category, r.drawing, u.name, r.timestamp, r.purpose, r.id, r.project_id FROM ' \
                            'drawing_requests r LEFT OUTER JOIN projects p on p.project_id=r.project_id ' \
                            ' LEFT OUTER JOIN App_users u on u.user_id=r.created_by_user' \
                            ' WHERE r.status!="closed" AND p.project_id IN ' + str(get_projects_for_current_user())
            cur.execute(get_requests) 
                       
        else: 
            get_requests = 'SELECT p.project_name, p.project_number, r.category, r.drawing, u.name, r.timestamp, r.purpose, r.id, r.project_id FROM ' \
                            'drawing_requests r LEFT OUTER JOIN projects p on p.project_id=r.project_id ' \
                            ' LEFT OUTER JOIN App_users u on u.user_id=r.created_by_user WHERE r.status!="closed"' 
            cur.execute(get_requests) 
        res = cur.fetchall()
            
        return render_template('drawing_requests.html', requests=res)


@app.route('/delete_drawing_request', methods=['GET','POST'])
def delete_drawing_request():
    request_id = request.args['id']
    cur = mysql.connection.cursor()
    query = 'DELETE from drawing_requests WHERE id='+str(request_id)
    cur.execute(query)
    make_entry_in_audit_log(session['name'] + ' with email '+ session['email'] + ' deleted drawing request with id ' + str(request_id))
    mysql.connection.commit()
    flash("Drawing request has been deleted",'danger')
    return redirect('/view_drawings_requests')

@app.route('/upload_revised_drawing', methods=['GET', "POST"])
def upload_revised_drawing():
    if request.method == 'GET':
        projects = get_projects()
        drawing_types = ['Architect', 'Structural', 'Electrical', 'Plumbing']

        return render_template('upload_revised_drawing.html', projects=projects, drawing_types=drawing_types)
    else:
        cur = mysql.connection.cursor()
        project_id = request.form['project_id']
        type = request.form['drawing_type']
        name = request.form['drawing_name']
        new_drawing_query = 'INSERT into revised_drawings (name, type, project_id) values (%s, %s, %s)'
        cur.execute(new_drawing_query, (name, type, str(project_id)))
        drawing_id = cur.lastrowid
        if 'drawing' in request.files:
            file = request.files['drawing']
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                drawing_filename = 'rd_' + str(drawing_id) + '.pdf'
                output = send_to_s3(file, app.config["S3_BUCKET"], drawing_filename)
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
            mysql.connection.commit()
            flash('Revised drawing uploaded successfully', 'success')
            return redirect('/revised_drawings')


@app.route('/view_drawings', methods=['GET'])
def  view_drawings():            
    return ''


@app.route('/drawings', methods=['GET'])
def drawings():
    table_name = ''
    if 'category' in request.args:
        table_name = request.args['category']
    else:
        table_name = get_drwaings_table_name()
    session['category'] = table_name
    drawings_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + table_name + "'"
    cur = mysql.connection.cursor()
    cur.execute(drawings_query)
    result = cur.fetchall()

    query_string = 'p.project_id, p.project_name, p.project_number, '

    drawing_names = []
    for i in result[2:]:
        query_string += 'd.' + i[0] + ', '
        drawing_names.append(i[0].replace('_', ' ').capitalize())

    query_string = query_string[:-2]
    drawings = []
    if len(get_projects_for_current_user()) > 0:
        if session['role'] not in ['Super Admin', 'Purchase Head', 'COO', 'QS Head','QS Engineer', 'Purchase Head', 'Site Engineer',
                                   'Design Head']:
            drawings_info = "SELECT " + query_string + " FROM projects p LEFT OUTER JOIN " + table_name + " d on " \
                            "p.project_id=d.project_id AND p.is_approved=1 AND p.archived=0 " \
                            ' WHERE p.project_id IN ' + str(get_projects_for_current_user()) +' ORDER BY p.project_number'

            cur.execute(drawings_info)
            drawings = cur.fetchall()

        else:
            drawings_info = "SELECT " + query_string + " FROM projects p LEFT OUTER JOIN " + table_name + " d on " \
                            "p.project_id=d.project_id WHERE p.is_approved=1 AND p.archived=0 ORDER BY p.project_number"
            cur.execute(drawings_info)
            drawings = cur.fetchall()

    return render_template('drawings.html', role=session['role'], drawing_names=drawing_names, drawings=drawings)


def get_drwaings_table_name():
    role = session['role']
    if role in ['Super Admin', 'COO', 'Senior Architect', 'Architect', 'Design Head']:
        return 'architect_drawings'
    elif role == 'Structural Designer':
        return 'structural_drawings'
    elif role == 'Electrical Designer':
        return 'electrical_drawings'
    elif role == 'PHE Designer':
        return 'plumbing_drawings'


@app.route('/upload_drawing', methods=['POST'])
def upload_drawing():
    project_id = request.form['project_id']
    drawing_name = request.form['drawing_name']
    drawing_name = drawing_name.lower().replace(' ', '_')
    if request.method == 'POST':
        drawing_filenames = []
        drawing_filename = ''
        files = request.files.getlist("drawings[]")
        index = 1
        for file in files:
            if file.filename == '':
                flash('No selected file', 'danger ')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                drawing_filename = 'd_'+str(project_id) + '_' + str(drawing_name) + '_' + str(index) + '_' + str(int(time.time())) + '.pdf'
                output = send_to_s3(file, app.config["S3_BUCKET"], drawing_filename)
                drawing_filenames.append(drawing_filename)
                index = index + 1
                if output != 'success':
                    flash('File upload failed', 'danger')
                    return redirect(request.referrer)
        

        cur = mysql.connection.cursor()
        table_name = ''
        if 'category' in request.form:
            table_name = request.form['category']
        elif 'category' in session:
            table_name = session['category']
        else:
            table_name = get_drwaings_table_name()
        check_if_drawing_exists_query = 'SELECT id, '+ drawing_name +' FROM ' + table_name + ' WHERE project_id=' + str(project_id)
        cur.execute(check_if_drawing_exists_query)
        result = cur.fetchone()
        if result is not None:
            update_drawing_query = 'UPDATE ' + table_name + ' set ' + drawing_name + '="' + '||'.join(drawing_filenames) + '" WHERE id=' + str(
                result[0])
            cur.execute(update_drawing_query)
            drawing_name = drawing_name.replace('_', ' ').capitalize()
            if str(result[1]).strip() != '':
                revision = 1
                revised_drawing_no_query = 'SELECT id from revised_drawings WHERE name="'+drawing_name+'" AND ' \
                                            'type="'+table_name+'" AND project_id='+str(project_id)
                cur.execute(revised_drawing_no_query)
                res = cur.fetchall()
                if res is not None: 
                    revision = len(res) + 1
                revised_drawing_query = 'INSERT into revised_drawings (name, type, project_id, file, revision) values (%s, %s, %s, %s, %s)'
                cur.execute(revised_drawing_query, (drawing_name, table_name, str(project_id), result[1], revision))


            flash(drawing_name + ' Drawing uploaded to project ' + request.form['project_name'], 'success')
        else:
            insert_drawing_query = 'INSERT into ' + table_name + ' (project_id, ' + drawing_name + ') values (%s, %s)'
            cur.execute(insert_drawing_query, (str(project_id), '||'.join(drawing_filenames)))
            drawing_name = drawing_name.replace('_', ' ').capitalize()
            flash(drawing_name + ' Drawing uploaded to project ' + request.form['project_name'], 'success')

        if 'drawing_request_id' in request.form:
            IST = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(IST)
            timestamp = current_time.strftime('%d %m %Y at %H %M')
            query = 'UPDATE drawing_requests SET status="closed" ' \
                    'WHERE id='+str(request.form['drawing_request_id'])
            cur.execute(query)

            mysql.connection.commit()
            return redirect('/view_drawings_requests')

        mysql.connection.commit()            
        return redirect('/drawings')

@app.route('/change_drawing_status', methods=['POST'])
def change_drawing_status():
    project_id = request.form['project_id']
    drawing_name = request.form['drawing_name']
    action = request.form['action']
    drawing_name = drawing_name.lower().replace(' ', '_')
    
    cur = mysql.connection.cursor()
    table_name = ''
    if 'category' in session:
        table_name = session['category']
    else:
        table_name = get_drwaings_table_name()

    cur = mysql.connection.cursor()
    check_if_drawing_exists_query = 'SELECT id FROM ' + table_name + '  WHERE project_id=' + str(project_id)
    cur.execute(check_if_drawing_exists_query)
    result = cur.fetchone()
    if result is not None:
        if action == 'pending':
            update_drawing_query = 'UPDATE ' + table_name + ' set ' + drawing_name + '="" WHERE id=' + str(
                result[0])
            cur.execute(update_drawing_query)
        elif action == 'not_applicable':
            update_drawing_query = 'UPDATE ' + table_name + ' set ' + drawing_name + '="-1" WHERE id=' + str(
                result[0])
            cur.execute(update_drawing_query)
        mysql.connection.commit()
        flash('Drawing marked as in progress!', 'success')
        return redirect('/drawings')
    else:
        insert_drawing_query = 'INSERT into ' + table_name + ' (project_id, ' + drawing_name + ') values (%s, %s)'
        if action == 'pending':
            cur.execute(insert_drawing_query, (str(project_id), ''))
        if action == 'not_applicable':    
            cur.execute(insert_drawing_query, (str(project_id), '-1'))
        mysql.connection.commit()
        flash('Drawing marked as in progress!', 'success')
        return redirect('/drawings')



@app.route('/mark_drawing_in_progress', methods=['POST'])
def mark_drawing_in_progress():
    project_id = request.form['project_id']
    drawing_name = request.form['drawing_name']
    drawing_name = drawing_name.lower().replace(' ', '_')

    cur = mysql.connection.cursor()
    table_name = ''
    if 'category' in session:
        table_name = session['category']
    else:
        table_name = get_drwaings_table_name()

    cur = mysql.connection.cursor()
    check_if_drawing_exists_query = 'SELECT id FROM ' + table_name + '  WHERE project_id=' + str(project_id)
    cur.execute(check_if_drawing_exists_query)
    result = cur.fetchone()
    if result is not None:
        update_drawing_query = 'UPDATE ' + table_name + ' set ' + drawing_name + '="0" WHERE id=' + str(
            result[0])
        cur.execute(update_drawing_query)
        mysql.connection.commit()
        flash('Drawing marked as in progress!', 'success')
        return redirect('/drawings')
    else:
        insert_drawing_query = 'INSERT into ' + table_name + ' (project_id, ' + drawing_name + ') values (%s, %s)'
        cur.execute(insert_drawing_query, (str(project_id), '0'))
        mysql.connection.commit()
        flash('Drawing marked as in progress!', 'success')
        return redirect('/drawings')


@app.route('/logout', methods=['GET'])
def logout():
    del session['email']
    del session['name']
    del session['role']
    return redirect('/login')


# APIs for mobile app
@app.route('/API/login', methods=['POST'])
def API_login():
    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()
    login_check_query = 'SELECT user_id, role, phone, password FROM App_users WHERE name="'+str(username)+'" or email="'+str(username)+'" LIMIT 1'
    cur.execute(login_check_query)
    login_result = cur.fetchone()
    API_response = {}
    if login_result is None:
        API_response['message'] = 'Login failed. Incorrect username'
        return jsonify(API_response)
    else:
        API_response['user_id'] = login_result[0]
        API_response['role'] = login_result[1]
        API_response['phone'] = login_result[2]

        # If password matches the phone number or the password set on ERP
        if password == API_response['phone'] or hashlib.sha256(password.encode()).hexdigest() == login_result[3]:
            API_response['message'] = 'success'

            API_response['api_token'] = str(uuid.uuid4())
            update_api_token_query = 'UPDATE App_users SET api_token="'+API_response['api_token']+'" WHERE user_id="'+str(API_response['user_id'])+'"'
            cur.execute(update_api_token_query)
            mysql.connection.commit()
            
            if API_response['role'] == 'Client':
                get_project_for_client_query = 'SELECT project_id, project_name, project_value, completed_percentage, project_location ' \
                                            'FROM projects WHERE client_phone="'+str(API_response['phone'])+'" LIMIT 1'
                cur.execute(get_project_for_client_query)
                project_response = cur.fetchone()
                if project_response is not None:
                    API_response['project_id'] = str(project_response[0])
                    API_response['project_name'] = project_response[1]
                    API_response['project_value'] = project_response[2]
                    API_response['completed_percentage'] = project_response[3]
                    API_response['project_location'] = project_response[4]
                    API_response['location'] = project_response[4]
                else: 
                    API_response['message'] = 'Mismatch is phone number. Please contact your coordinator to update your phone number'
        else:
            API_response['message'] = 'Login failed. Incorrect password'   
    return jsonify(API_response)     

@app.route('/API/get_projects_for_user', methods=['POST'])
def API_get_projects_for_user():
    user_id = request.form['user_id']
    role = request.form['role']
    api_token = request.form['api_token']

    cur = mysql.connection.cursor()

    verify_token_query = 'SELECT user_id from App_users WHERE user_id='+user_id+' AND api_token="'+api_token+'" LIMIT 1'
    cur.execute(verify_token_query)
    verify_token_res = cur.fetchone()
    if verify_token_res is None:
        return jsonify([])


    if role in ['Admin', 'Super Admin', 'COO', 'QS Head', 'Purchase Head', 'Design Head', 'Billing', 'Planning', 'QS Info']:
        query = 'SELECT project_id, project_name, client_name, client_phone FROM projects WHERE archived=0 AND is_approved=1 ORDER BY project_number'
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'Site Engineer':
        projects_user_has_access_to_query = 'SELECT access FROM App_users WHERE user_id='+user_id+' LIMIT 1'
        cur.execute(projects_user_has_access_to_query)
        project_user_has_access_to_res = cur.fetchone()
        if project_user_has_access_to_res is not None:
            project_access_string = project_user_has_access_to_res[0]
            if project_access_string[0] == ',':
                project_access_string = project_access_string[1:]
            if project_access_string[-1] == ',':
                project_access_string = project_access_string[:-1]
            if len(project_access_string.split(',')) == 1:
                project_access_string = project_access_string + ',0'
                
            project_user_has_access_to = str(tuple(project_access_string.split(','))).replace("'",'').replace('"','')   

            query = 'SELECT project_id, project_name, client_name, client_phone FROM projects WHERE project_id IN ' + project_user_has_access_to + ' AND archived=0 AND is_approved=1 ORDER BY project_number'
            cur.execute(query)
            query_result = cur.fetchall()
            API_response = []
            for i in query_result:
                project = {}
                project['id'] = i[0]
                project['name'] = i[1]
                project['client'] = i[2]
                project['client_phone'] = i[3]
                API_response.append(project)
            return jsonify(API_response) 

    elif role == 'Project Coordinator':
        query = 'SELECT pot.project_id, p.project_name, p.client_name, p.client_phone from project_operations_team pot INNER JOIN projects p on p.project_id=pot.project_id WHERE p.archived=0 AND p.is_approved=1 AND co_ordinator=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 
        
    elif role == 'Project Manager':
        query = 'SELECT pot.project_id, p.project_name, p.client_name, p.client_phone from project_operations_team pot INNER JOIN projects p on p.project_id=pot.project_id WHERE p.archived=0 AND p.is_approved=1 AND project_manager=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'Purchase Executive':
        query = 'SELECT pot.project_id, p.project_name, p.client_name, p.client_phone from project_operations_team pot INNER JOIN projects p on p.project_id=pot.project_id WHERE p.archived=0 AND p.is_approved=1 AND purchase_executive=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'QS Engineer':
        query = 'SELECT pot.project_id, p.project_name, p.client_name, p.client_phone from project_operations_team pot INNER JOIN projects p on p.project_id=pot.project_id WHERE p.archived=0 AND p.is_approved=1 AND qs_engineer=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 
        
    elif role == 'Architect':
        query = 'SELECT pdt.project_id, p.project_name, p.client_name, p.client_phone from project_design_team pot INNER JOIN projects p on p.project_id=pdt.project_id WHERE p.archived=0 AND p.is_approved=1 AND architect=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'Structural Designer':
        query = 'SELECT pdt.project_id, p.project_name, p.client_name, p.client_phone from project_design_team pot INNER JOIN projects p on p.project_id=pdt.project_id WHERE p.archived=0 AND p.is_approved=1 AND structural_designer=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'Electrical Designer':
        query = 'SELECT pdt.project_id, p.project_name, p.client_name, p.client_phone from project_design_team pot INNER JOIN projects p on p.project_id=pdt.project_id WHERE p.archived=0 AND p.is_approved=1 AND electrical_designer=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'PHE Designer':
        query = 'SELECT pdt.project_id, p.project_name, p.client_name, p.client_phone from project_design_team pot INNER JOIN projects p on p.project_id=pdt.project_id WHERE p.archived=0 AND p.is_approved=1 AND phe_designer=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    elif role == 'Senior Architect':
        query = 'SELECT pdt.project_id, p.project_name, p.client_name, p.client_phone from project_design_team pot INNER JOIN projects p on p.project_id=pdt.project_id WHERE p.archived=0 AND p.is_approved=1 AND senior_architect=' + str(user_id) + " ORDER BY p.project_number"
        cur.execute(query)
        query_result = cur.fetchall()
        API_response = []
        for i in query_result:
            project = {}
            project['id'] = i[0]
            project['name'] = i[1]
            project['client'] = i[2]
            project['client_phone'] = i[3]
            API_response.append(project)
        return jsonify(API_response) 

    else:
        return []
        

@app.route('/API/get_materials', methods=['GET'])
def get_materials():
    if request.method == 'GET':
        return jsonify({'materials': materials})

@app.route('/API/get_project_block_status', methods=['GET'])
def get_project_block_status():
    if request.method == 'GET':
        try:
            if 'project_id' not in request.args:
                return jsonify({'status': 'open'})
            project_id = request.args['project_id']
            cur = mysql.connection.cursor()
            query = 'SELECT blocked, block_reason from projects WHERE project_id='+str(project_id)
            cur.execute(query)
            result = cur.fetchone()
            if result is not None:
                if str(result[0]) == '1':
                    return jsonify({'status': 'blocked', 'reason': result[1]})

            return jsonify({'status': 'open'})
        except:
            f = open('custom_error_log.txt', 'a')
            f.write(str(request.args))
            f.write('SELECT blocked, block_reason from projects WHERE project_id='+str(project_id)+'/n')
            f.close()
            return jsonify({'status': 'open'})

@app.route('/API/nt_nmr', methods=['GET'])
def api_nt_nmr():
    if request.method == 'GET':
        project_id=request.args['project_id']
        bills_query = 'SELECT wo_bills.id, wo_bills.contractor_name, wo_bills.contractor_code, wo_bills.stage, wo_bills.quantity,' \
                        ' wo_bills.rate, wo_bills.approval_2_amount FROM wo_bills WHERE project_id='+str(project_id)+' AND trade="NT/NMR"'
        cur = mysql.connection.cursor()
        cur.execute(bills_query)
        nt_nmr_bills = cur.fetchall()

        return jsonify(nt_nmr_bills)


@app.route('/API/view_bills', methods=['GET'])
def api_view_bills():
    if request.method == 'GET':
        project_id = request.args['project_id']
        contractor_name = request.args['name']
        contractor_code = request.args['code']
        trade = request.args['trade']

        cur = mysql.connection.cursor()
        data = {'name': '', 'code': '', 'pan': '', 'value': '', 'balance': '', 'trade': '', 'contractor_id': ''}

        get_contractor_query = 'SELECT id, name, code, pan from contractors WHERE code="'+contractor_code+'"'
        cur.execute(get_contractor_query)
        res = cur.fetchone()
        if res is not None:
            data['name'] = res[0]
            data['code'] = res[1]
            data['pan'] = res[2]

        get_wo_query = 'SELECT id, value, balance from work_orders WHERE trade=%s AND project_id=%s'
        cur.execute(get_wo_query, (trade, project_id))
        res = cur.fetchone()
        if res is not None:
            data['value'] = res[1]
            data['balance'] = res[2]
            data['trade'] = trade
            data['work_order_id'] = res[0]

        get_bills_query = 'SELECT w.stage, w.percentage, b.amount, b.approval_2_amount, b.trade, b.approved_on' \
                            ' FROM wo_milestones w LEFT OUTER JOIN wo_bills b ON b.stage=w.stage AND b.contractor_code=%s AND b.project_id=%s WHERE w.work_order_id=%s'
        cur.execute(get_bills_query, (contractor_code, project_id, str(data['work_order_id'])))
        bills = cur.fetchall()

        get_project_query = 'SELECT project_name, project_number from projects WHERE project_id=' + str(project_id)
        cur.execute(get_project_query)
        project = cur.fetchone()
        return jsonify(bills)

@app.route('/API/post_comment', methods=['GET','POST'])
def post_comment():
    if request.method == 'POST':
        user_id = request.form['user_id']
        project_id = request.form['project_id']
        note = request.form['note']


        IST = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(IST)
        timestamp = current_time.strftime('%d %m %Y at %H %M')

        cur = mysql.connection.cursor()
        query = 'INSERT into notes_and_comments(note, timestamp, user_id, project_id) values(%s, %s, %s, %s)'
        cur.execute(query, (note, timestamp, user_id, project_id))
        mysql.connection.commit()
        return jsonify({'message':'success', 'note_id': str(cur.lastrowid) })

@app.route('/API/notes_picture_uplpoad', methods=['GET','POST'])
def notes_picture_uplpoad():
    if request.method == 'POST':
        note_id = request.form['note_id']
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger ')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filetype = file.filename.split('.')[-1]
            output = send_to_s3(file, app.config["S3_BUCKET"], 'note_'+str(note_id)+'.'+filetype)
            if output != 'success':
                return jsonify({'message':'failed'})

            cur = mysql.connection.cursor()
            query = 'UPDATE notes_and_comments SET attachment="note_'+str(note_id)+'.'+filetype+'" WHERE id='+str(note_id)
            cur.execute(query)
            mysql.connection.commit()
            return jsonify({'message':'success'})

@app.route('/API/mark_notifications_as_read', methods=['GET','POST'])
def mark_notifications_as_read():
    if request.method == 'GET':
        if 'user_id' not in request.args:
            return 'No user'
        else:
            user_id = request.args['user_id']
            cur = mysql.connection.cursor()
            query = 'UPDATE app_notifications SET unread=0 WHERE user_id='+str(user_id)

            cur.execute(query)
            mysql.connection.commit()
            return 'success'

@app.route('/API/get_POs', methods=['GET','POST'])
def get_POs():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            return 'No project'
        else:
            project_id = request.args['project_id']
            cur = mysql.connection.cursor()
            get_POs ='SELECT id, material, quantity, unit, purchase_order FROM indents' \
                            ' WHERE status="approved_by_ph" AND project_id =' + str(project_id)
            cur.execute(get_POs)
            res = cur.fetchall()
            return jsonify(res)

@app.route('/API/get_work_orders', methods=['GET','POST'])
def get_work_orders():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            return ()
        else:
            project_id = request.args['project_id']
            work_orders = get_work_orders_for_project(project_id)            
            return jsonify(work_orders)

@app.route('/API/get_notes', methods=['GET','POST'])
def get_notes():
    if request.method == 'GET':
        if 'project_id' not in request.args:
            return ()
        else:
            project_id = request.args['project_id']
            cur = mysql.connection.cursor()
            get_notes = 'SELECT n.note, n.timestamp, u.name, n.id , n.attachment FROM ' \
                            'notes_and_comments n LEFT OUTER JOIN projects p on p.project_id=n.project_id ' \
                            ' LEFT OUTER JOIN App_users u on u.user_id=n.user_id' \
                            ' WHERE n.internal=0 AND p.project_id =' + str(project_id)
            cur.execute(get_notes)
            res = cur.fetchall()
            return jsonify(res)

@app.route('/API/dpr_image_upload', methods=['POST'])
def dpr_image_upload():
    if request.method == 'POST':
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'danger ')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            content_type = file.content_type
            in_mem_file = BytesIO(file.read())
            im = Image.open(in_mem_file)
            im.thumbnail((600, 1000))
            in_mem_file = BytesIO()
            im.save(in_mem_file, format=im.format)
            in_mem_file.seek(0)
            
            filename = secure_filename(file.filename)
            output = send_to_s3(in_mem_file, app.config["S3_BUCKET"], 'migrated/'+filename, "public-read", content_type)
            if output != 'success':
                return output
        return 'success'

@app.route('/API/create_indent', methods=['POST'])
def create_indent():
    if request.method == 'POST':
        project_id = request.form['project_id']
        material = request.form['material']
        quantity = request.form['quantity']
        unit = request.form['unit']
        purpose = request.form['purpose']
        timestamp = request.form['timestamp']
        user_id = request.form['user_id']
        status = 'unapproved'
        cur = mysql.connection.cursor()

        material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            project_id) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
        cur.execute(material_quantity_query)
        result = cur.fetchone()

        quantity = str(quantity).split()[0]
        if result is None:
            return jsonify({'message': 'failure','reason': 'Total quantity of material exceeded limit specified under KYP material'})
        if float(result[0]) < (float(quantity)):
            return jsonify({'message': 'failure','reason': 'Total quantity of material exceeded limit specified under KYP material'})


        if 'approvalTaken' in request.form and 'differenceCost' in request.form:
            

            approval_taken = request.form['approvalTaken']
            difference_cost = request.form['differenceCost']
            
            query = 'INSERT into indents(project_id, material, quantity, unit, purpose, status, created_by_user, timestamp, approval_taken, difference_cost) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            values = (project_id, material, quantity, unit, purpose, status, user_id, timestamp, approval_taken, difference_cost)
        else: 
            query = 'INSERT into indents(project_id, material, quantity, unit, purpose, status, created_by_user, timestamp) values (%s, %s, %s, %s, %s, %s, %s, %s)'
            values = (project_id, material, quantity, unit, purpose, status, user_id, timestamp)

        cur.execute(query, values)
        mysql.connection.commit()
        return jsonify({'message': 'success','indent_id': cur.lastrowid})

@app.route('/API/indent_file_uplpoad', methods=['GET','POST'])
def indent_file_uplpoad():
    if request.method == 'POST':
        indent_id = request.form['indent_id']
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger ')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filetype = file.filename.split('.')[-1]
            output = send_to_s3(file, app.config["S3_BUCKET"], 'indent_attachment_'+str(indent_id)+'.'+filetype)
            if output != 'success':
                return jsonify({'message':'failed'})

            cur = mysql.connection.cursor()
            query = 'UPDATE indents SET attachment="indent_attachment_'+str(indent_id)+'.'+filetype+'" WHERE id='+str(indent_id)
            cur.execute(query)
            mysql.connection.commit()
            return jsonify({'message':'success'})

@app.route('/API/create_drawing_request', methods=['POST'])
def create_drawing_request():
    if request.method == 'POST':
        project_id = request.form['project_id']
        category = request.form['category']
        drawing = request.form['drawing']
        purpose = request.form['purpose']
        timestamp = request.form['timestamp']
        user_id = request.form['user_id']

        cur = mysql.connection.cursor()
        query = 'INSERT into drawing_requests(project_id, category, drawing, purpose, created_by_user, timestamp) values (%s, %s, %s, %s, %s, %s)'
        values = (project_id, category, drawing, purpose, user_id, timestamp)
        cur.execute(query, values)
        mysql.connection.commit()
        return jsonify({'message': 'success'})

def save_notification_to_db(title, body, user_id, role, category, timestamp):
    cur = mysql.connection.cursor()
    notification_query = 'INSERT into app_notifications(title, body, user_id, role, category, timestamp) values (%s, %s, %s, %s, %s, %s)'
    values = (title, body, user_id, role, category, timestamp)
    cur.execute(notification_query, values)
    mysql.connection.commit()
    return


def send_app_notification(title, body, user_id, role, category, timestamp):
    save_notification_to_db(title, body, user_id, role, category, timestamp)
    recipient = ''
    if str(user_id).strip() == '':
        recipient = role
    else:
        recipient = user_id
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=AAAAlQ1Lrfw:APA91bHvI2-qFZNCf-oFfeZgM0JUDxxbuykH_ffka9hPUE0xBpiza4uHF0LmItT_SfMZ1Zl5amGUfAXigaR_VcMsEArqpOwHNup4oRTQ24htJ_GWYH0OWZzFrH2lRY24mnQ-uiHgLyln'
    }
    data = {
        "notification": {"title": title, "body": body, 'data': {'category': 'team_notifications'}},
        "to": "/topics/" + recipient,
    }
    requests.post(url, headers=headers, data=json.dumps(data))
    return


@app.route('/API/change_indent_status', methods=['POST'])
def change_indent_status():
    indent_id = request.form['indent_id']
    status = request.form['status']

    cur = mysql.connection.cursor()
    query = 'UPDATE indents SET status="' + status + '", acted_by_user=' + str(
        request.form['acted_by_user']) + ' WHERE id=' + str(indent_id)
    cur.execute(query)
    mysql.connection.commit()

    if status == 'approved':
        send_app_notification(
            'Indent Approved',
            request.form['notification_body'],
            request.form['user_id'],
            request.form['user_id'],
            'Indent Approval',
            request.form['timestamp']
        )
    elif status == 'rejected':
        send_app_notification(
            'Indent Rejected',
            request.form['notification_body'],
            request.form['user_id'],
            request.form['user_id'],
            'Indent Rejection',
            request.form['timestamp']
        )
    return jsonify({'message': 'success'})


@app.route('/API/edit_and_approve_indent', methods=['POST'])
def edit_and_approve_indent():
    indent_id = request.form['indent_id']
    status = 'approved'
    project_id = request.form['project_id']
    material = request.form['material']
    quantity = request.form['quantity']
    user_id = request.form['acted_by_user']
    unit = request.form['unit']
    purpose = request.form['purpose']
    cur = mysql.connection.cursor()

    material_quantity_query = "SELECT total_quantity from kyp_material WHERE project_id=" + str(
            project_id) + " AND material LIKE '%" + str(material).replace('"','').strip() + "%'"
    cur.execute(material_quantity_query)
    result = cur.fetchone()
    if result is None:
        return jsonify({'message': 'failure','reason': 'Total quantity of material exceeded limit specified under KYP material'})
    if float(result[0]) < (float(quantity)):
        return jsonify({'message': 'failure','reason': 'Total quantity of material exceeded limit specified under KYP material'})

    query = 'UPDATE indents SET status=%s, project_id=%s, material=%s, quantity=%s, unit=%s, purpose=%s, acted_by_user=%s WHERE id=%s'
    values = (status, project_id, material, quantity, unit, purpose, user_id, indent_id)
    cur.execute(query, values)
    mysql.connection.commit()
    send_app_notification(
        'Indent Approved',
        request.form['notification_body'],
        request.form['user_id'],
        request.form['user_id'],
        'Indent Approval',
        request.form['timestamp']
    )
    return jsonify({'message': 'success'})

@app.route('/API/get_my_indents', methods=['GET'])
def get_my_indents():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        user_id = request.args['user_id']
        access_query = 'SELECT access, role from App_users WHERE user_id=' + str(user_id)
        cur.execute(access_query)
        res = cur.fetchone()
        access = res[0]
        role = res[1]
        if role == 'Admin':
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.created_by_user, indents.status , indents.difference_cost, indents.approval_taken FROM indents INNER JOIN projects on indents.project_id=projects.project_id ' \
                            ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id AND indents.created_by_user='+str(user_id)+' ORDER by indents.id DESC'
            cur.execute(indents_query)
            res = cur.fetchall()
            data = []
            for i in res:
                indent_entry = {}
                indent_entry['id'] = i[0]
                indent_entry['project_id'] = i[1]
                indent_entry['project_name'] = i[2]
                indent_entry['material'] = i[3]
                indent_entry['quantity'] = i[4]
                indent_entry['unit'] = i[5]
                indent_entry['purpose'] = i[6]
                indent_entry['created_by_user'] = i[7]
                indent_entry['timestamp'] = i[8]
                indent_entry['created_by_user_id'] = i[9]
                indent_entry['status'] = i[10].replace('_',' ').title()
                indent_entry['difference_cost'] = i[11]
                indent_entry['approval_taken'] = i[12]
                data.append(indent_entry)

            return jsonify(data)
        elif len(access) > 0:
            access = access.split(',')
            access_as_int = [int(i) for i in access]
            access_tuple = ''
            if len(access_as_int) == 1:
                access_tuple = '('+str(access_as_int[0])+')'
            else:
                access_tuple = tuple(access_as_int)
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.created_by_user, indents.status , indents.difference_cost, indents.approval_taken FROM indents INNER JOIN projects on indents.project_id=projects.project_id AND indents.project_id IN ' + str(
                access_tuple) + '' \
                                ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id AND indents.created_by_user='+str(user_id)+' ORDER by indents.id DESC'
            cur.execute(indents_query)
            res = cur.fetchall()
            data = []
            for i in res:
                indent_entry = {}
                indent_entry['id'] = i[0]
                indent_entry['project_id'] = i[1]
                indent_entry['project_name'] = i[2]
                indent_entry['material'] = i[3]
                indent_entry['quantity'] = i[4]
                indent_entry['unit'] = i[5]
                indent_entry['purpose'] = i[6]
                indent_entry['created_by_user'] = i[7]
                indent_entry['timestamp'] = i[8]
                indent_entry['created_by_user_id'] = i[9]
                indent_entry['status'] = i[10].replace('_',' ').title()
                indent_entry['difference_cost'] = i[11]
                indent_entry['approval_taken'] = i[12]
                data.append(indent_entry)

            return jsonify(data)
        else:
            return jsonify([])


@app.route('/API/get_unapproved_indents', methods=['GET'])
def get_unapproved_indents():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        user_id = request.args['user_id']
        access_query = 'SELECT access, role from App_users WHERE user_id=' + str(user_id)
        cur.execute(access_query)
        res = cur.fetchone()
        access = res[0]
        role = res[1]
        if role == 'Admin':
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.created_by_user , indents.difference_cost, indents.approval_taken FROM indents INNER JOIN projects on indents.status="unapproved" AND indents.project_id=projects.project_id ' \
                            ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
            cur.execute(indents_query)
            res = cur.fetchall()
            data = []
            for i in res:
                indent_entry = {}
                indent_entry['id'] = i[0]
                indent_entry['project_id'] = i[1]
                indent_entry['project_name'] = i[2]
                indent_entry['material'] = i[3]
                indent_entry['quantity'] = i[4]
                indent_entry['unit'] = i[5]
                indent_entry['purpose'] = i[6]
                indent_entry['created_by_user'] = i[7]
                indent_entry['timestamp'] = i[8]
                indent_entry['created_by_user_id'] = i[9]
                indent_entry['difference_cost'] = i[10]
                indent_entry['approval_taken'] = i[11]
                data.append(indent_entry)

            return jsonify(data)
        elif len(access):
            access = access.split(',')
            access_as_int = [int(i) for i in access]
            access_tuple = ''
            if len(access_as_int) == 1:
                access_tuple = '('+str(access_as_int[0])+')'
            else:
                access_tuple = tuple(access_as_int)
            indents_query = 'SELECT indents.id, projects.project_id, projects.project_name, indents.material, indents.quantity, indents.unit, indents.purpose' \
                            ', App_users.name, indents.timestamp, indents.created_by_user , indents.difference_cost, indents.approval_taken FROM indents INNER JOIN projects on indents.status="unapproved" AND indents.project_id=projects.project_id AND indents.project_id IN ' + str(
                access_tuple) + '' \
                                ' LEFT OUTER JOIN App_users on indents.created_by_user=App_users.user_id'
            cur.execute(indents_query)
            res = cur.fetchall()
            data = []
            for i in res:
                indent_entry = {}
                indent_entry['id'] = i[0]
                indent_entry['project_id'] = i[1]
                indent_entry['project_name'] = i[2]
                indent_entry['material'] = i[3]
                indent_entry['quantity'] = i[4]
                indent_entry['unit'] = i[5]
                indent_entry['purpose'] = i[6]
                indent_entry['created_by_user'] = i[7]
                indent_entry['timestamp'] = i[8]
                indent_entry['created_by_user_id'] = i[9]
                indent_entry['difference_cost'] = i[10]
                indent_entry['approval_taken'] = i[11]
                data.append(indent_entry)

            return jsonify(data)
        else:
            return jsonify([])


@app.route('/API/get_notifications', methods=['GET'])
def get_notifications():
    recipient = request.args['recipient']
    cur = mysql.connection.cursor()
    notifications_query = 'SELECT title, body, timestamp, unread from app_notifications WHERE user_id=' + str(recipient)
    cur.execute(notifications_query)
    data = []
    result = cur.fetchall()
    for i in result:
        data.append({'title': i[0], 'body': i[1], 'timestamp': i[2], 'unread': i[3]})
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
