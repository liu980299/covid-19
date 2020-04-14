# -*- coding: utf-8 -*-

#  Copyright (c) 2020. @ Xiang Liu

from __future__ import unicode_literals

#from jsoneditor.fields.postgres_jsonfield import JSONField
from django.contrib.postgres.fields import *
#from django_postgres_extensions.models.fields import JSONField
from django.contrib.auth.models import *
from django.db import models
from django.db.models import F
from django.core.validators import RegexValidator
import datetime
import json

# Create your models here.

class Profile(models.Model):
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
								 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

	phone = models.CharField(validators=[phone_regex], blank=True,max_length=20, unique=True, db_index=True)
	user = models.OneToOneField(User, related_name="info", null=True)
	contacts = JSONField(default={})
	data = JSONField(default={})
	places = JSONField(default={})
	status = models.SmallIntegerField(default=0)
	need_isolated = models.BooleanField(default=False)
	isolated = models.BooleanField(default=False)
	need_test = models.BooleanField(default=False)
	contacted = models.BooleanField(default=False)
	risk = models.SmallIntegerField(default=0)
	infection = models.FloatField(default=1.0)

	def updateStatus(self, data):
		data = data["data"]
		risks = Config.objects.get(name="risks")
		infections = Config.objects.get(name="infections").data
		propagations = Config.objects.get(name="propagation").data
		risks = risks.data
		p_risk = self.risk
		p_status = self.status
		for key in risks:
			#if not in previous, include risk
			if key not in self.data and key in data:
				self.risk = 100 - (100 - risks[key]) * (100 - self.risk) / 100
				self.status = 2
			#if not in current, exclude rik
			if key in self.data and key not in data:
				self.risk = 100 - (100 - self.risk)*100/(100 - risks[key])
				self.status = 2
		if self.risk > p_risk:
			if str(self.status) in propagations["tracks"]:
				gap = propagations["tracks"][str(self.status)]
				date_list = []
				for i in range(gap):
					date_list.append((datetime.datetime.now()-datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
				contact_lists = {}
				for key in propagations["levels"]:
					contact_lists[key] = []
					for date in date_list:
						if date in self.contacts and key in self.contacts[date]:
							contact_lists[key].extend(self.contacts[date][key])
					infection = propagations["levels"][key]["infection"]
					Profile.objects.filter(id__in=contact_lists[key]).update(risk=100-(100-F("risk"))*(100-self.risk*infection*F("infection"))/(100-p_risk*infection*F("infection")))


		self.setInfections()
		for key in infections:
			if key in self.data and self.data[key]:
				if self.infection > infections[key]:
					self.infection = infections[key]
		for key in propagations["tracks"]:
			infection = "infection" + key
			if infection not in data:
				data[infection] = self.infection

		data["infection_set"] = datetime.datetime.now().strftime("%Y-%m-%d")
		if self.status == 0:
			self.status = 1
		self.save()

	def setInfections(self):
		infections = Config.objects.get(name="infections").data
		if "infection_set" in self.data:
			setTime = datetime.datetime().strptime(self.data["infection_set"],"%Y-%m-%d")
			dayGap = (datetime.datetime.now() - setTime).days
			for key in infections:
				if dayGap > int(key):
					infection = "infection" + key
					self.data[infection] = self.infection
			self.save()

	def updateContact(self,date,contacts):
		propagation = Config.objects.get(name="propagation").data["levels"]
		tracks = Config.objects.get(name="propagation").data["tracks"]
		propagations = []
		for key in propagation:
			propagation[key]["name"] = key
			smallest = True
			for index in range(len(propagations)):
				if propagation[key]["contacts"] > propagations[index]:
					propagations.insert(index,propagation[key],propagation[key])
					smallest = False
					break
			if smallest:
				propagations.append(propagation[key])
		reverse = {}
		newInfections = {}
		if date in self.contacts and self.contacts[date]:
			for contact_id in contacts:
				if contact_id not in propagation.keys():
					if contact_id in self.contacts and self.contacts[date][contact_id]:
						if self.contacts[date][contact_id] < contacts[contact_id]:
							self.contacts[date][contact_id] = contacts[contact_id]
					elif contacts[contact_id] > 3:
						self.contacts[date][contact_id] = contacts[contact_id]
		else:
			self.contacts[date] = contacts

		for item in propagations:
			if item["name"] not in self.contacts[date]:
				self.contacts[date][item["name"]] = []

		for contact_id in self.contacts[date]:
			index = 0
			if contact_id not in propagation.keys():
				target_id = int(contact_id)
				for item in propagations:
					index += 1
					if self.contacts[date][contact_id] > item["contacts"]:
						newInfectionLevel = False
						if item["name"] not in self.contacts[date]:
							self.contacts[date][item["name"]] = [target_id]
							newInfectionLevel = True
						else:
							if target_id not in self.contacts[date][item["name"]]:
								self.contacts[date][item["name"]].append(target_id)
								newInfectionLevel = True
						if item["name"] not in newInfections:
							if newInfectionLevel:
								newInfections[item["name"]] = [contact_id]
						else:
							if newInfectionLevel:
								newInfections[item["name"]].append(contact_id)
						break

				for i in range(index, len(propagations)):
					if propagations[i]["name"] in self.contacts[date] and target_id in self.contacts[date][propagations[i]["name"]]:
						self.contacts[date][propagations[i]["name"]].remove(target_id)
						if propagations[i]["name"] in reverse:
							reverse[propagations[i]["name"]].append(target_id)
						else:
							reverse[propagations[i]["name"]] = [target_id]
		if str(self.status) in tracks and self.risk > 0:
			for key in reverse:
				infection = propagation[key]["infection"]
				Profile.objects.filter(id__in=reverse[key]).update(risk=100 - (100-F("risk"))/(1-infection*F("infection")))
			for key in newInfections:
				infection = propagation[key]["infection"]
				Profile.objects.filter(id__in=newInfections[key]).update(risk=100 -(100-F("risk"))*(1-infection*F("infection")))

	def syncContact(self, profile):
		today = datetime.datetime.now().strftime("%Y-%m-%d")
		if today in profile.contacts:
			profile_id = str(profile.id)
			id = str(self.id)
			if today in self.contacts and self.contacts[today]:
				if profile_id in self.contacts[today] and self.contacts[today][profile_id]:
					if self.contacts[today][profile_id] < profile.contacts[today][id]:
						self.contacts[today][profile_id] = profile.contacts[today][id]
				else:
					self.contacts[today][profile_id] = profile.contacts[today][id]
			else:
				self.contacts[today] = {profile_id:profile.contacts[today][id]}
		self.save()

	def getRisk(self):
		risk = Risk.objects.exclude(level__gt=self.risk).order_by("-level")[0]
		colors = Config.objects.get(name='colors')
		colors_cfg = colors.data
		risk_dict = {}
		risk_dict["title"] = risk.title
		risk_dict["value"] = self.risk
		risk_dict["policy"] = risk.policy
		risk_dict["color"] = colors_cfg[risk.color]
		return risk_dict

class Form(models.Model):
	name = models.CharField(max_length=256)
	description = models.TextField(max_length=1024)
	url = models.CharField(max_length=1024)
	form = JSONField(default={})

class Place(models.Model):
	name = models.CharField(max_length=256)
	profile = models.ForeignKey(Profile)
	data = JSONField(default={})

class Risk(models.Model):
	name = models.CharField(max_length=256)
	title = models.TextField(max_length=1024)
	type = models.SmallIntegerField(default=0)
	level = models.SmallIntegerField(default=0)
	isolation = models.BooleanField(default=False)
	test = models.BooleanField(default=False)
	color = models.CharField(max_length=256, blank=True)
	policy = JSONField(default={})

class Config(models.Model):
	name = models.CharField(max_length=256)
	data = JSONField(default={})