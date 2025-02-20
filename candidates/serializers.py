from rest_framework import serializers
from .models import (Candidate, CV, CVData, Job, JobSearch, Payment, CreditPurchase, Template, Location, Keyword,
                     Price, Pack, AbstractTemplate, Favorite, Ad, Question, AnswerOption, CandidateResponse,
                     CareerTranslation, Career)
from django.contrib.auth.models import User
from rest_framework.response import Response
from langdetect import detect, LangDetectException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
        use_url=True
    )

    class Meta:
        model = Candidate
        fields = ['id', 'first_name', 'last_name', 'phone', 'age', 'city', 'country', 'credits', 'profile_picture', 'user']

    def validate_profile_picture(self, value):
        """
        Ensure the profile picture is valid or None.
        """
        if value:
            if not hasattr(value, 'name') or not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise serializers.ValidationError("Invalid file type. Only PNG, JPG, and JPEG are allowed.")
        return value


class TemplateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="abstract_template.name", read_only=True)
    reference = serializers.CharField(source="abstract_template.reference", read_only=True)
    templateData = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = [
            "id", "name", "language", "reference", "identity", "templateData", "created_at", "updated_at"
        ]

    def get_templateData(self, obj):
        """
        Return the nested structure for `templateData`, mimicking the old serializer.
        """
        return {
            "identity": obj.abstract_template.reference,
            "template": obj.abstract_template.name,
            "company_logo": obj.company_logo,
            "page": obj.page,
            "certifications": obj.certifications,
            "education": obj.education,
            "experience": obj.experience,
            "volunteering": obj.volunteering,
            "interests": obj.interests,
            "languages": obj.languages,
            "projects": obj.projects,
            "references": obj.references,
            "skills": obj.skills,
            "social": obj.social,
            "theme": obj.theme,
            "personnel": obj.personnel,
            "typography": obj.typography,
        }


class AbstractTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractTemplate
        fields = ["id", "name", "reference", "image", "created_at", "updated_at"]


class CVDataSerializer(serializers.ModelSerializer):
    cv_id = serializers.IntegerField(source='cv.id', read_only=True)
    title = serializers.SerializerMethodField()

    class Meta:
        model = CVData
        fields = [
            "cv_id", "title", "name", "email", "phone", "age", "city",
            "work", "educations", "languages", "skills", "interests",
            "social", "certifications", "projects", "volunteering",
            "references", "headline", "summary",
        ]

    def get_title(self, obj):
        return obj.headline

    def to_internal_value(self, data):
        # Convert empty strings to None for nullable fields
        for field in self.fields:
            if data.get(field) == "":
                data[field] = None
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """
        Override the to_representation method to ensure JSONFields return
        an empty list instead of None.
        """
        representation = super().to_representation(instance)

        # List of JSONFields in the CVData model
        json_fields = [
            "work", "educations", "languages", "skills", "interests",
            "social", "certifications", "projects", "volunteering", "references"
        ]

        # Replace None with an empty list for JSONFields
        for field in json_fields:
            if representation.get(field) is None:
                representation[field] = []

        return representation


class JobSerializer(serializers.ModelSerializer):
    similarity_scores = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    click_count = serializers.SerializerMethodField()
    is_ad = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ["id", "title", "description", "requirements", "company_name", "company_logo", "company_size", "location", "linkedin_profiles", "employment_type", "original_url", "min_salary", "max_salary", "benefits", "skills_required", "posted_date", "industry", "job_type", "similarity_scores", "is_favorite", "is_applied", "click_count", "is_ad"]

    def get_similarity_scores(self, obj):
        similarity_scores_map = self.context.get('similarity_scores_map', {})
        return similarity_scores_map.get(obj.id, [])

    def get_is_favorite(self, obj):
        favorites_map = self.context.get('favorites_map', {})
        return favorites_map.get(obj.id, None)

    def get_is_applied(self, obj):
        applies_map = self.context.get('applies_map', {})
        return applies_map.get(obj.id, False)

    def get_click_count(self, obj):
        return obj.clicked_by.count()

    def get_is_ad(self, obj):
        return False


class AdSerializer(serializers.ModelSerializer):
    is_ad = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ["id", "title", "description", "original_url", "background", "ad_type", "is_ad"]

    def get_is_ad(self, obj):
        return True


class CareerTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerTranslation
        fields = ["language", "title", "transition_path"]


class CareerSerializer(serializers.ModelSerializer):
    translations = CareerTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Career
        fields = ["id", "group_identifier", "translations"]


class CVSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    career = CareerSerializer()
    cv_data = CVDataSerializer()
    thumbnail = serializers.ImageField(read_only=True)
    template = serializers.SerializerMethodField()
    lang = serializers.SerializerMethodField()

    class Meta:
        model = CV
        fields = ['id', 'uid', 'name', 'original_file', 'cv_type', 'generated_pdf',
                  'thumbnail', 'cv_data', 'job', 'career', 'template', 'lang', 'created_at', 'updated_at']

    def get_template(self, obj):
        # Serialize the associated template, if it exists
        if obj.template:
            return TemplateSerializer(obj.template).data
        return None

    def get_lang(self, obj):
        if obj.cv_data:
            languages = []
            for experience in obj.cv_data.work:
                responsibilities = experience.get('responsibilities', '')
                if responsibilities:
                    try:
                        languages.append(detect(responsibilities))
                    except LangDetectException:
                        pass
            return max(set(languages), key=languages.count) if languages else None
        return None


class JobSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSearch
        fields = ["similarity_score", "search_date", "status"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class CreditPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPurchase
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['credits', 'price']


class PackSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True)

    class Meta:
        model = Pack
        fields = ['id', 'name', 'description', 'is_active', 'prices']
        

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializes the Question model with language codes and flattens answer set details.
    """
    language = serializers.CharField(source="language.code", read_only=True)  # Return language code instead of ID
    answer_set_id = serializers.SerializerMethodField()
    answer_set_occurrence = serializers.SerializerMethodField()
    answer_set_options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "group_identifier",
            "language",
            "name",
            "text",
            "description",
            "question_type",
            "answer_set_id",
            "answer_set_occurrence",
            "answer_set_options",
        ]

    def get_answer_set_id(self, obj):
        """ Returns the ID of the answer set if it exists, else None. """
        return obj.answer_set.id if obj.answer_set else None

    def get_answer_set_occurrence(self, obj):
        """
        Returns the occurrence of this question using the same answer set.
        """
        if obj.answer_set:
            all_questions = Question.objects.filter(answer_set=obj.answer_set).order_by("id")
            return list(all_questions.values_list("id", flat=True)).index(obj.id) + 1
        return None

    def get_answer_set_options(self, obj):
        """ Returns the list of answer options (ID + text) if the question has an answer set. """
        if obj.answer_set:
            return list(obj.answer_set.options.values("id", "text"))  # Fetch ID and text as objects
        return None

    def validate(self, data):
        """
        Ensure that the combination of group_identifier and language is unique.
        """
        group_identifier = data.get("group_identifier")
        language = data.get("language")

        if Question.objects.filter(group_identifier=group_identifier, language=language).exists():
            raise serializers.ValidationError(
                {"error": "A question with this group identifier already exists in the selected language."}
            )

        return data


class CandidateResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)  # Include full question details
    selected_option = serializers.PrimaryKeyRelatedField(
        queryset=AnswerOption.objects.all(), required=False, allow_null=True
    )
    selected_options = serializers.PrimaryKeyRelatedField(
        queryset=AnswerOption.objects.all(), many=True, required=False, allow_null=True
    )

    class Meta:
        model = CandidateResponse
        fields = [
            "id", "candidate", "question", "text_answer", "selected_option", "selected_options", "created_at"
        ]
        read_only_fields = ["created_at"]

    def validate(self, data):
        """ Ensure that response type matches the question type. """
        question = self.context["question"]

        # if question.question_type == Question.TEXT and not data.get("text_answer"):
        #     raise serializers.ValidationError({"text_answer": "This question requires a text response."})
        #
        # if question.question_type == Question.RADIO and not data.get("selected_option"):
        #     raise serializers.ValidationError({"selected_option": "This question requires a single selected option."})
        #
        # if question.question_type == Question.CHECKBOX and not data.get("selected_options"):
        #     raise serializers.ValidationError({"selected_options": "This question requires multiple selected options."})

        return data