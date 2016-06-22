#/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
import time
import datetime
import shutil
import string
import configparser
import multiprocessing

def varInit(str):
	if str == 'string':
		return '""'
	if str == 'int':
		return '"0"'
	return '""'


def generateJs(data):
	strand = '''
		var %s = {
				add : function () {
						var P = new RBAC('%s',{},'%s');
						$('#submitModal').on("click", function () {
								var arr = {
												%s
								};
								P.post('%s', arr);
						});
						P.add();
				},
				edit: function (id) {
						var P = new RBAC('%s', {'id' : id}, '%s');
						$('#submitModal').on("click", function () {
								var arr = {
									'id' : $('#id').val(),
												%s
								};
								P.post('%s', arr);
						});
						P.edit();
				},
				del: function (id) {
						var P = new RBAC('%s', {'id': id}, 'delete');
						P.delete();
				}
		}
	'''
	return strand % (data["a"].capitalize(),data["addUrl"],data["addTitle"],data["jsAddArr"],data["postAddUrl"],data["editUrl"],data["editTitle"],data["jsAddArr"],data["postEditUrl"],data["delUrl"])

def generateController(module,content):
	strand = '''
		module %s;

		import std.json;
		import std.stdio;
		import std.datetime;
		import std.experimental.logger;

		import core.stdc.time;

		import hunt.application;

		import application.config;
		import application.controllers.base;
		import application.common.helpers;
		import %s;
		import %s;

		class %s : BaseController , IController
		{
				mixin HuntDynamicCallFun;
				void lists(Request req,Response res)
				{
						this.viewContext.data = %s.getData();
						this.display!"%s"(res);
				}
				void add(Request req,Response res)
				{
						this.displayWithNothing!"%s"(res); 
				}
				void postAdd(Request req,Response res)
				{
						%s

						%s

						%s

						auto result = %s.add(data);

						if(result["status"] == "success")
						{
								this.successJson(res);
						}
						else
						{
								this.errorJson(res,result["msg"],40001);
						}
				}
				void edit(Request req,Response res)
				{
						auto id = req.get("id","0");
						this.viewContext.id = id;
						auto info = %s.getDataByID(to!int(id));
						if(info)
						{
							%s
						}
						else
						{
							%s
						}
						this.displayWithNothing!"%s"(res); 
				}
				void postEdit(Request req,Response res)
				{
						auto id = req.post("id","");
						%s

						%s

						%s

						auto result = %s.edit(data,id);
						if(result["status"] == "success")
						{
								this.successJson(res);
						}
						else
						{
								this.errorJson(res,result["msg"],40001);
						}
				}
				void del(Request req,Response res)
				{
						auto id = req.post("id","");

						if(!id.length)
						{
								this.errorJson(res,"params error",40001);
						}
						auto result = %s.del(id);
						if(result["status"] == "success")
						{
								this.successJson(res);
						}
						else
						{
								this.errorJson(res,result["msg"],40001);
						}
				}
		}
	'''
	m = module[0]
	c = module[1]
	a = module[2]
	moduleName = 'application.%s.controller.%s.%s' % (m,c,a) 
	importHelper = 'application.%s.helpers' %a
	importModel = 'application.%s.models' %a
	controllerName = '%sController' % a.capitalize()
	add_html = '%s/%s/add.html' %(c,a)
	list_html = '%s/%s/list.html' %(c,a)
	postAdd_arr = ''
	postAddRequired = ''
	postAddData = ''
	editTrueViewContent = ''
	editFalseViewContent = ''
	for i in content:
		postAdd_arr = postAdd_arr +  'auto %s = req.post("%s","");' %(i[0],i[0])
		if i[2] == 'required':
			postAddRequired = postAddRequired + '!%s.length ||' %i[0]
		postAddData = postAddData + '"%s" : %s,' %(i[0],i[0])
		editTrueViewContent = editTrueViewContent + ' this.viewContext.%s = info["%s"];' %(i[0],i[0])
		editFalseViewContent = editFalseViewContent + ' this.viewContext.%s = "";' %i[0]

	postAddRequired = postAddRequired[:-2]
	postAddData = postAddData[:-1]
	helperName = '%sHelper' %a
	edit_html = '%s/%s/edit.html' %(c,a)

	return strand % (moduleName,importHelper,importModel,controllerName,helperName,list_html,add_html,postAdd_arr)

def generateHelper(module,content):
		strand = '''
		module application.admin.helpers.menu;
import std.conv;
import std.json;
import std.stdio;
import std.array;
import std.random;
import std.string;
import std.digest.md;
import std.experimental.logger;
import application.config;
import application.admin.models;
import application.common.helpers;
struct Menu 
{
		int id;
		string name;
		string icon;
		string router;
}
class menuHelper
{
		public static string[string][] getData()
		{
				auto data = adminMenuModel.getInstance.getData();
				return data;	
		}
		public static string[string] getDataByID(int id)
		{
				return adminMenuModel.getInstance.getDataByID(id);
		}
		public static string[string] add(string[string] data)
		{
				auto result = adminMenuModel.getInstance.insert(data);

				if(result)
				{
						return [
								"status" : "success",
						];	
				}
				else
				{
						return [
								"status" : "error",
								"msg" : "db error"
						];		
				}
		}
		public static string[string] edit(string[string] data,string id)
		{
				auto result = adminMenuModel.getInstance.update(data,["id":id]);

				if(result)
				{
						return [
								"status" : "success",
						];	
				}
				else
				{
						return [
								"status" : "error",
								"msg" : "db error"
						];		
				}
		}
		public static string[string] del(string id)
		{
				auto result = adminMenuModel.getInstance.remove(["id":id]);

				if(result)
				{
						return [
								"status" : "success",
						];	
				}
				else
				{
						return [
								"status" : "error",
								"msg" : "db error"
						];		
				}
		}
}
		'''
		return strand

def generateModel(module,content):
		strand = '''
		module application.admin.models.menu;
		import std.stdio;
		import std.format;
		import std.experimental.logger;
		import core.thread;
		import core.stdc.time;
		import application.model;
		import application.utils;
		import application.admin.models;
		import kerisy.db.sql.factory;
		class adminMenuModel : Model 
		{
		public{
				string tableName = "pt_admin_menu";
				static Model _model;
		}
		static @property getInstance(){
				if(_model is null)
				{
						_model = new adminMenuModel();
				}
				return _model;
		}
		mixin ModelCommon;
		}
		'''
		return strand

def generateHTMLList(module,content):
		strand = '''
		<div class="row wrapper border-bottom white-bg page-heading">
		<div class="col-lg-10">
				<h2>FooTable</h2>
				<ol class="breadcrumb">
						<li>
								<a href="index.html">Home</a>
						</li>
						<li>
								<a>Tables</a>
						</li>
						<li class="active">
								<strong>FooTable</strong>
						</li>
				</ol>
		</div>
		<div class="col-lg-2">
		</div>
		</div>
		<div class="wrapper wrapper-content animated fadeInRight">
				<div class="row">
						<div class="col-lg-12">
								<div class="ibox float-e-margins">
										<div class="ibox-title">
												<h5>菜单列表</h5>
												<div class="ibox-tools">
														<a class="link" href="#" onclick="Menu.add({{var.index}})">
																<i class="fa fa-plus"></i>
														</a>
														<a class="collapse-link">
																<i class="fa fa-chevron-up"></i>
														</a>
														<a class="close-link">
																<i class="fa fa-times"></i>
														</a>
												</div>
										</div>
										<div class="ibox-content">
												<table class="footable table table-stripped toggle-arrow-tiny" data-page-size="8">
														<thead>
																<tr>
																		<th data-toggle="true">ID</th>
																		<th>Name</th>
																		<th>Router</th>
																		<th data-hide="all">icon</th>
																		<th data-hide="all">parent_id</th>
																		<th data-hide="all">created_at</th>
																		<th data-hide="all">updated_at</th>
																		<th>Action</th>
																</tr>
														</thead>
														<tbody>
																{%  foreach(string[string] value; var.data) { %}
																<tr>
																		<td>{{ value["id"]  }}</td>
																		<td>{{ value["name"] }}</td>
																		<td>{{ value["router"] }}</td>
																		<td>{{ value["icon"] }}</td>
																		<td><span class="pie">{{ value["parent_id"]  }}</span></td>
																		{% import std.datetime;import std.conv;   %}
																		<td>{{ SysTime.fromUnixTime(to!long(value["created_at"])).toISOExtString() }}</td>
																		<td>{{ SysTime.fromUnixTime(to!long(value["updated_at"])).toISOExtString() }}</td>
																		<td>
																				<a class="btn btn-info btn-rounded btn-outline" href="#" onclick="Menu.edit({{value["id"]}})">编辑</a>
																				<a class="btn btn-danger btn-rounded btn-outline" href="#" onclick="Menu.del({{ value["id"] }})">删除</a>
																				<a class="btn btn-info btn-rounded btn-outline" href="/admin/menu/lists?index={{value["id"]}}">查看下级</a>
																		</td>
																</tr>
																{%  }  %}
														</tbody>
														<tfoot>
																<tr>
																		<td colspan="5">
																				<ul class="pagination pull-right"></ul>
																		</td>
																</tr>
														</tfoot>
												</table>
										</div>
								</div>
						</div>
				</div>
		</div>
		<div class="modal inmodal" id="myModal" tabindex="-1" role="dialog" aria-hidden="true">
				<div class="modal-dialog">
						<div class="modal-content animated fadeIn">
								<div class="modal-header">
										<button type="button" class="close" data-dismiss="modal">
												<span aria-hidden="true">&times;</span>
												<span class="sr-only">Close</span>
										</button>
										<h4 class="modal-title" id="modalLable">Add</h4>
								</div>
								<div class="modal-body" id="ajaxContent"></div>
								<div class="modal-footer">
										<button type="button" class="btn btn-white" data-dismiss="modal">Close</button>
										<button type="button" class="btn btn-primary" id="submitModal">Save</button>
								</div>
						</div>
				</div>
		</div>
		'''
		return strand

def generateHTMLAdd(module,content):
		strand = '''
		<div class="form-group">
				<label >name</label>
				<input type="text" name="name" id="name" class="form-control" value=""/>
		</div>
		<div class="form-group">
				<label>icon</label>
				<input type="text" name="icon" id="icon" class="form-control" value=""/>
		</div>
		<div class="form-group">
				<label>router</label>
				<input type="text" name="router" id="router" class="form-control" value=""/>
		</div>
		'''
		return strand
def generateHTMLEdit(module,content):
		strand = '''
		<input type="hidden" name="id" id="id" class="form-control" value="{{ var.id }}"/>
		<div class="form-group">
				<label >name</label>
				<input type="text" name="name" id="name" class="form-control" value="{{ var.name }}"/>
		</div>
		<div class="form-group">
				<label>icon</label>
				<input type="text" name="icon" id="icon" class="form-control" value="{{ var.icon }}"/>
		</div>
		<div class="form-group">
				<label>router</label>
				<input type="text" name="router" id="router" class="form-control" value="{{ var.router }}"/>
		</div>
		'''
		return strand
def generateHTMLEdit(module,content):
		strand = '''
		#admin role
		GET    /admin/role/lists admin/admin.role.lists before:application.middleware.UserAuthMiddleWare;after:
		GET    /admin/role/add admin/admin.role.add before:application.middleware.UserAuthMiddleWare;after:
		POST   /admin/role/postAdd admin/admin.role.postAdd before:application.middleware.UserAuthMiddleWare;after:
		GET    /admin/role/edit admin/admin.role.edit before:application.middleware.UserAuthMiddleWare;after:
		POST   /admin/role/postEdit admin/admin.role.postEdit before:application.middleware.UserAuthMiddleWare;after:
		POST   /admin/role/del admin/admin.role.del before:application.middleware.UserAuthMiddleWare;after:
		'''
		return strand

def parseContent(content):
	result = []
	content = content.split()
	for c in content:
		result.append(c.split('_'))
	return result


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("error argv,examples: python migrate.py example.migrate")
		exit()

	filename = sys.argv[1]

	config = configparser.ConfigParser()

	result = config.read(filename)
	if not result:
		print("error migrate file")
		exit()

	sections = config.sections()
	if not sections:
		print("error migrate config")
		exit()
	if not config['db']['tablename']:
		print("error migrate config db table name")
		exit()
	if not config['db']['content']:
		print("error migrate config module")
		exit()
	if not config['module']['module']:
		print("error migrate config module")
		exit()

	tablename = config['db']['tablename']
	content = config['db']['content']
	module = config['module']['module']

	content = parseContent(content)
	module = module.split('_')

	m = module[0]
	c = module[1]
	a = module[2]

	addUrl = "/%s/%s/add" %(c,a)
	editUrl = "/%s/%s/edit" %(c,a)
	delUrl = "/%s/%s/del" %(c,a)
	postAddUrl = "/%s/%s/postAdd" %(c,a)
	postEditUrl = "/%s/%s/postEdit" %(c,a)
	addTemple = "%s/%s/%s/add.html" %(m,c,a)
	editTemple = "%s/%s/%s/edit.html" %(m,c,a)
	listTemple = "%s/%s/%s/list.html" %(m,c,a)
	addTitle = "add %s" %a
	editTitle = "edit %s" %a
	controllerModuleName = 'application.%s.controller.%s.%s' % (m,c,a) 
	helperModuleName = 'application.%s.controller.%s.%s' % (m,c,a) 
	moduleModuleName = 'application.%s.controller.%s.%s' % (m,c,a) 
	jsAddArr = ""
	postAddRequestParams = ''
	postAddRequestParamsCheck = ''
	postAddToHelperData = ''
	editTrueViewContent = ''
	editFalseViewContent = ''
	for i in content:
		jsAddArr = jsAddArr + "'%s': $('#%s').val()," %(i[0],i[0])
		postAddRequestParams = postAddRequestParams +  'auto %s = req.post("%s","");' %(i[0],i[0])
		if i[2] == 'required':
			postAddRequired = postAddRequired + '!%s.length ||' %i[0]
		postAddData = postAddData + '"%s" : %s,' %(i[0],i[0])
		editTrueViewContent = editTrueViewContent + ' this.viewContext.%s = info["%s"];' %(i[0],i[0])
		editFalseViewContent = editFalseViewContent + ' this.viewContext.%s = "";' %i[0]

	postAddRequired = postAddRequired[:-2]
	postAddData = postAddData[:-1]

	data = {
		"m":m,
		"c":c,
		"a":a,
		"addUrl" : addUrl,
		"editUrl" : editUrl,
		"delUrl" : delUrl,
		"postAddUrl" : postAddUrl,
		"postEditUrl" : postEditUrl,
		"addTemple" : addTemple,
		"editTemple" : editTemple,
		"listTemple" : listTemple,
		"addTitle" : addTitle,
		"editTitle" : editTitle,
		"jsAddArr" : jsAddArr,
		"postAddRequestParams" : postAddRequestParams,
		"postAddRequestParamsCheck" : postAddRequestParamsCheck,
		"postAddToHelperData" : postAddToHelperData,
		"editTrueViewContent" : editTrueViewContent,
		"editFalseViewContent" : editFalseViewContent
	}

	print(data)
	print(generateJs(data))
