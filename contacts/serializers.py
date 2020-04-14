#  Copyright (c) 2020. @ Xiang Liu

from contacts.models import *
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['contacts', 'phone', 'places', 'data','risk']


class FormSerializer(serializers.ModelSerializer):
	form = serializers.JSONField()


	data = serializers.SerializerMethodField("get_form_data")

	def get_form_data(self,obj):
		request = self.context["request"]
		if obj.name=="set_profile" and request.user.is_authenticated:
			return request.user.info.data
		else:
			return {}


	class Meta:
		model = Form
		fields = ['name', 'description','url','form','data']



class PlaceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Place
		fields = ['name','data']

class RiskSerializer(serializers.ModelSerializer):
	policy = serializers.JSONField()
	class Meta:
		model = Risk
		fields = ['name','title','type','level','color','policy','isolation','test']

class ConfigSerializer(serializers.ModelSerializer):
	data = serializers.JSONField()
	class Meta:
		model = Config
		fields = ['name', 'data']