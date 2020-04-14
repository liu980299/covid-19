# -*- coding: utf-8 -*-

#  Copyright (c) 2020. @ Xiang Liu

from __future__ import unicode_literals
from rest_framework.decorators  import api_view
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from django.contrib.auth import *
from django.shortcuts import render
from django.core.exceptions import ValidationError
from contacts.serializers import *
from content.models import VerficationCode
from contacts.models import *
from django.http import Http404
from rest_framework.permissions import *
from contacts.permissions import *
from django.views.decorators.csrf import csrf_exempt
import datetime
import json

# Create your views here.
def add_profile(request):
	data = json.loads(request.body)["data"]
	user = request.user
	if user.is_authenticated:
		profile = user.info
	else:
		phone = data["phone"]
		try:
			Profile.phone_regex(phone)
		except ValidationError as e:
			return Response({"result":False,"error":e.message})
		if "code" in data:
			session = request.session.session_key
			try:
				verification = VerficationCode.objects.get(session_key=session)
			except VerficationCode.DoesNotExist:
				return HttpResponse(json.dumps({"result": False, "error": "Please input verification code!"}))

			code = data["code"]
			if not code == verification.code:
				return HttpResponse(json.dumps({"result":False,"error":"Please input correct verification code!"}))
			else:
				user, created = User.objects.get_or_create(username=phone)
				if created:
					user.save()
				profile,created = Profile.objects.get_or_create(phone=phone)
				profile.user = user
				profile.save()
				login(request,user)
		else:
			return HttpResponse(json.dumps({"result": False, "error": "Please input verification code!"}))

	profile.data = data
	if profile.status == 0:
		form = Form.objects.get(name="set_profile")
		form.form["description"] = form.description
		risk = profile.getRisk()
		return HttpResponse(json.dumps({"phone":profile.phone,"id":profile.id,"form":form.form, "url":form.url,"risk":risk}))
	else:
		risk = profile.getRisk()
		return HttpResponse(json.dumps({"phone": profile.phone, "id": profile.id, "risk":risk}))


@api_view(["POST"])
def set_profile(request):
	data = request.data
	user = request.user
	phone = data["phone"]
	profile = Profile.objects.get(phone = phone)
	res = check_permission(user, profile)
	if not res:
		return Response(res)
	if profile.user == user:
		if not profile.id == data["id"]:
			return Http404
	profile.updateStatus(data)
	risk = profile.getRisk()
	return Response({"phone": profile.phone, "id": profile.id, "risk":risk})

def check_permission(user, profile):
	if user.is_authenticated:
		if not profile.user == user:
			return {"result": False, "error": "Invaild User"}
	else:
		return {"result": False, "error": "Invaild User"}


@api_view(["POST"])
def check_risk(request):
	data = request.data
	phone = data["phone"]
	profile = Profile.objects.get(phone=phone)
	res = check_permission(request.user, profile)
	if res:
		return Response(res)

	risks = Config.objects.get(name="env_risks").data
	contact_list = data["contact_list"]
	contacts = Profile.objects.filter(id__in = contact_list)
	risk = 0
	for contact in contacts:
		if contact.risk > risk:
			risk = contact.risk
	res = {"risk":risk}
	for item in risks:
		if risk <= item["value"]:
			color = item["color"]
	res["color"] = color
	return Response(res)


@api_view(["POST"])
def update_contacts(request):
	data = request.data
	phone = data["phone"]
	profile = Profile.objects.get(phone=phone)
	res = check_permission(request.user, profile)
	if res:
		return Response(res)

	contacts = data["contacts"]
	contact_list = get_all_contacts(contacts)
	for date in contacts:
		profile.updateContact(date,contacts[date])
	profiles = Profile.objects.filter(id__in = contact_list)
	profile.save()
	for target in profiles:
		target.syncContact(profile)
	return Response({"phone":profile.phone, "id":profile.id,"contacts":profile.contacts,"risk":profile.getRisk()})


def get_all_contacts(contacts):
	res = []
	today = datetime.datetime.now().strftime("%Y-%m-%d")
	if today in contacts:
		date_list = contacts[today].keys()
		res.extend(date_list)
	return res

class FormList(generics.ListCreateAPIView):
	serializer_class = FormSerializer
	permission_classes = [IsAdminUser|ReadOnly]
	queryset = Form.objects.all()

class ProfileList(generics.ListCreateAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	serializer_class = ProfileSerializer
	queryset = Profile.objects.all()

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	def get_object(self):
		id = self.kwargs.get('profile_id', None)
		try:
			return Profile.objects.get(id=id)
		except (TypeError, ValueError, Profile.DoesNotExist):
			raise Http404

	serializer_class = ProfileSerializer
	model = Profile



class RiskList(generics.ListCreateAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	serializer_class = RiskSerializer
	queryset = Risk.objects.all()

class RiskDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	def get_object(self):
		name = self.kwargs.get('risk_name', None)
		try:
			return Risk.objects.get(name=name)
		except (TypeError, ValueError, Risk.DoesNotExist):
			raise Http404

	serializer_class = RiskSerializer
	model = Risk


class ConfigList(generics.ListCreateAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	serializer_class = ConfigSerializer
	queryset = Config.objects.all()

class ConfigDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	def get_object(self):
		name = self.kwargs.get('config_name', None)
		try:
			return Config.objects.get(name=name)
		except (TypeError, ValueError, Risk.DoesNotExist):
			raise Http404

	serializer_class = ConfigSerializer
	model = Config


class FormDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAdminUser | ReadOnly]
	renderer_classes = [JSONRenderer]


	def get_object(self):
		name = self.kwargs.get('form_name', None)
		try:
			return Form.objects.get(name=name)
		except (TypeError, ValueError, Form.DoesNotExist):
			raise Http404

	serializer_class = FormSerializer
	model = Form


class FormUpdate(generics.RetrieveUpdateDestroyAPIView):

	def get_object(self):
		name = self.kwargs.get('form_name', None)
		try:
			return Form.objects.get(name=name)
		except (TypeError, ValueError, Form.DoesNotExist):
			raise Http404

	serializer_class = FormSerializer
	model = Form


